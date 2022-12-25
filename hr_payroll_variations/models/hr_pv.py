# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import pytz
import datetime
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools import float_compare
from odoo import api, fields, models, _, exceptions
from odoo.exceptions import UserError, ValidationError, Warning
# from ip2geotools.databases.noncommercial import DbIpCity
from odoo.http import request
import datetime


def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)


class Hrpv(models.Model):
    _name = 'hr.pv'
    _description = 'Human Resources Payroll Variants'
    _inherit = [
        'mail.thread', 'mail.activity.mixin'
    ]

    """@api.depends('employee_id.address_home_id.vat')
    def _compute_identification_id(self):
        for rec in self:
            if rec.employee_id.address_home_id.vat:
                rec.identification_id = rec.employee_id.address_home_id.vat"""

    @api.depends('employee_id')
    def _compute_wage(self):
        for rec in self:
            contract = self.env['hr.contract'].search(
                [('state', 'not in', ['close', 'cancel']),
                 ('employee_id', '=', rec.employee_id.id)],
                limit=1)
            if contract:
                rec.contract_id = contract.id
                rec.wage = contract.wage
                rec.fix_wage_amount = contract.fix_wage_amount
                rec.flex_wage_amount = contract.flex_wage_amount
            else:
                rec.wage = 0
                rec.fix_wage_amount = 0
                rec.flex_wage_amount = 0

    name = fields.Char(copy=False, required=True, readonly=True,
                       default=lambda self: _('New'), help="Sequence Name",
                       tracking=True)
    code = fields.Char(tracking=True, related="event_id.code")
    state = fields.Selection(
        [('draft', 'Draft'), ('wait', 'Wait'),
         ('wait_comments', 'Wait for comments'),
         ('wait_second_approval', 'Waiting Second Approval'),
         ('approved', 'Approved'),
         ('processed', 'Processed'),
         ('cancel', 'Cancel'),
         ('rejected', 'Rejected')],
        default='draft',
        tracking=True,
        readonly=True)

    type_id = fields.Many2one('hr.pv.type', string="Type", readonly=True,
                              states={'draft': [('readonly', False)]},
                              tracking=True)

    subtype_id = fields.Many2one('hr.pv.type.subtype', string="Sub-Type",
                                 readonly=True, tracking=True,
                                 states={'draft': [('readonly', False)]})
    event_id = fields.Many2one(
        'hr.pv.event', string="Event", readonly=True,
        states={'draft': [('readonly', False)]},
        tracking=True)
    responsible_required = fields.Boolean(
        related="event_id.responsible_required")
    responsible_id = fields.Many2one(
        'hr.employee', string="Responsible",
        readonly=True, tracking=True,
        states={'draft': [('readonly', False)]}, )
    employee_id = fields.Many2one(
        'hr.employee', string="Employee", readonly=True,
        tracking=True,
        states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner', tracking=True,
                                 help="third party who owns the debt")
    start_date = fields.Datetime(readonly=True,
                                 required=True,
                                 # default=lambda self: fields.datetime.now().replace(day=self.start_ hour=0, minute=0, second=0),
                                 states={'draft': [('readonly', False)]},
                                 tracking=True)
    unit_half = fields.Boolean(string="Half Day", tracking=True)
    start_date_period = fields.Selection(
        [('am', 'Morning'), ('pm', 'Afternoon')],
        tracking=True)
    end_date = fields.Datetime(readonly=True, tracking=True,
                               states={'draft': [('readonly', False)]})
    approved_date = fields.Datetime(readonly=True, tracking=True,
                                    states={'draft': [('readonly', False)]})
    total_days = fields.Float(compute='_compute_total_days', store=True,
                              readonly=True, states={'draft': [('readonly', False)]})
    total_days_calendar = fields.Float(string="Total days Calendar",
                                       readonly=True, states={'draft': [('readonly', False)]})
    total_hours = fields.Float(compute='_compute_total_days', store=True,
                               readonly=True, states={'draft': [('readonly', False)]})
    total_minutes = fields.Float(compute='_compute_total_days', store=True,
                                 readonly=True, states={'draft': [('readonly', False)]})
    amount = fields.Float(readonly=True, tracking=True,
                          states={'draft': [('readonly', False)]}, )
    description = fields.Text(readonly=True, tracking=True,
                              states={'draft': [('readonly', False)]}, )
    reject_reason = fields.Text(string="Reject Reason", readonly=True,
                                states={'draft': [('readonly', False)]},
                                tracking=True)
    is_user_appr = fields.Boolean(
        "Logged user is the approver",
        compute='compute_is_user_appr',
        store=False)
    is_sec_appr_user = fields.Boolean(
        "Logged user is the second approver",
        compute='compute_is_sec_appr_user',
        store=False)
    company_only = fields.Boolean(
        related="event_id.company_only")
    is_apply_date_finish = fields.Boolean(
        related="event_id.is_apply_date_finish")
    leave_id = fields.Many2one('hr.leave', 'Leave',
                               tracking=True)
    file_name = fields.Char("File Name", tracking=True)
    support = fields.Binary('Support')
    support_name = fields.Char('Support Name', tracking=True)
    support_size = fields.Char('Support Size', tracking=True)
    identification_id = fields.Char(string='Identification No', readonly=True, tracking=True,
                                    related="employee_id.identification_id", states={'draft': [('readonly', False)]})
    hr_job_id = fields.Many2one(
        'hr.job', string="HR Job", copy=False, tracking=True)
    recruitment_reason_id = fields.Many2one(
        'recruitment.reason',
        'Recruitment Reasons', copy=False, tracking=True)
    support_attach_url = fields.Char(
        "Support URL", tracking=True)
    is_attach_available = fields.Boolean(
        related="event_id.is_attach_available")
    is_recruitment = fields.Boolean(
        related="event_id.is_recruitment")
    is_contract_completion = fields.Boolean(
        related="event_id.is_contract_completion")
    is_h_e_procedure = fields.Boolean(
        related="event_id.is_h_e_procedure")
    h_e_procedure = fields.Selection([
        ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),
        ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'),
        ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'),
        ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20'),
        ('21', '21'), ('22', '22'), ('23', '23'), ('24', '24'), ('25', '25'),
        ('26', '26'), ('27', '27'), ('28', '28'), ('29', '29'), ('30', '30'),
        ('31', '31'), ('32', '32'), ('33', '33'), ('34', '34'), ('35', '35'),
        ('36', '36'), ('37', '37'), ('38', '38'), ('39', '39'), ('40', '40'),
        ('41', '41'), ('42', '42'), ('43', '43'), ('44', '44'), ('45', '45'),
        ('46', '46'), ('47', '47'), ('48', '48'), ('49', '49'), ('50', '50'),
        ('51', '51'), ('52', '52'), ('53', '53'), ('54', '54'), ('55', '55'),
        ('56', '56'), ('57', '57'), ('58', '58'), ('59', '59'), ('60', '60'),
        ('61', '61'), ('62', '62'), ('63', '63'), ('64', '64'), ('65', '65'),
        ('66', '66'), ('67', '67'), ('68', '68'), ('69', '69'), ('70', '70'),
        ('71', '71'), ('72', '72'), ('73', '73'), ('74', '74'), ('75', '75'),
        ('76', '76'), ('77', '77'), ('78', '78'), ('79', '79'), ('80', '80'),
        ('81', '81'), ('82', '82'), ('83', '83'), ('84', '84'), ('85', '85'),
        ('86', '86'), ('87', '87'), ('88', '88'), ('89', '89'), ('90', '90')],
        string='H.E Procedure', tracking=True)
    is_hour_fix = fields.Boolean(
        related="event_id.is_hour_fix")
    total_fix_hours = fields.Float(string="Total Fix Hours",
                                   tracking=True,
                                   readonly=True,
                                   states={'draft': [('readonly', False)]})
    total_fix_hour = fields.Selection([
        ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),
        ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'),
        ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'),
        ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20'),
        ('21', '21'), ('22', '22'), ('23', '23'), ('24', '24'), ('25', '25'),
        ('26', '26'), ('27', '27'), ('28', '28'), ('29', '29'), ('30', '30'),
        ('31', '31'), ('32', '32'), ('33', '33'), ('34', '34'), ('35', '35'),
        ('36', '36'), ('37', '37'), ('38', '38'), ('39', '39'), ('40', '40'),
        ('41', '41'), ('42', '42'), ('43', '43'), ('44', '44'), ('45', '45'),
        ('46', '46'), ('47', '47'), ('48', '48'), ('49', '49'), ('50', '50'),
        ('51', '51'), ('52', '52'), ('53', '53'), ('54', '54'), ('55', '55'),
        ('56', '56'), ('57', '57'), ('58', '58'), ('59', '59'), ('60', '60'),
        ('61', '61'), ('62', '62'), ('63', '63'), ('64', '64'), ('65', '65'),
        ('66', '66'), ('67', '67'), ('68', '68'), ('69', '69'), ('70', '70'),
        ('71', '71'), ('72', '72'), ('73', '73'), ('74', '74'), ('75', '75'),
        ('76', '76'), ('77', '77'), ('78', '78'), ('79', '79'), ('80', '80'),
        ('81', '81'), ('82', '82'), ('83', '83'), ('84', '84'), ('85', '85'),
        ('86', '86'), ('87', '87'), ('88', '88'), ('89', '89'), ('90', '90')],
        string='Total Fix Hours Procedure', tracking=True)
    is_type_leave = fields.Boolean(
        related="event_id.is_type_leave")
    use_extension = fields.Boolean(
        related="event_id.use_extension")
    is_eps = fields.Boolean(string='EPS', related="event_id.is_eps",
                            tracking=True)
    is_arl = fields.Boolean(string='ARL', related="event_id.is_arl",
                            tracking=True)
    is_required_attach = fields.Boolean(
        related="event_id.is_required_attach")
    currency_id = fields.Many2one(
        'res.currency', 'Currency',
        default=lambda self: self.env.ref('base.COP'),
        tracking=True)
    # hr_payroll_variations_job_id = fields.Many2one(
    #     'hr.pv.job', 'Job Position', tracking=True)
    leave_message = fields.Char('Leave Message', tracking=True)
    bank_account_id = fields.Many2one(
        'res.partner.bank', 'Bank Account', tracking=True)
    requered_account = fields.Boolean(
        related="event_id.requered_account")
    increase_salary = fields.Boolean(
        related="event_id.increase_salary", store=True)
    requered_attach_lic = fields.Boolean(
        related="event_id.requered_attach_lic")
    wage = fields.Float(compute='_compute_wage')
    fix_wage_amount = fields.Float(
        compute='_compute_wage')
    flex_wage_amount = fields.Float(
        compute='_compute_wage')
    birth_certificate = fields.Binary()
    certificate_born_alive = fields.Binary()
    certificate_week_of_gestation = fields.Binary()
    original_maternity_leave = fields.Binary()
    # relationship_id = fields.Many2one(
    #     'hr.family.relationship', 'Family Relationship',
    #     tracking=True)
    leave_code_id = fields.Many2one(
        'hr.leave.code', 'Leave Code', tracking=True)
    approved_by = fields.Many2one('res.users', 'Approved By')
    confidential = fields.Boolean()
    hiring_type = fields.Selection(
        [('direct', 'Direct'), ('temporary', 'Temporary')],
        default='direct')
    observation_recruitment = fields.Text()
    project_type = fields.Text()
    observation_increase = fields.Text()
    date = fields.Datetime(
        tracking=True)
    location = fields.Char(
        'Location',
        tracking=True)
    ip_from = fields.Char(
        'IP From',
        tracking=True)
    approved_ip_date = fields.Datetime(
        tracking=True, string="Approved IP Date")
    approved_location = fields.Char(
        'Approved Location',
        tracking=True)
    approved_ip_from = fields.Char(
        'Approved IP From',
        tracking=True)
    contact_id = fields.Many2one('res.partner', 'Contact', copy=False)
    contract_id = fields.Many2one('hr.contract', 'Contract', copy=False)
    subcontract_id = fields.Many2one('hr.contract', 'Sub Contract', copy=False)
    wage_assign = fields.Float()
    Fix_wage_assing = fields.Float()
    company_id = fields.Many2one('res.company', string='Company', readonly=True, copy=False,
                                 default=lambda self: self.env.company,
                                 states={'draft': [('readonly', False)]}, required=True)
    subcontract = fields.Boolean(
        related="contract_id.subcontract")
    is_end_business_day = fields.Boolean(
        related="event_id.is_end_business_day")
    end_business_day = fields.Datetime()
    is_optional_calendar = fields.Boolean("Is optional calendar",
                                          related="event_id.is_optional_calendar")
    calendar_id = fields.Many2one('resource.calendar', 'Calendar')
    is_apply_amount_absence = fields.Boolean(related="event_id.amount_absence")
    amount_absence = fields.Float(string='Amount Absence Convention Aid')
    pv_amount_absence_aid_id = fields.Many2one(comodel_name='hr.pv', string='PV Amount Absence Aid')
    diagnosis_is_required = fields.Boolean("Diagnosis is required", related='event_id.diagnosis_is_required')
    extension = fields.Boolean(string='extension', default=False)
    real_start_date = fields.Datetime(readonly=True, states={'draft': [('readonly', False)]},
                                      tracking=True)
    real_end_date = fields.Datetime(readonly=True, tracking=True, states={'draft': [('readonly', False)]})
    cancel_date = fields.Datetime(readonly=True, tracking=True, states={'cancel': [('readonly', False)]})
    count_days_extension = fields.Float(string='Count days extension', compute="_onchange_count_days_extension")

    """Field Automatically Remove PV"""
    pv_id = fields.Many2one('hr.pv', string='Processed PV')
    check_remove_pv = fields.Boolean(related='event_id.is_automatically_remove')

    """Extend pv"""
    extend_pv_id = fields.Many2one('hr.pv', string='Extend Pv', copy=False)
    total_day_extend = fields.Float('Total days extend')
    start_date_extend = fields.Datetime(readonly=True, related='extend_pv_id.start_date')
    end_date_extend = fields.Datetime(readonly=True, related='extend_pv_id.end_date')
    create_third_pv = fields.Boolean('Create third pv', default=False)

    """Assignment Fields"""
    replace_employee_id = fields.Many2one('hr.employee', string="Employee to replace", readonly=True,
                                          tracking=True,
                                          states={'draft': [('readonly', False)]})
    current_salary = fields.Float('Current salary', readonly=True)
    employee_id_current_salary = fields.Float('Current employee salary', readonly=True)
    employee_assignment_id = fields.Many2one('hr.assignment.employee', string='Assignment')

    """Fields type Salary"""
    salary_value = fields.Float('Salary value')
    wage_difference = fields.Float('Wage difference')

    fixed_value = fields.Float('Fixed value', readonly=True, states={'draft': [('readonly', False)]})
    type_assignment = fields.Selection(
        string='Type Assignment',
        selection=[('employee', 'Employee'),
                   ('salary', 'Salary'), ('fixed', 'Fixed')],
        required=False, readonly=True, states={'draft': [('readonly', False)]})
    flex_wage_ids = fields.One2many('hr.contract.flex_wage', 'pv_id')

    bonus_id = fields.Many2one('hr.employee.bonus', string='Bonus', readonly=True,
                               domain="[('employee_id', '=', employee_id)]",
                               states={'draft': [('readonly', False)]})
    is_bonus = fields.Boolean('Is Bonus', related='event_id.is_bonus')
    is_payment_type = fields.Boolean('Type Payment', related='event_id.is_payment_type')
    is_upc_add = fields.Boolean('UPC Add', related='event_id.is_upc_add')
    payment_type = fields.Selection(
        string='Assignment Type',
        selection=[('first', 'First'),
                   ('second', 'Second'), ('both', 'Both')],
        states={'draft': [('readonly', False)]})
    vals_visible = fields.Boolean('Vals Visible')
    is_extension = fields.Boolean(string='Is extension')
    # beneficiary_id = fields.Many2one('beneficiary', string='Beneficiary', readonly=True,
    #                                  domain="[('employee_id', '=', employee_id)]",
    #                                  states={'draft': [('readonly', False)]})

    capital_amount = fields.Float('Capital Amount')
    interest_amount = fields.Float('Interest Amount')

    """Boolean assignment fields"""
    check_type_event_assignment = fields.Boolean(related='event_id.is_type_assignment', default=False)
    manage_real_date = fields.Boolean(related='event_id.manage_date_real', default=False)

    """Discounts relation Field"""
    # is_dis_aid = fields.Boolean(string='Is_dis_aid', default=False, required=False)
    # dis_aid_id = fields.Many2one(comodel_name='hr.payroll.dis.aid', string='Discount/Aid', required=False)
    send_to_employee = fields.Boolean(related='event_id.send_to_employee')
    quotes = fields.Integer('Quotes', default=1)
    total_value = fields.Float('Total Value')
    check_calculate_amount = fields.Boolean(related='event_id.calculate_amount')

    """Discounts Sunday"""

    check_discount_sunday = fields.Boolean(related='event_id.discount_sunday')

    """Retroactive Fields"""
    generate_retroactive = fields.Boolean()
    retroactive_event = fields.Many2one(
        'hr.pv.event', string="Event", readonly=True,
        states={'draft': [('readonly', False)]},
        tracking=True)
    retroactive_initial_date = fields.Date("Retroactive From Date")
    is_generated_retroactive = fields.Boolean()
    automatically_remove = fields.Boolean(
        related="event_id.is_automatically_remove")
    contribution_deduction = fields.Boolean(
        related="event_id.contribution_deduction")
    affiliation_date = fields.Date("Affiliation Date")
    affiliation_number = fields.Char("Affiliation Number")
    affiliation_partner_id = fields.Many2one('res.partner', tracking=True)
    contribution_company = fields.Boolean("Contribution Company")
    percentage_company = fields.Float('Percentage Company')
    percentage_employee = fields.Float('Percentage Employee')
    total_company = fields.Float('Total Company')
    total_employee = fields.Float('Total Employee')

    @api.onchange('percentage_company', 'percentage_employee')
    def calculate_total_value_deductions(self):
        if self.amount > 0:
            if self.percentage_company > 0:
                self.total_company = (self.amount * self.percentage_company / 100)
            if self.percentage_employee > 0:
                self.total_employee = (self.amount * self.percentage_employee / 100)

    @api.onchange('quotes', 'total_value')
    def calculate_total_value(self):
        if self.total_value != 0:
            self.amount = (self.total_value / self.quotes)

    @api.onchange('real_start_date', 'is_extension')
    def calculate_domain_extend_pv(self):
        if self.is_extension:
            current_date = self.real_start_date - relativedelta(days=2)
            current_date = current_date.strftime('%Y-%m-%d %H:%M:%S')
            comain = self.search([('employee_id', '=', self.employee_id.id), ('is_type_leave', '=', True),
                                  ('real_end_date', '>', current_date), ('id', 'not in', self.ids)])
            res = {}
            res['domain'] = {
                'extend_pv_id': [('employee_id', '=', self.employee_id.id), ('is_type_leave', '=', True),
                                 ('real_end_date', '>', current_date), ('id', 'not in', self.ids)]}

            return res

    @api.onchange('extend_pv_id')
    def onchange_extend_pv_id(self):
        if self.extend_pv_id:
            self.total_day_extend = 0
            pv_principal = self.extend_pv_id

            if pv_principal:
                count_days_extension = 0
                while pv_principal:
                    if not pv_principal.extend_pv_id:
                        count_days_extension += pv_principal.count_days_extension
                        pv_principal = pv_principal.extend_pv_id
                    else:
                        count_days_extension += pv_principal.count_days_extension
                        pv_principal = pv_principal.extend_pv_id

            if count_days_extension > 0:
                self.count_days_extension = self.count_days_extension + count_days_extension

            if self.count_days_extension > 180:
                raise exceptions.ValidationError(
                    _('Extension days exceed 180 days, create an extension for the 180 days'))
            else:
                self.total_day_extend = self.count_days_extension

    @api.onchange('is_arl')
    def clear_fields_arl(self):
        if self.is_arl == True:
            self.is_eps = False

    @api.onchange('is_eps')
    def clear_fields_eps(self):
        if self.is_eps == True:
            self.is_arl = False
            if self.employee_id.eps_id.required_physical_evidence:
                raise ValidationError(_('You have delivery evidence phisical of the leave'))

    @api.onchange('event_id')
    def clear_fields(self):
        self.type_assignment = None
        if self.event_id.is_apply_date_finish:
            if fields.datetime.now().hour > 0 and fields.datetime.now().hour < 5:
                self.start_date = fields.datetime.now().replace(hour=5, minute=0, second=0) - timedelta(days=1)
                self.real_start_date = self.start_date
            else:
                self.start_date = fields.datetime.now().replace(hour=5, minute=0, second=0)
                self.real_start_date = self.start_date
            self.end_date = self.start_date.replace(day=self.start_date.day, hour=4, minute=59, second=59) + timedelta(
                days=1)
            self.real_end_date = self.end_date

    @api.onchange('salary_value')
    def onchange_salary_value(self):
        if self.salary_value:
            if self.salary_value > self.employee_id_current_salary:
                self.wage_difference = self.salary_value - self.employee_id_current_salary
            else:
                self.wage_difference = self.employee_id_current_salary - self.salary_value

            if self.wage_difference < 0:
                raise exceptions.ValidationError(_('You cannot replace an employee with a lower salary'))

            amount = (self.wage_difference) / 30
            self.amount = amount

    @api.onchange('type_assignment')
    def clear_fields_assignment(self):
        self.replace_employee_id = None
        self.current_salary = None
        self.fixed_value = None
        self.amount = None

    @api.onchange('replace_employee_id')
    def onchange_replace_employee(self):
        self.current_salary = None
        if self.replace_employee_id:
            if self.replace_employee_id == self.employee_id:
                raise ValidationError(_('The employee cannot be equal to the employee to be replaced'))
            else:
                contract = self.env['hr.contract'].search(
                    [('employee_id', '=', self.replace_employee_id.id), ('active', '=', True), ('state', '=', 'open')])
                if contract:
                    self.current_salary = contract.wage
                    self.flex_wage_ids = contract.flex_wage_ids

                    if self.current_salary < self.employee_id_current_salary:
                        return {
                            'warning': {
                                'title': _('Warning!'),
                                'message': _("The selected assignment is of lower salary allocation")}
                        }

    @api.onchange('fixed_value')
    def onchange_fixed_value(self):
        if self.fixed_value != 0:
            self.amount = self.fixed_value

    @api.onchange('current_salary')
    def onchange_current_salary(self):
        if self.current_salary != 0:
            if self.current_salary > self.employee_id_current_salary:
                self.wage_difference = self.current_salary - self.employee_id_current_salary
            else:
                self.wage_difference = self.employee_id_current_salary - self.current_salary

            amount = (self.wage_difference * self.total_days) / 30
            self.amount = amount

    def search(self, args, offset=0, limit=None, order=None, count=False):
        res = super(Hrpv, self).search(args, offset, limit, order, count=count)
        if not self._context.get('pv_approve'):
            return res
        login_user = self.env['res.users'].sudo().browse(self._uid)
        daf_pv = bp_pv = sst_pv = self.env['hr.pv']
        if login_user.has_group('hr_payroll_variations.group_daf'):
            daf_pv = res.filtered(lambda pv: pv.event_id.approver == 'daf')
        if login_user.has_group('hr_payroll_variations.group_bp'):
            bp_pv = res.filtered(lambda pv: pv.event_id.approver == 'bp')
        if login_user.has_group('hr_payroll_variations.group_sst'):
            sst_pv = res.filtered(lambda pv: pv.event_id.approver == 'sst')
        pv_combination = daf_pv + bp_pv + sst_pv
        remaining_pv = res - pv_combination
        for pv in remaining_pv:
            if pv.event_id and pv.event_id.is_optional_approver and pv.event_id.optional_approver_group_id:
                self._cr.execute("""SELECT 1 FROM res_groups_users_rel WHERE uid=%s AND gid=%s""",
                                 (self._uid, pv.event_id.optional_approver_group_id.id))
                if bool(self._cr.fetchone()):
                    pv_combination += pv
            if pv.event_id and pv.event_id.is_optional_approver_2 and pv.event_id.optional_approver2_group_id:
                self._cr.execute("""SELECT 1 FROM res_groups_users_rel WHERE uid=%s AND gid=%s""",
                                 (self._uid, pv.event_id.optional_approver2_group_id.id))
                if bool(self._cr.fetchone()):
                    pv_combination += pv
        return pv_combination

    @api.constrains('total_days', 'start_date', 'end_date', 'subtype_id')
    def limit_total_days(self):
        for rec in self:
            if rec.state == 'draft' and \
                    rec.subtype_id.id == self.env.ref(
                'hr_payroll_variations.pv_subtype_AUS').id:
                min_days = rec.event_id.min_days
                max_days = rec.event_id.max_days
                if (rec.total_days < min_days) or (rec.total_days > max_days) and \
                        rec.subtype_id.id == self.env.ref(
                    'hr_payroll_variations.pv_subtype_AUS').id:
                    raise UserError(_("the amount of days exceeds "
                                      "(default or excess) the event limit"))
        return False

    @api.constrains('amount', 'percentage')
    def amount_percentage(self):
        for rec in self:
            if rec.state == 'draft' and \
                    rec.type_id.id == self.env.ref(
                'hr_payroll_variations.pv_type_ECO').id:
                if rec.amount == 0.0 and rec.percentage == 0.0:
                    raise UserError(_("the amount or percentage must be better 0"))
        return False

    @api.constrains('employee_id', 'identification_id', 'start_date', 'end_date')
    def _check_date(self):
        for item in self:
            if item.employee_id and item.employee_id.identification_id:
                if item.identification_id != item.employee_id.identification_id:
                    raise UserError(
                        _("El número de identificación no corresponde al empleado")
                    )
            elif item.identification_id and not item.employee_id:
                pv_id = self.search([
                    ('id', '=', self.id)])
                if pv_id and pv_id.employee_id and item.identification_id != pv_id.employee_id.identification_id:
                    raise UserError(
                        _("El número de identificación no corresponde al empleado")
                    )
            if not item.event_id.is_fuero_salud and not item.event_id.allow_collision:
                if item.subtype_id.name not in ('Fija', 'Ocasional') and \
                        not item.event_id.is_hour_fix:
                    item_ids = self.search([
                        ('start_date', '<=', item.end_date),
                        ('end_date', '>=', item.start_date),
                        ('employee_id', '=', item.employee_id.id),
                        ('id', '<>', item.id),
                        ('subtype_id', '=', self.env.ref(
                            'hr_payroll_variations.pv_subtype_AUS').id),
                        ('state', 'not in', ('rejected', 'cancel'))])
                    if item_ids and not item_ids[0].event_id.allow_collision:
                        raise UserError(
                            _("You cannot create two pv with the same Employee "
                              "and Start Date and End Date mix. The other record is " + str(item_ids[0].name) +
                              " in dates " + str(item_ids[0].start_date) + " - " + str(item_ids[0].end_date)) +
                            " with the event " + str(item_ids[0].event_id.name)
                        )
            if item.is_extension and item.count_days_extension > 0 and \
                    item.count_days_extension != item.total_days_calendar and \
                    item.subtype_id.id == self.env.ref(
                'hr_payroll_variations.pv_subtype_AUS').id:
                raise UserError(
                    _("Los días aplicados como extensión y los días calendario no pueden ser diferentes")
                )

        return True

    @api.depends('start_date', 'end_date', 'unit_half',
                 'total_fix_hours', 'employee_id')
    def _compute_total_days(self):
        for rec in self:
            if rec.event_id.is_hour_fix and rec.total_fix_hours:
                rec.total_days = float((rec.total_fix_hours) / 8)
                rec.total_days_calendar = float((rec.total_fix_hours) / 8)
            else:
                if rec.start_date and rec.end_date and rec.employee_id:
                    dif_years = rec.end_date.year - rec.start_date.year
                    if dif_years <= 100:
                        start_date = rec.start_date - datetime.timedelta(hours=5)
                        end_date = rec.end_date - datetime.timedelta(hours=5)
                        aux = rec.event_id.get_total_days_calendar(
                            rec.start_date, rec.end_date, rec.employee_id)
                        rec.total_days = rec.event_id.get_total_days(
                            rec.start_date, rec.end_date, rec.employee_id, rec.calendar_id)
                        rec.total_hours = rec.total_days * 8
                        rec.total_minutes = rec.total_hours * 60

                        if (start_date.year == end_date.year) and (start_date.month == end_date.month) and (
                                start_date.day == end_date.day):
                            rec.total_hours = end_date.hour - start_date.hour

                        rec.total_minutes = rec.total_hours * 60

                        global_leave_days = 0
                        rec.total_days_calendar = aux
                        if rec.event_id.calendar_type == 'employee':
                            global_leave_days = self.env[
                                'resource.calendar.leaves'].search_count(
                                [('calendar_id', '=',
                                  rec.employee_id.resource_calendar_id.id),
                                 ('resource_id', '=', False),
                                 ('date_from', '>=', start_date),
                                 ('date_to', '<=', end_date)])
                    else:
                        rec.total_hours = 0
                        rec.total_minutes = 0
                        rec.total_days_calendar = 0
                        rec.total_days = 0

                elif rec.start_date and rec.unit_half and rec.employee_id:
                    rec.total_days = 0.5
                    rec.total_days_calendar = 0.5
                    rec.total_hours = 4
                    rec.total_minutes = 240
                else:
                    rec.total_days = rec.total_days or 0
                    rec.total_days_calendar = rec.total_days_calendar or 0
                    rec.total_hours = rec.total_hours or 0
                    rec.total_minutes = rec.total_minutes or 0

    @api.constrains('start_date', 'end_date', 'unit_half', 'event_id', 'type_id')
    def _validate_working_hours(self):
        if self.event_id:
            for item in self:
                if item.employee_id:
                    working_structure = item.employee_id.contract_id.structure_type_id.default_resource_calendar_id.attendance_ids
                    working_days = []
                    for day in working_structure:
                        working_days.append(day.dayofweek)
                    working_days = list(set(working_days))
                    if item.type_id.name == _("Time") and item.event_id.only_work_hours:
                        if not item.start_date.weekday() in working_days:
                            raise ValidationError(
                                _(
                                    "The working hours do not match the assigned schedule please check the dates entered"))
                        if not item.end_date.weekday() in working_days:
                            raise ValidationError(
                                _(
                                    "The working hours do not match the assigned schedule please check the dates entered"))
                    if item.event_id.name == _("Inability"):
                        if not item.start_date.weekday() in working_days:
                            raise ValidationError(
                                _("The PV is not on working hours"))
                else:
                    raise ValidationError(
                        _("Please select the employee first"))

    @api.constrains('start_date', 'end_date', 'unit_half', 'event_id', 'type_id')
    def _validate_working_days(self):
        if self.event_id:
            for item in self:
                if item.employee_id:
                    working_structure = item.employee_id.resource_calendar_id.attendance_ids
                    working_days = []
                    for day in working_structure:
                        working_days.append(int(day.dayofweek))
                    working_days = list(set(working_days))
                    if item.event_id.only_work_days and item.start_date.weekday() not in working_days:
                        raise ValidationError(
                            _("This event cannot be create in days  work employee calendar out "))
                else:
                    raise ValidationError(
                        _("Please select the employee first"))

    @api.onchange('event_id', 'employee_id')
    def onchange_event_id_change(self):
        if self.event_id.subtype_id.name == 'Terminación de Contrato':
            if self.employee_id:
                pv = self.env['hr.pv'].search(
                    [('employee_id', '=', self.employee_id.id), ('subtype_id', '=', 'Ausencia'),
                     ('type_id', '=', 'Tiempo'), ('end_date', '>=', self.start_date),
                     ('start_date', '>=', self.start_date)])
                if pv:
                    raise UserError(_("The employee is absent"))

        self.type_id = self.subtype_id = False
        if self.event_id:
            self.type_id = self.event_id.type_id
            self.subtype_id = self.event_id.subtype_id

        if self.employee_id:
            self.company_id = self.employee_id.company_id

        """Domain on employee based on the event."""
        """if not self.event_id and self.employee_id:
            self.employee_id = ''"""
        if self.event_id and self.event_id.name == \
                'Licencia de Maternidad' and self.employee_id and \
                self.employee_id.gender != 'female':
            self.employee_id = ''
        if self.event_id and self.event_id.name == \
                'Licencia de Paternidad' and self.employee_id and \
                self.employee_id.gender != 'male':
            self.employee_id = ''
        if self.event_id and self.event_id.name == 'Licencia de Maternidad':
            return {'domain': {'employee_id': [('gender', '=', 'female')]}}
        if self.event_id and self.event_id.name == 'Licencia de Paternidad':
            return {'domain': {'employee_id': [('gender', '=', 'male')]}}
        return {'domain': {'employee_id': []}}

    @api.onchange('unit_half')
    def onchange_unithalf(self):
        self.end_date = ''

    @api.onchange('identification_id')
    def onchange_identification_id(self):
        if self.identification_id:
            employee = self.env['hr.employee'].search([('identification_id', '=', self.identification_id)])
            if employee:
                self.employee_id = employee.id

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id:
            self.identification_id = self.employee_id.identification_id
            contract = self.env['hr.contract'].search(
                [('employee_id', '=', self.employee_id.id), ('active', '=', True), ('state', '=', 'open')])
            if contract:
                self.employee_id_current_salary = contract.wage

    @api.constrains('start_date', 'end_date')
    def check_dates(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise UserError(_("The start date cannot "
                                  "occur after end date"))

    def action_wait(self):
        if self.event_id.is_required_attach:
            self.check_exist_attach()
        vals = {}
        if self.name == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'hr.pv') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('hr.pv') or _('New')
        vals['state'] = 'wait'
        self.write(vals)

    def check_exist_attach(self):
        ''' Attachment in DB use next code
        att_ids = self.env['ir.attachment'].search([
            ('res_model', '=', 'hr.pv'),
            ('res_id', '=', self.id)])
        '''
        # Attachment in filestore use next code
        if not self.support:
            raise UserError(_("This event requires an attach"))

    def action_wait_comments(self):
        self.state = 'wait_comments'

    """ def action_recruitment(self):
        for rec in self:
            if rec.hr_job_id:
                rec.hr_job_id.write({
                    'no_of_recruitment': rec.hr_job_id.no_of_recruitment + 1})
                # hr_payroll_variations_job_id = self.env['hr.pv.job'].create({
                #     'pv_id': rec.id,
                #     'job_id': rec.hr_job_id.id,
                #     'recruitment_reason_id': rec.recruitment_reason_id.id,
                #     'employee_id': rec.employee_id.id or '',
                #     'state': rec.hr_job_id.state
                # })
                rec.write({'hr_payroll_variations_job_id': hr_payroll_variations_job_id.id})"""

    def action_approve(self, boss_employee=False):
        res = {}
        if boss_employee and self.event_id.approver == 'jd':
            if self.employee_id.id == boss_employee:
                if not self.event_id.is_apply_date_finish:
                    if self.event_id.second_approver_required:
                        self.state = 'wait_second_approval'
                    else:
                        res = self._create_record()
                        self.state = 'approved'
                        self.approved_date = str(fields.Datetime.now())
                        self.approved_by = self.env.uid
                else:
                    if not self.end_date and not self.is_hour_fix and \
                            self.type_id.id != self.env.ref('hr_payroll_variations.pv_type_ECO').id:
                        raise UserError(_("Please fill end date."))
                    else:
                        if self.event_id.second_approver_required:
                            self.state = 'wait_second_approval'
                        else:
                            res = self._create_record()
                            self.state = 'approved'
                            self.approved_date = str(fields.Datetime.now())
                            self.approved_by = self.env.uid
        else:
            if not self.event_id.is_apply_date_finish:
                if self.event_id.second_approver_required:
                    self.state = 'wait_second_approval'
                else:
                    res = self._create_record()
                    self.state = 'approved'
                    self.approved_date = str(fields.Datetime.now())
                    self.approved_by = self.env.uid
            else:
                if not self.end_date and not self.is_hour_fix and \
                        self.type_id.id != self.env.ref('hr_payroll_variations.pv_type_ECO').id:
                    raise UserError(_("Please fill end date."))
                else:
                    if self.event_id.second_approver_required:
                        self.state = 'wait_second_approval'
                    else:
                        res = self._create_record()
                        self.state = 'approved'
                        self.approved_date = str(fields.Datetime.now())
                        self.approved_by = self.env.uid
        # try:
        #     ip_addr = request.httprequest.environ.get(
        #         'HTTP_X_FORWARDED_FOR', '').rsplit(',', 1)[0]
        #     if ip_addr:
        #         self.approved_ip_from = ip_addr
        #         response = DbIpCity.get(ip_addr, api_key='free')
        #         self.approved_location = 'Latitude:-' + str(
        #             response.latitude) + ' Longitude:-' + str(
        #             response.longitude)
        #         country = response.country
        #         country_tz = pytz.country_timezones(country)
        #         if country_tz:
        #             local = country_tz[0]
        #             naive = datetime.datetime.strptime(
        #                 fields.Datetime.to_string(
        #                     fields.Datetime.now()),
        #                 DEFAULT_SERVER_DATETIME_FORMAT)
        #             local_time = naive.astimezone(pytz.timezone(local))
        #             utc_time = local_time.astimezone(pytz.utc)
        #             self.approved_ip_date = utc_time.strftime(
        #                 DEFAULT_SERVER_DATETIME_FORMAT)
        # except:
        #     pass

        if self.state == 'approved' and self.event_id.discount_sunday:
            date_to = self.end_date
            next_sunday = next_weekday(date_to, 6)
            pv = self.env['hr.pv'].create({
                'event_id': self.event_id.event_id.id,
                'employee_id': self.employee_id.id,
                'start_date': next_sunday + timedelta(minutes=1),
                'end_date': next_sunday + timedelta(hours=23, minutes=59),
            })

            pv.action_approve()

            self.pv_id = pv.id

        if self.state == 'approved' and self.is_apply_amount_absence:
            pv = self.env['hr.pv'].create({
                'event_id': self.event_id.convention_aid_event_id.id,
                'employee_id': self.employee_id.id,
                'start_date': self.start_date,
                'end_date': self.end_date,
                'amount': self.amount_absence
            })
            self.pv_amount_absence_aid_id = pv.id

        if self.state == 'approved' and self.event_id.report_employee_tag:
            if self.event_id.category_id:
                category = self.event_id.category_id
                self.employee_id.write({
                    'category_ids': [(4, category.id)]
                })

        if self.state == 'approved' and self.event_id.is_automatically_remove:
            pv_process = self.env['hr.pv'].search(
                [('employee_id', '=', self.employee_id.id), ('state', '=', 'approved'),
                 '&', ('event_id', '=', self.event_id.id), ('check_remove_pv', '=', True),
                 ('is_generated_retroactive', '=', False), ('id', '!=', self.id)],
                limit=1)
            if pv_process:
                for pv in pv_process:
                    pv.update({
                        'state': 'processed',
                        'end_date': self.start_date - relativedelta(days=1)
                    })
                    amount = pv.amount
                    self.update({
                        'pv_id': pv.id,
                    })
            if self.generate_retroactive:
                if self.retroactive_initial_date >= self.start_date.date():
                    raise exceptions.ValidationError(
                        _('The starting date cannot be greater than the retroactive starting date'))

                dif_date = relativedelta(self.start_date, self.retroactive_initial_date)
                dif_month = dif_date.years * 12 + dif_date.months

                if pv_process:
                    retroactive_amount = self.amount - pv_process.amount

                else:
                    retroactive_amount = self.amount

                vals = {
                    'employee_id': self.employee_id.id,
                    'event_id': self.retroactive_event.id,
                    'start_date': self.start_date,
                    'end_date': self.start_date,
                    'type_id': self.retroactive_event.type_id.id,
                    'subtype_id': self.retroactive_event.subtype_id.id,
                    'pv_id': self.id,
                    'is_generated_retroactive': True,
                    'amount': retroactive_amount * dif_month,
                    'payment_type': self.payment_type,
                }
                retroactive_id = self.env['hr.pv'].create(vals)
                retroactive_id.write({
                    'state': 'approved'
                })

            if self.end_date and self.create_third_pv:
                pv_id = self.env['hr.pv'].browse(self.id)
                new_pv_id = pv_id.copy()
                new_pv_id.write({
                    'start_date': self.end_date + relativedelta(days=1),
                    'end_date': None,
                    'pv_id': None,
                    'amount': self.pv_id.amount or pv_id.amount,
                    'state': 'draft',
                    'create_third_pv': False,
                    'approved_by': False,
                    'approved_date': False,
                })

        if self.state == 'approved' and self.type_assignment == 'employee':

            for flex_wage in self.flex_wage_ids:
                for flex_wage_employee in self.contract_id.flex_wage_ids:
                    if flex_wage.salary_rule_id == flex_wage_employee.salary_rule_id:
                        amount = flex_wage.amount - flex_wage_employee.amount
                        if not amount <= 0:
                            vals = {
                                'check_type_event_assignment': True,
                                'type_id': self.type_id.id,
                                'subtype_id': self.subtype_id.id,
                                'event_id': self.event_id.id,
                                'employee_id': self.employee_id.id,
                                'identification_id': self.identification_id,
                                'employee_id_current_salary': self.employee_id_current_salary,
                                'type_assignment': self.type_assignment,
                                'replace_employee_id': self.replace_employee_id.id,
                                'flex_wage_ids': self.flex_wage_ids,
                                'current_salary': self.current_salary,
                                'start_date': self.start_date,
                                'end_date': self.end_date,
                                'description': flex_wage.salary_rule_id.name,
                                'amount': amount,
                            }
                            pv = self.env['hr.pv'].create(vals)
                            pv.update({
                                'state': 'approved',
                                'flex_wage_ids': pv.flex_wage_ids,
                            })

        return res

    def action_massive_approval(self):
        """Massive Approval pv."""
        flag = False
        pvs = ''
        for approval in self:
            if approval.state in ['draft', 'wait', 'wait_comments'] and \
                    approval.is_user_appr:
                try:
                    approval.action_approve()
                except:
                    raise ValidationError(_(
                        'pv:- ' + str(approval.name) +
                        ' has a problem for approval'))
            else:
                flag = True
                if not pvs:
                    pvs += str(approval.name)
                else:
                    pvs += ', ' + str(approval.name)
        if flag:
            raise ValidationError(_(
                'Some pvs are not in the Wait/Wait for Comments or may '
                'be Logged user is the approver is False.\n pvs:- ' +
                pvs))

    def action_second_approval(self):
        # if not self.contact_id:
        #    raise UserError(_(
        #        "Please enter Contact"))
        # if not self.employee_id:
        #    raise UserError(_(
        #        "Please enter Employee"))
        # if not self.contract_id:
        #    raise UserError(_(
        #        "Please enter Contract"))
        if self.is_sec_appr_user:
            self._create_record()
            self.state = 'approved'
            self.approved_date = str(fields.Date.today())
        else:
            raise UserError(_(
                "This user can't approve. He/She is not in the "
                "group %s" % self.event_id.second_approver_group_id.name))

    def action_draft(self):
        for rec in self:
            if rec.leave_id:
                if rec.leave_id.state == 'validate':
                    rec.leave_id.action_refuse()
                    rec.leave_id.action_draft()
                rec.leave_id.unlink()
            rec.after_close = False
            rec.state = 'draft'

    def action_cancel(self):
        for rec in self:
            if rec.leave_id:
                if rec.leave_id.state == 'validate':
                    rec.leave_id.action_refuse()
                    rec.leave_id.action_draft()
                rec.leave_id.unlink()
            if rec.pv_amount_absence_aid_id:
                rec.pv_amount_absence_aid_id.state = 'cancel'
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hr.pv.cancel.wizard',
            'target': 'new',
        }

    def _create_record(self):
        # Override this method from new modules

        if self.subtype_id == self.env.ref(
                'hr_payroll_variations.pv_subtype_AUS') and self.employee_id:
            message = self.create_leave()
            self.message_post(
                body=message,
                subtype='mail.mt_comment',
                message_type='email',
                partner_ids=self.message_follower_ids.mapped('partner_id.id'))

            tz_name = self._context.get('tz') or self.env.user.tz or 'UTC'

            st_utc = pytz.timezone('UTC').localize(
                self.start_date, is_dst=False)
            if self.end_date:
                en_utc = pytz.timezone('UTC').localize(self.end_date, is_dst=False)
            else:
                en_utc = pytz.timezone('UTC').localize(self.start_date, is_dst=False)

            start_date_local = st_utc.astimezone(pytz.timezone(tz_name)).date()
            end_date_local = en_utc.astimezone(pytz.timezone(tz_name)).date()

            if start_date_local != self.leave_id.request_date_from or end_date_local != self.leave_id.request_date_to:
                self.leave_message = 'The leave create with Start Date (%s) and End Date (%s)!' % (
                    self.leave_id.request_date_from, self.leave_id.request_date_to)
                view_id = self.env.ref('hr_payroll_variations.check_date_wizard').id
                return {
                    'name': _('Mismatch Date'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'hr.pv.check.date.wizard',
                    'view_id': view_id,
                    'target': 'new',
                    'context': {'message': self.leave_message},
                }
        return True

    def create_leave(self):
        res = False
        if self.event_id.advance_holidays:
            res = self.create_leave_allocation()
        elif self.event_id.projection_vacation:
            res = self.create_projection_leave_allocation()
        tz_name = self._context.get('tz') or self.env.user.tz or 'UTC'
        if not self.end_date and self.event_id.is_hour_fix:
            self.end_date = self.start_date

        if self.start_date and self.end_date and self.employee_id:
            st_utc = pytz.timezone('UTC').localize(
                self.start_date, is_dst=False)
            en_utc = pytz.timezone('UTC').localize(self.end_date, is_dst=False)
            leave_id = self.env['hr.leave'].create({
                'pv_ref': self.name,
                'name': self.description,
                'holiday_status_id': self.event_id.leave_type_id.id,
                'holiday_type': 'employee',
                'employee_id': self.employee_id.id,
                'request_date_from': st_utc.astimezone(pytz.timezone(tz_name)),
                'request_date_to': en_utc.astimezone(pytz.timezone(tz_name)),
                'number_of_days': self.total_days,
                'report_note': self.description,
                'is_arl': self.is_arl,
                'is_eps': self.is_eps,
                'date_from': self.start_date,
                'date_to': self.end_date,
                'allow_collision': self.event_id.allow_collision
            })
            leave_id.action_approve()
            self.leave_id = leave_id
            if res:
                res.action_refuse()
                res.action_draft()
                self._cr.execute(
                    "DELETE FROM hr_leave_allocation WHERE id=%s", (res.id,))
        return "A new Leave has been created in HR Leaves"

    def create_leave_allocation(self):
        """ Allocates New Leaves to Employees based on Limit Advance in pv Event - Darshan
        :param self:     pv.
        :return:         Leave Allocation."""
        for rec in self:
            leave_days = rec.event_id.leave_type_id.get_days(rec.employee_id.id)[rec.event_id.leave_type_id.id]
            if float_compare(leave_days['virtual_remaining_leaves'], rec.total_days, precision_digits=2) == -1:
                if rec.total_days - leave_days['virtual_remaining_leaves'] > rec.event_id.limit_advance:
                    raise UserError(_(
                        "pv Event doesn't have enough Limit Advance Days : %d assigned. Please review the process before continue." % rec.event_id.limit_advance))
                elif float_compare(rec.total_days - leave_days['virtual_remaining_leaves'],
                                   rec.event_id.limit_advance,
                                   precision_digits=2) == -1 or \
                        float_compare(rec.total_days - leave_days['virtual_remaining_leaves'],
                                      rec.event_id.limit_advance, precision_digits=2) == 0:
                    leave_allocation_id = self.env['hr.leave.allocation'].create({
                        'name': rec.name,
                        'holiday_status_id': rec.event_id.leave_type_id.id,
                        'holiday_type': 'employee',
                        'employee_id': rec.employee_id.id,
                        'number_of_days': rec.total_days - leave_days['virtual_remaining_leaves'],
                    })
                    leave_allocation_id.action_approve()
                return leave_allocation_id
            return True

    def create_projection_leave_allocation(self):
        """ Allocates New Leaves to Employees based on Projection for Advance Months - Darshan
        :param self:     pv.
        :return:         Leave Allocation."""
        for rec in self:
            leave_days = rec.event_id.leave_type_id.get_days(rec.employee_id.id)[rec.event_id.leave_type_id.id]
            if float_compare(leave_days['virtual_remaining_leaves'], rec.total_days, precision_digits=2) == -1:
                # today = date.today()
                date1 = rec.start_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                date1 = datetime.datetime.strptime(date1, DEFAULT_SERVER_DATETIME_FORMAT)
                current_date = datetime.date.today().replace(day=1).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                current_date = datetime.datetime.strptime(current_date, DEFAULT_SERVER_DATETIME_FORMAT)
                month_diff = relativedelta(date1, current_date).months
                if month_diff:
                    projected_leave = month_diff * 1.25
                    if rec.total_days > leave_days['virtual_remaining_leaves'] + projected_leave:
                        raise UserError(_(
                            "pv Event doesn't have enough Projection Vacation leaves. Please review the process before continue."))
                    leave_allocation_id = self.env['hr.leave.allocation'].create({
                        'name': rec.name,
                        'holiday_status_id': rec.event_id.leave_type_id.id,
                        'holiday_type': 'employee',
                        'employee_id': rec.employee_id.id,
                        'number_of_days': rec.total_days - leave_days['virtual_remaining_leaves'],
                    })
                    leave_allocation_id.action_approve()
                    return leave_allocation_id
            return True

    def action_process(self):
        if not self.env.user.has_group('hr_payroll_variations.group_pv_process'):
            raise ValidationError(_("You are not allowed for this process!"))
        if not self.event_id.is_apply_date_finish:
            self.state = 'processed'
        else:
            payslip = self.env['hr.payslip'].search_count([
                ('state', 'in', ['done', 'paid']),
                ('employee_id', '=', self.employee_id.id),
                ('date_from', '<=', self.end_date),
                ('date_to', '>=', self.end_date)])
            if self.end_date:
                if fields.Date.today().month >= self.end_date.month and \
                        fields.Date.today().year >= self.end_date.year:
                    self.state = 'processed'

    def action_set_to_approve(self):
        self.state = 'approved'

    def action_reject(self):
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hr.pv.reject.wizard',
            'target': 'new',
        }

    @api.model
    def add_follower_id(self, res_id, model, partner_id):
        follower_obj = self.env['mail.followers']
        subtype = self.env['mail.message.subtype'].search([
            ('name', '=', 'Discussions')], limit=1)
        exist_partner = follower_obj.search(
            [('res_id', '=', res_id),
             ('res_model', '=', model),
             ('partner_id', '=', partner_id)])
        if not exist_partner:
            follower_id = False
            reg = {
                'res_id': res_id,
                'res_model': model,
                'partner_id': partner_id
            }
            if subtype:
                reg.update({'subtype_ids': [(6, 0, [subtype.id])]})
            follower_id = self.env['mail.followers'].create(reg)
            return follower_id
        else:
            return False

    @api.model
    def create(self, vals):
        if vals.get('event_id', ''):
            event = self.env['hr.pv.event'].browse(
                vals.get('event_id', ''))
            vals['type_id'] = event.type_id.id
            vals['subtype_id'] = event.subtype_id.id
            if vals.get('employee_id') and vals.get('event_id') and \
                    vals.get('start_date') and vals.get('amount') and not \
                    event.is_automatically_remove and not vals.get('dis_aid_id'):
                equal_pv = self.search(
                    [('employee_id', '=', vals.get('employee_id')),
                     ('event_id', '=', vals.get('event_id')),
                     ('start_date', '=', vals.get('start_date')),
                     ('amount', '=', vals.get('amount')),
                     ('state', 'not in', ('processed', 'cancel', 'rejected')),
                     
                     ], limit=1)
                if equal_pv:
                    raise ValidationError(
                        _('You have another PV with the sequence %s with the same data' % (equal_pv.name)))
            if event.holiday_event_id:
                vacation_pv = self.search(
                    [('employee_id', '=', vals.get('employee_id')),
                     ('event_id', '=', event.holiday_event_id.id),
                     ('start_date', '<=', vals.get('start_date')),
                     ('end_date', '>=', vals.get('start_date')),
                     ('state', 'in', ('processed', 'approved'))], limit=1)
                if vacation_pv and (vacation_pv.total_days / 2) < vals.get('total_days'):
                    raise UserError(_(
                        "The total_days must not be greater than the holidays taken on business days in the PV %s" % (
                            vacation_pv.name)))
                elif not vacation_pv:
                    raise UserError(_("The employee don't have created the PV with event %s between these dates" % (
                        event.holiday_event_id.name)))
                elif vals.get('total_days') > self.env['hr.employee'].browse(
                        vals.get('employee_id')).remaining_leaves_count:
                    raise UserError(_("The employee don't have days availabel for this request"))

        res = super(Hrpv, self).create(vals)  # Save the form
        if vals.get('is_eps') and vals.get('is_eps') == True:
            employee = self.env['hr.employee'].browse(
                vals.get('employee_id', ''))
            if employee and employee.eps_id and employee.eps_id.required_physical_evidence and not vals.get('support'):
                raise ValidationError(_('You have to delivery leave phisical evidence'))

        if vals.get('state'):
            if vals.get('state') == 'approved':
                raise ValidationError(_(
                    'The variation no can create in state approved.'))
        if vals.get('event_id', ''):
            event = self.env['hr.pv.event'].browse(
                vals.get('event_id', ''))
            seguidores_partner = []
            if event.followers_group_ids:
                for seguidores in event.followers_group_ids:
                    seguidores_partner.extend(
                        x for x in seguidores.users.mapped(
                            'partner_id').ids if x not in seguidores_partner)
            if seguidores_partner:
                for follower in seguidores_partner:
                    self.add_follower_id(res.id, 'hr.pv', follower)
        # Message posting is optional. Add_follower_id will
        # still make the partner follow the record
        res.message_post(
            body=_("A new pv has been Created"),
            subtype_xmlid='mail.mt_comment',
            message_type='email',
            partner_ids=res.message_follower_ids.mapped('partner_id.id'))
        users = res.event_id.group_ids.mapped('users').ids
        if self.env.context.get('uid') and self.env.user.id not in users:
            raise ValidationError(_(
                'This user has no access right to create pv.'))
        # res.name = self.env['ir.sequence'].next_by_code("hr.pv")
        if res.company_id:
            res.name = self.env['ir.sequence'].with_context(force_company=res.company_id.id).next_by_code('hr.pv') or _(
                'New')
        else:
            res.name = self.env['ir.sequence'].next_by_code('hr.pv') or _('New')
        res.extension = True
        # try:
        #     ip_addr = request.httprequest.environ.get(
        #         'HTTP_X_FORWARDED_FOR', '').rsplit(',', 1)[0]
        #     if ip_addr:
        #         res.ip_from = ip_addr
        #         response = DbIpCity.get(ip_addr, api_key='free')
        #         res.location = 'Latitude:-' + str(
        #             response.latitude) + ' Longitude:-' + str(
        #             response.longitude)
        #         country = response.country
        #         country_tz = pytz.country_timezones(country)
        #         if country_tz:
        #             local = country_tz[0]
        #             naive = datetime.datetime.strptime(
        #                 fields.Datetime.to_string(
        #                     fields.Datetime.now()),
        #                 DEFAULT_SERVER_DATETIME_FORMAT)
        #             local_time = naive.astimezone(pytz.timezone(local))
        #             utc_time = local_time.astimezone(pytz.utc)
        #             res.date = utc_time.strftime(
        #                 DEFAULT_SERVER_DATETIME_FORMAT)
        # except:
        #     pass

        if res.event_id.is_contract_completion:
            contract = self.env['hr.contract'].search(
                [('employee_id', '=', res.employee_id.id), ('active', '=', True), ('state', '=', 'open')])
            if contract:
                if contract.date_end:
                    if not contract.date_end == res.start_date.date():
                        raise exceptions.ValidationError(
                            _('The contract termination date is not the same as the current contract date.'))

            pv_ids = self.search(
                [('employee_id', '=', res.employee_id.id),
                 ('start_date', '<=', res.start_date),
                 ('end_date', '>=', res.start_date),
                 ('state', '=', 'approved'),
                 ('subtype_id', '=', self.env.ref(
                     'hr_payroll_variations.pv_subtype_AUS').id)])
            if pv_ids:
                raise exceptions.ValidationError(_(
                    "You cannot generate process contract termination why the employee have a leave registered with sequence " + str(
                        pv_ids[0].name)))

        return res

    def write(self, vals):
        users = self.event_id.group_ids.mapped('users').ids
        if self.env.context.get('uid') and self.env.user.id not in \
                users and not self._context.get('support_data'):
            raise ValidationError(_(
                'This user has no access right to write pv.'))
        if self.state and vals.get('state', ''):
            self.message_post(
                body=_(self.state + " -> " + vals.get('state', '')),
                subtype_xmlid='mail.mt_comment',
                message_type='email',
                partner_ids=self.message_follower_ids.mapped('partner_id.id'))
        return super(Hrpv, self).write(vals)

    @api.depends('event_id')
    def compute_is_user_appr(self):
        for rec in self:
            rec.is_user_appr = rec.check_approver()
            if rec.type_id.id == self.env.ref('hr_payroll_variations.pv_type_ECO').id:
                rec.vals_visible = True
            else:
                rec.vals_visible = False

    def check_approver(self):
        for rec in self:
            if rec.event_id.approver:
                if rec.event_id.approver == 'daf' and self.env.user.has_group(
                        'hr_payroll_variations.group_daf'):
                    return True
                elif rec.event_id.approver == 'bp' and self.env.user.has_group(
                        'hr_payroll_variations.group_bp'):
                    return True
                elif rec.event_id.approver == 'sst' and \
                        self.env.user.has_group('hr_payroll_variations.group_sst'):
                    return True
                elif rec.event_id.approver == 'jd' and \
                        rec.employee_id.parent_id in \
                        self.env.user.employee_ids:
                    return True
            if rec.event_id.is_optional_approver and \
                    rec.event_id.optional_approver_group_id:
                event_group = self.event_id.optional_approver_group_id
                if event_group.id in self.env.user.groups_id.ids:
                    return True
            if rec.event_id.is_optional_approver_2 and \
                    rec.event_id.optional_approver2_group_id:
                event_group = self.event_id.optional_approver2_group_id
                if event_group.id in self.env.user.groups_id.ids:
                    return True
            else:
                return False

    @api.depends('event_id')
    def compute_is_sec_appr_user(self):
        for record in self:
            event_group = record.event_id.second_approver_group_id
            if event_group.id in record.env.user.groups_id.ids:
                record.is_sec_appr_user = True
            else:
                record.is_sec_appr_user = False

    def pv_create_subcontract(self):
        if self.contract_id and self.amount:
            contract_id = self.contract_id
            percentage = float((((
                                     contract_id.wage) + self.amount) * 100) / contract_id.wage)
            new_subcontract_id = contract_id.copy()
            new_subcontract_id.with_context(from_pv=True).write({
                'subcontract': True, 'father_contract_id': contract_id.id,
                'wage': contract_id.wage + self.amount,
                'fix_wage_amount': self.amount + contract_id.fix_wage_amount})
            new_subcontract_id.onchange_fix_wage_amount()
            self.subcontract_id = new_subcontract_id.id

    # @api.onchange('real_start_date', 'start_date')
    # def _onchange(self):
    #    if self.real_start_date and self.start_date and self.real_start_date != self.start_date:
    #        self.is_extension = True
    #    else:
    #        self.is_extension = False

    '''
    @api.onchange('start_date', 'end_date')
    def _compute_real_date(self):
        for pv in self:
            if not pv.extension and pv.start_date:
                pv.real_start_date = pv.start_date
            if pv.end_date:
                pv.real_end_date = pv.end_date
    '''

    @api.depends('real_end_date', 'real_start_date')
    def _onchange_count_days_extension(self):
        for rec in self:
            if rec.employee_id:
                if rec.real_start_date and rec.real_end_date:
                    days_exten = rec.event_id.get_total_days_calendar(
                        rec.real_start_date, rec.real_end_date, rec.employee_id)
                    rec.count_days_extension = days_exten
                if rec.count_days_extension and rec.count_days_extension >= 180:
                    raise ValidationError(_(
                        "You cannot enter a disability of more than 180 days or exceed the days with extensions, please select another event"))

            else:
                raise ValidationError(
                    _("Please select the employee first"))

    @api.onchange('employee_id', 'event_id')
    def _onchange_employee_contract_active(self):
        if self.event_id or self.employee_id:
            for rec in self:
                if rec.event_id and not self.event_id.exclude_restriction_leave and rec.employee_id:
                    if rec.event_id.subtype_id.name == 'Ausencia':
                        if not rec.employee_id.contract_id.state == 'open':
                            raise ValidationError(_("Employee with non-active contract"))
                        if not rec.employee_id.contract_id.create_absence:
                            raise ValidationError(_("Cannot load news of absence type by restriction in the contract."))

    def send_to_employee_action(self):
        """Send to Employee."""
        for rec in self:
            if rec.support and rec.state not in ['approved', 'processed'] and rec.send_to_employee:
                attachment = self.env['ir.attachment'].create(
                    {'name': rec.file_name,
                     'type': 'binary',
                     'datas': rec.support,
                     'res_model': 'hr.employee',
                     'res_id': rec.employee_id.id, })
                rec.employee_id.message_post(attachment_ids=[attachment.id])


