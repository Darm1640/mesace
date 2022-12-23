from odoo import models, fields, api
from odoo.tests.common import Form
from odoo.exceptions import UserError
from werkzeug.urls import url_encode
class ProjectTaskModel(models.Model):
    """Heredado para crear funcion de cron quie enviara notificaciones"""
    _inherit="project.task"
    
    def write(self, vals):
        bandera=False
        bandera_dos = False
        if 'user_id' in vals:
            if vals['user_id'] == 20:
                bandera=True
            else:
                bandera_dos=True
        res = super(ProjectTaskModel, self).write(vals)
        if bandera== True:
            a=0
            valores_email = self.env['mail.template'].search([('id','=',96)])
            if valores_email:
                nombre_modelo = valores_email.model_id.model
                self.as_send_email_customer_change(valores_email.id, nombre_modelo)
        return res
    

    def as_send_email_customer_change(self, template_id, nombre_modelo):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        attachment = self.env['ir.attachment'].search([('res_id','=',self.id),('res_model','=',nombre_modelo)])
        ctx = {
             'default_model': 'project.task',
             'default_res_id': self.ids[0],
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
        self.message_post(body = "<b style='color:green;'>Enviado correo</b>")

    # def _find_mail_template_sending_change(self, force_confirmation_template=False):
    #     template_id = self.env['ir.model.data'].xmlid_to_res_id('as_spectrocom_sales.as_mail_template_tarea_adjuntos', raise_if_not_found=False)
    #     return template_id
    
    
#     def as_send_email_customer_change_dos(self):
#         ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
#         self.ensure_one()
#         template_id = self._find_mail_template_sending_change_dos()
#         lang = self.env.context.get('lang')
#         template = self.env['mail.template'].browse(template_id)
#         # attachment = self.env['ir.attachment'].search([('res_id','=',self.id),('res_model','=','project.task')])
#         if template.lang:
#             lang = template._render_lang(self.ids)[self.id]
#         ctx = {
#              'default_model': 'project.task',
#              'default_res_id': self.ids[0],
#              'default_use_template': bool(template_id),
#              'default_template_id': template_id,
#              'default_composition_mode': 'comment',
#              'custom_layout': "mail.mail_notification_paynow",
#              'force_email': True,
#             #  'default_attachment_ids': attachment.ids,
#          }
#         wiz = {
#             'type': 'ir.actions.act_window',
#             'view_mode': 'form',
#             'res_model': 'mail.compose.message',
#             'views': [(False, 'form')],
#             'view_id': False,
#             'target': 'new',
#             'context': ctx,
#         }
#         wiz = Form(self.env['mail.compose.message'].with_context(ctx)).save()
#         wiz.action_send_mail()
#         self.message_post(body = "<b style='color:green;'>Enviado correo</b>")

#     def _find_mail_template_sending_change_dos(self, force_confirmation_template=False):
#         template_id = self.env['ir.model.data'].xmlid_to_res_id('as_bo_notificaciones_estrict_email.as_template_envio_email_dos', raise_if_not_found=False)
#         return template_id
    
    
#     def as_send_email_customer_change_tres(self):
#         ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
#         self.ensure_one()
#         template_id = self._find_mail_template_sending_change_tres()
#         lang = self.env.context.get('lang')
#         template = self.env['mail.template'].browse(template_id)
#         attachment = self.env['ir.attachment'].search([('res_id','=',self.id),('res_model','=','project.task')])
#         if template.lang:
#             lang = template._render_lang(self.ids)[self.id]
#         ctx = {
#              'default_model': 'project.task',
#              'default_res_id': self.ids[0],
#              'default_use_template': bool(template_id),
#              'default_template_id': template_id,
#              'default_composition_mode': 'comment',
#              'custom_layout': "mail.mail_notification_paynow",
#              'force_email': True,
#              'default_attachment_ids': attachment.ids,
#          }
#         wiz = {
#             'type': 'ir.actions.act_window',
#             'view_mode': 'form',
#             'res_model': 'mail.compose.message',
#             'views': [(False, 'form')],
#             'view_id': False,
#             'target': 'new',
#             'context': ctx,
#         }
#         wiz = Form(self.env['mail.compose.message'].with_context(ctx)).save()
#         wiz.action_send_mail()
#         self.message_post(body = "<b style='color:green;'>Enviado correo</b>")

#     def _find_mail_template_sending_change_tres(self, force_confirmation_template=False):
#         template_id = self.env['ir.model.data'].xmlid_to_res_id('as_bo_notificaciones_estrict_email.as_template_envio_email_tres', raise_if_not_found=False)
#         return template_id
    
    
#     def as_send_email_customer_change_cuatro(self):
#         ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
#         self.ensure_one()
#         template_id = self._find_mail_template_sending_change_cuatro()
#         lang = self.env.context.get('lang')
#         template = self.env['mail.template'].browse(template_id)
#         if template.lang:
#             lang = template._render_lang(self.ids)[self.id]
#         ctx = {
#              'default_model': 'project.task',
#              'default_res_id': self.ids[0],
#              'default_use_template': bool(template_id),
#              'default_template_id': template_id,
#              'default_composition_mode': 'comment',
#              'custom_layout': "mail.mail_notification_paynow",
#              'force_email': True,
#          }
#         wiz = {
#             'type': 'ir.actions.act_window',
#             'view_mode': 'form',
#             'res_model': 'mail.compose.message',
#             'views': [(False, 'form')],
#             'view_id': False,
#             'target': 'new',
#             'context': ctx,
#         }
#         wiz = Form(self.env['mail.compose.message'].with_context(ctx)).save()
#         wiz.action_send_mail()
#         self.message_post(body = "<b style='color:green;'>Enviado correo</b>")

#     def _find_mail_template_sending_change_cuatro(self, force_confirmation_template=False):
#         template_id = self.env['ir.model.data'].xmlid_to_res_id('as_bo_notificaciones_estrict_email.as_template_envio_email_cuatro', raise_if_not_found=False)
#         return template_id
    
#     def as_send_email_customer_change_cinco(self):
#         ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
#         self.ensure_one()
#         template_id = self._find_mail_template_sending_change_cinco()
#         lang = self.env.context.get('lang')
#         template = self.env['mail.template'].browse(template_id)
#         attachment = self.env['ir.attachment'].search([('res_id','=',self.id),('res_model','=','project.task')])
#         if template.lang:
#             lang = template._render_lang(self.ids)[self.id]
#         ctx = {
#              'default_model': 'project.task',
#              'default_res_id': self.ids[0],
#              'default_use_template': bool(template_id),
#              'default_template_id': template_id,
#              'default_composition_mode': 'comment',
#              'custom_layout': "mail.mail_notification_paynow",
#              'force_email': True,
#              'default_attachment_ids': attachment.ids,
#          }
#         wiz = {
#             'type': 'ir.actions.act_window',
#             'view_mode': 'form',
#             'res_model': 'mail.compose.message',
#             'views': [(False, 'form')],
#             'view_id': False,
#             'target': 'new',
#             'context': ctx,
#         }
#         wiz = Form(self.env['mail.compose.message'].with_context(ctx)).save()
#         wiz.action_send_mail()
#         self.message_post(body = "<b style='color:green;'>Enviado correo</b>")

#     def _find_mail_template_sending_change_cinco(self, force_confirmation_template=False):
#         template_id = self.env['ir.model.data'].xmlid_to_res_id('as_bo_notificaciones_estrict_email.as_template_envio_email_cinco', raise_if_not_found=False)
#         return template_id
    
#     def as_send_email_customer_change_seis(self):
#         ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
#         self.ensure_one()
#         template_id = self._find_mail_template_sending_change_seis()
#         lang = self.env.context.get('lang')
#         template = self.env['mail.template'].browse(template_id)
#         if template.lang:
#             lang = template._render_lang(self.ids)[self.id]
#         ctx = {
#              'default_model': 'project.task',
#              'default_res_id': self.ids[0],
#              'default_use_template': bool(template_id),
#              'default_template_id': template_id,
#              'default_composition_mode': 'comment',
#              'custom_layout': "mail.mail_notification_paynow",
#              'force_email': True,
#          }
#         wiz = {
#             'type': 'ir.actions.act_window',
#             'view_mode': 'form',
#             'res_model': 'mail.compose.message',
#             'views': [(False, 'form')],
#             'view_id': False,
#             'target': 'new',
#             'context': ctx,
#         }
#         wiz = Form(self.env['mail.compose.message'].with_context(ctx)).save()
#         wiz.action_send_mail()
#         self.message_post(body = "<b style='color:green;'>Enviado correo</b>")

#     def _find_mail_template_sending_change_seis(self, force_confirmation_template=False):
#         template_id = self.env['ir.model.data'].xmlid_to_res_id('as_bo_notificaciones_estrict_email.as_template_envio_email_seis', raise_if_not_found=False)
#         return template_id
    
# class AsRequestMaterialesModel(models.Model):
    
#     _inherit='as.request.materials'
    
    
#     def as_action_confirm(self):
#         res = super(AsRequestMaterialesModel, self).as_action_confirm()
#         self.as_send_email_customer_change_siete()

#         return res

#     def _get_share_url(self, redirect=False, signup_partner=False, share_token=None):
#         """
#         Build the url of the record  that will be sent by mail and adds additional parameters such as
#         access_token to bypass the recipient's rights,
#         signup_partner to allows the user to create easily an account,
#         hash token to allow the user to be authenticated in the chatter of the record portal view, if applicable
#         :param redirect : Send the redirect url instead of the direct portal share url
#         :param signup_partner: allows the user to create an account with pre-filled fields.
#         :param share_token: = partner_id - when given, a hash is generated to allow the user to be authenticated
#             in the portal chatter, if any in the target page,
#             if the user is redirected to the portal instead of the backend.
#         :return: the url of the record with access parameters, if any.
#         """
#         self.ensure_one()
#         params = {
#             'model': self._name,
#             'res_id': self.id,
#         }
#         if hasattr(self, 'access_token'):
#             params['access_token'] = self._portal_ensure_token()
#         if share_token:
#             params['share_token'] = share_token
#             params['hash'] = self._sign_token(share_token)
#         if signup_partner and hasattr(self, 'partner_id') and self.partner_id:
#             params.update(self.partner_id.signup_get_auth_param()[self.partner_id.id])

#         return '%s?%s' % ('/mail/view' if redirect else self.access_url, url_encode(params))
        
#     def as_send_email_customer_change_siete(self):
#         ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
#         self.ensure_one()
#         template_id = self._find_mail_template_sending_change_siete()
#         lang = self.env.context.get('lang')
#         template = self.env['mail.template'].browse(template_id)
#         if template.lang:
#             lang = template._render_lang(self.ids)[self.id]
#         ctx = {
#              'default_model': 'as.request.materials',
#              'default_res_id': self.ids[0],
#              'default_use_template': bool(template_id),
#              'default_template_id': template_id,
#              'default_composition_mode': 'comment',
#              'custom_layout': "mail.mail_notification_paynow",
#              'force_email': True,
#          }
#         wiz = {
#             'type': 'ir.actions.act_window',
#             'view_mode': 'form',
#             'res_model': 'mail.compose.message',
#             'views': [(False, 'form')],
#             'view_id': False,
#             'target': 'new',
#             'context': ctx,
#         }
#         wiz = Form(self.env['mail.compose.message'].with_context(ctx)).save()
#         wiz.action_send_mail()
#         self.message_post(body = "<b style='color:green;'>Enviado correo</b>")

#     def _find_mail_template_sending_change_siete(self, force_confirmation_template=False):
#         template_id = self.env['ir.model.data'].xmlid_to_res_id('as_bo_notificaciones_estrict_email.as_template_envio_email_siete', raise_if_not_found=False)
#         return template_id