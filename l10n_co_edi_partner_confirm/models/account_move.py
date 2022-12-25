from odoo import models, fields, api, _
from datetime import datetime, timedelta
from pytz import timezone

class AccountMove(models.Model):
	_inherit = "account.move"

	email_response = fields.Selection(
		[("accepted", "ACEPTADA"), ("rejected", "RECHAZADA"), ("pending", "PENDIENTE")],
		string="Decisión del cliente",
		required=True,
		default="pending",
		readonly=True,
	)
	date_email_send = fields.Datetime(
		string="Fecha envío email", readonly=True
	)
	date_email_acknowledgment = fields.Datetime(
		string="Fecha acuse email", readonly=True
	)
	email_reject_reason = fields.Char(
		string="Motivo del rechazo", readonly=True
	)

	def action_invoice_sent(self):
		res = super(AccountMove, self).action_invoice_sent()
		self.ensure_one()
		template = self.env.ref('l10n_co_edi_partner_confirm.email_template_edi_invoice_dian', raise_if_not_found=False)
		lang = False
		if template:
			lang = template._render_lang(self.ids)[self.id]
		res.get('context')['default_use_template'] = bool(template)
		res.get('context')['default_template_id'] = template and template.id or False
		return res

	def write_response(self, response, payload):
		super(AccountMove, self).write_response(response, payload)
		for rec in self:
			if rec.ei_is_valid:
				rec.date_email_send = fields.Datetime.now()

	def _get_datetime(self):
		fmt = "%Y-%m-%d %H:%M:%S"
		date_time_envio = datetime.now(timezone("UTC"))
		date_time_envio = date_time_envio + timedelta(hours=-5)
		date_time_envio = date_time_envio.strftime(fmt)
		return date_time_envio

	def _cron_validate_accept_email_dian(self):
		date_current = self._get_datetime()
		date_current = datetime.strptime(date_current, "%Y-%m-%d %H:%M:%S")

		rec_dian_documents = (
		    self.env["account.move"]
		    .sudo()
		    .search([("ei_is_valid", "=", True), ("email_response", "=", "pending")])
		)
		for move_dian in rec_dian_documents:
		    if move_dian.date_email_send:
		        time_difference = date_current - move_dian.date_email_send
		        if time_difference.days > 3:
		            move_dian.date_email_acknowledgment = fields.Datetime.now()
		            move_dian.email_response = "accepted"