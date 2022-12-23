# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import string
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta
from odoo.tests import Form, tagged
from werkzeug.urls import url_encode

class AsRquestMaterials(models.Model):
    """Modulo par almacenar informacion de solicitud de materiales"""
    _name = "as.request.materials"
    _description = 'Modulo par almacenar informacion de solicitud de materiales'
    _inherit = ['mail.thread']

    name = fields.Char(string="Titulo")
    as_picking_type_id = fields.Many2one('stock.picking.type', 'Tipo Operación', required=True)
    as_location_id = fields.Many2one('stock.location', "Ubicación Origen",
        default=lambda self: self.env['stock.picking.type'].browse(self._context.get('default_picking_type_id')).default_location_src_id, required=True)
    as_location_dest_id = fields.Many2one('stock.location', "Ubicación Destino",
        default=lambda self: self.env['stock.picking.type'].browse(self._context.get('default_picking_type_id')).default_location_dest_id, required=True)
    as_location_alquiler_id = fields.Many2one('stock.location', "Ubicación Alquiler Cliente", required=True)
    as_project_id = fields.Many2one('project.task', string="Proyecto")
    as_scheduled_date = fields.Date('Fecha Planificada', store=True,index=True, default=fields.Date.context_today, tracking=True)
    as_date_done = fields.Date('Fecha de Realizada', copy=False)
    user_id = fields.Many2one('res.users', string="Usuario")
    as_origin = fields.Char('Origen')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('to_prove', 'Aprobar'),
        ('confirmed', 'Esperando'),
        ('done', 'Hecho'),
        ('devuelto', 'Devuelto'),
        ('aceptado', 'Aceptado'),
        ('cancel', 'Cancelado'),
    ], string='Estado',  default="draft")
    lines_ids = fields.One2many('as.request.lines', 'as_request_id', string="Lineas de Productos")
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company)
    as_return_picks = fields.Many2many('stock.picking', string="Movimiento de Devolución")
    as_bandera = fields.Boolean(string="Devuelto", default=False,)
    as_gerente_id = fields.Many2one('res.users', string="Gerente",domain="[('as_aprobar_materiales', '=', True)]")
    as_approval = fields.Boolean(string="Permitido aprobar",compute="_get_approvals")
    as_fecha_instructiva = fields.Date('Fecha Instructiva de trabajo', compute='extraer_fecha_instrucutiva', readonly=True)
    picking_count = fields.Integer(compute='_compute_picking_count')
    as_nro_nota = fields.Char('Nro Nota Remisión')
    as_note = fields.Text('Observaciones')
    partner_id = fields.Char('Cliente', compute='_as_obtener_cliente')
    
    def _as_obtener_cliente(self):
        result = self.env['project.task'].search([('id','=',self.as_project_id.id)])
        if result:
            self.partner_id = result.partner_id
            return self.partner_id


    def _compute_picking_count(self):
        result = self.env['stock.picking'].search([('as_solicitud_id','=',self.id)])
        for order in self:
            order.picking_count = len(result)
            
    def action_picking_expense(self):
        self.ensure_one()
        action_pickings = self.env.ref('stock.action_picking_tree_all')
        action = action_pickings.read()[0]
        action['context'] = {}
        result = self.env['stock.picking'].search([('as_solicitud_id','=',self.id)])
        action['domain'] = [('id', 'in', result.ids)]
        return action


    @api.onchange("as_picking_type_id")
    def cambiar_valores_tipo_operacion(self):
        aux = 0
        for line in self:
            line.as_location_id=line.as_picking_type_id.default_location_src_id
            line.as_location_dest_id=line.as_picking_type_id.default_location_dest_id
    
    def extraer_fecha_instrucutiva(self):
        valor=0
        as_fecha_instructiva = ''
        if self.as_origin != False:
            lineas_instructiva=self.env['project.task'].sudo().search([('name','=',self.as_origin)],limit=1)
            if lineas_instructiva:
                lineas_projecto=self.env['sale.order'].sudo().search([('id','=',lineas_instructiva.sale_order_id.id)])
                if lineas_projecto:
                    lineas_venta=self.env['as.instructive.sale'].sudo().search([('as_sale_id','=',lineas_projecto.id)],limit=1)
                    if lineas_venta.as_fecha_planificada == False:
                        as_fecha_instructiva=''
                    else:
                        as_fecha_instructiva=lineas_venta.as_fecha_planificada
                    # return as_fecha_instructiva
        else:
            as_fecha_instructiva=''
        self.as_fecha_instructiva = as_fecha_instructiva
            
    def button_change_state_materials(self):
        #momentos para envio de emails 
        #CASO 7: AL PRESIONAR BOTON APROBAR        
        #el numero de la plantilla es el ID de la plantilla que corresponde
        valores_email = self.env['mail.template'].search([('id','=',149)])
        remitente = ''
        if valores_email:
            nombre_modelo = valores_email.model_id.model
            #envio de email con adjuntos
            self.env['mail.template'].sudo().as_send_email_sin_adjuntos(self, valores_email.id, nombre_modelo)
            if valores_email.as_mobile:
                number = valores_email.as_mobile
                if valores_email.as_desde and valores_email.as_asunto:
                    
                    if valores_email.as_desde == '${object.env.user.partner_id.email}':
                        remitente = str(self.env.user.partner_id.email)
                    if valores_email.as_desde == '${object.as_project_id.user_id.login}':
                        remitente = str(self.as_project_id.user_id.login)
                    if valores_email.as_desde != '${object.env.user.partner_id.email}' and valores_email.as_desde != '${object.as_project_id.user_id.login}':
                        remitente = str(valores_email.as_desde)
                    
                    mensajito = str('DE: ')+remitente+': '+ valores_email.as_asunto +': '+valores_email.as_mensaje_whatsapp_email +' '+str(self.as_project_id.partner_id.name) +'; Tarea: ' + str(self.as_project_id.name)
                    
                    self.env['as.whatsapp'].sudo().as_send_whatsapp(number,mensajito)
                    self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'CASO 7'</b>")
        
        #CASO 13: AL PRESIONAR BOTON APROBAR        
        #el numero de la plantilla es el ID de la plantilla que corresponde
        valores_email_seg = self.env['mail.template'].search([('id','=',151)])
        if valores_email_seg:
            nombre_modelo_seg = valores_email_seg.model_id.model
            #envio de email con adjuntos
            self.env['mail.template'].as_send_email_sin_adjuntos(self, valores_email_seg.id, nombre_modelo_seg)
            if valores_email_seg.as_mobile:
                number = valores_email_seg.as_mobile
                if valores_email_seg.as_desde and valores_email_seg.as_asunto:
                    
                    if valores_email_seg.as_desde == '${object.env.user.partner_id.email}':
                        remitente = str(self.env.user.partner_id.email)
                    if valores_email_seg.as_desde == '${object.as_project_id.user_id.login}':
                        remitente = str(self.as_project_id.user_id.login)
                    if valores_email_seg.as_desde != '${object.env.user.partner_id.email}' and valores_email_seg.as_desde != '${object.as_project_id.user_id.login}':
                        remitente = str(valores_email_seg.as_desde)
                    
                    mensajito = str('DE: ')+remitente+': '+ valores_email_seg.as_asunto + ': '+ valores_email_seg.as_mensaje_whatsapp_email +' '+str(self.as_project_id.partner_id.name) +'; Tarea: ' + str(self.as_project_id.name)
                    
                    self.env['as.whatsapp'].sudo().as_send_whatsapp(number,mensajito)
                    self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'Caso 13'</b>")
                
        for viaje in self:
            viaje.state = 'to_prove'
            # monto = viaje.total
        
            
    def button_confirm_material(self):
        for project in self:
            project.state = 'confirmed'
            # project.as_send_email([project.user_id.partner_id.id],'approval')

    @api.depends('state')
    def _get_approvals(self):
        for order in self:
            aprobar = False
            # monto = order.total
            usuario = order.env.user.id
            # rango_approval = self.env['as.level.approval'].sudo().search([('as_type','=','viajes'),('as_amount_min','<=',monto),('as_amount_max','>=',monto)],order=" id desc",limit=1)
            # if rango_approval:
            #     if usuario in rango_approval.as_users_ids.ids:
            #         aprobar = True 
            if usuario == order.as_gerente_id.id:
                aprobar = True 
            order.as_approval = aprobar
    
    # def get_sale(self):
    #     sale = self.env['sale.order'].search([('id','=',self.id)])
    #     return sale
    def _lineas_ordenadas(self):
        """generar lineas ordenadas"""
        definitiva = self.env['as.request.lines'].sudo()
        order_lines= self.env['as.request.lines'].sudo().search([('as_request_id','=',self.id)])
        for line in order_lines:
            cant = line.as_product_qty-line.as_devolver
            if cant > 0:
                definitiva += line
        return definitiva
    
    def action_hecho(self):
        #CASO 37: AL PRESIONAR BOTON GENERAR NOTA DE REMISION (materiales)        
        #el numero de la plantilla es el ID de la plantilla que corresponde
        valores_email_tresiete = self.env['mail.template'].search([('id','=',134)])   
        if valores_email_tresiete:
            nombre_modelo_tresiete = valores_email_tresiete.model_id.model
            #envio de email sin adjuntos
            self.env['mail.template'].as_send_email_sin_adjuntos(self, valores_email_tresiete.id, nombre_modelo_tresiete)
            if valores_email_tresiete.as_mobile:
                number_treitres = valores_email_tresiete.as_mobile
                if valores_email_tresiete.as_desde and valores_email_tresiete.as_asunto:
                    if valores_email_tresiete.as_desde == '${object.env.user.partner_id.email}':
                        remitente_seis = str(self.env.user.partner_id.email)
                    if valores_email_tresiete.as_desde == '${object.as_project_id.user_id.login}':
                        remitente_seis = str(self.as_project_id.user_id.login)
                    if valores_email_tresiete.as_desde != '${object.env.user.partner_id.email}' and valores_email_tresiete.as_desde != '${object.as_project_id.user_id.login}':
                        remitente_seis = str(valores_email_tresiete.as_desde)
                        
                    mensajito = str('DE: ')+ remitente_seis +': '+ valores_email_tresiete.as_asunto +': '+valores_email_tresiete.as_mensaje_whatsapp_email + str(self.as_project_id.name) +' cliente: '+str(self.as_project_id.partner_id.name)
                    
                    self.env['as.whatsapp'].sudo().as_send_whatsapp(number_treitres,mensajito)
                    self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'Caso 37'</b>")
                
        #CASO 40: AL PRESIONAR BOTON GENERAR NOTA DE REMISION (materiales)        
        #el numero de la plantilla es el ID de la plantilla que corresponde
        valores_email_cuarenta = self.env['mail.template'].search([('id','=',136)])
        if valores_email_cuarenta:
            nombre_modelo_tresiete = valores_email_cuarenta.model_id.model
            #envio de email sin adjuntos
            self.env['mail.template'].as_send_email_sin_adjuntos(self, valores_email_cuarenta.id, nombre_modelo_tresiete)
            if valores_email_cuarenta.as_mobile:
                number_treitres = valores_email_cuarenta.as_mobile
                if valores_email_cuarenta.as_desde and valores_email_cuarenta.as_asunto:
                    if valores_email_cuarenta.as_desde == '${object.env.user.partner_id.email}':
                        remitente_seis = str(self.env.user.partner_id.email)
                    if valores_email_cuarenta.as_desde == '${object.as_project_id.user_id.login}':
                        remitente_seis = str(self.as_project_id.user_id.login)
                    if valores_email_cuarenta.as_desde != '${object.env.user.partner_id.email}' and valores_email_cuarenta.as_desde != '${object.as_project_id.user_id.login}':
                        remitente_seis = str(valores_email_cuarenta.as_desde)
                        
                    mensajito = str('DE: ')+ remitente_seis +': '+ valores_email_cuarenta.as_asunto +': '+ valores_email_cuarenta.as_mensaje_whatsapp_email + str(self.as_project_id.name) +' cliente: '+str(self.as_project_id.partner_id.name)
                    
                    self.env['as.whatsapp'].sudo().as_send_whatsapp(number_treitres,mensajito)
                    self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'Caso 40'</b>")
                
        if not self.as_nro_nota:
            secuence =  self.env['ir.sequence'].next_by_code('as.nota.remision.code')
            self.as_nro_nota = secuence
        return self.env.ref('as_spectrocom_project.as_reporte_nota_remision').report_action(self)

    def action_copiar_lineas_ventas(self):
        aux = 0
        for res in self.as_project_id:
            # sale_line = self.env['sale.order.line'].search([('order_id','=',res.sale_order_id.id)])
            sale_line = self.env['sale.order.line'].sudo().search([('order_id','=',res.sale_order_id.id)])
            for lineas in sale_line:
                if lineas.display_type != 'line_section' and  lineas.display_type != 'line_note':
                    linea_material = self.env['as.request.lines'].create({
                        'product_id': lineas.product_id.id,
                        'product_uom': lineas.product_uom.id,
                        'as_request_id': self.id,
                        'as_product_qty': lineas.product_uom_qty,
                        'as_devolver': 0,
                        # 'lot_id': lineas.lot_id.id,
                        'as_alquiler': False,
                        'as_location_id': self.as_location_id.id,
                        'as_location_dest_id': self.as_location_dest_id.id
                    })

    def action_cancelar(self):
        movs = self.env['stock.picking'].search([('as_solicitud_id','=',self.id),('picking_type_code','=','internal')])
        out = self.env['stock.picking'].search([('origin','=',self.name),('picking_type_code','=','outgoing')])
        for picking_id_2 in movs: 
            # cont += 1
            # if cont == 1:
            #     continue
            if picking_id_2.state == 'done':
                if picking_id_2.as_bandera_system == True:
                    lotes = []
                    bandera = False
                    for line in picking_id_2.move_line_ids:
                        lotes.append({'product_id':line.product_id.id,'lot_id':line.lot_id.id})
                    StockReturnPicking = self.env['stock.return.picking']
                    stock_return_picking_form = Form(self.env['stock.return.picking']
                        .with_context(active_ids=picking_id_2.ids, active_id=picking_id_2.ids[0],
                        active_model='stock.picking'))
                    stock_return_picking = stock_return_picking_form.save()
                    cont =0
                    for move_line in picking_id_2.move_line_ids_without_package:
                        stock_return_picking.product_return_moves[cont].quantity = move_line.qty_done
                        cont += 1

                    res = stock_return_picking.create_returns()
                    return_pick = self.env['stock.picking'].browse(res['res_id'])
                    for move_line in return_pick.move_line_ids:
                        for lot_line in lotes:
                            if move_line.product_id.id == lot_line['product_id']:
                                move_line.update({'lot_id':lot_line['lot_id']})
                        move_line.qty_done= move_line.product_qty

                    return_pick.action_assign()
                    wiz_act = return_pick.button_validate()
                    if wiz_act != True:
                        wiz = Form(self.env[wiz_act['res_model']].with_context(wiz_act['context'])).save()
                        wiz.process()
            else:
                picking_id_2.action_cancel()
        # Devolucion de outs
        for picking_id in out: 
            if picking_id.state == 'done':
                lotes = []
                bandera = False
                for line in picking_id.move_line_ids:
                    lotes.append({'product_id':line.product_id.id,'lot_id':line.lot_id.id})
                StockReturnPicking = self.env['stock.return.picking']
                stock_return_picking_form = Form(self.env['stock.return.picking']
                    .with_context(active_ids=picking_id.ids, active_id=picking_id.ids[0],
                    active_model='stock.picking'))
                stock_return_picking = stock_return_picking_form.save()
                cont =0
                for move_line in picking_id.move_line_ids_without_package:
                    stock_return_picking.product_return_moves[cont].quantity = move_line.qty_done
                    cont += 1

                res = stock_return_picking.create_returns()
                return_pick = self.env['stock.picking'].browse(res['res_id'])
                for move_line in return_pick.move_line_ids:
                    for lot_line in lotes:
                        if move_line.product_id.id == lot_line['product_id']:
                            move_line.update({'lot_id':lot_line['lot_id']})
                    move_line.qty_done= move_line.product_qty

                return_pick.action_assign()
                wiz_act = return_pick.button_validate()
                if wiz_act != True:
                    wiz = Form(self.env[wiz_act['res_model']].with_context(wiz_act['context'])).save()
                    wiz.process()
            else:
                picking_id.action_cancel()
        # mostrar boton devolver transeferencia
        self.as_bandera = True
        self.state = 'done'
        if self.state == 'done':
            #CASO 63: AL PRESIONAR BOTON GUARDAR        
            #el numero de la plantilla es el ID de la plantilla que corresponde
            valores_email_seiscinco = self.env['mail.template'].search([('id','=',166)])
            
            if valores_email_seiscinco:
                nombre_modelo_seiscuatro = valores_email_seiscinco.model_id.model
                self.env['mail.template'].as_send_email_con_adjuntos(self, valores_email_seiscinco.id, nombre_modelo_seiscuatro)
                if valores_email_seiscinco.as_mobile:
                    number = valores_email_seiscinco.as_mobile
                    if valores_email_seiscinco.as_desde and valores_email_seiscinco.as_asunto:
                        
                        if valores_email_seiscinco.as_desde == '${object.env.user.partner_id.email}':
                            remitente = str(self.env.user.partner_id.email)
                        if valores_email_seiscinco.as_desde == '${object.as_project_id.user_id.email}':
                            remitente = str(self.as_project_id.user_id.email)
                        if valores_email_seiscinco.as_desde != '${object.env.user.partner_id.email}' and valores_email_seiscinco.as_desde != '${object.as_project_id.user_id.email}':
                            remitente = str(valores_email_seiscinco.as_desde)
                        
                        mensajito = str('DE: ')+remitente+': '+ valores_email_seiscinco.as_asunto + ' '+ valores_email_seiscinco.as_mensaje_whatsapp_email +' '+str(self.as_project_id.name)+ ' esta listo para ser entregado. '
                        
                        self.env['as.whatsapp'].sudo().as_send_whatsapp(number,mensajito)
                        self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'Caso 65'</b>")
        
            
    def action_devolver(self):
        """devolver stock de una ubicacion a otra"""
        picking_ids = []
        picking_ids_2 = []
        picking_ids_3 = []
        #generar movimiento general
        # picking_general_2 = self.env['stock.picking'].create({
        #         'location_id': self.as_location_dest_id.id,
        #         'location_dest_id': self.as_location_id.id, 
        #         'partner_id': self.env.user.partner_id.id,
        #         'picking_type_id': self.as_picking_type_id.id,
        #         'project_id': self.as_project_id.id,
        #         'origin': self.name,
        #         'scheduled_date':self.as_scheduled_date,
        #         'as_solicitud_id':self.id,
        #         'as_bandera_system':True,
        #         'as_es_salida':True
        #     })
        # # cont_dev = 0
        # for lines in self.lines_ids:
        #     # cont_dev+=lines.as_devolver
        #     if lines.as_alquiler == False:
        #         if lines.as_devolver > lines.as_product_qty:
        #             raise UserError("No se puede devolver mas de la cantidad solicitada")
        #         if lines.as_product_qty:
        #             move_id = self.env['stock.move'].create({
        #                 'name': lines.product_id.name,
        #                 'product_id': lines.product_id.id,
        #                 'product_uom_qty': lines.as_product_qty,
        #                 'product_uom': lines.product_uom.id,
        #                 'picking_id': picking_general_2.id,
        #                 'lot_ids': lines.lot_id.ids,
        #                 'location_id': self.as_location_dest_id.id,  
        #                 'location_dest_id':  self.as_location_id.id,
        #                 'reserved_availability':lines.as_product_qty
        #             })
        #             move_line_pbw = self.env['stock.move.line'].create({
        #                 'product_id': lines.product_id.id,
        #                 'product_uom_id': lines.product_uom.id,
        #                 'picking_id': picking_general_2.id,
        #                 'qty_done': lines.as_product_qty,
        #                 # 'lot_id': lines.lot_id.id,
        #                 'move_id': move_id.id,
        #                 'location_id': self.as_location_dest_id.id ,
        #                 'location_dest_id': self.as_location_id.id
        #             })
        #         # lines.as_solicitud_line.picking_general_2_id = picking_general_2.id
        #         # lines.as_solicitud_line.as_transfer = True
        #         # lines.as_solicitud_line.as_qty_done = lines.as_solicitud_line.as_qty_done+lines.as_product_qty
        #         solicitud_qty_done = 0.0
        # # if cont_dev == 0:
        # #     raise UserError("Debe devolver al menos un producto")
        # picking_ids_2.append(picking_general_2.id)
        # # picking_general_2.action_assign()
        # # backorder_wizard_dict_2 = picking_general_2.button_validate()
        # # Asiento individual
        cont = 0
        for lineas in self.lines_ids:
            cont+=lineas.as_devolver
        if cont > 0:
            picking_general_4 = self.env['stock.picking'].create({
                    'location_id': self.as_location_dest_id.id,
                    'location_dest_id': self.as_location_id.id, 
                    'partner_id': self.env.user.partner_id.id,
                    'picking_type_id': self.as_picking_type_id.id,
                    'project_id': self.as_project_id.id,
                    'origin': self.name,
                    'scheduled_date':self.as_scheduled_date,
                    'as_solicitud_id':self.id,
                    'as_bandera_system':True
                    # 'as_es_salida':True
                })
        # cont_dev = 0
        for lines in self.lines_ids:
            # cont_dev+=lines.as_devolver
            # if lines.as_devolver == 0:
            #     continue
            # else:
            #     devolver =lines.as_devolver
            # if lines.as_alquiler == False:
            if lines.as_devolver != 0:
                move_id = self.env['stock.move'].create({
                    'name': lines.product_id.name,
                    'product_id': lines.product_id.id,
                    'product_uom_qty': lines.as_devolver,
                    'product_uom': lines.product_uom.id,
                    'picking_id': picking_general_4.id,
                    'lot_ids': lines.lot_dev_id.ids,
                    'location_id': self.as_location_dest_id.id,  
                    'location_dest_id':  self.as_location_id.id,
                    'reserved_availability':lines.as_product_qty
                })
                move_line_pbw = self.env['stock.move.line'].create({
                    'product_id': lines.product_id.id,
                    'product_uom_id': lines.product_uom.id,
                    'picking_id': picking_general_4.id,
                    'qty_done': lines.as_devolver,
                    # 'lot_id': lines.lot_id.id,
                    'move_id': move_id.id,
                    'location_id': self.as_location_dest_id.id,
                    'location_dest_id': self.as_location_id.id
                })
            # lines.as_solicitud_line.picking_general_4_id = picking_general_4.id
            # lines.as_solicitud_line.as_transfer = True
            # lines.as_solicitud_line.as_qty_done = lines.as_solicitud_line.as_qty_done+lines.as_product_qty
            solicitud_qty_done = 0.0
        # if cont_dev == 0:
        #     raise UserError("Debe devolver al menos un producto")
        if cont > 0:
            picking_ids.append(picking_general_4.id)
            # picking_general_4.action_assign()
            # backorder_wizard_dict_2 = picking_general_4.button_validate()

        # Movimiento de out
        cont2 = 0
        for lineas in self.lines_ids:
            cont2+=lineas.as_devolver
        if cont2 > 0:
            stock_picking_type = self.env['stock.picking.type'].sudo().search([('default_location_src_id','=',self.as_location_id.id),('code','=','outgoing')])

            if not stock_picking_type.default_location_dest_id:
                stock_picking_type = self.env['stock.picking.type'].sudo().search([('code','=','outgoing')],order="id asc",limit=1)
            if not self.as_location_alquiler_id:
                raise ValidationError(_("Debe completar la ubicación de alquiler cliente."))
            picking_general_3 = self.env['stock.picking'].create({
                    'location_id': self.as_location_id.id,
                    'location_dest_id': self.as_location_alquiler_id.id, 
                    'partner_id': self.env.user.partner_id.id,
                    'picking_type_id': self.as_picking_type_id.id,
                    'project_id': self.as_project_id.id,
                    'origin': self.name,
                    'scheduled_date':self.as_scheduled_date,
                    'as_solicitud_id':self.id,
                    'as_bandera_system':True
                })
            # picking_general_3.picking_type_code = 'outgoing'
            for lines in self.lines_ids:
                if lines.as_alquiler == True:
                    if lines.as_product_qty:
                        move_id = self.env['stock.move'].create({
                            'name': lines.product_id.name,
                            'product_id': lines.product_id.id,
                            'product_uom_qty': lines.as_product_qty,
                            'product_uom': lines.product_uom.id,
                            'picking_id': picking_general_3.id,
                            'lot_ids': lines.lot_id.ids,
                            'location_id': self.as_location_id.id,
                            'location_dest_id': stock_picking_type.default_location_dest_id.id,  
                            'reserved_availability':lines.as_product_qty
                        })
                        move_line_pbw = self.env['stock.move.line'].create({
                            'product_id': lines.product_id.id,
                            'product_uom_id': lines.product_uom.id,
                            'picking_id': picking_general_3.id,
                            'qty_done': lines.as_product_qty,
                            # 'lot_id': lines.lot_id.id,
                            'move_id': move_id.id,
                            'location_id': self.as_location_id.id,
                            'location_dest_id': stock_picking_type.default_location_dest_id.id
                        })

                    solicitud_qty_done = 0.0
        # picking_general_3.picking_type_code = 'outgoing'
        picking_ids_3.append(picking_general_3.id)
        self.as_bandera = False
        self.state = 'devuelto'

    def info_sucursal(self, requerido):
        """obtener datos de la empresa ordenadamente"""
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

    def get_datos_formulario_de_materiales(self,requerido):
        val=''
        datos=self.env['project.task'].sudo().search([('id','=',self.as_project_id.id)],limit=1)
        if datos:
            ot=datos.as_ot
        else:
            ot=''
        json={
            'nombre_ot':ot
        }
        total_neto = json[str(requerido)]
        return total_neto

    def as_create_retunrn_picking(self):
        """devolver stock de una ubicacion a otra"""
        picking_posi = self.env['stock.picking'].create({
            'location_id': self.as_location_id.id,
            'location_dest_id': self.as_location_dest_id.id,
            'partner_id': self.env.user.partner_id.id,
            'picking_type_id': self.as_picking_type_id.id,
            'project_id': self.as_project_id.id,
            'origin': self.name,
        })
        for lines in self.lines_ids:
            move_id = self.env['stock.move'].create({
                'name': lines.product_id.name,
                'product_id': lines.product_id.id,
                'product_uom_qty': abs(lines.as_product_qty),
                'product_uom': lines.product_uom.id,
                'picking_id': picking_posi.id,
                'location_id': self.as_location_id.id,
                'location_dest_id': self.as_location_dest_id.id,
            })
            move_line_pbw = self.env['stock.move.line'].create({
                'product_id': lines.product_id.id,
                'product_uom_id': lines.product_uom.id,
                'picking_id': picking_posi.id,
                'qty_done': abs(lines.as_product_qty),
                # 'lot_id': lines.lot_id.id,
                'move_id': move_id.id,
                'location_id': self.as_location_id.id,
                'location_dest_id': self.as_location_dest_id.id
            })
        # picking_posi.action_assign()
        self.as_return_pick = picking_posi
        # if self.as_return_pick:
        #     self.state = 'confirmed'
        backorder_wizard_dictposi = picking_posi.button_validate()
        if not backorder_wizard_dictposi:
            backorder_wizard_posi = Form(self.env[backorder_wizard_dictposi['res_model']].with_context(backorder_wizard_dictposi['context'])).save()
            backorder_wizard_posi.process()
    
    def as_action_confirm(self):
        """Confirmar movimientos de inventario"""
        as_project_task=self.env['project.task'].sudo().search([('name','=',self.as_origin)],limit=1)
        as_project_task.update({'stage_id':101})
        # as_project_task.stage_id.id = 101
        self.state = 'confirmed'
        picking_ids = []
        #generar movimiento general
        fechas = []
        picking_general = self.env['stock.picking']
        picking_general_alquiler = self.env['stock.picking']
        for lineas_fechas in self.lines_ids:
            fechas.append(lineas_fechas.as_deliver_date)
        s = []
        for i in fechas:
            if i not in s:
                s.append(i)
        #comprobar si hay lineas con alquiler

        for asientos in s:
            sin_alquiler = False
            alquiler = False
            for lines in self.lines_ids:
                if lines.as_alquiler and lines.as_deliver_date == asientos:
                    alquiler = True
                elif not lines.as_alquiler and lines.as_deliver_date == asientos:
                    sin_alquiler = True
            #sin marcado el check de alquiler
            if sin_alquiler:
                picking_general = self.env['stock.picking'].create({
                    'location_id': self.as_location_id.id,
                    'location_dest_id': self.as_location_dest_id.id,
                    'partner_id': self.env.user.partner_id.id,
                    'picking_type_id': self.as_picking_type_id.id,
                    'project_id': self.as_project_id.id,
                    'origin': self.name,
                    'scheduled_date':asientos,
                    'as_solicitud_id':self.id
                })
            if alquiler:
                picking_general_alquiler = self.env['stock.picking'].create({
                    'location_id': self.as_location_id.id,
                    'location_dest_id': self.as_location_dest_id.id,
                    'partner_id': self.env.user.partner_id.id,
                    'picking_type_id': self.as_picking_type_id.id,
                    'project_id': self.as_project_id.id,
                    'origin': self.name,
                    'scheduled_date':asientos,
                    'as_solicitud_id':self.id,
                    'priority':'1',
                })
            for lines in self.lines_ids:
                if picking_general:
                    if lines.as_deliver_date == asientos and lines.as_alquiler == False:
                        # if lines.display_type != 'line_note':
                        move_id = self.env['stock.move'].create({
                                'name': lines.product_id.name,
                                'product_id': lines.product_id.id,
                                'product_uom_qty': lines.as_product_qty,
                                'product_uom': lines.product_uom.id,
                                'picking_id': picking_general.id,
                                'location_id': self.as_location_id.id,
                                'location_dest_id': self.as_location_dest_id.id,  
                                'reserved_availability':lines.as_product_qty,
                                'as_nota':lines.as_nota,
                                'as_solicitud_line_id':lines.id
                            })
                                
                        solicitud_qty_done = 0.0
                if picking_general_alquiler:
                    if lines.as_deliver_date == asientos and lines.as_alquiler == True:
                        move_id2 = self.env['stock.move'].create({
                            'name': lines.product_id.name,
                            'product_id': lines.product_id.id,
                            'product_uom_qty': lines.as_product_qty,
                            'product_uom': lines.product_uom.id,
                            'picking_id': picking_general_alquiler.id,
                            'location_id': self.as_location_id.id,
                            'location_dest_id': self.as_location_dest_id.id,  
                            'reserved_availability':lines.as_product_qty,
                            'as_solicitud_line_id':lines.id
                        })
                        solicitud_qty_done = 0.0
            if picking_general:
                picking_general.scheduled_date = asientos 
                picking_general.scheduled_date = picking_general.scheduled_date + timedelta(hours=4)  
            if picking_general_alquiler:
                picking_general_alquiler.scheduled_date = asientos   
                picking_general_alquiler.scheduled_date = picking_general_alquiler.scheduled_date + timedelta(hours=4)  
        
                
        #CASO 8: AL PRESIONAR BOTON CONFIRMAR        
        #el numero de la plantilla es el ID de la plantilla que corresponde
        valores_email_seg = self.env['mail.template'].search([('id','=',150)])
        if valores_email_seg:
            nombre_modelo_seg = valores_email_seg.model_id.model
            #envio de email con adjuntos
            self.env['mail.template'].as_send_email_sin_adjuntos(self, valores_email_seg.id, nombre_modelo_seg)
            if valores_email_seg.as_mobile:
                number = valores_email_seg.as_mobile
                if valores_email_seg.as_desde and valores_email_seg.as_asunto:
                    
                    if valores_email_seg.as_desde == '${object.env.user.partner_id.email}':
                        remitente = str(self.env.user.partner_id.email)
                    if valores_email_seg.as_desde == '${object.as_project_id.user_id.login}':
                        remitente = str(self.as_project_id.user_id.login)
                    if valores_email_seg.as_desde != '${object.env.user.partner_id.email}' and valores_email_seg.as_desde != '${object.as_project_id.user_id.login}':
                        remitente = str(valores_email_seg.as_desde)
                    
                    mensajito = str('DE: ')+remitente+': '+ valores_email_seg.as_asunto +': '+ valores_email_seg.as_mensaje_whatsapp_email +' '+str(self.as_project_id.partner_id.name) +' fue aprobada. ' +'; Tarea: ' + str(self.as_project_id.name)
                    
                    self.env['as.whatsapp'].sudo().as_send_whatsapp(number,mensajito)
                    self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'Caso 8'</b>")
                    
        #CASO 14: AL PRESIONAR BOTON CONFIRMAR        
        #el numero de la plantilla es el ID de la plantilla que corresponde
        valores_email_catorce = self.env['mail.template'].search([('id','=',164)])
        if valores_email_catorce:
            nombre_modelo_seg = valores_email_catorce.model_id.model
            self.env['mail.template'].as_send_email_sin_adjuntos(self, valores_email_catorce.id, nombre_modelo_seg)
            if valores_email_catorce.as_mobile:
                number = valores_email_catorce.as_mobile
                if valores_email_catorce.as_desde and valores_email_catorce.as_asunto:
                    
                    if valores_email_catorce.as_desde == '${object.env.user.partner_id.email}':
                        remitente = str(self.env.user.partner_id.email)
                    if valores_email_catorce.as_desde == '${object.as_project_id.user_id.login}':
                        remitente = str(self.as_project_id.user_id.login)
                    if valores_email_catorce.as_desde != '${object.env.user.partner_id.email}' and valores_email_catorce.as_desde != '${object.as_project_id.user_id.login}':
                        remitente = str(valores_email_catorce.as_desde)
                    
                    mensajito = str('DE: ')+remitente+': '+ valores_email_catorce.as_asunto +': '+ valores_email_catorce.as_mensaje_whatsapp_email +' '+str(self.as_project_id.partner_id.name) +' fue aprobada. ' +'; Tarea: ' + str(self.as_project_id.name)
                    
                    self.env['as.whatsapp'].sudo().as_send_whatsapp(number,mensajito)
                    self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'Caso 14'</b>")
                
        #CASO 64: AL PRESIONAR BOTON CONFIRMAR        
        #el numero de la plantilla es el ID de la plantilla que corresponde
        valores_email_seiscuatro = self.env['mail.template'].search([('id','=',162)])
        
        if valores_email_seiscuatro:
            nombre_modelo_seiscuatro = valores_email_seiscuatro.model_id.model
            self.env['mail.template'].as_send_email_sin_adjuntos(self, valores_email_seiscuatro.id, nombre_modelo_seiscuatro)
            if valores_email_seiscuatro.as_mobile:
                number = valores_email_seiscuatro.as_mobile
                if valores_email_seiscuatro.as_desde and valores_email_seiscuatro.as_asunto:
                    
                    if valores_email_seiscuatro.as_desde == '${object.env.user.partner_id.email}':
                        remitente = str(self.env.user.partner_id.email)
                    if valores_email_seiscuatro.as_desde == '${object.as_project_id.user_id.login}':
                        remitente = str(self.as_project_id.user_id.login)
                    if valores_email_seiscuatro.as_desde != '${object.env.user.partner_id.email}' and valores_email_seiscuatro.as_desde != '${object.as_project_id.user_id.login}':
                        remitente = str(valores_email_seiscuatro.as_desde)
                    
                    mensajito = str('DE: ')+remitente+': '+ valores_email_seiscuatro.as_asunto+': '+valores_email_seiscuatro.as_mensaje_whatsapp_email +' '+str(self.as_project_id.name)
                    
                    self.env['as.whatsapp'].sudo().as_send_whatsapp(number,mensajito)
                    self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'Caso 64'</b>")

    @api.model_create_multi
    def create(self, vals_list):
        for vals_product in vals_list:
            secuence =  self.env['ir.sequence'].next_by_code('as.project.code')
            vals_product['name'] = secuence
        templates = super(AsRquestMaterials, self).create(vals_list)
        return templates

    def as_get_draft(self):
        self.state = 'draft'
        
    #funcion necesaria para poder enviar emails
    def _get_share_url(self, redirect=False, signup_partner=False, share_token=None):
        """
        Build the url of the record  that will be sent by mail and adds additional parameters such as
        access_token to bypass the recipient's rights,
        signup_partner to allows the user to create easily an account,
        hash token to allow the user to be authenticated in the chatter of the record portal view, if applicable
        :param redirect : Send the redirect url instead of the direct portal share url
        :param signup_partner: allows the user to create an account with pre-filled fields.
        :param share_token: = partner_id - when given, a hash is generated to allow the user to be authenticated
            in the portal chatter, if any in the target page,
            if the user is redirected to the portal instead of the backend.
        :return: the url of the record with access parameters, if any.
        """
        self.ensure_one()
        params = {
            'model': self._name,
            'res_id': self.id,
        }
        if hasattr(self, 'access_token'):
            params['access_token'] = self._portal_ensure_token()
        if share_token:
            params['share_token'] = share_token
            params['hash'] = self._sign_token(share_token)
        if signup_partner and hasattr(self, 'partner_id') and self.partner_id:
            params.update(self.partner_id.signup_get_auth_param()[self.partner_id.id])

        return '%s?%s' % ('/mail/view' if redirect else self.access_url, url_encode(params))