class HrpvEvent(models.Model):
    _name = 'hr.pv.event'
    _description = 'HR PV Event'
    _inherit = [
        'mail.thread',
    ]

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(tracking=True)
    type_id = fields.Many2one('hr.pv.type', string="Type",
                              tracking=True)
    subtype_id = fields.Many2one('hr.pv.type.subtype', string="Sub-Type",
                                 tracking=True)
    leave_type_id = fields.Many2one('hr.leave.type', string="Leave Type",
                                    help="Only if event is a leave",
                                    tracking=True)
    responsible_required = fields.Boolean(tracking=True)
    approver = fields.Selection([('daf', 'Financial and administrative Director'),
                                 ('bp', 'Business partner'),
                                 ('sst', 'Admin healt in work'),
                                 ('jd', 'Boss'),
                                 ], tracking=True)
    second_approver_required = fields.Boolean(tracking=True)
    second_approver_group_id = fields.Many2one('res.groups',
                                               tracking=True)
    is_optional_approver = fields.Boolean(
        'Optional Approver', tracking=True)
    optional_approver_group_id = fields.Many2one(
        'res.groups',
        tracking=True)
    is_optional_approver_2 = fields.Boolean(
        'Optional Approver 2', tracking=True)
    optional_approver2_group_id = fields.Many2one(
        'res.groups',
        tracking=True)
    affectation = fields.Selection(
        [('allowance', 'Allowance'), ('deduction', 'Deduction')],
        tracking=True)
    allow_collision = fields.Boolean('Allow Collision')
    restriction_day = fields.Date(
        tracking=True,
        help='Limit day of the month to create a "novedad" of this type')
    min_days = fields.Float(
        tracking=True,
        help='Minimun limit for the days in the "Novedad"')
    max_days = fields.Float(
        tracking=True,
        help='Maximun limit for the days in the "Novedad"')
    calendar_type = fields.Selection(
        [('employee', 'Employee'), ('full', 'Full Calendar')],
        help="This is the way the total days are calculated:"
             "Based on Employee's Calendar or Full Calendar",
        tracking=True)
    company_only = fields.Boolean(tracking=True)
    group_ids = fields.Many2many('res.groups')
    followers_group_ids = fields.Many2many(
        'res.groups', 'res_groups_grupo_de_seguidores_default_rel',
        'res_groups_id', 'grupo_de_seguidores_id', string='Group Followers'
    )
    new_recruitment = fields.Boolean(tracking=True)
    is_recruitment = fields.Boolean(
        'Recruitment', tracking=True)
    is_apply_date_finish = fields.Boolean('Apply date Finish')
    active = fields.Boolean(string='Active', default=True)
    is_attach_available = fields.Boolean('Availabe attach')
    is_required_attach = fields.Boolean('Attahment required')
    is_contract_completion = fields.Boolean("Is Contract Completion")
    is_h_e_procedure = fields.Boolean("H.E Procedimiento")
    is_hour_fix = fields.Boolean("Fix Hours")
    is_type_leave = fields.Boolean("Type Leave")
    is_eps = fields.Boolean(string='EPS', tracking=True)
    is_arl = fields.Boolean(string='ARL', tracking=True)
    use_extension = fields.Boolean("Use Extension")
    is_type_assignment = fields.Boolean('Assignment')
    unjustified = fields.Boolean("Unjustified")
    requered_account = fields.Boolean('Requered Account')
    increase_salary = fields.Boolean()
    requered_attach_lic = fields.Boolean()
    prepaid_medicine_id = fields.Many2one(
        'res.partner', 'Prepaid Medicine',
        tracking=True
    )
    limit_advance = fields.Float("Limit Advance")
    advance_holidays = fields.Boolean("Advance Holidays")
    projection_vacation = fields.Boolean("Projection Vacation")
    is_end_business_day = fields.Boolean("Available Business Day")
    description = fields.Text(tracking=True)
    is_optional_calendar = fields.Boolean("Is optional calendar")
    only_work_hours = fields.Boolean("Only work hours")
    only_work_days = fields.Boolean("Only work Days")
    company_id = fields.Many2one('res.company', string='Company', copy=False)
    amount_absence = fields.Boolean('Amount Absence')
    convention_aid_event_id = fields.Many2one('hr.pv.event', string='Convention Aid Event')
    holiday_event_id = fields.Many2one('hr.pv.event', string='Holiday related')
    diagnosis_is_required = fields.Boolean("Diagnosis is required")
    is_fuero_salud = fields.Boolean(
        'Fuero de Salud', tracking=True)
    is_bonus = fields.Boolean(
        'Bonus', tracking=True)
    is_payment_type = fields.Boolean(
        'Type Payment', tracking=True)
    exclude_restriction_leave = fields.Boolean(
        'Exclude Restriction Leave', tracking=True)
    report_employee_tag = fields.Boolean(tracking=True)
    category_id = fields.Many2one('hr.employee.category', 'Category')
    is_upc_add = fields.Boolean('UPC Add', tracking=True)
    calculate_amount = fields.Boolean('Calculate Amount')
    distribution_by_days = fields.Boolean('Distribution by Days')

    """Field Automatically Remove PV"""
    is_automatically_remove = fields.Boolean('Automatically Remove PV')

    """Discount Sunday"""
    discount_sunday = fields.Boolean('Discount Sunday', default=False)
    event_id = fields.Many2one('hr.pv.event', 'Event')

    """Date Real"""
    manage_date_real = fields.Boolean('Real Date')
    send_to_employee = fields.Boolean(copy=False)

    """ Contribution process """
    contribution_deduction = fields.Boolean("Contribution Deduction")

    @api.onchange('is_arl')
    def clear_fields_arl(self):
        if self.is_arl == True:
            self.is_eps = False
            self.is_type_leave = True

    @api.onchange('is_eps')
    def clear_fields_eps(self):
        if self.is_eps == True:
            self.is_arl = False
            self.is_type_leave = True

    def get_total_days(self, start_date, end_date, employee, calendar_id=False):
        if self.is_optional_calendar and calendar_id:
            calendar = calendar_id  # Employee's default calendar
        elif self.calendar_type == 'employee':
            calendar = None  # Employee's default calendar
        else:
            calendar = self.env['resource.calendar'].search(
                [('full_calendar', '=', True)],
                limit=1)
            if not calendar:
                calendar = self.env.ref('hr_payroll_variations.resource_calendar_std_full')
        return employee._get_work_days_data(
            start_date, end_date, calendar=calendar)['days']

    def get_total_days_calendar(self, start_date, end_date, employee):
        calendar = self.env['resource.calendar'].search(
            [('full_calendar', '=', True)],
            limit=1)
        if not calendar:
            calendar = self.env.ref('hr_payroll_variations.resource_calendar_std_full')
        if calendar:
            return employee._get_work_days_data(
                start_date, end_date, calendar=calendar)['days']
        return 0

    @api.onchange('type_id')
    def onchange_type(self):
        self.subtype_id = ''

    @api.onchange('subtype_id')
    def onchange_subtype(self):
        self.leave_type_id = ''
        self.responsible_required = ''


