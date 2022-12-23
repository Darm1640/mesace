# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import api, fields, models, _
from odoo.tests.common import Form
from odoo.exceptions import UserError
from werkzeug.urls import url_encode
from odoo.exceptions import UserError
class AsPurchaseOrder(models.Model):
    """Modulo heredado para agregar campos de horas, meses, etc"""
    _inherit = "project.task"

    as_u_tiempo = fields.Selection(selection=[('Horas','Horas'),('Dias','Dias'),('Meses','Meses'),('Años','Años')],default='Horas', string="Duracion del proyecto")
    as_medida_tiempo = fields.Many2one('uom.uom', string= "Duracion del proyecto")
    as_unidad = fields.Integer(string="Tipo duración del proyecto")
    as_hora = fields.Integer(string="Hora")
    as_gestion_viajes_id = fields.One2many('as.gestion.viaje', 'as_project_task_id', string="Viaticos")
    as_gestion_viaje_count = fields.Integer(compute='_compute_gestion_viaje_count')
    as_viajeros=fields.Many2many('hr.employee', string="Viajeros")
    as_ot = fields.Char(string='Nro de OT')
    as_state_viatico = fields.Selection([
        ('draft', 'Borrador'),
        ('to_approval', 'Para Aprobar'),
        ('approval', 'Aprobado')
    ], string='Estado Viatico', default='draft')
    as_approval = fields.Boolean(string="Permitido aprobar",compute="_get_approvals")
    as_analytic_account_id = fields.Many2one('account.analytic.account', string='Cuenta Analitica')
    as_saldo_reembolso = fields.Float(string="Saldo Desembolso",compute="_compute_saldo_reembolso")
    as_saldo_diferencia = fields.Float(string="Saldo Diferencia",compute="_compute_saldo_diferencia")
    as_saldo_diferencia_negativa = fields.Float(string="Saldo Diferencia",compute="_compute_saldo_diferencia_negativa")
    as_description_ot = fields.Text(translate=True)

    def _compute_saldo_reembolso(self):
        for task in self:
            payment = self.env['as.payment.multi'].search([('as_project_id','=',task.id),('as_type','=','Desembolso'),('state','=','confirm'),('as_is_negativo','=',False)])
            monto = 0.0
            for line in task.as_viaticos_id:
                monto += line.as_presupuestado
            if payment:
                total = 0.0
                for pay in payment:
                    total += pay.as_amount
                task.as_saldo_reembolso = monto - total
            else:
                task.as_saldo_reembolso = monto

    def _compute_saldo_diferencia(self):
        for task in self:
            payment = self.env['as.payment.multi'].search([('as_project_id','=',task.id),('as_type','=','Diferencia'),('state','=','confirm')])
            monto = 0.0
            for line in task.as_viaticos_id:
                if line.as_diferencia > 0.0:
                    monto += line.as_diferencia
            if payment:
                total = 0.0
                for pay in payment:
                    total += pay.as_amount
                task.as_saldo_diferencia = monto - total
            else:
                task.as_saldo_diferencia = monto

    def _compute_saldo_diferencia_negativa(self):
        for task in self:
            payment = self.env['as.payment.multi'].search([('as_project_id','=',task.id),('as_type','=','Desembolso'),('state','=','confirm'),('as_is_negativo','=',True)])
            monto = 0.0
            for line in task.as_viaticos_id:
                if line.as_diferencia < 0.0:
                    monto += line.as_diferencia
            if payment:
                total = 0.0
                for pay in payment:
                    total += pay.as_amount
                task.as_saldo_diferencia_negativa = monto + total
            else:
                task.as_saldo_diferencia_negativa = monto

    @api.depends('as_presupuesto_viaticos')
    def _get_approvals(self):
        for order in self:
            aprobar = False
            monto = order.as_presupuesto_viaticos
            usuario = order.env.user.id
            rango_approval = self.env['as.level.approval'].sudo().search([('as_type','=','viatico'),('as_amount_min','<=',monto),('as_amount_max','>=',monto)],order=" id desc",limit=1)
            if rango_approval:
                if usuario in rango_approval.as_users_ids.ids:
                    aprobar = True 
            order.as_approval = aprobar

    def button_confirm_approval(self):
        for project in self:
            project.as_state_viatico = 'approval'
            project.as_send_email([project.user_id.partner_id.id],'approval')
                        
            #CASO 20: AL PRESIONAR BOTON APROBAR (VIATICOS)        
            #el numero de la plantilla es el ID de la plantilla que corresponde            
            if self.as_presupuesto_viaticos < 1000:
                valores_email_seg = self.env['mail.template'].search([('id','=',113)])
                if valores_email_seg:
                    nombre_modelo_seg = valores_email_seg.model_id.model
                    #envio de email con adjuntos
                    self.env['mail.template'].sudo().as_send_email_sin_adjuntos(self, valores_email_seg.id, nombre_modelo_seg)
                        
                    if valores_email_seg.as_mobile:
                        number_vencinco = valores_email_seg.as_mobile
                        if valores_email_seg.as_desde and valores_email_seg.as_asunto:
                            
                            if valores_email_seg.as_desde == '${object.env.user.partner_id.email}':
                                remitente_seis = str(self.env.user.partner_id.email)
                            if valores_email_seg.as_desde == '${object.user_id.login}':
                                remitente_seis = str(self.user_id.login)
                            if valores_email_seg.as_desde != '${object.env.user.partner_id.email}' and valores_email_seg.as_desde != '${object.user_id.login}':
                                remitente_seis = str(valores_email_seg.as_desde)
                                
                            mensajito = str('DE: ')+ remitente_seis +': '+ valores_email_seg.as_asunto+': '+ valores_email_seg.as_mensaje_whatsapp_email +' '+str(self.partner_id.name) +' fue aprobado. Tarea:' + str(self.name)
                            
                            self.env['as.whatsapp'].sudo().as_send_whatsapp(number_vencinco,mensajito)
                            self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'Caso 20'</b>")
            
            #CASO 25: AL PRESIONAR BOTON APROBAR (VIATICOS)        
            #el numero de la plantilla es el ID de la plantilla que corresponde
            if self.as_presupuesto_viaticos > 1000:
                valores_email_vencinco = self.env['mail.template'].search([('id','=',155)])    
                if valores_email_vencinco:
                    nombre_modelo = valores_email_vencinco.model_id.model
                    #envio de email sin adjuntos
                    self.env['mail.template'].as_send_email_sin_adjuntos(self, valores_email_vencinco.id, nombre_modelo)
                    if valores_email_vencinco.as_mobile:
                        number_vencinco = valores_email_vencinco.as_mobile
                        if valores_email_vencinco.as_desde and valores_email_vencinco.as_asunto:
                            
                            if valores_email_vencinco.as_desde == '${object.env.user.partner_id.email}':
                                remitente_seis = str(self.env.user.partner_id.email)
                            if valores_email_vencinco.as_desde == '${object.user_id.login}':
                                remitente_seis = str(self.user_id.login)
                            if valores_email_vencinco.as_desde != '${object.env.user.partner_id.email}' and valores_email_vencinco.as_desde != '${object.user_id.login}':
                                remitente_seis = str(valores_email_vencinco.as_desde)
                                
                            mensajito = str('DE: ')+ remitente_seis +' '+ valores_email_vencinco.as_asunto+': '+valores_email_vencinco.as_mensaje_whatsapp_email +' '+str(self.partner_id.name) +' fue depositado. Tarea:' + str(self.name)
                            
                            self.env['as.whatsapp'].sudo().as_send_whatsapp(number_vencinco,mensajito)
                            self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'Caso 25'</b>")
            
            
            #CASO 28: AL PRESIONAR BOTON APROBAR (VIATICOS)        
            #el numero de la plantilla es el ID de la plantilla que corresponde
            valores_email_venocho = self.env['mail.template'].search([('id','=',156)])
            if valores_email_venocho:
                nombre_modelo = valores_email_venocho.model_id.model
                #envio de email sin adjuntos
                self.env['mail.template'].as_send_email_sin_adjuntos(self, valores_email_venocho.id, nombre_modelo)
                if valores_email_venocho.as_mobile:
                    number_venocho = valores_email_venocho.as_mobile
                    if valores_email_venocho.as_desde and valores_email_venocho.as_asunto:
                        
                        if valores_email_venocho.as_desde == '${object.env.user.partner_id.email}':
                            remitente_seis = str(self.env.user.partner_id.email)
                        if valores_email_venocho.as_desde == '${object.user_id.login}':
                            remitente_seis = str(self.user_id.login)
                        if valores_email_venocho.as_desde != '${object.env.user.partner_id.email}' and valores_email_venocho.as_desde != '${object.user_id.login}':
                            remitente_seis = str(valores_email_venocho.as_desde)
                            
                        mensajito = str('DE: ')+ remitente_seis +' '+ valores_email_venocho.as_asunto +': '+ valores_email_venocho.as_mensaje_whatsapp_email +' '+str(self.partner_id.name) +' por aprobar. Tarea:' + str(self.name)
                        
                        self.env['as.whatsapp'].sudo().as_send_whatsapp(number_venocho,mensajito)
                        self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'Caso 28'</b>")
                        
            #CASO 29: AL PRESIONAR BOTON APROBAR (VIATICOS)        
            #el numero de la plantilla es el ID de la plantilla que corresponde
            valores_email_venueve = self.env['mail.template'].search([('id','=',157)])
            if valores_email_venueve:
                nombre_modelo = valores_email_venueve.model_id.model
                #envio de email sin adjuntos
                self.env['mail.template'].as_send_email_sin_adjuntos(self, valores_email_venueve.id, nombre_modelo)
                if valores_email_venueve.as_mobile:
                    number_venueve = valores_email_venueve.as_mobile
                    if valores_email_venueve.as_desde and valores_email_venueve.as_asunto:
                        
                        if valores_email_venueve.as_desde == '${object.env.user.partner_id.email}':
                            remitente_seis = str(self.env.user.partner_id.email)
                        if valores_email_venueve.as_desde == '${object.user_id.login}':
                            remitente_seis = str(self.user_id.login)
                        if valores_email_venueve.as_desde != '${object.env.user.partner_id.email}' and valores_email_venueve.as_desde != '${object.user_id.login}':
                            remitente_seis = str(valores_email_venueve.as_desde)
                            
                        mensajito = str('DE: ')+ remitente_seis +' '+ valores_email_venueve.as_asunto +': '+ valores_email_venueve.as_mensaje_whatsapp_email +' '+str(self.partner_id.name) +' por efectuar. Tarea:' + str(self.name)
                        
                        self.env['as.whatsapp'].sudo().as_send_whatsapp(number_venueve,mensajito)
                        self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'Caso 29'</b>")
                    
            #CASO 33: AL PRESIONAR BOTON APROBAR (VIATICOS)      
            #el numero de la plantilla es el ID de la plantilla que corresponde  
            valores_email_treitres = self.env['mail.template'].search([('id','=',132)])   
            if valores_email_treitres:
                nombre_modelo = valores_email_treitres.model_id.model
                #envio de email sin adjuntos
                self.env['mail.template'].as_send_email_sin_adjuntos(self, valores_email_treitres.id, nombre_modelo)
                if valores_email_treitres.as_mobile:
                    number_treitres = valores_email_treitres.as_mobile
                    if valores_email_treitres.as_desde and valores_email_treitres.as_asunto:
                        if valores_email_treitres.as_desde == '${object.env.user.partner_id.email}':
                            remitente_seis = str(self.env.user.partner_id.email)
                        if valores_email_treitres.as_desde == '${object.user_id.login}':
                            remitente_seis = str(self.user_id.login)
                        if valores_email_treitres.as_desde != '${object.env.user.partner_id.email}' and valores_email_treitres.as_desde != '${object.user_id.login}':
                            remitente_seis = str(valores_email_treitres.as_desde)
                            
                        mensajito = str('DE: ')+ remitente_seis +' '+ valores_email_treitres.as_asunto +': '+ valores_email_treitres.as_mensaje_whatsapp_email +' '+str(self.partner_id.name) +' por aprobar. Tarea:' + str(self.name)
                        
                        self.env['as.whatsapp'].sudo().as_send_whatsapp(number_treitres,mensajito)
                        self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'Caso 33'</b>")
            
            #CASO 34: AL PRESIONAR BOTON APROBAR (VIATICOS)        
            #el numero de la plantilla es el ID de la plantilla que corresponde  
            valores_email_treicuatro = self.env['mail.template'].search([('id','=',133)])
            if valores_email_treicuatro:
                nombre_modelo = valores_email_treicuatro.model_id.model
                #envio de email sin adjuntos
                self.env['mail.template'].as_send_email_sin_adjuntos(self, valores_email_treicuatro.id, nombre_modelo)
                if valores_email_treicuatro.as_mobile:
                    number_treitres = valores_email_treicuatro.as_mobile
                    if valores_email_treicuatro.as_desde and valores_email_treicuatro.as_asunto:
                        if valores_email_treicuatro.as_desde == '${object.env.user.partner_id.email}':
                            remitente_seis = str(self.env.user.partner_id.email)
                        if valores_email_treicuatro.as_desde == '${object.user_id.login}':
                            remitente_seis = str(self.user_id.login)
                        if valores_email_treicuatro.as_desde != '${object.env.user.partner_id.email}' and valores_email_treicuatro.as_desde != '${object.user_id.login}':
                            remitente_seis = str(valores_email_treicuatro.as_desde)
                            
                        mensajito = str('DE: ')+ remitente_seis +' '+ valores_email_treicuatro.as_asunto +': '+ valores_email_treicuatro.as_mensaje_whatsapp_email +' '+str(self.partner_id.name) +' por depositado. Tarea:' + str(self.name)
                        
                        self.env['as.whatsapp'].sudo().as_send_whatsapp(number_treitres,mensajito)
                        self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'Caso 34'</b>")
    
    def button_approval_approval(self):
        
        #CASO 19: AL PRESIONAR BOTON APROBAR (VIATICOS)      
        #el numero de la plantilla es el ID de la plantilla que corresponde
        if self.as_presupuesto_viaticos < 1000:
            valores_email_seg = self.env['mail.template'].search([('id','=',152)])
            if valores_email_seg:
                nombre_modelo = valores_email_seg.model_id.model
                #envio de email sin adjuntos
                self.env['mail.template'].as_send_email_sin_adjuntos(self, valores_email_seg.id, nombre_modelo)
                if valores_email_seg.as_mobile:
                    number_seg = valores_email_seg.as_mobile
                    if valores_email_seg.as_desde and valores_email_seg.as_asunto:
                        
                        if valores_email_seg.as_desde == '${object.env.user.partner_id.email}':
                            remitente_seis = str(self.env.user.partner_id.email)
                        if valores_email_seg.as_desde == '${object.user_id.login}':
                            remitente_seis = str(self.user_id.login)
                        if valores_email_seg.as_desde != '${object.env.user.partner_id.email}' and valores_email_seg.as_desde != '${object.user_id.login}':
                            remitente_seis = str(valores_email_seg.as_desde)
                            
                        mensajito = str('DE: ')+ remitente_seis +': '+ valores_email_seg.as_asunto +': '+ valores_email_seg.as_mensaje_whatsapp_email +' '+str(self.partner_id.name) +' por aprobar. Tarea:' + str(self.name)
                        
                        self.env['as.whatsapp'].sudo().as_send_whatsapp(number_seg,mensajito)
                        self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'Caso 19'</b>")
                        
        #CASO 23: AL PRESIONAR BOTON APROBAR (VIATICOS)        
        #el numero de la plantilla es el ID de la plantilla que corresponde
        if self.as_presupuesto_viaticos > 1000:
            valores_email_terc = self.env['mail.template'].search([('id','=',153)])
            if valores_email_terc:
                nombre_modelo = valores_email_terc.model_id.model
                #envio de email sin adjuntos
                self.env['mail.template'].as_send_email_sin_adjuntos(self, valores_email_terc.id, nombre_modelo)
                if valores_email_terc.as_mobile:
                    number_seg = valores_email_terc.as_mobile
                    if valores_email_terc.as_desde and valores_email_terc.as_asunto:
                        
                        if valores_email_terc.as_desde == '${object.env.user.partner_id.email}':
                            remitente_seis = str(self.env.user.partner_id.email)
                        if valores_email_terc.as_desde == '${object.user_id.login}':
                            remitente_seis = str(self.user_id.login)
                        if valores_email_terc.as_desde != '${object.env.user.partner_id.email}' and valores_email_terc.as_desde != '${object.user_id.login}':
                            remitente_seis = str(valores_email_terc.as_desde)
                            
                        mensajito = str('DE: ')+ remitente_seis +': '+ valores_email_terc.as_asunto +': '+ valores_email_terc.as_mensaje_whatsapp_email +' '+str(self.partner_id.name) +' por aprobar. Tarea:' + str(self.name)
                        
                        self.env['as.whatsapp'].sudo().as_send_whatsapp(number_seg,mensajito)
                        self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'Caso 23'</b>")
                        
        #CASO 24: AL PRESIONAR BOTON APROBAR (VIATICOS)        
        #el numero de la plantilla es el ID de la plantilla que corresponde
        if self.as_presupuesto_viaticos > 1000:
            valores_email_cuart = self.env['mail.template'].search([('id','=',154)])
            if valores_email_cuart:
                nombre_modelo = valores_email_cuart.model_id.model
                #envio de email sin adjuntos
                self.env['mail.template'].as_send_email_sin_adjuntos(self, valores_email_cuart.id, nombre_modelo)
                if valores_email_cuart.as_mobile:
                    number_seg = valores_email_cuart.as_mobile
                    if valores_email_cuart.as_desde and valores_email_cuart.as_asunto:
                        
                        if valores_email_cuart.as_desde == '${object.env.user.partner_id.email}':
                            remitente_seis = str(self.env.user.partner_id.email)
                        if valores_email_cuart.as_desde == '${object.user_id.login}':
                            remitente_seis = str(self.user_id.login)
                        if valores_email_cuart.as_desde != '${object.env.user.partner_id.email}' and valores_email_cuart.as_desde != '${object.user_id.login}':
                            remitente_seis = str(valores_email_cuart.as_desde)
                            
                        mensajito = str('DE: ')+ remitente_seis +': '+ valores_email_cuart.as_asunto +': '+ valores_email_cuart.as_mensaje_whatsapp_email +' '+str(self.partner_id.name) +' por efectuar. Tarea:' + str(self.name)
                        
                        self.env['as.whatsapp'].sudo().as_send_whatsapp(number_seg,mensajito)
                        self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'Caso 24'</b>")
        
                        
        for order in self:
            monto = order.as_presupuesto_viaticos
            usuario = order.env.user.id
            rango_approval = self.env['as.level.approval'].sudo().search([('as_type','=','viatico'),('as_amount_min','<=',monto),('as_amount_max','>=',monto)],order=" id desc",limit=1)
            if rango_approval:
                order.as_state_viatico = 'to_approval'
                partners = []
                for users in rango_approval.as_users_ids:
                    partners.append(users.partner_id.id)
                order.as_send_email(partners,'to_approval')
            else:
                order.as_state_viatico = 'approval'
                order.as_send_email([order.user_id.partner_id.id],'approval')


    def as_send_email(self,as_partner,as_type):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template_id = self._find_mail_template_send(as_type=as_type)
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        attachment = self.env['ir.attachment'].search([('res_id','=',self.sale_order_id.id)])
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'project.task',
            'default_res_id': self.ids[0],
            'default_partner_ids': as_partner,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
            'default_attachment_ids': attachment.ids,
        }
        wiz =  {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

        wiz = Form(self.env['mail.compose.message'].with_context(ctx)).save()
        wiz.action_send_mail()
        enviados = self.as_partners_get(as_partner)
        self.message_post(body = "<b style='color:blue;'>Enviado correo para aprobación a "+str(enviados)+"</b>")

    def as_partners_get(self,partner):
        usuarios = ''
        partners = self.env['res.partner'].sudo().search([('id','in',partner)])
        if partners:
            for part in partners:
                usuarios += str(part.name)+', '
        return usuarios

    def _find_mail_template_send(self, force_confirmation_template=False,as_type=''):
        if as_type =='to_approval':
            template_id = self.env['ir.model.data'].xmlid_to_res_id('as_spectrocom_project.as_template_project_to_approval_email', raise_if_not_found=False)
        else:
            template_id = self.env['ir.model.data'].xmlid_to_res_id('as_spectrocom_project.as_template_project_approval_email', raise_if_not_found=False)
        return template_id


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

    @api.model_create_multi
    def create(self, vals_list):
        
        for vals_product in vals_list:
            secuence =  self.env['ir.sequence'].next_by_code('as.secuence.ot')
            vals_product['as_ot'] = secuence
        creacion = super(AsPurchaseOrder, self).create(vals_list)
        return creacion
    
    def button_gestion_viajes(self):
        self.env['as.gestion.viaje'].create({
                    'name': self.name,
                    'distancia_recorrer': '1',
                    'clima': '1',
                    'ruta': '1',
                    'conocimiento_ruta': '1',
                    'comunicacio_disponible': '1',
                    'personas_por_vehiculo': '1',
                    'horas_viaje': '1',
                    'total': '8',
                    'as_project_task_id':self.id
                })

    @api.onchange("as_medida_tiempo","as_unidad")
    def as_tiempo(self):
        aux = 0
        # self.as_hora = self.as_medida_tiempo.factor * self.as_unidad
        unidad_horas = self.env['uom.uom'].search([('name','=','Horas')])
        self.planned_hours = self.as_medida_tiempo._compute_quantity(self.as_unidad,unidad_horas,round=False)

    def _compute_gestion_viaje_count(self):
        result = self.env['as.gestion.viaje'].search([('as_project_task_id','=',self.id)])
        for gestio_viaje in self:
            gestio_viaje.as_gestion_viaje_count = len(result)

    def action_gestion_viaje(self):
        self.ensure_one()
        action_pickings = self.env.ref('as_spectrocom_project.as_plantilla_action_x')
        action = action_pickings.read()[0]
        action['context'] = {}
        result = self.env['as.gestion.viaje'].search([('as_project_task_id','=',self.id)])
        action['domain'] = [('id', 'in', result.ids)]
        return action
    
    def write(self, vals):
        #para notificaciones, 1er caso, segundo caso de la plantilla excel
        bandera=False
        bandera_dos = False
        bandera_tres = False
        bandera_cuatro = False
        bandera_cinco = False
        bandera_seis = False
        bandera_cinc_tres = False
        bandera_seis_dos = False
        if 'user_id' in vals:
            if vals['user_id'] == 20:
                bandera=True
            else:
                bandera_dos=True
                bandera_tres=True
                bandera_cuatro=True
                bandera_cinco=True
                bandera_seis=True
                bandera_cinc_tres = True
                bandera_seis_dos = True
        res = super(AsPurchaseOrder, self).write(vals)
        
        #CASO 1: JEAN CAMARA
        if bandera== True:
            remitente = ''
            #el numero de la plantilla es el ID de la plantilla que corresponde
            valores_email = self.env['mail.template'].search([('id','=',159)])
            if valores_email:
                nombre_modelo = valores_email.model_id.model
                #envio de email con adjuntos
                self.env['mail.template'].sudo().as_send_email_con_adjuntos(self, valores_email.id, nombre_modelo)
                if valores_email.as_mobile:
                    number_mail = valores_email.as_mobile
                    if valores_email.as_desde and valores_email.as_asunto:
                        if valores_email.as_desde == '${object.env.user.partner_id.email}':
                            remitente = str(self.env.user.partner_id.email)
                        if valores_email.as_desde == '${object.user_id.email}':
                            remitente = str(self.user_id.email)
                        if valores_email.as_desde != '${object.env.user.partner_id.email}' and valores_email.as_desde != '${object.user_id.email}':
                            remitente = str(valores_email.as_desde)
                        mensajito = str('DE: ')+ remitente +' '+ valores_email.as_asunto + ': '+valores_email.as_mensaje_whatsapp_email +' '+str(self.partner_id.name) +'; De la tarea: ' + str(self.name)
                        self.env['as.whatsapp'].sudo().as_send_whatsapp(number_mail,mensajito)
                        self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'CASO 1'</b>")
    
            
        #CASO 2: REASIGNADO
        if bandera_dos== True:
            remitente_dos = ''
            #el numero de la plantilla es el ID de la plantilla que corresponde
            valores_email_dos = self.env['mail.template'].search([('id','=',131)])
            if valores_email_dos:
                nombre_modelo = valores_email_dos.model_id.model
                #envio de email con adjuntos
                self.env['mail.template'].sudo().as_send_email_sin_adjuntos(self, valores_email_dos.id, nombre_modelo)
                if valores_email_dos.as_mobile:
                    number_mail = valores_email_dos.as_mobile
                    if valores_email_dos.as_desde and valores_email_dos.as_asunto:
                        if valores_email_dos.as_desde == '${object.env.user.partner_id.email}':
                            remitente_dos = str(self.env.user.partner_id.email)
                        if valores_email_dos.as_desde == '${object.user_id.email}':
                            remitente_dos = str(self.user_id.email)
                        if valores_email_dos.as_desde != '${object.env.user.partner_id.email}' and valores_email_dos.as_desde != '${object.user_id.email}':
                            remitente_dos = str(valores_email_dos.as_desde)
                        mensajito = str('DE: ')+ remitente_dos +' '+ valores_email_dos.as_asunto + ': '+valores_email_dos.as_mensaje_whatsapp_email +' '+str(self.partner_id.name) +'; De la tarea: ' + str(self.name)
                        self.env['as.whatsapp'].sudo().as_send_whatsapp(number_mail,mensajito)
                        self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'CASO 2'</b>")
                
        #CASO 3: MODIFICADO        
        if bandera_tres == True:
            remitente_tres = ''
            #el numero de la plantilla es el ID de la plantilla que corresponde
            valores_email_tres = self.env['mail.template'].search([('id','=',135)])
            if valores_email_tres:
                nombre_modelo = valores_email_tres.model_id.model
                #envio de email con adjuntos
                self.env['mail.template'].sudo().as_send_email_con_adjuntos(self, valores_email_tres.id, nombre_modelo)
                if valores_email_tres.as_mobile:
                    number_tres = valores_email_tres.as_mobile
                    if valores_email_tres.as_desde and valores_email_tres.as_asunto:
                        if valores_email_tres.as_desde == '${object.env.user.partner_id.email}':
                            remitente_tres = str(self.env.user.partner_id.email)
                        if valores_email_tres.as_desde == '${object.user_id.email}':
                            remitente_tres = str(self.user_id.email)
                        if valores_email_tres.as_desde != '${object.env.user.partner_id.email}' and valores_email_tres.as_desde != '${object.user_id.email}':
                            remitente_tres = str(valores_email_tres.as_desde)
                        mensajito = str('DE: ')+ remitente_tres +' '+ valores_email_tres.as_asunto + ': '+valores_email_tres.as_mensaje_whatsapp_email +' '+str(self.partner_id.name) +'; De la tarea: ' + str(self.name)
                        self.env['as.whatsapp'].sudo().as_send_whatsapp(number_tres,mensajito)
                        self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'CASO 3'</b>")
                
        #CASO 4: REASIGNADO        
        if bandera_cuatro == True:
            remitente_cuatro = ''
            #el numero de la plantilla es el ID de la plantilla que corresponde
            valores_email_cuatro = self.env['mail.template'].search([('id','=',144)])
            if valores_email_cuatro:
                nombre_modelo = valores_email_cuatro.model_id.model
                #envio de email sin adjuntos
                self.env['mail.template'].as_send_email_sin_adjuntos(self, valores_email_cuatro.id, nombre_modelo)
                if valores_email_cuatro.as_mobile:
                    number_cuatro = valores_email_cuatro.as_mobile
                    if valores_email_cuatro.as_desde and valores_email_cuatro.as_asunto:
                        if valores_email_cuatro.as_desde == '${object.env.user.partner_id.email}':
                            remitente_cuatro = str(self.env.user.partner_id.email)
                        if valores_email_cuatro.as_desde == '${object.user_id.email}':
                            remitente_cuatro = str(self.user_id.email)
                        if valores_email_cuatro.as_desde != '${object.env.user.partner_id.email}' and valores_email_cuatro.as_desde != '${object.user_id.email}':
                            remitente_cuatro = str(valores_email_cuatro.as_desde)
                        mensajito = str('DE: ')+ remitente_cuatro +' '+ valores_email_cuatro.as_asunto + ': '+valores_email_cuatro.as_mensaje_whatsapp_email +' '+str(self.partner_id.name) +'; De la tarea: ' + str(self.name)
                        self.env['as.whatsapp'].sudo().as_send_whatsapp(number_cuatro,mensajito)
                        self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'CASO 4'</b>")
        
        #CASO 5: MODIFICADO        
        if bandera_cinco == True:
            remitente_cinco=''
            #el numero de la plantilla es el ID de la plantilla que corresponde
            valores_email_cinco = self.env['mail.template'].search([('id','=',147)])
            if valores_email_cinco:
                nombre_modelo = valores_email_cinco.model_id.model
                #envio de email con adjuntos
                self.env['mail.template'].as_send_email_con_adjuntos(self, valores_email_cinco.id, nombre_modelo)
                if valores_email_cinco.as_mobile:
                    number_cinco = valores_email_cinco.as_mobile
                    if valores_email_cinco.as_desde and valores_email_cinco.as_asunto:
                        
                        if valores_email_cinco.as_desde == '${object.env.user.partner_id.email}':
                            remitente_cinco = str(self.env.user.partner_id.email)
                        if valores_email_cinco.as_desde == '${object.user_id.email}':
                            remitente_cinco = str(self.user_id.email)
                        if valores_email_cinco.as_desde != '${object.env.user.partner_id.email}' and valores_email_cinco.as_desde != '${object.user_id.email}':
                            remitente_cinco = str(valores_email_cinco.as_desde)
                            
                        mensajito = str('DE: ')+ remitente_cinco +' '+ valores_email_cinco.as_asunto + ': '+valores_email_cinco.as_mensaje_whatsapp_email +' '+str(self.partner_id.name) +'; De la tarea: ' + str(self.name)
                        
                        self.env['as.whatsapp'].sudo().as_send_whatsapp(number_cinco,mensajito)
                        self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'CASO 5'</b>")
                
        #CASO 6: REASIGNADO        
        if bandera_seis == True:
            remitente_seis=''
            #el numero de la plantilla es el ID de la plantilla que corresponde
            valores_email_seis = self.env['mail.template'].search([('id','=',148)])
            if valores_email_seis:
                nombre_modelo = valores_email_seis.model_id.model
                #envio de email sin adjuntos
                self.env['mail.template'].as_send_email_sin_adjuntos(self, valores_email_seis.id, nombre_modelo)
                if valores_email_seis.as_mobile:
                    number_seis = valores_email_seis.as_mobile
                    if valores_email_seis.as_desde and valores_email_seis.as_asunto:
                        
                        if valores_email_seis.as_desde == '${object.env.user.partner_id.email}':
                            remitente_seis = str(self.env.user.partner_id.email)
                        if valores_email_seis.as_desde == '${object.user_id.email}':
                            remitente_seis = str(self.user_id.email)
                        if valores_email_seis.as_desde != '${object.env.user.partner_id.email}' and valores_email_seis.as_desde != '${object.user_id.email}':
                            remitente_seis = str(valores_email_seis.as_desde)
                            
                        mensajito = str('DE: ')+ remitente_seis +' '+ valores_email_seis.as_asunto + ': '+valores_email_seis.as_mensaje_whatsapp_email +' '+str(self.partner_id.name) +'; De la tarea: ' + str(self.name)
                        
                        self.env['as.whatsapp'].sudo().as_send_whatsapp(number_seis,mensajito)
                        self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'CASO 6'</b>")
                    
        #CASO 53: AL ASIGNAR LA TAREA       
        #el numero de la plantilla es el ID de la plantilla que corresponde
        if bandera_cinc_tres == True:
            valores_email_cintres = self.env['mail.template'].search([('id','=',163)])
            if valores_email_cintres:
                nombre_modelo = valores_email_cintres.model_id.model
                #envio de email sin adjuntos
                self.env['mail.template'].as_send_email_sin_adjuntos(self, valores_email_cintres.id, nombre_modelo)
                if valores_email_cintres.as_mobile:
                    number_cintres = valores_email_cintres.as_mobile
                    if valores_email_cintres.as_desde and valores_email_cintres.as_asunto:
                        
                        if valores_email_cintres.as_desde == '${object.env.user.partner_id.email}':
                            remitente_seis = str(self.env.user.partner_id.email)
                        if valores_email_cintres.as_desde == '${object.user_id.email}':
                            remitente_seis = str(self.user_id.email)
                        if valores_email_cintres.as_desde != '${object.env.user.partner_id.email}' and valores_email_cintres.as_desde != '${object.user_id.email}':
                            remitente_seis = str(valores_email_cintres.as_desde)
                            
                        mensajito_cintres = str('DE: ')+ remitente_seis +' '+ valores_email_cintres.as_asunto + ': '+valores_email_cintres.as_mensaje_whatsapp_email +' '+str(self.partner_id.name) +'; De la tarea: ' + str(self.name)
                        
                        self.env['as.whatsapp'].sudo().as_send_whatsapp(number_cintres,mensajito_cintres)
                        self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'CASO 53'</b>")
                    
        #CASO 62: AL GUARDAR LA TAREA       
        #el numero de la plantilla es el ID de la plantilla que corresponde
        if bandera_seis_dos == True:
            valores_email_seisdos = self.env['mail.template'].search([('id','=',160)])
            if valores_email_seisdos:
                nombre_modelo = valores_email_seisdos.model_id.model
                #envio de email sin adjuntos
                self.env['mail.template'].as_send_email_sin_adjuntos(self, valores_email_seisdos.id, nombre_modelo)
                if valores_email_seisdos.as_mobile:
                    number_seisdos = valores_email_seisdos.as_mobile
                    
                    if valores_email_seisdos.as_desde and valores_email_seisdos.as_asunto:
                        
                        if valores_email_seisdos.as_desde == '${object.env.user.partner_id.email}':
                            remitente_seis = str(self.env.user.partner_id.email)
                        if valores_email_seisdos.as_desde == '${object.user_id.email}':
                            remitente_seis = str(self.user_id.email)
                        if valores_email_seisdos.as_desde != '${object.env.user.partner_id.email}' and valores_email_seisdos.as_desde != '${object.user_id.email}':
                            remitente_seis = str(valores_email_seisdos.as_desde)
                            
                        mensajito_seisdos = str('DE: ')+ remitente_seis +' '+ valores_email_seisdos.as_asunto + ': '+valores_email_seisdos.as_mensaje_whatsapp_email +' asignado. Favor proceder con la solicitud de material ' 
                        
                        self.env['as.whatsapp'].sudo().as_send_whatsapp(number_seisdos,mensajito_seisdos)
                        self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'CASO 62'</b>")
        return res


    
class as_project_task_type(models.Model):
    _inherit = "project.task.type"

    as_repartir = fields.Boolean(string="Aceptar proyectos entrantes")
    as_repartir_nuevo = fields.Boolean(string="Etapa Nueva")
