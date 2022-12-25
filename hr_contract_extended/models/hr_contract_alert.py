# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields


class HrContractAlert(models.Model):
    _name = 'hr.contract.alert'

    name = fields.Char()
    number_days_alert = fields.Integer()
    type = fields.Selection([('individual', 'Individual'),
                             ('group', 'Group')],
                            default='individual')
    group_ids = fields.Many2many(
        'res.groups', 'hr_contract_alert_res_groups_rel',
        'hr_contract_alert_id', 'res_groups_id', string='Groups')
    user_ids = fields.Many2many(
        'res.users', 'hr_contract_alert_res_users_rel',
        'hr_contract_alert_id', 'res_users_id', string='Users')
    template_id = fields.Many2one(
        'mail.template', 'Use template',
        domain="[('model', '=', 'hr.contract.alert')]")
    alert_ids = fields.Many2many(
        'hr.contract', 'hr_contract_alert_hr_contract_rel',
        'hr_contract_alert_id', 'hr_contract_id', string='Alert Contract')
    text_message = fields.Html(related='template_id.body_html')
    is_schedule = fields.Boolean(copy=False)

    @api.model
    def fetch_contract_alert_mail(self, contract_alert):
        if contract_alert:
            contract_alert_rec = self.env[
                'hr.contract.alert'].browse(contract_alert)
            template = self.env.ref(
                'hr_contract_extended.email_template_edi_sale')
            if contract_alert_rec.type == 'individual' and template:
                template.write({'partner_to': str(
                    contract_alert_rec.user_ids.mapped(
                        'partner_id').ids)[1:-1]})
                template.send_mail(contract_alert, force_send=True)
            if contract_alert_rec.type == 'group' and template:
                if contract_alert_rec.group_ids:
                    group_user_partner_rec = []
                    for group_rec in contract_alert_rec.group_ids:
                        group_user_partner_rec.extend(group_rec.users.mapped(
                            'partner_id').ids)
                    if group_user_partner_rec:
                        group_user_partner_rec = list(
                            set(group_user_partner_rec))
                        template.write({'partner_to': str(
                            group_user_partner_rec)[1:-1]})
                        template.send_mail(contract_alert, force_send=True)

    def action_create_schedule(self):
        for rec in self:
            for rec in self:
                if rec.alert_ids:
                    self.env['ir.cron'].create({
                        'name': rec.display_name + ' Contract Alert',
                        'model_id': self.env.ref(
                            'hr_contract_extended.model_hr_contract_alert').id,
                        'user_id': self.env.user.id,
                        'interval_number': 1,
                        'interval_type': 'days',
                        'nextcall': fields.Datetime.now(),
                        'numbercall': rec.number_days_alert,
                        'code': 'model.fetch_contract_alert_mail(' +
                                str(rec.id) + ')'
                    })
                    rec.is_schedule = True
