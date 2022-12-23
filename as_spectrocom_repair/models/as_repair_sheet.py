# -*- coding: utf-8 -*-
from unicodedata import name
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import time
import datetime
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date
from bs4 import BeautifulSoup
class as_stock_picking(models.Model):
    """Modelo que agrupa reparaciones"""
    _name = 'as.repair.order.sheet'
    _description = "Modelo para agrupar reparaciones"

    @api.depends('as_sale_ids')
    def _compute_sale_order(self):
        """funcion para cantidad de lineas en ventas"""
        for order in self:
            order.as_count_sale = len(order.as_sale_ids.ids)
            
    def confirmate_sheet(self):
        """funcion confirmar hoja"""
        self.state='confirmed'    
        for repair in self.as_repair_line_ids:
            if repair.state == 'draft':
                repair.action_validate()    
    
    def reparate_sheet(self):
        """funcion para hacer reparadas las lineas reparaciones del informe"""
        self.state='done'    
        for repair in self.as_repair_line_ids:
            if repair.state == 'confirmed':
                repair.action_repair_start()
                repair.action_repair_end()

    def _compute_account_move(self):
        """funcion para contar el numero de ventas en informe"""
        for order in self:
            invoice = []
            for sale in order.as_sale_ids:
                for inv in sale.invoice_ids:
                    invoice.append(inv.id)
            order.as_count_invoice = len(invoice)

    def compute_account_move(self):
        """funcion para generar las ventas de facturas"""
        self.ensure_one()
        action_sale = self.env.ref('account.view_move_form')
        action = action_sale.read()[0]
        action['context'] = {}
        invoice = []
        for sale in order.as_sale_ids:
            invoice.append(sale.id)
        action['domain'] = [('id', '=', invoice)]
        return action

    name = fields.Char(string="Titulo")
    as_repair_line_ids = fields.One2many('repair.order', 'as_sheet_id', string='Lineas de Reparaciones', copy=False)
    as_partner_id = fields.Many2one('res.partner', 'Cliente')
    as_cant = fields.Integer(compute='_compute_cantidad',string="Cantidad")
    as_user_id = fields.Many2one('res.users', 'Responsable')
    as_date_recepcion = fields.Date(string="Fecha Recepción",  default=lambda *a: (datetime.now() - timedelta(hours = 4)).strftime('%Y-%m-%d'), required=True)
    as_location_id = fields.Many2one('stock.location', 'Ubicación Origen')
    as_location_dest_id = fields.Many2one('stock.location', 'Ubicación Destino')
    as_pricelist_id = fields.Many2one('product.pricelist', 'Tarifa Piezas')
    as_pricelist_service_id = fields.Many2one('product.pricelist', 'Tarifa Servicio')
    as_currency_id = fields.Many2one(related='as_pricelist_id.currency_id')
    as_count_sale = fields.Integer(compute='_compute_sale_order')
    as_count_invoice = fields.Integer(compute='_compute_account_move')
    as_sale_ids = fields.One2many('sale.order', 'as_repair_sheet_id', string='Cotizaciones')
    as_sale_piezas = fields.Boolean(string="Cotizacion de piezas realizada")
    as_sale_servicio = fields.Boolean(string="Cotizacion de operaciones realizada")
    as_secuencia_reparaciones = fields.Integer(string="Reparacion")
    as_reference = fields.Char(string="Referencia para cotizaciones", required=True)

    company_id = fields.Many2one(
        'res.company', 'Company',
        readonly=True, required=True, index=True,
        default=lambda self: self.env.company)
    state = fields.Selection([
        ('draft', 'Reparación'),
        ('confirmed', 'Confirmado'),
        ('done', 'Procesado'),
    ], string='Estado',  default="draft")

    @api.depends('as_repair_line_ids')
    def _compute_cantidad(self):
        """cantidad de reparaciones"""
        for order in self:
            order.as_cant = len(order.as_repair_line_ids)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals_product in vals_list:
            secuence =  self.env['ir.sequence'].next_by_code('as.reparaciones.secuencia')
            vals_product['as_secuencia_reparaciones'] = secuence
        templates = super(as_stock_picking, self).create(vals_list)
        return templates

    def as_cotizacion_pieza(self):
        """Generar cotizaciones"""
        lines = []
        secuencia = 0
        for repair in self.as_repair_line_ids:
            if repair.operations:
                numero_serie = ''
                if repair.lot_id.name:
                    numero_serie = repair.lot_id.name
                diccionario = {
                    # 'order_id':sale_line.order_id.id,
                    'name':repair.product_id.name + ' SN ' + numero_serie,
                    'display_type':'line_section',
                    'sequence':secuencia
                    }
                # sale_line.env['sale.order.line'].create(diccionario)
                lines.append((0, 0,diccionario))
                for line_sale in repair.operations:
                    val_line = {
                        'product_id': line_sale.product_id.id,
                        'name': line_sale.name,
                        'as_repair_id': repair.id,
                        'product_uom_qty': line_sale.product_uom_qty,
                        'product_uom': line_sale.product_uom.id,
                        'price_unit': line_sale.price_unit,
                        'tax_id': line_sale.tax_id.ids,
                        'sequence':secuencia +1
                    }
                    lines.append((0, 0,val_line))
                if repair.internal_notes:
                    diccionario = {
                        # 'order_id':sale_line.order_id.id,
                        'name': repair.product_id.name + ' SN ' + numero_serie+' '+repair.internal_notes,
                        'display_type':'line_note',
                        'sequence':secuencia+2
                        }
                    # sale_line.env['sale.order.line'].create(diccionario)
                    lines.append((0, 0,diccionario))
                secuencia += 3
        if len(lines) <= 0:
            raise UserError(_("Las Reparaciones asociadas no posee lineas en piezas."))
        so_vals = {
            'partner_id': self.as_partner_id.id,
            'order_line': lines,
            'as_repair_sheet_id': self.id,
            'company_id': self.company_id.id,
            'pricelist_id': self.as_pricelist_id.id,
            'currency_id': self.as_currency_id.id,
            'as_alias_lugar': self.as_location_id.name,
            'as_referencia': self.as_reference,
        }
        sale_order = self.env['sale.order'].create(so_vals)
        self.as_sale_piezas = True


    def as_cotizacion_servicio(self):
        """Generar cotizaciones"""
        lines = []
        secuencia = 0
        for repair in self.as_repair_line_ids:
            if repair.fees_lines:
                numero_serie = ''
                if repair.lot_id.name:
                    numero_serie = repair.lot_id.name
                diccionario = {
                    # 'order_id':sale_line.order_id.id,
                    'name':repair.product_id.name + ' SN ' + numero_serie,
                    'display_type':'line_section',
                    'sequence':secuencia
                    }
                # sale_line.env['sale.order.line'].create(diccionario)
                lines.append((0, 0,diccionario))
                for line_sale in repair.fees_lines:
                    val_line = {
                        'product_id': line_sale.product_id.id,
                        'name': line_sale.name,
                        'as_repair_id': repair.id,
                        'product_uom_qty': line_sale.product_uom_qty,
                        'product_uom': line_sale.product_uom.id,
                        'price_unit': line_sale.price_unit,
                        'tax_id': line_sale.tax_id.ids,
                        'sequence':secuencia + 1

                    }
                    lines.append((0, 0,val_line))
                if repair.internal_notes:
                    diccionario = {
                        # 'order_id':sale_line.order_id.id,
                        'name': repair.product_id.name + ' SN ' + numero_serie+' '+repair.internal_notes,
                        'display_type':'line_note',
                        'sequence':secuencia+2
                        }
                    # sale_line.env['sale.order.line'].create(diccionario)
                    lines.append((0, 0,diccionario))
                secuencia += 3
        if len(lines) <= 0:
            raise UserError(_("Las Reparaciones asociadas no posee lineas en servicios."))
        so_vals = {
            'partner_id': self.as_partner_id.id,
            'order_line': lines,
            'as_repair_sheet_id': self.id,
            'company_id': self.company_id.id,
            'pricelist_id': self.as_pricelist_service_id.id,
            'currency_id': self.as_currency_id.id,
            'as_alias_lugar': self.as_location_id.name,
            'as_referencia': self.as_reference,
        }
        sale_order = self.env['sale.order'].create(so_vals)
        self.as_sale_servicio = True


    def action_sale_repair(self):
        """retornar reparacion """
        self.ensure_one()
        action_sale = self.env.ref('sale.action_quotations_with_onboarding')
        action = action_sale.read()[0]
        action['context'] = {}
        action['domain'] = [('id', '=', self.as_sale_ids.ids)]
        return action

    def action_informe_reparaciones(self):
        """utilidad para reporte """
        return self.env.ref('as_spectrocom_repair.as_informe_reparaciones').report_action(self)

    def action_informe_reparaciones_recepcion(self):
        """utilidad para reporte """
        return self.env.ref('as_spectrocom_repair.as_imprimir_informe_reparaciones').report_action(self)

    def get_pobs(self,text):
        """utilidad para reporte """
        textstr = ''
        if text:
            textstr = BeautifulSoup(text,"html.parser").text
        return textstr

    def _lineas_ordenadas(self):
        """utilidad para reporte """
        order_lines= self.env['repair.order'].sudo().search([('as_sheet_id','=',self.id)])
        for y in order_lines:
            aux=0
        return order_lines
    
    def as_get_date_literal(self,fecha):
        dia = datetime.strptime(str(fecha), '%Y-%m-%d').strftime('%d')
        mes = self.get_mes(datetime.strptime(str(fecha), '%Y-%m-%d').strftime('%m'))
        ano = datetime.strptime(str(fecha), '%Y-%m-%d').strftime('%Y')
        return str(dia)+' de '+ str(mes)+' de '+str(ano)
    
    def get_mes(self,mes):
        mesesDic = {
            "01":'Enero',
            "02":'Febrero',
            "03":'Marzo',
            "04":'Abril',
            "05":'Mayo',
            "06":'Junio',
            "07":'Julio',
            "08":'Agosto',
            "09":'Septiembre',
            "10":'Octubre',
            "11":'Noviembre',
            "12":'Diciembre'
        }
        return mesesDic[str(mes)]