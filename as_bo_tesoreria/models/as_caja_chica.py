# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo.exceptions import UserError
from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare
from odoo.tools.float_utils import float_is_zero
_logger = logging.getLogger(__name__)


class AsCajaChica(models.Model):
    _name = 'as.caja.chica'

    tipo_de_compra = [
        ('1','Actividad gravada'),
        ('2','Actividad no gravada'),
        ('3','Sujetas a proporcionalidad'),
        ('4','Exportaciones'),
        ('5','Interno/Exportaciones')
    ]

    @api.depends('as_tipo_factura','as_amount')
    def _compute_tipo_factura(self):
        for invoice in self:
            monto = 0.0
            if invoice.as_tipo_factura:
                monto = invoice.as_amount * ((invoice.as_tipo_factura.as_factor or 0)/100.0)
            invoice.update({'as_monto_exento' : monto,'as_impuesto_especifico' : monto})

    #formatea el campo codigo de control
    @api.onchange('as_codigo_control_compra')
    def change_as_codigo_control_compra(self):
        cont=0
        if self.as_codigo_control_compra:
            codigo=self.as_codigo_control_compra
            codigo= codigo.replace('-','')
            codigo= codigo.replace("'",'')
            self.as_codigo_control_compra = ''
            if len(codigo) > 10:
                raise UserError(_("No puede exceder los 5 pares de caracteres permitidos"))
            else:
                permitidos = ('ABCDEF0123456789')
                for char in codigo.upper():
                    if char not in permitidos: 
                        raise UserError(_("No puede se permiten letras diferentes a de A-F ni caracteres extras a numeros"))
                    else:
                        cont+=1
                        if (cont % 2)==0: 
                            if cont >= len(codigo):
                                self.as_codigo_control_compra += char
                            else:
                                self.as_codigo_control_compra += char + '-'
                        else:
                            self.as_codigo_control_compra += char

    def _get_default_retencion(self):
        acc = self.env['as.tipo.retencion'].sudo().search([('name', '=', 'Sin retencion')], limit=1)
        if acc:
            return acc.id
        else:
            return self.env['as.tipo.retencion']

    def _get_default_facturas(self):
        acc = self.env['as.tipo.factura'].sudo().search([('name', '=', 'Normal')], limit=1)
        if acc:
            return acc.id
        else:
            return self.env['as.tipo.factura']

    def _get_default_compra(self):
        acc = self.env['as.tipo.compra'].sudo().search([('name', '=', 'Compras para mercado interno con destino a actividades gravadas')], limit=1)
        if acc:
            return acc.id
        else:
            return self.env['as.tipo.compra']

    def _get_default_currency(self):
        return self.env.user.company_id.currency_id

    name = fields.Char('Titulo')
    as_nota = fields.Char('Comentario')
    date = fields.Date(string='Fecha Registro', default=fields.Date.context_today)
    as_partner_id = fields.Many2one('res.partner', string="Empresa")
    currency_id = fields.Many2one('res.currency', string='Moneda', default=_get_default_currency)
    move_line_id  = fields.Many2many('account.move', string='Linea asiento')
    as_account_gasto_id = fields.Many2one('account.account', string="Cuenta de Gasto")
    as_tipo_documento  = fields.Selection([('Factura','Factura'),('Prefactura/Recibo','Prefactura/Recibo')] ,'Tipo de documento', help=u'Tipo de documento que pertenece la factura.', default='Prefactura/Recibo')
    as_tipo_factura  = fields.Many2one('as.tipo.factura',string='Tipo de Factura', help=u'Tipo de factura para el registro de libro de compra y calculo del monto exento automatico.', default=_get_default_facturas)
    as_amount = fields.Float('Monto')
    as_tesoreria_id = fields.Many2one('as.tesoreria',string="Caja de Tesoreria")
    state = fields.Selection([('cancel', 'Cancelado'),('new', 'Nuevo'), ('data', 'Ventas'),('confirm', 'Procesado')], string='Status', required=True, readonly=True, copy=False, default='new')
    as_tipo_retencion = fields.Many2one('as.tipo.retencion',string='Tipo de Retencion',default=_get_default_retencion)
    as_tipo_de_compra = fields.Selection(selection=tipo_de_compra, string="Tipo de compra", default='1')
    as_numero_factura_compra  = fields.Char(string='No Factura', help='Numero de factura.')
    as_codigo_control_compra = fields.Char('Codigo Control')
    as_numero_autorizacion_compra  = fields.Char(string='No Autorizacion', help='Numero de Autorizacion.', digits=(15, 0))
    as_placa = fields.Many2one('fleet.vehicle', string ="Nro de Placa", help='Este campo solo es requerido para gastos de gasolina, cambio de aceite entre otros.')
    as_monto_exento = fields.Float('Monto Exento.',store=True, readonly=True, compute='_compute_tipo_factura', help=u'factor de descuento total por monto excento de tipo de de factura de compra.')
    as_factor = fields.Float(related="as_tipo_factura.as_factor", store=True, string='Factor %')
    as_impuesto_especifico = fields.Float(string='Otro no sujeto a credito fiscal', default=0.0)
    as_numero_dui = fields.Char(string='No DUI', help='Numero de DUI si corresponde a una factura.',default='0')
    as_invoice_id = fields.Many2one('account.move', string="Factura", copy=False)
    product_id = fields.Many2one('product.product', string="Servicio", domain=[('type', '=', 'service')])
    product_name_id = fields.Many2one('as.product.name', string="Servicio")
    as_facturado = fields.Boolean(string="Facturado", default=False)
    as_invoice_fiscal = fields.Boolean('Es Fiscal', default=False)
    as_scan_qr = fields.Char(string="QR factura", help="Click aqui para que el cursor lea el codigo de QR de la factura de compra")
    as_importe_ic = fields.Float(string='Importe ICE ', default=0.0)
    as_importe_iehd = fields.Float(string='Importe IEHD ', default=0.0)
    as_importe_ipj = fields.Float(string='Importe IPJ ', default=0.0)
    as_tasas = fields.Float(string='Tasas ', default=0.0)
    as_exentos = fields.Float(string='Importes exentos', default=0.0)
    as_gift_card = fields.Float(string='Importes Gift Card', default=0.0)
    as_compras_gravadas = fields.Float(string='Importe compras gravadas a tasa cero', default=0.0)
    as_tipo_compra = fields.Many2one('as.tipo.compra',string='Tipo de compra', default=_get_default_compra)
    account_analytic_id = fields.Many2one('account.analytic.account', string='Cuenta Analitíca', groups="analytic.group_analytic_accounting")
    as_tax_ids = fields.Many2many('account.tax',string='Impuestos')
    as_interes = fields.Float(string='Intereses ', default=0.0)
    as_descuento_tesoreria = fields.Float('Descuento')

    """ Funcion de escanear qr """
    @api.onchange('as_scan_qr')
    def escanear_codigo_qr(self):
        if self.as_scan_qr:
            array = (self.as_scan_qr).split(']')
            if len(array) != 12:
                raise UserError(_("Formato de QR invalido"))
            # self.as_nit = array[0]
            self.as_numero_factura_compra = str(int(array[1]))
            self.as_numero_autorizacion_compra = array[2]
            fecha = array[3].split("-")
            self.date = fecha[2] +"-"+ fecha[1] + "-" + fecha[0]
            self.as_codigo_control_compra = array[6]
            self.as_codigo_control_compra = self.as_codigo_control_compra.replace("'",'-')
            self.as_tasas = array[8]
            self.as_compras_gravadas = array[9]
            self.as_scan_qr = None

    @api.onchange('product_name_id')
    def get_product_name_id(self):
        for line in self:
            line.as_account_gasto_id = line.product_name_id.as_account_gasto_id

    @api.onchange('as_partner_id','date','product_name_id','as_numero_factura_compra')
    def get_as_nota(self):
        fecha = ''
        if self.date:
            fecha = self.date.strftime('%d-%m-%Y')
        self.as_nota = str(fecha)+' '+str(self.as_numero_factura_compra)+' '+str(self.as_partner_id.name)+' '+str(self.product_name_id.name)

    @api.onchange('as_tipo_factura','as_amount')
    def onchange_as_tipo_factura(self):  
        if self.as_tipo_factura.as_calcular: 
            self.as_impuesto_especifico =  (self.as_amount*(self.as_tipo_factura.as_factor/100))

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('account.chica') or _('New')
        result = super(AsCajaChica, self).create(vals)
        if result.as_tesoreria_id.journal_id.as_fiscal == True and result.as_invoice_fiscal == False: 
            raise UserError(_("El diario requiere que el campo *Es fiscal* sea tiqueado"))
        if result.as_tesoreria_id.journal_id.as_fiscal == False and result.as_invoice_fiscal == True: 
            raise UserError(_("El diario requiere que el campo *Es fiscal* no este tiqueado"))
        if result.as_amount <= 0:
            raise UserError(_("Monto no puede estar en Cero"))
        return result


    def get_sale_process(self):
        as_bandera = self.env['account.journal'].sudo().search([("id","=",self.as_tesoreria_id.journal_id.id)])
        if as_bandera.as_fiscal == True and self.as_invoice_fiscal == False: 
            raise UserError(_("El diario requiere que el campo *Es fiscal* sea tiqueado"))
        if as_bandera.as_fiscal == False and self.as_invoice_fiscal == True: 
            raise UserError(_("El diario requiere que el campo *Es fiscal* no este tiqueado"))
        if self.as_amount <= 0:
            raise UserError(_("Monto no puede estar en Cero"))
        for line in self.as_tesoreria_id:
            cantidad = len(line.as_caja_chica_ids)
            cont = 0
            for line1 in line.as_caja_chica_ids:
                if line1.as_invoice_fiscal == True:
                    cont += 1
            if cont == 0:
                 line.as_es_fiscal = False
            elif cont == cantidad:
                # self.update({'as_es_fiscal': s})
                line.as_es_fiscal = True
            else:
                line.as_es_fiscal = False
        self.action_create_invoice()
        return True


    def cancel_payment(self):
        self.state='cancel'
        if self.as_invoice_id:
            self.as_invoice_id.button_draft()
            self.as_invoice_id.button_cancel()

    #crear factura de importacion
    def action_create_invoice(self):
        """Create the invoice associated to the PO.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoice_vals_list = []
        for order in self:
            if order.as_invoice_id:
                raise UserError(_('Ya ha generado una factura, cancele el registro.'))
            if not order.as_partner_id:
                raise UserError(_('El proveedor es obligatorio.'))
            order = order.with_company(order.env.user.company_id)
            # Invoice values.
            invoice_vals = order._prepare_invoice()
            # Invoice line values (keep only necessary sections).
          
            if not float_is_zero(order.as_amount, precision_digits=precision):
                invoice_vals['invoice_line_ids'].append((0, 0, order._prepare_account_move_line()))
            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise UserError(_('There is no invoiceable line. If a product has a control policy based on received quantity, please make sure that a quantity has been received.'))
        if not invoice_vals_list:
            raise UserError(_('There is no invoiceable line. If a product has a control policy based on received quantity, please make sure that a quantity has been received.'))

        # 3) Create invoices.
        moves = self.env['account.move']
        AccountMove = self.env['account.move'].with_context(default_move_type='in_invoice')
        for vals in invoice_vals_list:
            moves |= moves.with_company(vals['company_id']).create(vals)
            moves.as_amount_discount = self.as_descuento_tesoreria 
        self.as_invoice_id = moves
        self.as_invoice_id.action_post()
        if self.as_invoice_id:
            if self.as_tipo_factura.as_seg_anticipado:
                for line_move1 in self.as_invoice_id.line_ids:
                    if line_move1.account_id == self.as_invoice_id.partner_id.property_account_payable_id:
                        as_account_id = self.as_tesoreria_id.as_account_gasto_id.id
                        self.env.cr.execute('UPDATE account_move_line SET  account_id='+str(as_account_id)+' WHERE id='+str(line_move1.id))
                for line_move in self.as_invoice_id.invoice_line_ids:
                    as_account_id = self.product_name_id.as_account_gasto_id.id
                    self.env.cr.execute('UPDATE account_move_line SET  account_id='+str(as_account_id)+' WHERE id='+str(line_move.id))
        self.as_invoice_id.invoice_origin = self.as_tesoreria_id.name

        # for x in moves.invoice_line_ids:
        #     x.as_discount_amount = self.as_descuento_tesoreria 

        return moves

    def _prepare_invoice(self):
        """Prepare the dict of values to create the new invoice for a purchase order.
        """
        self.ensure_one()
        move_type = self._context.get('default_move_type', 'in_invoice')
        journal = self.as_tesoreria_id.journal_id
        if not journal:
            raise UserError(_('La caja no posee diario seleccionado.'))
        if self.as_partner_id.vat == False:
            raise UserError(_('Por favor ingrese nit') )
        if self.as_partner_id.as_razon_social == False:
            raise UserError(_('Por favor ingrese razon social') )
        if self.as_codigo_control_compra == False:
            if self.as_tipo_documento != "Prefactura/Recibo":
                raise UserError(_('Por favor ingrese codigo de control') )
        if self.as_tipo_factura == False:
            raise UserError(_('Por favor ingrese tipo de factura') )
        if self.as_numero_autorizacion_compra == False:
            if self.as_tipo_documento != "Prefactura/Recibo":
                raise UserError(_('Por favor ingrese numero de autorizacion') )
        if self.as_numero_factura_compra == False:
            if self.as_tipo_documento != "Prefactura/Recibo":
                raise UserError(_('Por favor ingrese numero de factura') )
        invoice_vals = {
            'move_type': move_type,
            'currency_id': self.env.user.company_id.currency_id.id,
            'invoice_user_id': self.env.user.id,
            'invoice_origin': self.name,
            'invoice_line_ids': [],
            'company_id': self.env.user.company_id.id,
            'partner_id': self.as_partner_id.id,
            'invoice_date' : self.date,
            'as_tipo_documento' : self.as_tipo_documento,
            'as_nit' : self.as_partner_id.vat,
            'as_contable' : True,
            'as_razon_social' : self.as_partner_id.as_razon_social,
            'as_numero_factura_compra' : self.as_numero_factura_compra,
            'as_codigo_control_compra' : self.as_codigo_control_compra,
            'as_numero_autorizacion_compra' : self.as_numero_autorizacion_compra,
            'as_tipo_factura' : self.as_tipo_factura.id,
            'as_impuesto_especifico' : self.as_impuesto_especifico,
            'as_tipo_retencion' : self.as_tipo_retencion.id,
            'invoice_origin' : self.name,
            'as_importe_ic':self.as_importe_ic,
            'as_importe_iehd':self.as_importe_iehd,
            'as_importe_ipj':self.as_importe_ipj,
            'as_tasas':self.as_tasas,
            'as_compras_gravadas':self.as_compras_gravadas,
            'as_tipo_compra':self.as_tipo_compra.id,
            'as_exentos':self.as_exentos,
            'as_gift_card':self.as_gift_card,
            'journal_id':self.as_tesoreria_id.journal_id.id,
            'as_is_gasto':True,
            'as_interes': self.as_interes,
            # 'as_amount_discount': self.as_descuento_tesoreria,
            
        }
        return invoice_vals

    def _prepare_account_move_line(self, move=False):
        self.ensure_one()
        taxes=[]
        price_unit = 0.0
        price_unit =  self.as_amount 
        account_id = self.product_name_id.as_account_gasto_id.id
        if self.as_tipo_factura.as_seg_anticipado:
            account_id =  self.as_tesoreria_id.journal_id.default_account_id.id    
        if self.as_tipo_documento == 'Factura':
            for x in self.as_tax_ids:
                taxes.append(x.id)
        res = {
            'name': '%s' % (self.as_nota),
            'product_id': False,
            'quantity': 1,
            'account_id': account_id,
            'price_unit': price_unit,
            'tax_ids': [(6, 0, taxes)],
            'as_discount_amount': self.as_descuento_tesoreria,
            'discount': (self.as_descuento_tesoreria*100)/(price_unit*1),
            'analytic_account_id':self.account_analytic_id.id,
        }
      
        res.update({
            # 'move_id': move.id,
            'currency_id': self.env.user.company_id.currency_id.id,
            'partner_id': self.as_partner_id.id,
        })
        return res