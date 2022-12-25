# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrContractCompletion(models.Model):
    _name = 'hr.contract.completion'
    _inherit = [
        'mail.thread', 'mail.activity.mixin'
    ]
    _description = 'HR Contract Completion'

    @api.depends('payslip_ids', 'payslip_ids.number')
    def _compute_reference(self):
        for rec in self:
            reference = False
            for payslip in rec.payslip_ids:
                if payslip.number:
                    if reference:
                        reference += ', ' + payslip.number
                    if not reference:
                        reference = payslip.number
            rec.reference = reference

    name = fields.Char(copy=False, required=True, readonly=True,
                       default=lambda self: _('New'), help="Sequence Name",
                       tracking=True)
    employee_id = fields.Many2one(
        'hr.employee', required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    date = fields.Date(
        required=True, readonly=True,
        states={'draft': [('readonly', False), ('required', False)],
                'wait': [('readonly', False)]})
    withdrawal_reason_id = fields.Many2one(
        'hr.contract.completion.withdrawal_reason',
        readonly=True,
        states={'draft': [('readonly', False)]})
    unjustified = fields.Boolean(
        readonly=True,
        states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'),
                              ('wait', 'Wait'),
                              ('approved', 'Approved'),
                              ('rejected', 'Rejected'),
                              ('paid', 'Paid'),
                              ('reversed', 'Reversed')],
                             default='draft',
                             tracking=True)
    payslip_ids = fields.One2many(
        'hr.payslip', 'contract_completion_id',
        string='Payslips', readonly=True)
    reverse_reason = fields.Text()
    pv_id = fields.Many2one('hr.pv', 'Payroll Variation')
    contract_id = fields.Many2one('hr.contract', 'Contract')
    reference = fields.Text(compute="_compute_reference")

    @api.constrains('contract_id')
    def _check_contract_id(self):
        for rec in self:
            if not rec.contract_id:
                raise ValidationError(_(
                    "The employee don't have contract available"))

    def name_get(self):
        result = []
        name = '%s: %s' % (
            self.employee_id.name, self.withdrawal_reason_id.name)
        result.append((self.id, name))
        return result

    def action_wait(self):
        self.state = 'wait'

    def action_draft(self):
        self.state = 'draft'

    @api.onchange('employee_id', 'date')
    def onchange_employee_date_id(self):
        """Assign Contract."""
        contracts = 0
        if not self.employee_id or not self.date:
            self.contract_id = ''
        if self.employee_id and self.date:
            contract = self.employee_id._get_contracts(
                self.date.replace(day=1), self.date, states=['open'])
            if contract:
                contracts = len(contract)
                self.contract_id = contract[0]
            else:
                self.contract_id = ''
        if contracts > 1:
            return {
                'warning': {
                    'title': "Message", 'message':
                        _("This user has %s contracts" % contracts)},
            }

    def action_approve(self):
        contract = self.employee_id._get_contracts(
            self.date.replace(day=1), self.date, states=['open'])
        date_from = self.date.replace(day=1)
        date_to = self.date
        val_year = self.date.year
        slip_obj = self.env['hr.payslip']
        payslip = slip_obj.search(
            [('employee_id', '=', self.employee_id.id),
             ('date_from', '=', date_from),
             ('state', '!=', 'cancel')])
        if payslip:
            if date_from.month == 12:
                val_month = 1
                val_year = date_to.year + 1
            else:
                val_month = date_from.month + 1
            date_from = date_from.replace(month=val_month, year=val_year)
            date_to = date_from
        if not contract:
            slip_obj.create({
                'employee_id': self.employee_id.id,
                'date_from': date_from,
                'date_to': date_to,
                'name': "Contract Completion for %s" % self.employee_id.name,
                'contract_completion_id': self.id,
                'pay_annual': True,
                'pay_biannual': True,
                'unjustified': self.unjustified,
            })
        if contract:
            contract_rec = contract.id and contract or \
                           self.env['hr.contract'].browse(contract)
            if date_from.month == contract_rec.date_start.month and \
                    date_from.year == contract_rec.date_start.year:
                date_from = contract_rec.date_start
            payslip = self.env['hr.payslip'].with_context({
                'contract_completion': True}).create({
                'employee_id': self.employee_id.id,
                'date_from': date_from,
                'date_to': date_to,
                'name':
                    "Contract Completion for %s" % self.employee_id.name,
                'contract_completion_id': self.id,
                'contract_id': contract_rec.id,
                'pay_annual': True,
                'pay_biannual': True,
                'unjustified': self.unjustified,
            })
            payslip._onchange_employee()
            contract_rec.write({
                'state': 'close',
                'date_end': self.date or False,
                'reason_payroll_id': self.pv_id.reason_payroll_id.id or False,
                'reason_talent_id': self.pv_id.reason_talent_id.id or False})
        self.state = 'approved'
        # Disable employee and its user
        self.employee_id.active = False
        if self.employee_id.user_id:
            self.employee_id.user_id.active = False

    def action_reverse(self):

        # Enable employee and its user
        self.employee_id.active = True
        if self.employee_id.user_id:
            self.employee_id.user_id.active = True

        # Reverse all draft payslips
        for payslip in self.payslip_ids:
            if payslip.state == 'draft':
                payslip.state = 'cancel'
            if payslip.contract_id:
                payslip.contract_id.write({
                    'state': 'open',
                    'date_end': False,
                    'reason_payroll_id': False,
                    'reason_talent_id': False})
        self.state = 'reversed'

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hr.contract.completion.reverse.wizard',
            'target': 'new',
        }


class WithdrawalReason(models.Model):
    _name = 'hr.contract.completion.withdrawal_reason'
    _description = 'Contract Completion Withdrawal Reason'
    name = fields.Char()
    type = fields.Selection([('talent', 'Talent'),
                             ('payroll', 'Payroll')])
    description = fields.Text()
