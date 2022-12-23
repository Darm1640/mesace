# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    
    as_codigo_venta = fields.Char(string="Codigo:", compute="obtener_numero_cotizacion")
    
    def obtener_numero_cotizacion(self):
        move_lines = self.env['sale.order'].sudo().search([('name', '=', self.origin)],limit=1)
        numero_codigo=''
        if move_lines:
            numero_codigo=move_lines.as_template_id.name
        if self.as_solicitud_id:
            numero_codigo = self.as_solicitud_id.as_project_id.as_codigo
        self.as_codigo_venta=numero_codigo
        
    project_id = fields.Many2one('project.task', string="Proyecto")
    as_solicitud_id = fields.Many2one('as.request.materials', string="Proyecto")
    as_custodio_id = fields.Many2one('hr.employee', string="Técnico responsable",compute="obtener_cotization_id")
    as_bandera_system = fields.Boolean(string="Devuelto", default=False)
    as_es_salida = fields.Boolean(string="Aceptado", default=False)

    def obtener_cotization_id(self):
        for x in self:
            move_lines = x.env['sale.order'].sudo().search([('name', '=', x.origin)],limit=1)
            numero_cotization=''
            if move_lines:
                numero_cotization=move_lines.as_custodio_id
            x.as_custodio_id=numero_cotization
        # move_lines = self.env['sale.order'].sudo().search([('name', '=', self.origin)],limit=1)
        # numero_cotization=''
        # if move_lines:
        #     numero_cotization=move_lines.as_custodio_id
        # self.as_custodio_id=numero_cotization
    
    def button_validate(self):
        res = super().button_validate()
        if self.picking_type_code != 'incoming':
            for move_line in self.move_ids_without_package:
                if move_line.as_product_stock < 0 and move_line.reserved_availability >0:
                    raise UserError(_("No se puede validar debido a que el producto %s, tiene stock menor a 0.") % (move_line.product_id.name)) 
                if move_line.as_solicitud_line_id:
                    move_line.as_solicitud_line_id.lot_id = move_line.lot_ids

        # self.validate_webservice()
        movs = self.env['stock.picking'].search([('as_solicitud_id','=',self.as_solicitud_id.id)])
        cont = 0
        for movimiento in movs:
            if movimiento.state == 'done':
                cont += 1
            x = len(movs)
            materials = self.env['as.request.materials'].search([('id','=',self.as_solicitud_id.id)])
            if x == cont:
                if materials.state != 'done':
                    materials.as_bandera = True
                    materials.as_date_done = datetime.now()
                materials.state = 'done'
        if self.as_bandera_system == True:
            materials.state = 'aceptado'
        return res
class StockMove(models.Model):
    _inherit = "stock.move"

    as_solicitud_line_id = fields.Many2one('as.request.lines', string="Proyecto")

class StockLocation(models.Model):
    _inherit = "stock.location"

    as_solicitud = fields.Boolean(string="Aparecera en Solicitud de Materiales", default=False)
