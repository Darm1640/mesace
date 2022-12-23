from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from werkzeug.urls import url_encode
import time
import datetime
from datetime import datetime, timedelta, date
from time import mktime
from odoo.tests.common import Form
from dateutil.relativedelta import relativedelta
class as_crm_lead(models.Model):
    _inherit = 'crm.lead'

    as_worker_signature = fields.Binary(string='Firma del Responsable')
    as_customer_signature = fields.Binary(string='Firma del Cliente')
    as_nro = fields.Char(string='Numero')
    as_date_row = fields.Datetime(string='Fecha y Hora de Registro')
    
    def action_print_service(self):
        return self.env.ref('as_spectrocom_crm.as_action_crm_load').report_action(self)

    @api.model_create_multi
    def create(self, vals_list):
        
        for vals_product in vals_list:
            secuence =  self.env['ir.sequence'].next_by_code('as.crm.code')
            vals_product['as_nro'] = secuence
            vals_product['as_date_row']=fields.Datetime.now()
        templates = super(as_crm_lead, self).create(vals_list)
        return templates

    def action_crm_send(self):
        ''' Abre un asistente para redactar un correo electrónico, con la plantilla de correo relevante cargada de forma predeterminada '''
        self.ensure_one()
        template_id = self._find_mail_template()
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        attachment = self.env['ir.attachment'].search([('res_id','=',self.id),('res_model','=','crm.lead')])
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'crm.lead',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
            'default_attachment_ids': attachment.ids,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }
        # wiz = Form(self.env['mail.compose.message'].with_context(ctx)).save()
        # wiz.action_send_mail()
        # self.message_post(body = "<b style='color:green;'>Enviado correo</b>")

    def _find_mail_template(self, force_confirmation_template=False):
        template_id = self.env['ir.model.data'].xmlid_to_res_id('as_spectrocom_crm.as_template_crm_email_remplazo', raise_if_not_found=False)
        return template_id

    def _get_share_url(self, redirect=False, signup_partner=False, share_token=None):
        """funcion de envio de correo, se todo url share"""
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
