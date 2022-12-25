from odoo import api, fields, models, _, exceptions
from dateutil.relativedelta import relativedelta
from datetime import date

TYPE_ORDER = [('employee', 'Employee'),
              ('salary', 'Salary'), ('fixed', 'Fixed')]
STATE = [('draft', 'Draft'), ('approved', 'Approved'), ('canceled', 'Canceled')]


class HrAssignmentEmployee(models.Model):
    _name = 'hr.assignment.employee'
    _description = 'Hr Assignment Employee'
    _inherit = [
        'mail.thread', 'mail.activity.mixin'
    ]

    def _default_name(self):
        name = _('New')
        return name

    state = fields.Selection(STATE, string='State', default='draft', copy=False, tracking=True)

    name = fields.Char(default=_default_name)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company,
                                 tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id,
                                  tracking=True)
    sequence_id = fields.Many2one('ir.sequence', 'Sequence', tracking=True)

    employee_id = fields.Many2one('hr.employee', tracking=True)
    contract_id = fields.Many2one('hr.contract', 'Contract', tracking=True)
    structure_type_id = fields.Many2one('hr.payroll.structure.type', 'Structure Type', tracking=True)
    default_schedule_pay = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi-annually', 'Semi-annually'),
        ('annually', 'Annually'),
        ('weekly', 'Weekly'),
        ('bi-weekly', 'Bi-weekly'),
        ('bi-monthly', 'Bi-monthly'),
    ], string='Default Scheduled Pay', related='structure_type_id.default_schedule_pay')

    identification_id = fields.Char('Identification No', tracking=True)
    current_wage_employee = fields.Monetary('Current Wage Employee', tracking=True)

    employee_to_replace_id = fields.Many2one('hr.employee', 'Employee To Replace', tracking=True)

    date_start = fields.Date('Date Start', tracking=True)
    date_end = fields.Date('Date End', tracking=True)
    total_days = fields.Integer('Total Days', tracking=True)

    salary_value = fields.Monetary('Salary value', tracking=True)
    wage_employee_to_replace = fields.Monetary('Wage Employee To Replace', tracking=True)
    wage_difference = fields.Monetary('Wage difference', tracking=True)

    fixed_value = fields.Monetary('Fixed value', tracking=True)
    amount = fields.Monetary('Amount', tracking=True)

    type_assignment = fields.Selection(string='Type Assignment', selection=TYPE_ORDER, tracking=True)

    pv_ids = fields.One2many('hr.pv', 'employee_assignment_id')

    description = fields.Text('Description', tracking=True)

    pv_count = fields.Integer(compute='compute_number_pvs', string='Pvs')

    def get_pvs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pv',
            'view_mode': 'tree,form',
            'res_model': 'hr.pv',
            'domain': [('employee_assignment_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def compute_number_pvs(self):
        for record in self:
            record.pv_count = self.env['hr.pv'].search_count(
                [('employee_assignment_id', '=', self.id)])

    @api.model
    def create(self, vals):

        assigment = super(HrAssignmentEmployee, self).create(vals)

        sequence = assigment.sequence_id

        if sequence.use_date_range:
            assigment.name = sequence.next_by_id(sequence_date=assigment.date_start)
        else:
            assigment.name = sequence.next_by_id()

        return assigment

    @api.onchange('date_start', 'date_end')
    def _calculate_total_days(self):
        if self.date_start and self.date_end:
            if self.date_start <= self.date_end:
                total_days = self.date_end - self.date_start
                self.total_days = abs(total_days.days) + 1
            else:
                raise exceptions.ValidationError(_('The start date must be less than the end date'))

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        self.contract_id = False
        if self.employee_id:
            self.identification_id = self.employee_id.identification_id
            contract = self.env['hr.contract'].search(
                [('employee_id', '=', self.employee_id.id), ('state', '=', 'open')], limit=1)
            if contract:
                self.contract_id = contract.id
                self.current_wage_employee = contract.wage
                self.structure_type_id = contract.structure_type_id.id

    @api.onchange('employee_to_replace_id')
    def _calculate_wage_employee_to_replace(self):
        self.wage_employee_to_replace = None
        if self.employee_to_replace_id:
            contract = self.env['hr.contract'].search(
                [('employee_id', '=', self.employee_to_replace_id.id), ('state', '=', 'open')], limit=1)
            if contract:
                self.wage_employee_to_replace = contract.wage

    @api.onchange('current_wage_employee', 'salary_value', 'wage_employee_to_replace')
    def _calculate_difference_wage(self):
        wage_difference = 0
        if self.type_assignment == 'employee':
            if self.employee_id and self.employee_to_replace_id:
                wage_difference = self.wage_employee_to_replace - self.current_wage_employee

        if self.type_assignment == 'salary':
            if self.employee_id:
                wage_difference = self.salary_value - self.current_wage_employee

        self.wage_difference = abs(wage_difference)

    @api.onchange('wage_difference')
    def _calculate_amount(self):
        if self.wage_difference:
            amount = self.wage_difference / 30
            self.amount = amount
        else:
            self.amount = None

    """Buttons"""

    def approve(self):
        configuration_days = self.env['hr.assignment.configuration'].search(
            [('company_id', '=', self.company_id.id), ('date_from', '<=', date.today()),
             ('date_to', '>=', date.today())])

        total_days_assigment = self.total_days
        vals = {}

        if configuration_days:
            days_consumed = 0
            total_days = 0
            out_range_days = 0
            date_from = self.date_start
            date_to = self.date_end
            remaining_days = total_days_assigment
            flag = True

            for line in configuration_days.configuration_line_ids:

                while flag:

                    if out_range_days:
                        amount = ((self.wage_difference * line.percentage) / 100) / 30
                        pv = self.create_pv(self.id, date_from, (date_to + relativedelta(hours=23)), amount,
                                            configuration_days.event_id)
                        pv.write({
                            'state': 'approved',
                        })

                        out_range_days = 0
                        date_from = date_to + relativedelta(days=1)

                    if self.default_schedule_pay == 'monthly':
                        date_from = date_from
                        date_to = date_from + relativedelta(months=+ 1, day=1, days=-1)

                        if date_to > self.date_end:
                            date_to = self.date_end

                        days = (date_to - date_from)

                        total_days = days.days
                        days_consumed += total_days

                    if self.default_schedule_pay == 'bi-weekly':
                        date_from = date_from if days_consumed <= 0 else date_from.replace(day=1)
                        date_to = date_from + relativedelta(months=+ 1, day=1, days=-1)
                        if days_consumed < 0:
                            if date_from.day <= 15:
                                date_from = date_from.replace(day=1)
                                date_to = date_from.replace(day=15)
                            if date_from.day > 15:
                                date_from = date_from.replace(day=16)
                                date_to = date_from + relativedelta(months=+ 1, day=1, days=-1)

                            days = (date_to - date_from)

                            total_days = days.days
                            days_consumed += total_days

                    if days_consumed > total_days_assigment:
                        days_consumed = total_days_assigment

                    if line.day_to > 0:

                        if line.day_from <= days_consumed <= line.day_to:
                            amount = ((self.wage_difference * line.percentage) / 100) / 30

                            pv = self.create_pv(self.id, date_from, (date_to + relativedelta(hours=23)), amount,
                                                configuration_days.event_id)
                            pv.write({
                                'state': 'approved',
                            })

                            date_from = date_to + relativedelta(days=1)
                            remaining_days = total_days_assigment - days_consumed

                        else:
                            out_range_days = days_consumed - line.day_to
                            amount = ((self.wage_difference * line.percentage) / 100) / 30
                            date_to = date_to - relativedelta(days=out_range_days)

                            pv = self.create_pv(self.id, date_from, (date_to + relativedelta(hours=23)), amount,
                                                configuration_days.event_id)
                            pv.write({
                                'state': 'approved',
                            })

                            remaining_days = total_days_assigment - days_consumed

                            date_from = date_to + relativedelta(days=1)
                            date_to = date_to + relativedelta(days=out_range_days)
                            break

                    else:
                        amount = ((self.wage_difference * line.percentage) / 100) / 30

                        pv = self.create_pv(self.id, date_from, (date_to + relativedelta(hours=23)), amount,
                                            configuration_days.event_id)
                        pv.write({
                            'state': 'approved',
                        })

                        date_from = date_to + relativedelta(days=1)
                        remaining_days = total_days_assigment - days_consumed

                    if date_to >= self.date_end or remaining_days <= 0:
                        flag = False

            self.state = 'approved'

        else:
            raise exceptions.ValidationError(_('No configuration of days and percentages'))

    def create_pv(self, pv_id, start_date, end_date, amount, event_id):
        vals = {
            'employee_assignment_id': pv_id,
            'event_id': event_id.id,
            'employee_id': self.employee_id.id,
            'type_assignment': self.type_assignment,
            'replace_employee_id': self.employee_to_replace_id.id,
            'current_salary': self.wage_employee_to_replace,
            'employee_id_current_salary': self.current_wage_employee,
            'wage_difference': self.wage_difference,
            'salary_value': self.salary_value if self.type_assignment == 'salary' else 0,
            'amount': amount,
            'company_id': self.company_id.id,
            'start_date': start_date + relativedelta(hours=5),
            'end_date': end_date + relativedelta(hours=5),
            'state': 'draft',
        }
        pv = self.env['hr.pv'].create(vals)
        return pv


class AssigmentConfiguration(models.Model):
    _name = 'hr.assignment.configuration'
    _description = 'Hr Configuration Assignment'

    name = fields.Char('Name')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    event_id = fields.Many2one('hr.pv.event', 'Event', help='Event with which the pv of the orders will be created')

    configuration_line_ids = fields.One2many('assignment.lines.configuration', 'configuration_id')
    is_active = fields.Boolean('Active')

    @api.onchange('configuration_line_ids')
    def sequence_days(self):
        count = 0
        day_to = 0
        for line in self.configuration_line_ids:
            if count >= 1:
                if line.day_from != 0:
                    if line.day_from == day_to + 1:
                        pass
                    else:
                        raise exceptions.ValidationError('Los dias deben ser secuenciales')
            count += 1
            day_to = line.day_to


class AssignmentConfigurationLines(models.Model):
    _name = 'assignment.lines.configuration'
    _description = 'Assignment Configuration Lines'

    name = fields.Char()
    configuration_id = fields.Many2one('hr.assignment.configuration')

    day_from = fields.Integer('Day From')
    day_to = fields.Integer('Day To')
    percentage = fields.Float('Percentage (%)')
