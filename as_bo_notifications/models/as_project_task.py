from odoo import models, fields, api
from odoo.tests.common import Form
from odoo.exceptions import UserError
class ProjectTaskModel(models.Model):
    """Heredado para crear funcion de cron quie enviara notificaciones dde facturas a whtsapp"""
    _inherit="project.task"
    
    def write(self, vals):
        bandera=False
        if 'user_id' in vals:
            bandera=True
        res = super(ProjectTaskModel, self).write(vals)
        if bandera== True:
            self.as_send_email_customer_change()
        return res
    
    def as_send_email_customer(self,tipo_email):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        # self.ensure_one()
        template_id = self._find_mail_template_sending(tipo_email)
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        attachment = self.env['ir.attachment'].search([('res_id','=',self.id),('res_model','=','project.task')])
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
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
        self.message_post(body = "<b style='color:green;'>Enviado correo</b>")

    def _find_mail_template_sending(self, tipo_email, force_confirmation_template=False):
        if tipo_email == 'venta_servicios':
            template_id = self.env['ir.model.data'].xmlid_to_res_id('as_bo_notifications.as_template_pick_email_alquiler_servicios', raise_if_not_found=False)
        return template_id

    
    
    def as_send_email_customer_change(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template_id = self._find_mail_template_sending_change()
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'project.task',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
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
        self.message_post(body = "<b style='color:green;'>Enviado correo</b>")

    def _find_mail_template_sending_change(self, force_confirmation_template=False):
        template_id = self.env['ir.model.data'].xmlid_to_res_id('as_bo_notifications.as_template_pick_email_tarea', raise_if_not_found=False)
        return template_id