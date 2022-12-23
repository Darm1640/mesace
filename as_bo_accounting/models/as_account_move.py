# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime
from dateutil import relativedelta
from odoo.exceptions import UserError
from datetime import timedelta, datetime
import calendar
import time
from dateutil.relativedelta import relativedelta
import json
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"
    # secuencia = fields.Many2one('ir.sequence', string='Secuencia Diario',related="journal_id.secure_sequence_id",store=True)
    as_secuencia_id = fields.Many2one('ir.sequence', string='Secuencia Diario',related="journal_id.sequence_id",store=True)
    as_proveedor_factura =fields.Char(compute='_get_vendor_display_info',string="Proveedor")
    as_fecha_factura=fields.Char(string='fecha de Factura', compute="_get_as_fecha_factura")
    as_origin_invoice=fields.Char(string='Documento Origen', compute="_get_as_fecha_factura_origin")
    as_fecha_vencimiento=fields.Char(string='Fecha de Vencimiento', compute="_get_as_fecha_factura_vencimiento")
    as_contable = fields.Boolean(string='No es contable', default = False)
    as_si_contable = fields.Boolean(string='Es contable')
    
    def as_cancel_move(self):
        self.button_draft()
        self.button_cancel()

    @api.depends('posted_before', 'state', 'journal_id', 'date')
    def _compute_name(self):
        for move in self:
            if not move.as_contable:
                if not move.journal_id.sequence_id:
                    return super(AccountMove, self)._compute_name()
                sequence_id = move._get_sequence()
                if not sequence_id:
                    raise UserError('Please define a sequence on your journal.')
                if not move.sequence_generated and move.state == 'draft':
                    move.name = '/'
                elif not move.sequence_generated and move.state != 'draft':
                    if move.move_type == 'entry':
                        move.name = sequence_id.with_context({'ir_sequence_date': move.date, 'bypass_constrains': True}).next_by_id(sequence_date=move.date)
                    else:
                        if move.move_type == 'in_invoice':
                            move.name = sequence_id.with_context({'ir_sequence_date': move.date, 'bypass_constrains': True}).next_by_id(sequence_date=move.date)
                        else:
                            move.name = sequence_id.with_context({'ir_sequence_date': move.invoice_date, 'bypass_constrains': True}).next_by_id(sequence_date=move.invoice_date)
                    move.sequence_generated = True
            else:
                if not move.journal_id.as_sequence_wa_id:
                    raise UserError('Defina secuencia en diario, para facturas que no tienen asiento.')
                if not move.journal_id.as_sequence_wa_id and move.state == 'draft':
                    move.name = '/'
                elif move.journal_id.as_sequence_wa_id and move.state != 'draft':
                    move.name = move.journal_id.as_sequence_wa_id.with_context({'ir_sequence_date': move.invoice_date, 'bypass_constrains': True}).next_by_id(sequence_date=move.invoice_date)
                    move.as_secuencia_id = move.journal_id.as_sequence_wa_id


    @api.onchange('ref')
    def as_glosa_line(self):
        for account in self:
            if account.move_type == 'retry':
                for line in account.line_ids:
                    line.name = account.ref
    
    def _get_vendor_display_info(self):
        for account in self:
            vendor_display_name = account.partner_id.name
            account.as_proveedor_factura = vendor_display_name
        return True
    def _get_as_fecha_factura(self):
        for account in self:
            vendor_display_name = account.invoice_date
            account.as_fecha_factura = vendor_display_name
        return True
    def _get_as_fecha_factura_origin(self):
        for account in self:
            vendor_display_name = account.invoice_origin
            account.as_origin_invoice = vendor_display_name
        return True
    def _get_as_fecha_factura_vencimiento(self):
        for account in self:
            vendor_display_name = account.invoice_date_due
            account.as_fecha_vencimiento = vendor_display_name
        return True
    
    def get_partner(self,name):
        factura = self.env['account.move'].sudo().search([('name', '=', name)])
        if factura:
            if len(factura) > 1:
                return self.partner_id.name
            else:
                return factura.partner_id.name
        else:
            return self.partner_id.name

    def get_descripcion(self):
        for lineas in self.invoice_line_ids:
            return lineas.as_descripcion

    def get_exclude_from_invoice_tab(self):
        for lineas in self.invoice_line_ids:
            return lineas.exclude_from_invoice_tab

    def get_numero_fac(self,name):
        # factura = self.env['account.invoice'].sudo().search([('number', '=', name)])
        for lineas in self.line_ids:
            if lineas.payment_id.invoice_line_ids:
                for lines in lineas.payment_id.invoice_line_ids:
                    # if lines.invoice_number == 0:
                    #     return lines.as_numero_factura_compra
                    # else:
                    return 'Nº de factura : ' + str(lines.name)
            else:
                for lines in lineas.invoice_id:
                    # if lines.invoice_number == 0:
                    #     return 'Nº de factura : ' + str(lines.as_numero_factura_compra)
                    # else:
                    return 'Nº de factura : ' + str(lines.name)

    def get_print_lines_media_carta_led(self, invoice_obj):
        # filas_por_factura = self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_filas_por_factura_ledezma')
        # if not filas_por_factura:
        size_allowed = 26
        # else:
        #     size_allowed = int(filas_por_factura)
        count = 0
        res = []
        cont = 0
        for line in invoice_obj.line_ids:
            if line.name != False:
                x = line.name.rsplit('Factura-',1)
                cont += 1
                vals = {
                    'code'   : line.account_id.code,
                    'code_name'     : line.account_id.name,
                    'debit'       : line.debit,
                    'credit' : line.credit,
                    'name'   : x[0],
                }
            else:
                vals = {
                    'code'   : line.account_id.code,
                    'code_name'     : line.account_id.name,
                    'debit'       : line.debit,
                    'credit' : line.credit,
                    'name'   : 'N/H',
                }
            res.append(vals)
            count += 1
        if cont == 3:
            size_allowed = 20
        if cont == 4:
            size_allowed = 20
        if cont == 5:
            size_allowed = 19
        if cont == 6:
            size_allowed = 18
        if cont == 7:
            size_allowed = 17
        if cont == 8:
            size_allowed = 16
        if cont == 9:
            size_allowed = 0
        if cont == 10:
            size_allowed = 30
        if cont == 11:
            size_allowed = 0
        if cont == 12:
            size_allowed = 0
        if count < size_allowed:
            for i in range(size_allowed-count):
                vals = {
                    'code'   : 'ls',
                    'code_name'     : '',
                    'debit'       : '',
                    'credit' : '',
                    # 'subtotal'   : '',
                }
                res.append(vals)
        return res

    def _sumas_debe(self):
        total_debe=0.00
        for line in self.line_ids:
            total_debe +=line.debit
        return total_debe

    def _sumas_haber(self):
        total_haber=0.00
        for line in self.line_ids:
            total_haber +=line.credit
        return total_haber

    def info_sucursal(self, requerido):
        info = ''
        diccionario_dosificacion= {}
        # qr_code_id = self.env['qr.code'].search([('id', 'in', self.env['res.users'].browse(self._context.get('uid')).dosificaciones.ids),('activo', '=', True)],limit=1)
        # if qr_code_id:
        #     diccionario_dosificacion = {
        #         'nombre_empresa' : qr_code_id.nombre_empresa or '',
        #         'nit' : qr_code_id.nit_empresa or '',
        #         'direccion1' : qr_code_id.direccion1 or '',
        #         'telefono' : qr_code_id.telefono or '',
        #         'ciudad' : qr_code_id.ciudad or '',
        #         'pais' : self.env.user.company_id.country_id.name or '',
        #         'actividad' : qr_code_id.descripcion_actividad or '',
        #         'sucursal' : qr_code_id.sucursal or '',
        #         'fechal' : qr_code_id.fecha_limite_emision or '',
        #     }
        # else:
        diccionario_dosificacion = {
            'nombre_empresa' : self.env.user.company_id.name or '',
            'nit' : self.env.user.company_id.vat or '',
            'direccion1' : self.env.user.company_id.street or '',
            'telefono' : self.env.user.company_id.phone or '',
            'ciudad' : self.env.user.company_id.city or '',
            'sucursal' : self.env.user.company_id.city or '',
            'pais' : self.env.user.company_id.country_id.name or '',
            'actividad' :  self.env.user.company_id.name or '',
            'fechal' : self.env.user.company_id.phone or '',

        }
        info = diccionario_dosificacion[str(requerido)]
        return info

