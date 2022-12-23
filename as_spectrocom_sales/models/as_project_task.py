# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tests.common import Form
import logging
_logger = logging.getLogger(__name__)

class ProductTaskCustom(models.Model):
    _inherit = 'project.task'

    def extraer_solicitudes(self):

        solicitudes=self.env['as.request.materials'].sudo().search([('as_project_id','=',self.id)])
        return solicitudes
    
    @api.onchange('user_id')
    def activar_nombre_empleado(self):
        valor = self.env['hr.employee'].sudo().search([('user_id', '=', self.user_id.id)])
        if valor:
            if len(valor) <= 1:
                val_viaticos=self.env['as.viaticos'].sudo().search([('as_project_id', '=', self.id),('as_empleado','=',valor.id)])
                if val_viaticos:
                    value=''
                else:
                    vals={
                        'as_empleado' :valor.id,
                        'as_project_id':self.id
                    }
                    val_viaticos = self.env['as.viaticos'].sudo().create({
                                        'as_empleado' :valor.id,
                                        'as_project_id':self.id
                                    })
            else:
                raise UserError(_("el proyecto no esta asignado a una persona"))
        else:
            raise UserError(_("El empleado no tiene relacion con el Usuario"))
     
    def as_accion_quotation_sending(self):
        if self.user_id.id != False:
            self.ensure_one()
            template = self.env.ref('as_spectrocom_sales.as_mail_template_tarea_adjuntos', raise_if_not_found=False)
            compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
            attachment = self.env['ir.attachment'].search([('res_id','=',self.id),('res_model','=','project.task')])
            if template.lang:
                lang = template._render_lang(self.ids)[self.id]
            ctx = {
                'default_model': 'project.task',
                'default_use_template': bool(template),
                'default_template_id': template and template.id or False,
                'default_composition_mode': 'comment',
                'mark_so_as_sent': True,
                'custom_layout': "mail.mail_notification_paynow",
                'force_email': True,
                'default_attachment_ids': attachment.ids,
            }
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(compose_form.id, 'form')],
                'view_id': compose_form.id,
                'target': 'new',
                'context': ctx,
            }
        else:
            raise UserError(_("el proyecto no tiene un responsable asignado, imposible enviar el email")) 