class AsRquestMaterialsline(models.Model):
    """Modulo par almacenar informacion de solicitud de materiales por linea"""
    _name = "as.request.lines"
    _description = 'Modulo par almacenar informacion de solicitud de materiales por linea'

    def _domain_contacts(self):
        ids = []
        print(self._origin.lot_id)
        for part in self._origin.lot_id:
            ids.append(part.id)
        return [('id','in', tuple(ids))]
        
    as_request_id = fields.Many2one('as.request.materials', 'Solicitud')
    name = fields.Char('Name')
    as_nota = fields.Char('Nota')
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    sequence = fields.Integer()
    product_id = fields.Many2one(
        'product.product', 'Producto',
        domain="[('type', 'in', ['product', 'consu'])]", index=True)
    as_location_id = fields.Many2one(
        'stock.location', 'Ubicacion origen',domain="[('as_solicitud', '=', True)]",
        auto_join=True, index=True, 
        help="Sets a location if you produce at a fixed location. This can be a partner location if you subcontract the manufacturing operations.")
    as_location_dest_id = fields.Many2one(
        'stock.location', 'Ubicacion Destino',
        auto_join=True, index=True, 
        help="Location where the system will stock the finished products.")
    lot_id = fields.Many2many('stock.production.lot', string='Lote/Serie')
    lot_dev_id = fields.Many2many('stock.production.lot', 'lot_solicitud', string='Lote/Serie DEV',domain="[('id', 'in', lot_id)]")
    # lot_id = fields.Many2one('stock.production.lot', string='Lote/Serie', readonly=False, domain="[('product_id', '=', product_id)]")
    as_product_qty = fields.Float(string="Cantidad")
    as_qty_done = fields.Float(string="Cant. Transferida")
    as_devolver = fields.Float(string="Cant. a devolver")
    as_stock = fields.Float(string="Stock")
    product_uom = fields.Many2one('uom.uom', 'UdM')
    as_deliver_date = fields.Date('Fecha de Entrega', store=True,index=True, default=fields.Date.context_today, tracking=True)
    # as_campo_serie = fields.Many2one('stock.production.lot',string="Nro serie")
    picking_general_id = fields.Many2one('stock.picking', string='General')
    picking_in_id = fields.Many2one('stock.picking', string='Ingreso')
    picking_out_id = fields.Many2one('stock.picking', string='Salida')

    as_dpicking_general_id = fields.Many2one('stock.picking', string='Dev. General')
    as_dpicking_in_id = fields.Many2one('stock.picking', string='Dev. Ingreso')
    as_dpicking_out_id = fields.Many2one('stock.picking', string='Dev. Salida')

    as_transfer = fields.Boolean(string="Transferido",)
    as_devuelto = fields.Boolean(string="Devuelto",)
    company_id = fields.Many2one('res.company', readonly=True, default=lambda self: self.env.company)
    product_brand_id = fields.Many2one("product.brand", related="product_id.product_brand_id", string="Marca")
    product_model_id = fields.Many2one("product.model", related="product_id.product_model_id")
    as_alquiler = fields.Boolean(string="Alquilado")

    # @api.model
    # def create(self, values):
    #     if values.get('display_type', self.default_get(['display_type'])['display_type']):
    #         values.update(product_id=False, price_unit=0, product_uom_qty=0, product_uom=False, customer_lead=0)
    #     line = super(AsRquestMaterialsline, self).create(values)
    #     return line

    @api.onchange('as_deliver_date')
    def as_get_date(self):
        """obtener fecha"""
        for line in self:
            if line.as_request_id.as_scheduled_date and line.as_deliver_date > line.as_request_id.as_scheduled_date:
                line.as_deliver_date = line.as_request_id.as_scheduled_date
                raise ValidationError(_("Solo puede Seleccionar fechas inferiores a la planificada en la solicitud."))

    @api.onchange('product_id')
    def as_onchange_product(self):
        for line in self:
            line.as_location_id = line.as_request_id.as_location_id.id
            line.as_location_dest_id = line.as_request_id.as_location_dest_id.id
            line.product_uom = line.product_id.uom_id.id
            line.as_stock = line.product_id.with_context(location=[line.as_location_id.id]).qty_available
            if line.as_request_id.as_scheduled_date and line.as_deliver_date > line.as_request_id.as_scheduled_date:
                raise ValidationError(_("Solo puede Seleccionar fechas inferiores a la planificada en la solicitud."))

