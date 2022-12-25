# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta
import base64
from dateutil.relativedelta import relativedelta


class HrContract(models.Model):
    _inherit = 'hr.contract'

    @api.depends('father_contract_id', 'contract_type_id',
                 'contract_type_id.trial_period_duration',
                 'date_start')
    def _calculate_trial_period_end_date(self):
        for rec in self:
            if not rec.father_contract_id and rec.contract_type_id and rec.contract_type_id.trial_period_duration:
                rec.trial_period_end_date = rec.date_start + relativedelta(
                    months=+ rec.contract_type_id.trial_period_duration)
            else:
                rec.trial_period_end_date = False

    @api.depends('father_contract_id',
                 'father_contract_id.date_start',
                 'date_start')
    def _calculate_entry_date(self):
        for rec in self:
            is_father = rec.father_contract_id
            rec.entry_date = is_father.date_start
            if not rec.father_contract_id:
                rec.entry_date = rec.date_start
            while is_father:
                is_father = is_father.father_contract_id
                if is_father:
                    rec.entry_date = is_father.date_start
                if not is_father:
                    break

    subcontract = fields.Boolean('Subcontract?', tracking=True)
    father_contract_id = fields.Many2one(
        'hr.contract', 'Father Contract', tracking=True)
    reason_change_id = fields.Many2one(
        'hr.contract.reason.change', 'Reason Change',
        copy=False, tracking=True)
    signed_contract = fields.Binary(
        string='Signed Contract')
    ret_fue_2 = fields.Float('Retention Font 2', tracking=True)
    integral_salary = fields.Boolean('Integral Salary', tracking=True)
    check_integral_salary = fields.Boolean('Integral Salary', tracking=True)
    contribution_pay = fields.Boolean('Contribution Pay', tracking=True)
    center_formation_id = fields.Many2one(
        'hr.center.formation', 'Center Formation', tracking=True)
    currency_id = fields.Many2one(string="Currency",
                                  related='company_id.currency_id', readonly=True)
    exclude_from_seniority = fields.Boolean(
        help="Check this box if the contract "
             "is not included for the seniority calculation",
        tracking=True)
    fix_wage_amount = fields.Float(
        'Fix Wage Amount', tracking=True)
    fix_wage_perc = fields.Float('Fix Wage Percentage',
                                 compute='_compute_fix_wage_perc',
                                 store=True,
                                 tracking=True, digits=(3, 2))
    flex_wage_amount = fields.Float('Flex Wage Amount',
                                    compute='_compute_flex_wage_amount',
                                    store=True,
                                    tracking=True)
    flex_wage_perc = fields.Float('Flex Wage Percentage',
                                  compute='_compute_flex_wage_perc',
                                  store=True,
                                  tracking=True, digits=(3, 2))
    total_perc = fields.Float('Total Percentage',
                              compute='_compute_total_percentage',
                              store=True,
                              tracking=True, digits=(3, 2))
    flex_wage_ids = fields.One2many(
        'hr.contract.flex_wage',
        'contract_id',
        string="Detailed Flex Wage",
        copy=True)
    contract_type_id = fields.Many2one(
        'hr.contract.type', related='', string='Contract Type',
        tracking=True,)
    date_end_required = fields.Boolean(related='contract_type_id.date_end_required',
                                       tracking=True)
    arl_percentage = fields.Float('ARL Percentage', digits=(32, 6), tracking=True)
    compare_amount = fields.Float('Compare Amount(%)', tracking=True)
    struct_id = fields.Many2one(
        'hr.payroll.structure', string='Payroll Structure', tracking=True)
    tipo_de_salario_contrato = fields.Selection([
        ('SUELDO BÁSICO', 'SUELDO BÁSICO'),
        ('SALARIO INTEGRAL', 'SALARIO INTEGRAL'),
        ('APOYO SOSTENIMIENTO', 'APOYO SOSTENIMIENTO')],
        tracking=True)
    trial_period_duration = fields.Integer(
        related='contract_type_id.trial_period_duration')
    trial_period_end_date = fields.Date(compute='_calculate_trial_period_end_date')
    entry_date = fields.Date(compute='_calculate_entry_date')

    """Field Contract Client/Work"""

    contract_client_work = fields.Char('Contract Client/Work', tracking=True)

    @api.onchange('fix_wage_amount')
    def onchange_fix_wage_amount(self):
        if self.wage > 0 and self.fix_wage_amount > 0 and \
                self.wage > self.fix_wage_amount:
            if self.flex_wage_ids:
                self.flex_wage_ids[0].amount = self.wage - self.fix_wage_amount
            else:
                salary_rule_id = ''
                if self.struct_id.categ_id.name == 'Nuevo Flex':
                    salary_rule_id = self.env['hr.salary.rule'].search(
                        [('autocomplete_flex', '=', True)], limit=1).id
                self.flex_wage_ids = [
                    (0, 0,
                     {'salary_rule_id': salary_rule_id,
                      'amount': self.wage - self.fix_wage_amount}
                     )]
        if self.fix_wage_perc and self.fix_wage_perc < 60.0:
            return {
                'warning': {
                    'title': "Warning", 'message':
                        _("By law, the fixed salary can not be less than 60 "
                          "percent of the total salary.")},
            }

    def set_entry_date(self, contarct_id):
        """ get the entry date from the first contract start date """
        contract = self.env['hr.contract']
        domain = [
            ('employee_id', '=', self.employee_id.id),
            ('exclude_from_seniority', '=', False)]
        if contarct_id:
            domain += [('id', 'not in', contarct_id.ids)]
        contract_id = contract.search(domain, order='date_start asc', limit=1)
        self.employee_id.entry_date = contract_id.date_start

    @api.model
    def create(self, vals):
        res = super(HrContract, self).create(vals)
        if vals.get('date_start'):
            res.set_entry_date([])
        return res

    def write(self, vals):
        if vals.get('wage', ''):
            vals.update({'compare_amount': (float(vals.get(
                'wage', '') * 100 / vals.get('wage', '')) - 100)})
        if vals.get('date_start') or vals.get('employee_id'):
            self.set_entry_date([])
        # self.check_employee_details()
        if vals.get('state') == 'open':
            self.employee_id.write({
                'job_id': vals.get('job_id', False) or self.job_id.id,
                'job_title': vals.get('job_id', False) or self.job_id.name})
        if self.employee_id.required_restriction:
            if vals.get('state') == 'open' and self.father_contract_id:
                new_date = \
                    self.father_contract_id.date_end - timedelta(
                        days=1) if self.father_contract_id.date_end else False
                self.father_contract_id.write({
                    'date_end': new_date, 'state': 'close'})
        return super(HrContract, self).write(vals)

    def unlink(self):
        for record in self:
            record.set_entry_date(record)
        return super(HrContract, self).unlink()

    @api.constrains('flex_wage_perc')
    def _check_flex_wage_perc(self):
        for rec in self:
            if rec.flex_wage_perc and (
                    rec.flex_wage_perc < 0.0 or rec.flex_wage_perc > 100.0):
                raise ValidationError(
                    _('Flex Wage Percentage must be between 0 and 100.'))

    @api.depends('wage', 'fix_wage_amount', 'flex_wage_ids')
    def _compute_fix_wage_perc(self):
        for rec in self.filtered('wage'):
            rec.fix_wage_perc = round(rec.fix_wage_amount / rec.wage * 100, 2)
            rec.flex_wage_amount = rec.wage - rec.fix_wage_amount

    @api.depends('wage', 'flex_wage_ids', 'fix_wage_amount')
    def _compute_flex_wage_amount(self):
        for rec in self:
            rec.flex_wage_amount = sum(rec.flex_wage_ids.mapped('amount'))

    @api.onchange('flex_wage_ids')
    def _compute_flex_wage_ids_percentage(self):
        for rec in self:
            if rec.flex_wage_amount:
                for flex in rec.flex_wage_ids:
                    flex.percentage = flex.amount / rec.flex_wage_amount * 100

    @api.depends('wage', 'flex_wage_amount')
    def _compute_flex_wage_perc(self):
        for rec in self.filtered('wage'):
            rec.flex_wage_perc = round(rec.flex_wage_amount / rec.wage * 100, 2)

    @api.depends('wage', 'fix_wage_perc', 'flex_wage_perc')
    def _compute_total_percentage(self):
        for rec in self:
            rec.total_perc = rec.fix_wage_perc + rec.flex_wage_perc

    @api.constrains('total_perc')
    def _check_total_perc(self):
        for rec in self:
            if rec.wage != 0:
                total = 0
                rec.flex_wage_amount = rec.wage - rec.fix_wage_amount
                rec.flex_wage_perc = round(rec.flex_wage_amount / rec.wage * 100, 2)
                total = round((rec.fix_wage_perc + rec.flex_wage_perc), 2)
                if rec.total_perc and (total != 100.0) and not rec._context.get('from_pv', ''):
                    raise ValidationError(_(
                        "Total percentage must be 100.00."))

    @api.constrains('state', 'employee_id')
    def check_contracts(self):
        if self.employee_id.required_restriction:
            for contract in self:
                contract_ids = self.search([
                    ('state', '=', 'open'),
                    ('employee_id', '=', contract.employee_id.id),
                    ('id', '!=', contract.id)])
                if contract_ids and contract.state == 'open':
                    raise ValidationError(_('An employee can not have 2 '
                                            'contracts in Running state!'))
                if not contract.signed_contract and contract.state == 'open':
                    raise ValidationError(_(
                        'The contract can not be placed'
                        ' in the "Running" state!'))

    def get_user_id(self, id):
        contract = self.env['hr.contract'].browse(id)
        return contract.employee_id.user_id.partner_id.id

    @api.onchange('struct_id')
    def onchange_struct_id(self):
        """Fill one2many based on contract type."""
        salary_rule_id = self.env['hr.salary.rule'].search(
            [('autocomplete_flex', '=', True)], limit=1)
        if self.struct_id.categ_id.name == 'Nuevo Flex' and salary_rule_id:
            salary_rule_id = self.env['hr.contract.flex_wage'].create(
                {'salary_rule_id': salary_rule_id.id})
            if self.wage > 0 and self.fix_wage_amount > 0 and \
                    self.wage > self.fix_wage_amount:
                salary_rule_id.write(
                    {'amount': self.wage - self.fix_wage_amount})
            return {'value': {'flex_wage_ids': salary_rule_id.ids}}

    @api.onchange('job_id')
    def _onchange_job_id(self):
        if self.job_id and self.state == 'open':
            self.employee_id.write({'job_id': self.job_id.id, 'job_title': self.job_id.name})

    @api.onchange('state')
    def onchange_state(self):
        """Subcontract is Open original contract expired."""
        for contract in self:
            if contract.state == 'open':
                contract.employee_id.write({'job_id': contract.job_id.id, 'job_title': contract.job_id.name})
            if contract.subcontract and contract.father_contract_id and \
                    contract.state == 'open':
                contract.father_contract_id.write({'state': 'close'})

    def action_report_mass(self, report_id):
        report = self.env['ir.actions.report'].search([('id', '=', report_id)])
        pdf = report.render_qweb_pdf(self.ids)
        b64_pdf = base64.b64encode(pdf[0])
        attname = "Contract-" + self.employee_id.name + str(self.id) + '.pdf'

        return {'b64_pdf': b64_pdf, 'attname': attname}

    def action_send_email(self):

        for contract in self:

            contract.ensure_one()
            ir_model_data = contract.env['ir.model.data']
            try:
                template_id = \
                    ir_model_data.get_object_reference('hr_contract_completion', 'notice_letter_email_template')[1]
            except ValueError:
                template_id = False
            try:
                compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
            except ValueError:
                compose_form_id = False
            ctx = {
                'default_model': 'hr.contract',
                'default_res_id': contract.ids[0],
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'default_composition_mode': 'comment',
                'mark_so_as_sent': True,
                'force_email': True
            }
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(compose_form_id, 'form')],
                'view_id': compose_form_id,
                'target': 'new',
                'context': ctx,
            }

    def action_send_email_mass(self, template_id, report_id, ):
        mail_template = self.env['mail.template'].search([('id', '=', template_id)])
        report = self.env['ir.actions.report'].search([('id', '=', report_id)])
        pdf = report.render_qweb_pdf(self.ids)
        b64_pdf = base64.b64encode(pdf[0])
        attname = "Notice_Letter " + self.employee_id.name + '.pdf'

        att_id = self.env['ir.attachment'].create({
            'name': attname,
            'type': 'binary',
            'datas': b64_pdf,
            'store_fname': attname,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/x-pdf'
        })

        mail_template.attachment_ids = [att_id.id]

        # mail_template = self.env.ref('hr_contract_completion.notice_letter_email_template', raise_if_not_found=False)
        # attach_document = self.env.ref('hr_contract_completion.report_hr_contract_notice_letter').render_qweb_pdf()
        mail_template.send_mail(self.id, force_send=True)


class HrContractFlexWage(models.Model):
    _name = 'hr.contract.flex_wage'
    _description = 'Flex Wage Detailed List'
    _inherit = 'mail.thread'

    salary_rule_id = fields.Many2one(
        'hr.salary.rule',
        domain=[('is_flex', '=', True)],
        tracking=True)
    #fixed = fields.Boolean(related='salary_rule_id.fixed',
    #                       tracking=True)
    fixed = fields.Boolean(tracking=True)
    amount = fields.Float(tracking=True)
    percentage = fields.Float(tracking=True, digits=(3, 2))
    contract_id = fields.Many2one('hr.contract',
                                  tracking=True)
