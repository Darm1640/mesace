# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime, timedelta
from odoo.tests.common import Form
from time import mktime
from odoo.exceptions import UserError, RedirectWarning, ValidationError, MissingError
import time
from odoo import api, fields, models, _
from datetime import datetime, timedelta

class clase_as_bo_notificaciones(models.Model):
    _inherit = 'mail.template'
    
    as_mensaje_whatsapp_email = fields.Char(string='Texto para Whatsapp')
    as_mobile = fields.Char(string='Para Numero(s) de Celular', help="introduzca el numero de celular con el codigo del pais (5917777770), si desa añadir mas numeros separelos por comas (,)")
    as_asunto = fields.Char(string='Asunto', help="Introduzca el titulo del Asunto")
    as_desde = fields.Char(string='Desde', help="Introduzca el correo electronico de quien enviara el mensaje")
    
    
    def as_send_email_con_adjuntos(self, res_id, template_id, nombre_modelo):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        res_id.ensure_one()
        attachment = self.env['ir.attachment'].search([('res_id','=',res_id.id),('res_model','=',nombre_modelo)])
        ctx = {
             'default_model': nombre_modelo,
             'default_res_id': res_id.ids[0],
             'default_use_template': bool(template_id),
             'default_template_id': template_id,
             'default_composition_mode': 'comment',
             'custom_layout': "mail.mail_notification_paynow",
             'force_email': True,
             'default_attachment_ids': attachment.ids,
         }
        wiz = {
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
        res_id.message_post(body = "<b style='color:green;'>Enviado correo electronico con adjuntos</b>")
        a = 10
        
    def as_send_email_sin_adjuntos(self, res_id, template_id, nombre_modelo):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        res_id.ensure_one()
        attachment = self.env['ir.attachment'].search([('res_id','=',res_id.id),('res_model','=',nombre_modelo)])
        ctx = {
             'default_model': nombre_modelo,
             'default_res_id': res_id.ids[0],
             'default_use_template': bool(template_id),
             'default_template_id': template_id,
             'default_composition_mode': 'comment',
             'custom_layout': "mail.mail_notification_paynow",
             'force_email': True,
         }
        wiz = {
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
        res_id.message_post(body = "<b style='color:green;'>Enviado correo electronico sin adjuntos</b>")
        a = 10
        

    # def boton_send_whatsapp(self):
    #     if self.as_mobile:
    #         number = self.as_mobile
    #         self.env['as.whatsapp'].sudo().as_send_whatsapp(number,self.as_mensaje_whatsapp_email)
    #         # self.message_post(body = "<b style='color:green;'>envio de whatsapp</b>")
    #     # self.as_mensaje_whatsapp_email = ''