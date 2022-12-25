from odoo import api, fields, models
from datetime import date


class LaborRelation(models.Model):
    _name = 'hr.labor.relation'
    _description = 'Labor Relation'
    _inherit = [
        'mail.thread', 'mail.activity.mixin']
    _rec_name = 'request_number'

    name = fields.Char()

    """Header"""
    state = fields.Selection(
        string='State',
        selection=[('new', 'New'),
                   ('validation', 'Validation'),
                   ('citation', 'Citation'),
                   ('download', 'Downloads'),
                   ('sanction', 'Sanction'),
                   ('closed', 'Closed'),
                   ('rejected', 'Rejected')],
        required=False, default='new')

    request_number = fields.Char('Request number', default='New', copy=False)

    # todo falta por sub_etapa pendiente por el cliente

    """General data"""
    create_date = fields.Date('Create date')
    company_id = fields.Many2one('res.company')
    request_type = fields.Many2one('request.type', string='Request type')
    city_id = fields.Many2one('res.city', string='City')

    """Data of the immediate boss and/or who reports"""
    report_employee_id = fields.Many2one('hr.employee', string='Employee')
    charge = fields.Char('Charge')
    identification_number = fields.Char('No. identification')
    email = fields.Char('Email')

    """Worker's data"""
    employee_id = fields.Many2one('hr.employee', string='Employee name')
    employee_charge = fields.Char('Employee charge')
    programming_discharges = fields.Char('Shift assigned for programming of discharges')
    employee_identification_number = fields.Char('No. identification employee')
    headquarters = fields.Char('Headquarters')

    """Disciplinary Process Evaluation"""
    filename_process_evaluation = fields.Char()
    process_evaluation = fields.Binary(string="Disciplinary process evaluation")

    # Pages
    """Fault description"""
    description = fields.Char('Description')
    start_date_fault = fields.Date('Start date of the disciplinary offence')
    end_date_fault = fields.Date('End date of the disciplinary offence')
    fault_type = fields.Many2one('hr.disciplinary.offences', string='Fault type')
    rule_violating_worker = fields.Char('Rule violating worker')
    chapter = fields.Char('Chapter')
    article = fields.Text('Article')
    numeral = fields.Text('Numeral')
    observation = fields.Text('Observations')
    sanction_expected = fields.Selection(
        string='Sanction expected by the Company',
        selection=[('two_days', 'Penalty 2 days'),
                   ('three_days', 'Penalty 3 days'),
                   ('four_days', 'Penalty 4 days'),
                   ('five_days', 'Penalty 5 days'),
                   ('six_days', 'Penalty 6 days'),
                   ('seven_days', 'Penalty 7 days'),
                   ('eight_days', 'Penalty 8 days'),
                   ('termination_contract', 'Termination of contract')],
        required=False, )
    disciplinary_process = fields.Selection(
        string='Disciplinary Process Tests',
        selection=[('report', 'Report'),
                   ('mail', 'Mail'),
                   ('dials', 'Dials'),
                   ('direct_witnesses', 'Direct witnesses'),
                   ('commentary', 'Commentary'),
                   ('at3_report', 'AT 3 Report'),
                   ('productivity_day', 'Productivity 1 day'),
                   ('customer_complaint', 'Customer complaint'),
                   ('not_provide', 'Does not provide'),
                   ('videos', 'Videos'),
                   ('photos', 'Photos'),
                   ('free_versions', 'Free versions'),
                   ('others', 'Others')],
        required=False, )
    which_process = fields.Char('Which ?')
    filename_support = fields.Char()
    support = fields.Binary(string="Supports")

    """Proceedings"""
    date_and_time_minutes = fields.Datetime('Date and time of the minutes')
    employee_taking_minutes = fields.Many2one('hr.employee', string='Employee taking the minutes')
    date_time_signature_of_minutes = fields.Datetime('Date and time of signature of minutes')

    answers_and_questions_ids = fields.One2many('hr.answers.questions', 'answers_and_questions_related_id',
                                                string='Answers ans questions')
    question_1 = fields.Text('Question 1')
    question_2 = fields.Text('Question 2')
    question_3 = fields.Text('Question 3')
    question_4 = fields.Text('Question 4')
    answer_1 = fields.Text('Answer 1')
    answer_2 = fields.Text('Answer 2')
    answer_3 = fields.Text('Answer 3')
    answer_4 = fields.Text('Answer 4')

    ##Campos pestaña Procesos Disciplinarios
    description_sanction = fields.Text('Description')
    start_date_sanction = fields.Date('Start Date Sanction')
    end_date_sanction = fields.Date('End Date Sanction')
    days_sanction = fields.Integer('Sanction Days', readonly=True)

    """On change Methods"""

    @api.onchange('employee_id')
    def _onchange_headquarters(self):
        for record in self:
            if record.employee_id:
                record.headquarters = record.employee_id.sede_requi

    @api.onchange('start_date_sanction', 'end_date_sanction')
    def _onchange_diference_days_sanctions(self):
        for record in self:
            if record.start_date_sanction and record.end_date_sanction:
                start_date_sanction_datetime = datetime(record.start_date_sanction.year,
                                                        record.start_date_sanction.month,
                                                        record.start_date_sanction.day)
                end_date_sanction_datetime = datetime(record.end_date_sanction.year, record.end_date_sanction.month,
                                                      record.end_date_sanction.day, 23, 59, 59)
                working_calendar = record.employee_id.resource_calendar_id
                days_worked = working_calendar.get_work_duration_data(start_date_sanction_datetime,
                                                                      end_date_sanction_datetime, compute_leaves=True)
                record.days_sanction = days_worked['days']
                # record.hours_sanction = days_worked['hours']

    @api.onchange('report_employee_id')
    def loading_data_report_employee(self):
        self.charge = None
        self.email = None
        self.identification_number = None
        if self.report_employee_id:
            self.charge = self.report_employee_id.job_id.name
            self.identification_number = self.report_employee_id.identification_id
            self.email = self.report_employee_id.private_email

    @api.onchange('employee_id')
    def loading_data_employee(self):
        if self.employee_id:
            self.employee_charge = self.employee_id.job_id.name
            self.employee_identification_number = self.employee_id.identification_id

    @api.onchange('fault_type')
    def loading_data_fault(self):
        if self.fault_type:
            self.description = self.fault_type.description
            self.chapter = self.fault_type.chapter
            self.rule_violating_worker = self.fault_type.norm
            self.article = self.fault_type.article
            self.numeral = self.fault_type.numeral

    @api.model
    def create(self, vals):
        if vals.get('request_number', 'New') == 'New':
            vals['request_number'] = self.env['ir.sequence'].next_by_code(
                'labor.relation.seq') or 'New'

        vals['create_date'] = date.today()
        return super(LaborRelation, self).create(vals)


class RequestType(models.Model):
    _name = 'request.type'
    _description = 'Request type for Labor relation'

    name = fields.Char('Name')


class HrAnswersQuestions(models.Model):
    _name = 'hr.answers.questions'

    name = fields.Char('Name')
    answer = fields.Text('Answers')
    question = fields.Text('Questions')
    answers_and_questions_related_id = fields.Many2one('hr.labor.relation', string='Answers and questions')


class DisciplinaryOffences(models.Model):
    _name = 'hr.disciplinary.offences'
    _description = 'Disciplinary Offences'
    _inherit = [
        'mail.thread', 'mail.activity.mixin']

    name = fields.Char()

    fault_type = fields.Char('Fault type')
    chapter = fields.Char('Chapter')
    article = fields.Text('Article')
    numeral = fields.Text('Numeral')
    description = fields.Char('Description')
    norm = fields.Char('Norm')

    @api.onchange('fault_type')
    def change_name(self):
        if self.fault_type:
            self.name = self.fault_type


class EmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    organization_unit_id = fields.Many2one('organization.unit', string='Organization Unit')
