# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from pytz import utc
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import datetime
from odoo import fields, models, api, _
from odoo.tools.float_utils import float_round


class HrPersonalGroup(models.Model):
    _name = 'hr.personal.group'
    _description = 'Personal Group'
    _inherit = [
        'mail.thread', 'mail.activity.mixin'
    ]

    name = fields.Char(required=True, tracking=True)
    description = fields.Text(tracking=True)


class HrWagetype(models.Model):
    _name = 'hr.wage.type'
    _description = 'Wage Type'
    _inherit = [
        'mail.thread', 'mail.activity.mixin'
    ]

    name = fields.Char(required=True, tracking=True)
    description = fields.Text(tracking=True)


class HrPaymentMethod(models.Model):
    _name = 'hr.payment.method'
    _description = 'Payment Method'
    _inherit = [
        'mail.thread', 'mail.activity.mixin'
    ]

    name = fields.Char(required=True, tracking=True)
    description = fields.Text(tracking=True)


class HrEmployee(models.Model):
    """Hr Employee."""
    _inherit = "hr.employee"

    _rec_name = 'name'

    eps_id = fields.Many2one(
        'res.partner', 'EPS',
        domain="[('is_eps', '=', True)]",
        tracking=True)
    pension_fund_id = fields.Many2one(
        'res.partner', 'Pension Fund', domain="[('is_afp', '=', True)]",
        tracking=True)
    unemployment_fund_id = fields.Many2one(
        'res.partner', 'Unemployment Fund',
        domain="[('is_unemployee_fund', '=', True)]",
        tracking=True)
    arl_id = fields.Many2one(
        'res.partner', 'ARL',
        domain="[('is_arl', '=', True)]", tracking=True)
    prepaid_medicine_id = fields.Many2one(
        'res.partner', 'Prepaid Medicine',
        domain="[('is_prepaid_medicine', '=', True)]", tracking=True
    )
    prepaid_medicine2_id = fields.Many2one(
        'res.partner', 'Prepaid Medicine 2',
        domain="[('is_prepaid_medicine', '=', True)]", tracking=True
    )
    afc_id = fields.Many2one(
        'res.partner', 'AFC',
        domain="[('is_afc', '=', True)]", tracking=True)
    voluntary_contribution_id = fields.Many2one(
        'res.partner', 'Voluntary Contribution',
        domain="[('is_voluntary_contribution', '=', True)]",
        tracking=True)
    voluntary_contribution2_id = fields.Many2one(
        'res.partner', 'Voluntary Contribution2',
        domain="[('is_voluntary_contribution', '=', True)]",
        tracking=True)
    arl_percentage = fields.Float(
        'ARL Percentage', digits=(32, 6), tracking=True)
    medic_exam_attach = fields.Binary('Medica Exam Attachment')
    identification_id = fields.Char(tracking=True)
    private_email = fields.Char(readonly=False, tracking=True)
    ident_type = fields.Many2one('l10n_latam.identification.type', 'Identification Type',
                                 tracking=True)
    ident_issuance_date = fields.Date(
        'Identification Issuance Date', tracking=True)
    ident_issuance_city_id = fields.Char(
        'Identification Issuance City', tracking=True)
    permit_expire = fields.Date(tracking=True)
    found_layoffs_id = fields.Many2one(
        'res.partner', 'Found Layoffs',
        domain="[('is_found_layoffs', '=', True)]", tracking=True)
    hr_employee_acumulate_ids = fields.One2many(
        'hr.employee.acumulate', 'employee_id')
    allocation_leaves_count = fields.Float(
        'Allocation Leaves', tracking=True)
    leave_days_count = fields.Float(
        'Taken Leaves', tracking=True)
    remaining_leaves_count = fields.Float(
        'Remaining Leaves', tracking=True)
    personal_group_id = fields.Many2one(
        'hr.personal.group', 'Personal Group',
        tracking=True)
    wage_type_id = fields.Many2one(
        'hr.wage.type', 'Wage Type',
        tracking=True)
    payment_method_id = fields.Many2one(
        'hr.payment.method', 'Payment Method',
        tracking=True)

    def list_leaves_payroll(
            self, from_datetime, to_datetime, calendar=None, domain=None):
        """
            By default the resource calendar is used, but it can be
            changed using the `calendar` argument.

            `domain` is used in order to recognise the leaves to take,
            None means default value ('time_type', '=', 'leave')

            Returns a list of tuples (day, hours, resource.calendar.leaves)
            for each leave in the calendar.
        """
        resource = self.resource_id
        calendar = calendar or self.resource_calendar_id

        # naive datetimes are made explicit in UTC
        if not from_datetime.tzinfo:
            from_datetime = from_datetime.replace(
                tzinfo=utc)
        if not to_datetime.tzinfo:
            to_datetime = to_datetime.replace(
                tzinfo=utc)
        attendances = calendar._attendance_intervals(
            from_datetime, to_datetime, resource)
        leaves = calendar._leave_intervals_payroll(
            from_datetime, to_datetime, resource, domain)
        result = []
        for start, stop, leave in (leaves & attendances):
            hours = (stop - start).total_seconds() / 3600
            result.append((start.date(), hours, leave))
        return result

    def calculate_leaves_details(self):
        for employee in self:
            domain = [
                ('employee_id', 'in', self.ids),
                ('holiday_status_id.autocalculate_leave', '=', True),
                ('state', '=', 'validate')
            ]
            leave_not_count = 0.0
            contract_comp = self.env['hr.contract.completion'].search([
                ('employee_id', '=', employee.id)], limit=1)
            if contract_comp:
                for leave in self.env['hr.leave'].search(
                        [('employee_id', '=', employee.id),
                         ('holiday_status_id.name', '=', 'Vacaciones'),
                         ('request_date_to', '>', contract_comp.date)]):
                    leave_not_count += leave.number_of_days_display
            fields = ['number_of_days', 'employee_id']
            all_allocations = self.env['hr.leave.allocation'].read_group(
                domain, fields, groupby=['employee_id'])
            all_leaves = self.env['hr.leave.report'].read_group(
                domain, fields, groupby=['employee_id'])

            mapping_allocation = dict([(
                allocation['employee_id'][0], allocation['number_of_days']
            ) for allocation in all_allocations])
            mapping_leave = dict([(
                leave['employee_id'][0],
                leave['number_of_days']) for leave in all_leaves])

        for employee in self:
            allocation_leaves_count = float_round(
                mapping_allocation.get(employee.id, 0), precision_digits=2)
            remaining_leaves_count = float_round(
                mapping_leave.get(employee.id, 0), precision_digits=2)
            self._cr.execute('UPDATE hr_employee SET '
                             'allocation_leaves_count=%s, '
                             'remaining_leaves_count=%s, '
                             'leave_days_count=%s WHERE id=%s',
                             (allocation_leaves_count, remaining_leaves_count,
                              allocation_leaves_count - remaining_leaves_count - leave_not_count,
                              employee.id))

    def obtain_value(self, parameter, date):
        """Function to fetch Config of the salary rule."""
        result = 0
        payroll_config_id = self.env['hr.payroll.config'].search(
            [('start_date', '<=', date),
             ('end_date', '>=', date),
             ('state', '=', 'done')])
        for config in payroll_config_id:
            for config_line in config.config_line_ids:
                if config_line.name == parameter:
                    result += config_line.value
        return result

    def write(self, vals):
        if vals.get('identification_id') and self.address_home_id:
            self.address_home_id.write({
                'vat': vals.get('identification_id')})
        if vals.get('private_email') and self.address_home_id:
            email_before = self.env['hr.employee'].search([
                ('id', '=', self.id)]).private_email
            self.address_home_id.write({
                'email': vals.get('private_email')})
            self.message_post(
                subject="Calculate All",
                body=_(
                    "Private mail was changed %s -> %s" %
                    (email_before, vals.get('private_email'))))
        return super(HrEmployee, self).write(vals)

    @api.model
    def _search(self, args, offset=0, limit=None, order=None,
                count=False, access_rights_uid=None):
        if self._context.get('search_multiple_identification_id', '') and \
                self._context.get(
                    'search_multiple_identification_id_value', ''):
            new_id = self._context.get(
                'search_multiple_identification_id_value')[0].split(',')
            employee_id = []
            for rec in new_id:
                self.env.cr.execute("select id from hr_employee WHERE identification_id like %s", ['%' + rec + '%'])
                employee_recs = self.env.cr.dictfetchall()
                for employee_rec in employee_recs:
                    if employee_rec.get('id', ''):
                        employee_id.append(employee_rec.get('id', ''))
            if employee_id:
                args = [('id', 'in', employee_id)] + list(args)
        if self._context.get('not_search_multiple_identification_id', '') and \
                self._context.get(
                    'not_search_multiple_identification_id_value', ''):
            new_id = self._context.get(
                'not_search_multiple_identification_id_value')[0].split(',')
            employee_id = []
            for rec in new_id:
                self.env.cr.execute("select id from hr_employee WHERE identification_id like %s", ['%' + rec + '%'])
                employee_recs = self.env.cr.dictfetchall()
                for employee_rec in employee_recs:
                    if employee_rec.get('id', ''):
                        employee_id.append(employee_rec.get('id', ''))
            if employee_id:
                args = [('id', 'not in', employee_id)] + list(args)
        return super(HrEmployee, self)._search(
            args, offset, limit, order, count, access_rights_uid)
