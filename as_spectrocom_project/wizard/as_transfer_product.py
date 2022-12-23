# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, except_orm, ValidationError
import re
import xlrd
from xlrd import open_workbook
import math
from odoo import tools
import logging
from io import BytesIO
from datetime import datetime, timedelta
from odoo.tests import Form
import base64
_logger = logging.getLogger(__name__)

class as_wizard_fromulas_stock(models.Model):
    _name="as.transfer.product"
    _description="Para Generar Transferencia"

    start_date  = fields.Date(string="Fecha Inicio", default=lambda *a: (datetime.now() - timedelta(hours = 4)).strftime('%Y-%m-%d'), required=True)
    end_date    = fields.Date(string="Fecha Final",  required=True)
    as_picking_type_id = fields.Many2one('stock.picking.type', 'Tipo Operación')
    as_location_id = fields.Many2one('stock.location', "Ubicación Origen")
    as_location_dest_id = fields.Many2one('stock.location', "Ubicación Destino")
    wiz_lineas = fields.Many2many('as.transfer.lines', string='Lineas')
    as_solicitud = fields.Many2one('as.request.materials', 'Solicitud de material')

    # @api.model
    # def default_get_movimientos(self, fields):
    #     res = super(as_wizard_fromulas_stock, self).default_get(fields)
    #     res_ids = self._context.get('active_ids')
    #     as_modelo = self._context.get('active_model')
    #     so_line_obj = self.env[as_modelo].browse(res_ids)
    #     res['as_solicitud'] = so_line_obj
    #     res['as_picking_type_id'] = so_line_obj.as_picking_type_id.id
    #     res['as_location_id'] = so_line_obj.as_location_id.id
    #     res['as_location_dest_id'] = so_line_obj.as_location_dest_id.id

    @api.model
    def default_get(self, fields):
        res = super(as_wizard_fromulas_stock, self).default_get(fields)
        res_ids = self._context.get('active_ids')
        as_modelo = self._context.get('active_model')
        so_line_obj = self.env[as_modelo].browse(res_ids)
        res['as_solicitud'] = so_line_obj
        res['as_picking_type_id'] = so_line_obj.as_picking_type_id.id
        res['as_location_id'] = so_line_obj.as_location_id.id
        res['as_location_dest_id'] = so_line_obj.as_location_dest_id.id
        dictlinestock = []
        if ('start_date','end_date') in res:
            for line in so_line_obj.lines_ids:
                if (line.as_deliver_date - timedelta(hours = 4)) >= res['start_date'] and (line.as_deliver_date - timedelta(hours = 4)) <= res['end_date']:
                    vasl={
                    'product_id': line.product_id.id,
                    'lot_id': line.lot_id.id,
                    'product_uom': line.product_uom.id,
                    'as_qty': line.as_product_qty,
                    'as_qty_done': 0.0,
                    'as_qty_diff': 0.0,
                    'as_solicitud_line': line.id,
                    }
                    dictlinestock.append([0, 0, vasl])

            res.update({
                'wiz_lineas': dictlinestock,
            
            })
        return res

    @api.onchange('start_date','end_date')
    def as_get_line_wiz(self):
        dictlinestock=[]
        self.wiz_lineas.unlink()
        if self.start_date and self.end_date:
            for line in self.as_solicitud.lines_ids:
                if (line.as_deliver_date - timedelta(hours = 4)) >= self.start_date and (line.as_deliver_date - timedelta(hours = 4)) <= self.end_date and not line.as_transfer:
                    vasl={
                    'product_id': line.product_id.id,
                    'lot_id': line.lot_id.id,
                    'product_uom': line.product_uom.id,
                    'as_qty': line.as_product_qty,
                    'as_qty_done': 0.0,
                    'as_qty_diff': 0.0,
                    'as_solicitud_line': line.id,
                    }
                    dictlinestock.append([0, 0, vasl])
            if dictlinestock:
                self.wiz_lineas = dictlinestock
            else:
                self.wiz_lineas = []

    def as_get_process(self):
        picking_ids = []
        #generar movimiento general
        picking_general = self.env['stock.picking'].create({
            'location_id': self.as_location_id.id,
            'location_dest_id': self.as_location_dest_id.id,
            'partner_id': self.env.user.partner_id.id,
            'picking_type_id': self.as_picking_type_id.id,
            'project_id': self.as_solicitud.as_project_id.id,
            'origin': self.as_solicitud.name,
        })
        for lines in self.wiz_lineas:
            move_id = self.env['stock.move'].create({
                'name': lines.product_id.name,
                'product_id': lines.product_id.id,
                'product_uom_qty': lines.as_qty,
                'product_uom': lines.product_uom.id,
                'picking_id': picking_general.id,
                'location_id': self.as_location_id.id,
                'location_dest_id': self.as_location_dest_id.id,
                
            })
            move_line_pbw = self.env['stock.move.line'].create({
                'product_id': lines.product_id.id,
                'product_uom_id': lines.product_uom.id,
                'picking_id': picking_general.id,
                'qty_done': lines.as_qty,
                'lot_id': lines.lot_id.id,
                'move_id': move_id.id,
                'location_id': self.as_location_id.id,
                'location_dest_id': self.as_location_dest_id.id
            })
            lines.as_solicitud_line.picking_general_id = picking_general.id
            lines.as_solicitud_line.as_transfer = True
            lines.as_solicitud_line.as_qty_done = lines.as_solicitud_line.as_qty_done+lines.as_qty
        picking_ids.append(picking_general.id)
        picking_general.action_assign()
        backorder_wizard_dict = picking_general.button_validate()
        if not backorder_wizard_dict:
            backorder_wizard = Form(self.env[backorder_wizard_dict['res_model']].with_context(backorder_wizard_dict['context'])).save()
            backorder_wizard.process()

        #general movimiento positivos diferencias
        movimiento_posi_div = False
        for lines in self.wiz_lineas:
            if lines.as_qty_diff > 0:
                movimiento_posi_div = True
        if movimiento_posi_div:
            picking_posi = self.env['stock.picking'].create({
                'location_id': self.as_location_id.id,
                'location_dest_id': self.as_location_dest_id.id,
                'partner_id': self.env.user.partner_id.id,
                'picking_type_id': self.as_picking_type_id.id,
                'project_id': self.as_solicitud.as_project_id.id,
                'origin': self.as_solicitud.name,
            })
            for lines in self.wiz_lineas:
                if lines.as_qty_diff > 0:
                    move_id = self.env['stock.move'].create({
                        'name': lines.product_id.name,
                        'product_id': lines.product_id.id,
                        'product_uom_qty': abs(lines.as_qty_diff),
                        'product_uom': lines.product_uom.id,
                        'picking_id': picking_posi.id,
                        'location_id': self.as_location_id.id,
                        'location_dest_id': self.as_location_dest_id.id,
                        
                    })
                    move_line_pbw = self.env['stock.move.line'].create({
                        'product_id': lines.product_id.id,
                        'product_uom_id': lines.product_uom.id,
                        'picking_id': picking_posi.id,
                        'qty_done': abs(lines.as_qty_diff),
                        'lot_id': lines.lot_id.id,
                        'move_id': move_id.id,
                        'location_id': self.as_location_id.id,
                        'location_dest_id': self.as_location_dest_id.id
                    })
                    lines.as_solicitud_line.picking_in_id = picking_posi.id
            picking_ids.append(picking_posi.id)
            picking_posi.action_assign()
            backorder_wizard_dictposi = picking_posi.button_validate()
            if not backorder_wizard_dictposi:
                backorder_wizard_posi = Form(self.env[backorder_wizard_dictposi['res_model']].with_context(backorder_wizard_dictposi['context'])).save()
                backorder_wizard_posi.process()
        #general movimiento negativos diferencias
        movimiento_nega_div = False
        for lines in self.wiz_lineas:
            if lines.as_qty_diff < 0:
                movimiento_nega_div = True
        if movimiento_nega_div:
            picking_nega = self.env['stock.picking'].create({
                'location_id': self.as_location_dest_id.id,
                'location_dest_id': self.as_location_id.id,
                'partner_id': self.env.user.partner_id.id,
                'picking_type_id': self.as_picking_type_id.id,
                'project_id': self.as_solicitud.as_project_id.id,
                'origin': self.as_solicitud.name,
            })
            for lines in self.wiz_lineas:
                if lines.as_qty_diff < 0:
                    move_id = self.env['stock.move'].create({
                        'name': lines.product_id.name,
                        'product_id': lines.product_id.id,
                        'product_uom_qty': abs(lines.as_qty_diff),
                        'product_uom': lines.product_uom.id,
                        'picking_id': picking_nega.id,
                        'location_id': self.as_location_dest_id.id,
                        'location_dest_id': self.as_location_id.id,
                        
                    })
                    move_line_pbw = self.env['stock.move.line'].create({
                        'product_id': lines.product_id.id,
                        'product_uom_id': lines.product_uom.id,
                        'picking_id': picking_nega.id,
                        'qty_done': abs(lines.as_qty_diff),
                        'lot_id': lines.lot_id.id,
                        'move_id': move_id.id,
                        'location_id': self.as_location_dest_id.id,
                        'location_dest_id': self.as_location_id.id,
                    })
                    lines.as_solicitud_line.picking_out_id = picking_nega.id
            picking_ids.append(picking_nega.id)
            picking_nega.action_assign()
            backorder_wizard_dictnega = picking_nega.button_validate()
            if not backorder_wizard_dictnega:
                backorder_wizard_nega = Form(self.env[backorder_wizard_dictnega['res_model']].with_context(backorder_wizard_dictnega['context'])).save()
                backorder_wizard_nega.process()
        cant = len(self.as_solicitud.lines_ids)
        cant_hecha = len(self.as_solicitud.lines_ids.filtered(lambda sol: sol.as_transfer == True))
        if cant == cant_hecha:
            self.as_solicitud.state = 'done'


class as_wizard_fromulas_lines(models.Model):
    _name="as.transfer.lines"
    _description="Modelo wizard para lineas"

    product_id = fields.Many2one('product.product', 'Producto')
    lot_id = fields.Many2one('stock.production.lot', 'Lote/Serie', domain="[('product_id', '=', product_id)]")
    product_uom = fields.Many2one('uom.uom', 'Unit of Measure', )
    as_qty = fields.Float(string = 'Cantidad')
    as_qty_done = fields.Float(string = 'Cantidad Efectiva')
    as_qty_diff = fields.Float(string = 'Diferencia')
    as_solicitud_line = fields.Many2one('as.request.lines', 'Linea de solicitud', )
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company)

    @api.onchange('as_qty','as_qty_done')
    def as_get_onchange(self):
        for line in self:
            line.as_qty_diff = line.as_qty-line.as_qty_done

