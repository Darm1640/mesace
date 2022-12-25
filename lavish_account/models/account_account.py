import re
from odoo import models, fields, api, _

#PLAN CONTABLE - PUC

class account_account(models.Model):
    _name = 'account.account'
    _inherit = ['account.account','mail.thread', 'mail.activity.mixin']

    required_analytic_account = fields.Boolean('Obliga cuenta analítica', tracking=True)
    required_partner = fields.Boolean('Obliga tercero', tracking=True)
    accounting_class = fields.Char('Clase', tracking=True)
    code = fields.Char(tracking=True)
    user_type_id = fields.Many2one(tracking=True)
    tax_ids = fields.Many2many(tracking=True)
    group_id = fields.Many2one(tracking=True)
    company_id = fields.Many2one(tracking=True)
    account_distribution = fields.Boolean(tracking=True)
    exclude_balance_test = fields.Boolean('Permitir filtro de excluir en balance de prueba', tracking=True)

class ReportCertificationReport(models.AbstractModel):
    _inherit = 'l10n_co_reports.certification_report'

    def _get_lines(self, options, line_id=None):
        lines = []
        domain = []

        domain += self._get_domain(options)

        if line_id:
            partner_id = re.search('partner_(.+)', line_id).group(1)
            if partner_id:
                domain += [('partner_id.id', '=', partner_id)]

        amls = self.env['account.move.line'].search(domain, order='partner_id, date, id')
        previous_partner_id = self.env['res.partner']
        lines_per_group = {}

        for aml in amls:
            if previous_partner_id != aml.partner_id:
                partner_lines = self._generate_lines_for_partner(previous_partner_id, lines_per_group, options)
                if partner_lines:
                    lines += partner_lines
                    lines_per_group = {}
                previous_partner_id = aml.partner_id

            self._handle_aml(aml, lines_per_group)

        lines += self._generate_lines_for_partner(previous_partner_id, lines_per_group, options)

        return lines
