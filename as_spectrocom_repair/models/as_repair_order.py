# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import time
import datetime
from datetime import datetime, timedelta, date
from time import mktime
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
class as_repair_order(models.Model):
    _inherit = 'repair.order'

    fees_lines = fields.One2many(
        'repair.fee', 'repair_id', 'Operations',
        copy=True, readonly=True, states={'confirmed': [('readonly', False)],'draft': [('readonly', False)]})
    
    operations = fields.One2many(
        'repair.line', 'repair_id', 'Parts',
        copy=True, readonly=True, states={'confirmed': [('readonly', False)],'draft': [('readonly', False)]})

    picking_count = fields.Integer(compute='_compute_picking_count')
    picking_ids = fields.One2many('stock.picking', 'as_repair_id', string='Transferencias')
    location_dest_id = fields.Many2one('stock.location', 'Ubicación Destino')
    invoice_number = fields.Char(compute='_compute_invoice_count',string="Factura")
    sale_count = fields.Integer(compute='_compute_sale_order')
    sale_ids = fields.One2many('sale.order', 'as_repair_id', string='Cotizaciones')
    as_sheet_id = fields.Many2one('as.repair.order.sheet', string="Informe de Reparación", readonly=True, copy=False)
    as_in_report = fields.Boolean(string='En Reporte')
    fecha_confirmar=fields.Date(string="Fecha Inicial")
    fecha_finalizar=fields.Date(string="Fecha final")
    as_numero_serie = fields.Char(compute='_compute_lote',string="Nro serie")
    as_proposal_id = fields.Many2one('as.proposal.aux', string='Plantilla de Campos')
    as_texto = fields.Char(string='Texto')
    as_conditions_lines = fields.Many2many('as.proposal.conditions.sale.aux', string='Condiciones de la Propuesta')
    as_amount_total = fields.Float('Total', compute='_as_amount_total', store=True)
    as_internal_notes = fields.Text('Nota Recepción')

    @api.depends('product_id')
    def _compute_lote(self):
        for x in self:
            x.as_numero_serie = x.lot_id.name

    @api.depends('operations.price_subtotal','fees_lines.price_subtotal')
    def _as_amount_total(self):
        for order in self:
            total = sum(fees_lines.price_unit for fees_lines in order.fees_lines)
            
            # for fees in order.fees_lines:
            order.as_amount_total = total
                

    @api.onchange('as_proposal_id')
    def get_as_proposal_id(self):
        """Funcion para extraer condiciones de la propuesta"""
        for sale in self:   
            aux = sale.as_proposal_id.as_conditions_lines
            line_proposal = []
            vals = {}
            sale.as_conditions_lines = []
            # sale.write({'as_conditions_lines': [(0, 0, {})]}) 
            # self.env.cr.execute("delete from as_proposal_conditions_sale WHERE as_sale_id = "+ str(sale.id.origin))
            if sale.as_proposal_id.as_conditions_lines:
                for proposal in sale.as_proposal_id.as_conditions_lines:
                    vals_val = {
                        'name': proposal.name,
                        'as_valor': proposal.as_valor,
                        'as_valor_2': proposal.as_valor_2,
                        # 'as_sale_id': sale.id,
                        'as_proposal_id': sale.as_proposal_id.id,
                    }
                    aux = self.env['as.proposal.conditions.sale.aux'].create(vals_val)
                    line_proposal.append(aux.id)
            sale.as_conditions_lines = line_proposal

    def boton_add(self):
        for sale in self:   
            aux = sale.as_proposal_id.as_conditions_lines
            aux2 = sale.as_proposal_id.as_conditions_lines
            line_proposal = []
            vals = {}
            sale.as_conditions_lines = []

            for proposal in sale.as_conditions_lines:
                line_proposal.append(proposal.id)
            vals_val = {
                'name': sale.as_texto,
                'as_valor': '',
                # 'as_sale_id': sale.id,
                'as_proposal_id': False,
            }
                
            aux = self.env['as.proposal.conditions.sale.aux'].create(vals_val)
            line_proposal.append(aux.id)

        sale.as_conditions_lines = line_proposal
        sale.as_texto = ''
    
    state = fields.Selection(selection_add=[('recepcion', 'Recepcion Equipo')])
    def boton_recepcion(self):
        pass
    def _create_sheet_from_repair(self):
        """Crear hoja de reparaciones"""
        if any(expense.as_in_report != False or expense.as_sheet_id for expense in self):
            raise UserError(_("No puede informar dos veces la misma línea!"))
        if any(not expense.product_id for expense in self):
            raise UserError(_("You can not create report without product."))

        todo = self
        sheet = self.env['as.repair.order.sheet'].create({
            'name': todo[0].name,
            'as_partner_id': todo[0].partner_id.id,
            'as_user_id': todo[0].user_id.id,
            'as_location_id': todo[0].location_id.id,
            'as_location_dest_id': todo[0].location_dest_id.id,
            'as_pricelist_id': todo[0].pricelist_id.id,
            'as_repair_line_ids': [(6, 0, todo.ids)]
        })
        return sheet

    def action_submit_repair(self):
        """enviar reparacion"""
        sheet = self._create_sheet_from_repair()
        for line in sheet:
            for repair in line.as_repair_line_ids:
                repair.as_in_report = True
        return {
            'name': _('New Repair Report'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'as.repair.order.sheet',
            'target': 'current',
            'res_id': sheet.id,
        }

    def get_sale(self):
        sale = self.env['sale.order'].search([('as_repair_id','=',self.id)])
        return sale
    def action_reparado(self):
        return self.env.ref('as_spectrocom_repair.as_reporte_orden_trabajo_pdf').report_action(self)
    def action_confirmado(self):
        return self.env.ref('as_spectrocom_repair.as_reporte_recepcion_equipos_pdf').report_action(self)
    
    def _lineas_ordenadas(self):
        order_lines= self.env['repair.fee'].sudo().search([('repair_id','=',self.id)])
        return order_lines
    # def _nombre_reparacion(self):
    #     order_lines= self.env['repair.fee'].sudo().search([('repair_id','=',self.id)])
    #     return order_lines
    
    ####Funcion para quitar elementos de texto enriquecido en reportes
    def get_pobs(self,text):
        textstr = ''
        if text:
            textstr = BeautifulSoup(text,"html.parser").text
        return textstr
    def info_sucursal(self, requerido):
        info = ''
        diccionario_dosificacion = {
            'nombre_empresa' : self.env.user.company_id.name or '',
            'nit' : self.env.user.company_id.vat or '',
            'direccion1' : self.env.user.company_id.street or '',
            'telefono' : self.env.user.company_id.phone or '',
            'ciudad' : self.env.user.company_id.city or '',
            'pais' : self.env.user.company_id.country_id.name or '',
        }
        info = diccionario_dosificacion[str(requerido)]
        return info

    def action_repair_cotizacion(self):
        for repair in self:
            lines = []
            for line_sale in repair.operations:
                val_line = {
                    'product_id': line_sale.product_id.id,
                    'name': line_sale.name,
                    'product_uom_qty': line_sale.product_uom_qty,
                    'product_uom': line_sale.product_uom.id,
                    'price_unit': line_sale.price_unit,
                    'tax_id': line_sale.tax_id.ids,
                }
                lines.append((0, 0,val_line))
            for line_sale in repair.fees_lines:
                val_line = {
                    'product_id': line_sale.product_id.id,
                    'name': line_sale.name,
                    'product_uom_qty': line_sale.product_uom_qty,
                    'product_uom': line_sale.product_uom.id,
                    'price_unit': line_sale.price_unit,
                    'tax_id': line_sale.tax_id.ids,

                }
                lines.append((0, 0,val_line))
            so_vals = {
                'partner_id': repair.partner_id.id,
                'order_line': lines,
                'as_repair_id': repair.id,
                'company_id': repair.company_id.id,
                'pricelist_id': repair.pricelist_id.id,
                'currency_id': repair.currency_id.id,
                'as_alias_lugar': 'RR',
            }
            sale_order = self.env['sale.order'].create(so_vals)

    @api.depends('invoice_id')
    def _compute_invoice_count(self):
        for order in self:
            if order.invoice_id:
                order.invoice_number = order.invoice_id.name
            else:
                order.invoice_number = ''


    @api.depends('picking_ids')
    def _compute_picking_count(self):
        for order in self:
            order.picking_count = len(order.picking_ids)

    @api.depends('sale_ids')
    def _compute_sale_order(self):
        for order in self:
            order.sale_count = len(order.sale_ids)


    def action_stock_picking(self):
        self.ensure_one()
        action_picking = self.env.ref('stock.action_picking_tree_ready')
        action = action_picking.read()[0]
        action['context'] = {}
        action['domain'] = [('id', 'in', self.picking_ids.ids)]
        return action

    def action_sale_repair(self):
        self.ensure_one()
        action_sale = self.env.ref('sale.action_quotations_with_onboarding')
        action = action_sale.read()[0]
        action['context'] = {}
        action['domain'] = [('id', '=', self.sale_ids.ids)]
        return action


    def action_repair_end(self):
        """ Writes repair order state to 'To be invoiced' if invoice method is
        After repair else state is set to 'Ready'.
        @return: True
        """
        self.fecha_finalizar= fields.Date.context_today(self)
        if self.filtered(lambda repair: repair.state != 'under_repair'):
            raise UserError(_("La reparación debe estar en reparación para finalizar la reparación."))
        for repair in self:
            repair.write({'repaired': True})
            vals = {'state': 'done'}
            # vals['move_id'] = repair.action_repair_done().get(repair.id)
            if not repair.invoice_id and repair.invoice_method == 'after_repair':
                vals['state'] = '2binvoiced'
            repair.write(vals)
        if self.as_sheet_id:
            total = len(self.as_sheet_id.as_repair_line_ids)
            total_hecho = len(self.as_sheet_id.as_repair_line_ids.filtered(lambda order_repair: order_repair.state == 'done'))
            if total == total_hecho:
                self.as_sheet_id.state = 'done'
        return True

    def action_validate(self):
        self.ensure_one()
        self.fecha_confirmar= fields.Date.context_today(self)
        if self.filtered(lambda repair: any(op.product_uom_qty < 0 for op in repair.operations)):
            raise UserError(_("You can not enter negative quantities."))
        return self.action_repair_confirm()

    def action_repair_confirm(self):
        """ Repair order state is set to 'To be invoiced' when invoice method
        is 'Before repair' else state becomes 'Confirmed'.
        @param *arg: Arguments
        @return: True
        """
        if self.filtered(lambda repair: repair.state != 'draft'):
            raise UserError(_("Only draft repairs can be confirmed."))
        self._check_company()
        self.operations._check_company()
        self.fees_lines._check_company()
        before_repair = self.filtered(lambda repair: repair.invoice_method == 'b4repair')
        before_repair.write({'state': '2binvoiced'})
        to_confirm = self - before_repair
        to_confirm_operations = to_confirm.mapped('operations')
        if len(self.operations) > 0:
            self.create_picking()
        to_confirm_operations.write({'state': 'confirmed'})
        to_confirm.write({'state': 'confirmed'})
        return True

    def create_picking(self):
        picking = self.env['stock.picking'].create({
            'partner_id': self.partner_id.id,
            'picking_type_id': self.env.ref('stock.picking_type_internal').id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'origin': self.name,
            'as_repair_id': self.id,
        })
        for line_move in self.operations:
            lot_id = [line_move.lot_id.id]
            move_id = self.env['stock.move'].create({
                'name':line_move.product_id.name,
                'location_id': line_move.location_id.id,
                'location_dest_id': line_move.location_dest_id.id,
                'product_id':line_move.product_id.id,
                'product_uom':line_move.product_id.uom_id.id,
                'product_uom_qty': line_move.product_uom_qty,
                'picking_id': picking.id,
                'as_repair_line':line_move.id,
            })
        picking.action_assign()
        for lines in self.operations:
            for move in picking.move_line_ids_without_package:
                if lines.id == move.move_id.as_repair_line.id:
                    move.lot_id = lines.lot_id

        return True


class RepairLine(models.Model):
    _inherit = 'repair.line'

    as_stock_fisico_actual_repair_to = fields.Float(string="Stock Actual", compute='_detalle_producto')

    @api.onchange('product_id')
    def detalle_producto(self):
        for linea_reparacion in self:
            linea_reparacion.location_dest_id = self.repair_id.location_dest_id


    @api.onchange('product_id')
    def _detalle_producto(self):
        for record in self:
            if record:
                if record.repair_id.partner_id:
                    for producto in record:
                        if record.display_name == producto.display_name:
                            # _logger.info('\n\n %r \n\n', [moduleObj,record.route_id])
                            #se comento lo refente a stock virtual
                            cantidad = producto.product_id.qty_available
                            #previsto = producto.product_id.virtual_available
                            if (producto.product_id.id and record.location_id):
                                ruta = record.location_id.id
                                # cantidad= producto.product_id.with_context(location=[ruta]).qty_available
                                #previsto =  producto.product_id.with_context(location=[ruta]).virtual_available
                                record.as_stock_fisico_actual_repair_to = cantidad
                            else:
                                # Cuando tengamos el modulo de inventarios pero no estemos trabajando con rutas, mostraremos la cantidad total del producto en todas las ubicaciones

                                record.as_stock_fisico_actual_repair_to = producto.product_id.qty_available
                            record.as_stock_fisico_actual_repair_to = cantidad
                            #record.as_stock_virtual_actual = previsto
                else:
                    record.as_stock_fisico_actual_repair_to = 0.0
            else:
                record.as_stock_fisico_actual_repair_to = 0.0
