# -*- coding: utf-8 -*-
import time
import odoo
from odoo import api, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import psycopg2
from dateutil.relativedelta import relativedelta
from odoo.tests.common import Form
from odoo.exceptions import UserError
from werkzeug.urls import url_encode
import odoo.addons.decimal_precision as dp
from odoo.tools.float_utils import float_round, float_compare
from odoo.exceptions import UserError
from odoo import models, fields, api
from datetime import datetime, timedelta, date
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    state = fields.Selection(selection_add=[('to_prove', 'Por Aprobar')], ondelete={'to_prove': 'cascade'})
    as_approval = fields.Boolean(string="Permitido aprobar",compute="_get_approvals")
    as_users_ids = fields.Many2many('res.users', string="Usuario(s) Aprobador")

    @api.depends('amount_total')
    def _get_approvals(self):
        for order in self:
            aprobar = False
            if order.move_type == 'in_invoice' and not order.invoice_origin:
                monto = order.currency_id._convert(order.amount_total,order.env.user.company_id.currency_id, order.company_id, fields.Date.context_today(self),round=False) 
                usuario = order.env.user.id
                rango_approval = self.env['as.level.approval'].sudo().search([('as_type','=','in_invoice'),('as_amount_min','<=',monto),('as_amount_max','>=',monto)],order=" id desc",limit=1)
                if rango_approval:
                    if usuario in rango_approval.as_users_ids.ids:
                        aprobar = True 
            order.as_approval = aprobar


    def button_approve(self, force=False):
        for po in self:
            po.state = 'posted'
            if po.user_id.partner_id.id:
                po.as_send_email([po.user_id.partner_id.id],'approval')
        return True

    def action_post(self):
        res = super(AccountMove, self).action_post()
        for inv in self:
            if inv.move_type == 'in_invoice' and inv.as_approval:
                self.button_confirm_approval()
        return res

    def button_confirm_approval(self):
        for order in self:
            monto = order.currency_id._convert(order.amount_total,order.env.user.company_id.currency_id, order.company_id, fields.Date.context_today(self),round=False) 
            usuario = order.env.user.id
            rango_approval = self.env['as.level.approval'].sudo().search([('as_type','=','in_invoice'),('as_amount_min','<=',monto),('as_amount_max','>=',monto)],order=" id desc",limit=1)
            if rango_approval:
                order.as_users_ids = rango_approval.as_users_ids.ids
                order.state = 'to_prove'
                partners = []
                for users in order.as_users_ids:
                    partners.append(users.partner_id.id)
                order.as_send_email(partners,'to_approval')
            else:
                continue

    def as_send_email(self,as_partner,as_type):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template_id = self._find_mail_template_send(as_type=as_type)
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'account.move',
            'default_res_id': self.ids[0],
            'default_partner_ids': as_partner,
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
        enviados = self.as_partners_get(as_partner)
        if as_type == 'to_approval':
            self.message_post(body = "<b style='color:green;'>Enviado correo para aprobación a "+str(enviados)+"</b>")
        else:
            self.message_post(body = "<b style='color:green;'>Enviada notificación de aprobación a "+str(enviados)+" fue aprobado por "+str(self.env.user.partner_id.name)+"</b>")


    def as_partners_get(self,partner):
        usuarios = ''
        partners = self.env['res.partner'].sudo().search([('id','in',partner)])
        for part in partners:
            usuarios += str(part.name)+', '
        return usuarios

    def _find_mail_template_send(self, force_confirmation_template=False,as_type=False):
        if as_type == 'to_approval':
            template_id = self.env['ir.model.data'].xmlid_to_res_id('as_bo_invoice_approval.as_template_account_email', raise_if_not_found=False)
        else:
            template_id = self.env['ir.model.data'].xmlid_to_res_id('as_bo_invoice_approval.as_template_approval_account_email', raise_if_not_found=False)
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