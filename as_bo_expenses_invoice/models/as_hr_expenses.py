# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError, MissingError
#Generacion del QR
import qrcode
import tempfile
import base64
from odoo.tools import float_is_zero
import datetime
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError, RedirectWarning, ValidationError
import odoo.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)
from odoo.tools.float_utils import float_round, float_compare
tipo_de_compra = [
    ('1','Actividad gravada'),
    ('2','Actividad no gravada'),
    ('3','Sujetas a proporcionalidad'),
    ('4','Exportaciones'),
    ('5','Interno/Exportaciones')
]

class hr_expense(models.Model):
    _inherit = 'hr.expense'

    """ Monto de acuerdo al tipo de factura """
    @api.depends('as_tipo_factura','total_amount')
    def _compute_tipo_factura(self):
        for invoice in self:
            monto = 0.0
            if invoice.as_tipo_factura:
                monto = invoice.total_amount * ((invoice.as_tipo_factura.as_factor or 0)/100.0)
            invoice.update({'as_monto_exento' : monto})
            
    @api.model
    def _default_journal(self):
        journal_type = 'purchase'
        company_id = self.env.company.id
        if journal_type:
            journals = self.env['account.journal'].search([('type', '=', journal_type), ('company_id', '=', company_id), ('name', '=', 'FACTURA DE PROVEEDOR')])
            if journals:
                return journals[0]
        return self.env['account.journal']

    as_tipo_documento  = fields.Selection([('Factura','Factura'),('Prefactura/Recibo','Prefactura/Recibo')] ,'Tipo de documento', help=u'Tipo de documento que pertenece la factura.', default='Factura')
    as_tipo_retencion = fields.Many2one('as.tipo.retencion',string='Tipo de Retencion', default=lambda self: self.env['as.tipo.retencion'].search([('name', '=', 'Sin retencion')],limit=1))
    as_tipo_factura  = fields.Many2one('as.tipo.factura','Tipo de Factura', help=u'Tipo de factura para el registro de libro de compra y calculo del monto exento automatico.', default=lambda self: self.env['as.tipo.factura'].search([('name', '=', 'Normal')],limit=1))
    as_tipo_de_compra = fields.Selection(selection=tipo_de_compra, string="Tipo de compra", default='1',help="Tipo de compra para libro de compras Ejemplo:\n1: Actividad gravada \n2:Actividad no gravada \n3:Sujetas a proporcionalidad \n4:Exportaciones \n5:Interno/Exportaciones ")
    as_numero_factura_compra  = fields.Char(string='No Factura', help='Numero de factura.')
    as_codigo_control_compra = fields.Char('Codigo Control')
    as_numero_autorizacion_compra  = fields.Char(string='No Autorizacion', help='Numero de Autorizacion.', digits=(15, 0))
    as_monto_exento = fields.Float('Monto Exento.',store=True, readonly=True, compute='_compute_tipo_factura', help=u'factor de descuento total por monto excento de tipo de de factura de compra.')
    as_factor = fields.Float(related="as_tipo_factura.as_factor", store=True, string='Factor %')
    as_pagado = fields.Float('Pagos', help=u'Pagos que se tiene de la factura.')
    as_saldo = fields.Float('Saldo', help=u'Saldo que se tiene de la factura.')
    as_cuenta_gasto = fields.Many2one('account.account', string="Cuenta de gasto") # Tiene que ser obligatorio.
    # Lector Codigo QR
    as_scan_qr = fields.Char(string="QR factura", help="Click aqui para que el cursor lea el codigo de QR de la factura de compra")
    as_plazo = fields.Integer(string="Nro cuotas", readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    as_fecha_plan = fields.Date(string="Fecha", readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    as_payment_teas_id = fields.Many2one('account.payment.term', string="Plazo de pago")
    as_impuesto_especifico = fields.Float(string='Otro no sujeto a credito fiscal', default=0.0)
    # as_costo_cero = fields.Boolean(string='Tasa en Cero', default=False)
    # as_iva = fields.Boolean(string='IVA', default=False)
    as_numero_dui = fields.Char(string='No DUI', help='Numero de DUI si corresponde a una factura.')
    as_supplier_costo = fields.Many2one('res.partner', 'Proveedor', help=u'Proveedor del costo de importacion.')
    as_nit = fields.Char(string="NIT")
    as_razon_social = fields.Char(string="Razon Social")
    as_invoice_id = fields.Many2one('account.move', string="Factura", copy=False)
    as_journal_id = fields.Many2one('account.journal', string="Diario",domain=[("type", "=", "purchase")],default=_default_journal )
    as_es_fiscal = fields.Boolean('Es Fiscal', default=False)
    as_importe_ic = fields.Float(string='Importe ICE ', default=0.0)
    as_importe_iehd = fields.Float(string='Importe IEHD ', default=0.0)
    as_importe_ipj = fields.Float(string='Importe IPJ ', default=0.0)
    as_tasas = fields.Float(string='Tasas ', default=0.0)
    as_exentos = fields.Float(string='Importes exentos', default=0.0)
    as_gift_card = fields.Float(string='Importes Gift Card', default=0.0)
    as_placa = fields.Many2one('fleet.vehicle', string ="Nro de Placa", help='Este campo solo es requerido para gastos de gasolina, cambio de aceite entre otros.')
    as_compras_gravadas = fields.Float(string='Importe compras gravadas a tasa cero', default=0.0)
    as_tipo_compra = fields.Many2one('as.tipo.compra',string='Tipo de compra', default=lambda self: self.env['as.tipo.compra'].search([('name', '=', 'Compras para mercado interno con destino a actividades gravadas')],limit=1))
    as_descuento_hr = fields.Float('Descuento')
    
    """ Funcion de escanear qr """
    @api.onchange('as_scan_qr')
    def escanear_codigo_qr(self):
        if self.as_scan_qr:
            array = (self.as_scan_qr).split(']')
            if len(array) != 12:
                raise UserError(_("Formato de QR invalido"))
            self.as_nit = array[0]
            self.as_numero_factura_compra = str(int(array[1]))
            self.as_numero_autorizacion_compra = array[2]
            fecha = array[3].split("-")
            self.date = fecha[2] +"-"+ fecha[1] + "-" + fecha[0]
            self.as_codigo_control_compra = array[6]
            self.as_codigo_control_compra = self.as_codigo_control_compra.replace("'",'-')
            self.as_tasas = array[8]
            self.as_compras_gravadas = array[9]
            self.as_scan_qr = None

    @api.onchange('as_supplier_costo')
    def aS_onchange_supplier(self):
        for gasto in self:
            gasto.as_nit = gasto.as_supplier_costo.vat
            gasto.as_razon_social = gasto.as_supplier_costo.as_razon_social

    @api.onchange('as_tipo_factura')
    def onchange_as_tipo_factura(self):  
        if self.as_tipo_factura.as_calcular: 
            self.as_impuesto_especifico =  (self.total_amount*(self.as_tipo_factura.as_factor/100))

    def action_create_invoice(self):
        """Create the invoice associated to the PO.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoice_vals_list = []
        for order in self:
            order = order.with_company(order.env.user.company_id)
            # Invoice values.
            invoice_vals = order._prepare_invoice()
            # Invoice line values (keep only necessary sections).
          
            if not float_is_zero(order.unit_amount, precision_digits=precision):
                invoice_vals['invoice_line_ids'].append((0, 0, order._prepare_account_move_line()))
            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise UserError(_('There is no invoiceable line. If a product has a control policy based on received quantity, please make sure that a quantity has been received.'))

        # 3) Create invoices.
        moves = self.env['account.move']
        AccountMove = self.env['account.move'].with_context(default_move_type='in_invoice')
        for vals in invoice_vals_list:
            moves |= AccountMove.with_company(vals['company_id']).create(vals)
            # moves.as_amount_discount = self.as_descuento_hr
            # factura_obj.action_invoice_open()
        self.as_invoice_id = moves.id
        self.as_invoice_id.action_post()
        for line_move in self.as_invoice_id.line_ids:
            if line_move.account_id == self.as_invoice_id.partner_id.property_account_payable_id:
                if not self.employee_id:
                    raise UserError(_("No ha selecciono Empleado"))
                if not self.employee_id.user_id:
                    raise UserError(_("Empleado no posee plantilla de usuario"))
                as_account_id = self.employee_id.user_id.partner_id.as_account_viatic.id
                if not as_account_id:
                    raise UserError(_("El empleado no posee cuenta de viaticos"))
                self.env.cr.execute('UPDATE account_move_line SET  account_id='+str(as_account_id)+' WHERE id='+str(line_move.id))
        # for x in moves.invoice_line_ids:
        #     x.as_discount_amount = self.as_descuento_hr 
        return moves

    def _prepare_invoice(self):
        """Prepare the dict of values to create the new invoice for a purchase order.
        """
        self.ensure_one()
        move_type = self._context.get('default_move_type', 'in_invoice')
        journal = self.as_journal_id
        # journal = self.env['account.move'].with_context(default_move_type=move_type)._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting purchase journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))
        # if self.as_nit == False and self.as_facturado == True:
        #     raise UserError(_('Por favor ingrese nit') )
        # if self.as_razon_social == False and self.as_facturado == True:
        #     raise UserError(_('Por favor ingrese razon social') )
        # if self.as_codigo_control_compra == False and self.as_facturado == True:
        #     raise UserError(_('Por favor ingrese codigo de control') )
        # if self.as_tipo_factura == False and self.as_facturado == True:
        #     raise UserError(_('Por favor ingrese tipo de factura') )
        # if self.as_numero_autorizacion_compra == False and self.as_facturado == True:
        #     raise UserError(_('Por favor ingrese numero de autorizacion') )
        # if self.as_numero_factura_compra == False and self.as_facturado == True:
        #     raise UserError(_('Por favor ingrese numero de factura') )
        invoice_vals = {
            'move_type': move_type,
            'currency_id': self.env.user.company_id.currency_id.id,
            'invoice_user_id': self.env.user.id,
            'invoice_origin': self.name,
            'invoice_line_ids': [],
            'company_id': self.env.user.company_id.id,
            'partner_id': self.as_supplier_costo.id,
            'invoice_date' : self.date,
            'as_tipo_documento' : self.as_tipo_documento,
            'ref' : self.name+' - '+str(self.id),
            'as_nit' : self.as_nit,
            'journal_id' : self.as_journal_id.id,
            'as_razon_social' : self.as_razon_social,
            'as_numero_factura_compra' : self.as_numero_factura_compra,
            'as_codigo_control_compra' : self.as_codigo_control_compra,
            'as_numero_autorizacion_compra' : self.as_numero_autorizacion_compra,
            'as_tipo_factura' : self.as_tipo_factura.id,
            'as_impuesto_especifico' : self.as_impuesto_especifico,
            'as_tipo_retencion' : self.as_tipo_retencion.id,
            'invoice_origin' : self.name,
            'as_numero_dui' : self.as_numero_dui,
            'as_importe_ic':self.as_importe_ic,
            'as_importe_iehd':self.as_importe_iehd,
            'as_importe_ipj':self.as_importe_ipj,
            'as_tasas':self.as_tasas,
            'as_gift_card':self.as_gift_card,
            'as_compras_gravadas':self.as_compras_gravadas,
            'as_tipo_compra':self.as_tipo_compra.id,
            'as_exentos':self.as_exentos,
            'as_contable':True,
            # 'as_is_gasto':True,
            # 'as_amount_discount':self.as_descuento_hr,
        }
        return invoice_vals

    def _prepare_account_move_line(self, move=False):
        self.ensure_one()
        taxes=[]
        unit_amount = 0.0
        if self.as_tipo_documento =='Factura':
            for tax in self.tax_ids:
                taxes.append(tax.id)
   
        if self.as_tipo_factura.as_iva == False:
            unit_amount = self.unit_amount
        else:
            unit_amount =  self.unit_amount       
        res = {
            'name': '%s: %s' % (self.name, self.product_id.name),
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom_id.id,
            'quantity': self.quantity,
            'as_discount_amount': self.as_descuento_hr,
            'discount': (self.as_descuento_hr*100)/(unit_amount*self.quantity),
            'analytic_account_id': self.analytic_account_id.id,
            'price_unit': unit_amount,
            'tax_ids': [(6, 0, taxes)],
        }
      
        res.update({
            # 'move_id': move.id,
            'currency_id': self.env.user.company_id.currency_id.id,
            'partner_id': self.as_supplier_costo.id,
        })
        return res
    
    @api.onchange('as_tipo_documento')
    def quitar_impuesto(self):
        if self.tax_ids:
            self.tax_ids= None
            