class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    as_contable = fields.Boolean(related="move_id.as_contable",store=True)

    def _get_price_total_and_subtotal(self, price_unit=None, quantity=None, discount=None, currency=None, product=None, partner=None, taxes=None, move_type=None):
        self.ensure_one()
        return self._get_price_total_and_subtotal_model(
            price_unit=price_unit or self.price_unit,
            quantity=quantity or self.quantity,
            discount=discount or self.discount,
            currency=currency or self.currency_id,
            product=product or self.product_id,
            partner=partner or self.partner_id,
            taxes=taxes or self.tax_ids,
            move_type=move_type or self.move_id.move_type,
        )
        
    @api.onchange('product_id','journal_id')
    def _cuenta_contable_default(self):
        for line in self:
            if line.as_move_type == 'in_invoice' and  line.product_id.name == False:
                line.account_id = False
    
    
    @api.onchange('as_discount_amount')
    def _as_discount_factura(self):
        for line in self:
            if line.as_discount_amount > 0.0:
                if (line.price_unit*line.quantity) > 0:
                    line.sudo().discount = (line.as_discount_amount*100)/(line.price_unit*line.quantity)

    @api.onchange('discount','price_unit')
    def _as_discount_inversa(self):
        for line in self:
            if line.discount > 0.0:
                if (line.price_unit*line.quantity) > 0:
                    line.sudo().as_discount_amount = (line.discount*(line.price_unit*line.quantity))/100

    def as_discount_inversa2(self):
        for line in self:
            monto_discount = 0.0
            if line.discount > 0.0:
                if (line.price_unit*line.quantity) > 0:
                    line.sudo().as_discount_amount = (line.discount*(line.price_unit*line.quantity))/100
                    monto_discount = (line.discount*(line.price_unit*line.quantity))/100
            return monto_discount

    as_discount_amount = fields.Float(string="Monto Descuento", store=True)
    as_placa = fields.Many2one('fleet.vehicle', string ="Nro de Placa", help='Este campo solo es requerido para gastos de gasolina, cambio de aceite entre otros.')

    @api.onchange('account_id')
    def as_glosa_line(self):
        for accountline in self:
            if accountline.move_id.move_type == 'entry':
                accountline.name = accountline.move_id.ref

    # @api.model
    # def create(self, vals):
    #     res = super().create(vals)
    #     res._as_discount_factura()
    #     res._as_discount_inversa()
    #     return res

class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    @api.model
    def _query_get(self, options, domain=None):
        domain += [('as_contable', '=', False)]
        domain = self._get_options_domain(options) + (domain or [])
        self.env['account.move.line'].check_access_rights('read')

        query = self.env['account.move.line']._where_calc(domain)

        # Wrap the query with 'company_id IN (...)' to avoid bypassing company access rights.
        self.env['account.move.line']._apply_ir_rules(query)

        return query.get_sql()