class HrpvType(models.Model):
    _name = 'hr.pv.type'
    _description = 'HR Payroll Variations Type'
    _inherit = [
        'mail.thread',
    ]

    name = fields.Char(required=True, tracking=True)
    description = fields.Text(tracking=True)
    company_id = fields.Many2one('res.company', string='Company', copy=False)


class HrpvSubType(models.Model):
    _name = 'hr.pv.type.subtype'
    _description = 'HR Payroll Variations Subtype'
    _inherit = [
        'mail.thread',
    ]

    name = fields.Char(required=True, tracking=True)
    description = fields.Text(tracking=True)
    type_id = fields.Many2one('hr.pv.type', string="Type",
                              tracking=True)
    company_id = fields.Many2one('res.company', string='Company', copy=False)


class StageFollowers(models.Model):
    _name = 'hr.pv.stage_followers'
    _description = 'HR Payroll Variations Stage Followers'

    def stages(self):
        return self.env['hr.pv']._fields['state'].selection

    partner_id = fields.Many2one('res.partner', required=True, string='User')
    stage = fields.Selection(selection=stages, default='draft', string='Stage')

    def name_get(self):
        result = []
        name = '%s in %s' % (self.partner_id.name, self.stage)
        result.append((self.id, name))
        return result


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    full_calendar = fields.Boolean()

    @api.model
    def create(self, vals):
        resource_calendar = super(ResourceCalendar, self).create(vals)
        if resource_calendar.full_time_required_hours != resource_calendar.hours_per_week:
            raise exceptions.ValidationError(_('Total hours per week is different from full time'))

        return resource_calendar

    def write(self, vals):
        resource = super(ResourceCalendar, self).write(vals)
        if self.full_time_required_hours != self.hours_per_week:
            raise exceptions.ValidationError(_('Total hours per week is different from full time'))
        return resource
