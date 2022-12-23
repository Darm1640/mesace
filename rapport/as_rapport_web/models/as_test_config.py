import pytz
from odoo import http, api, fields, models, _
from datetime import datetime, timedelta  
from odoo.http import request
import json
import logging
_logger = logging.getLogger(__name__)
from odoo import models, fields, api
import datetime
from odoo.http import request
import requests, json
from odoo.tests.common import Form
from odoo.exceptions import UserError
    
class as_test_config(models.Model):
    _name = 'as.test.config'
    _description = 'Configuración del modelo de demo'

    name = fields.Char(string='Titulo')
    as_ini_massage = fields.Html(string='Mensaje de Ingreso a Formulario WEB')
    as_save_massage = fields.Html(string='Mensaje al guardar el Formulario WEB')

class AsEmployee(models.Model):
    _inherit = "hr.employee.test"

    def as_send_email(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template_id = self._find_mail_template_send()
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        ctx = {
            'default_model': 'hr.employee.test',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "as_rapport_web.mail_notification_light_rapport",
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


    def _find_mail_template_send(self, force_confirmation_template=False):
        template_id = self.env['ir.model.data'].xmlid_to_res_id('as_rapport_web.as_rapport_mail', raise_if_not_found=False)
        return template_id