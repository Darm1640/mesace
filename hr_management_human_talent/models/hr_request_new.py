from odoo import api, fields, models, _, exceptions
from datetime import date
from datetime import datetime
import datetime
from dateutil.relativedelta import relativedelta

TYPE_DOCUMENT = [('id_card', 'ID Card'),
                 ('cc', 'Citizenship Card'),
                 ('ce', 'Foreigner Identity Card')
                 ]


class RequestForNews(models.Model):
    _name = 'hr.request.for.news'
    _description = 'Request for news in contracts'
    _inherit = [
        'mail.thread', 'mail.activity.mixin']

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    name = fields.Char(store=True)
    state = fields.Selection(string='request status',
                             selection=[('new', 'NEW'), ('in_process', 'IN PROCESS'),
                                        ('finalized', 'FINALIZED')], default='new')

    model = fields.Selection(string='Model',
                             selection=[('employee', 'Employee'), ('contract', 'Contract')])
    employee_id = fields.Many2one('hr.employee', string='No. Identification')
    employee_name = fields.Char(related='employee_id.name', string='Employee')
    related_contract = fields.Char('Contract relation')
    document_number = fields.Char('Document number')
    request_date = fields.Date('Request date')
    filed_date = fields.Date('Filed date')
    status_procedure = fields.Selection(string='Status of procedure',
                                        selection=[('radicated', 'Radicate'), ('accepted', 'Accepted'),
                                                   ('refused_by_entity', 'Refused by the entity')])

    process = fields.Selection(string='Process', selection=[('inclusions', 'Inclusions'), ('transfers', 'Transfers')])
    type_novelty = fields.Many2one('type.novelty', string='Novelty type')
    subsystem = fields.Selection(string='Subsystem',
                                 selection=[('eps', 'EPS'), ('afp', 'AFP'), ('afc', 'AFC'), ('ccf', 'CCF'),
                                            ('arl', 'ARL')])
    start_date = fields.Date('Start date')
    final_date = fields.Date('Final date ')
    approval_date = fields.Date('Approval date')

    creation_date = fields.Date('Creation date')
    current_salary = fields.Float('Current Salary')

    beneficiary_line_ids = fields.One2many(
        comodel_name='beneficiary',
        inverse_name='request_news',
        string='Beneficiary',
        required=False)

    current_salary_type = fields.Selection(string='Current type of salary',
                                           selection=[('basic_salary', 'Basic salary'),
                                                      ('integral_salary', 'Integral salary'),
                                                      ('support_sustainability', 'Support sustainability')])
    salary_type = fields.Selection(string='Type of salary',
                                   selection=[('basic_salary', 'Basic salary'), ('integral_salary', 'Integral salary'),
                                              ('support_sustainability', 'Support sustainability')])
    new_salary = fields.Float('New salary')
    salary_percent = fields.Float('Salary Percent (%)')

    inclusion_entity = fields.Many2one('res.partner', string='Inclusion entity')
    source_entity = fields.Many2one('res.partner', string='Source entity')
    destination_entity = fields.Many2one('res.partner', string='Destination entity')

    """Promotion fields"""
    department = fields.Char('Department')
    position = fields.Char('Position')
    new_position = fields.Many2one('hr.job', string='New position')
    current_contract_type = fields.Many2one('hr.contract.type', 'Current contract type')
    contract_type_id = fields.Many2one('hr.contract.type', string='Contract type')
    duration_year = fields.Integer('Year')
    duration_month = fields.Integer('Month')
    duration_day = fields.Integer('Days')

    """Contract Client Work"""
    current_contract_client_work = fields.Char('Current Contract Client/Work')
    new_contract_client_work = fields.Char('New Contract Client/Work')

    """Cost Center fields"""
    current_center_cost_id = fields.One2many('hr.center.cost', 'request_news_id', string='Current cost center')
    new_center_cost_id = fields.One2many('hr.new.center.cost', 'request_news_id', string='New cost center')
    check_cost_center_distribution = fields.Boolean('Cost center distribution',
                                                    related='type_novelty.is_cost_center_distribution')

    """Organization Unit fields"""
    organization_unit_actual = fields.Char('Current organizational unit')
    new_organization_unit = fields.Many2one('unidades', 'New organizational unit')

    """Extend fields"""
    current_extension_number = fields.Integer('Current extension number')
    new_extension_number = fields.Integer('New extension number')
    date_start_current_contract = fields.Date('Date start current contract')
    date_end_current_contract = fields.Date('Date end current contract')
    date_start_extend = fields.Date('Date start extend')
    date_end_extend = fields.Date('Date end extend')

    """Retroactive Fields"""
    generate_retroactive = fields.Boolean()
    retroactive_event = fields.Many2one(
        'hr.pv.event', string="Event")
    retroactive_initial_date = fields.Date("Retroactive From Date")
    is_generated_retroactive = fields.Boolean()
    pv_id = fields.Many2one('hr.pv', 'Pv')

    """Labor Relation"""
    current_labor_relation_emp = fields.Selection(
        selection=[('01 LEY 50', '01 LEY 50'), ('02 REG ANTERIOR', '02 REG ANTERIOR'), ('03 INTEGRAL', '03 INTEGRAL'),
                   ('04 APRENDIZAJE', '04 APRENDIZAJE'), ('05 PENSIONADO', '05 PENSIONADO'),
                   ('06 EXTERNO/TEMPOR', '06 EXTERNO/TEMPOR')], string='Current labor relation')
    new_labor_relation_emp = fields.Selection(
        selection=[('01 LEY 50', '01 LEY 50'), ('02 REG ANTERIOR', '02 REG ANTERIOR'), ('03 INTEGRAL', '03 INTEGRAL'),
                   ('04 APRENDIZAJE', '04 APRENDIZAJE'), ('05 PENSIONADO', '05 PENSIONADO'),
                   ('06 EXTERNO/TEMPOR', '06 EXTERNO/TEMPOR')], string='New labor relation')

    """Change City"""
    current_city_id = fields.Many2one('res.city', 'Current City')
    new_city_id = fields.Many2one('res.city', 'New City')

    """Change Cotizante Subtype"""
    current_cotizante_subtype_id = fields.Many2one('subtipo.cotizante', 'Current cotizante subtype')
    new_cotizante_subtype_id = fields.Many2one('subtipo.cotizante', 'New cotizante subtype')

    """Change Stage Apprentice"""
    risk_level = fields.Selection(
        selection=[('1 RIESGO I', '1 RIESGO I'), ('2 RIESGO II', '2 RIESGO II'), ('3 RIESGO III', '3 RIESGO III'),
                   ('4 RIESGO IV', '4 RIESGO IV'), ('5 RIESGO V', '5 RIESGO V')])
    arl_id = fields.Many2one('res.partner', 'Arl', domain=[('is_arl', '=', True)])
    current_apprentice_type = fields.Selection(
        selection=[('ETAPA LECTIVA', 'ETAPA LECTIVA'), ('ETAPA PRODUCTIVA', 'ETAPA PRODUCTIVA'),
                   ('PRACTICANTE', 'PRACTICANTE UNIVERSITARIO')], string='Current Apprentice type')
    new_apprentice_type = fields.Selection(
        selection=[('ETAPA LECTIVA', 'ETAPA LECTIVA'), ('ETAPA PRODUCTIVA', 'ETAPA PRODUCTIVA'),
                   ('PRACTICANTE', 'PRACTICANTE UNIVERSITARIO')], string='New Apprentice type')

    end_date_stage_lective = fields.Date('End date lective stage')
    start_date_productive_stage = fields.Date('Start date productive stage')
    end_date_productive_stage = fields.Date('End date productive stage')

    """Boolean fields"""
    check_cost_center = fields.Boolean('¿Require change of cost center?', related='type_novelty.is_cost_center')
    check_change_organizational_unit = fields.Boolean(related='type_novelty.is_change_organization_unit')
    check_subcontract = fields.Boolean(related='type_novelty.sub_contract_check', store=True)
    check_salary = fields.Boolean(related='type_novelty.is_type_salary', store=True)
    check_promotion = fields.Boolean(related='type_novelty.is_type_promotion', store=True)
    check_contract_term = fields.Boolean(related='contract_type_id.date_end_required')
    check_extend = fields.Boolean(related='type_novelty.is_type_extend')
    check_date_end_type_contract = fields.Boolean(related='contract_type_id.date_end_required', default=True)
    check_extend_number = fields.Boolean()
    check_is_center_cost = fields.Boolean(related='type_novelty.is_cost_center')
    contract_type_end_date = fields.Boolean(related='contract_type_id.date_end_required')
    check_labor_relation = fields.Boolean(related='type_novelty.is_labor_relation')
    check_change_contract = fields.Boolean(related='type_novelty.is_change_contract')
    check_organitazion_unit = fields.Boolean(related='type_novelty.is_change_organization_unit')
    check_cotizante_subtype = fields.Boolean(related='type_novelty.is_change_cotizante_subtype')
    check_city = fields.Boolean(related='type_novelty.is_change_city')
    check_apprentice = fields.Boolean(related='type_novelty.is_change_stage_apprentice')

    observations = fields.Text('Observations')

    @api.onchange('new_apprentice_type')
    def onchange_new_apprentice(self):
        if self.check_apprentice:
            if self.new_apprentice_type == 'ETAPA PRODUCTIVA':
                if self.current_apprentice_type == 'ETAPA LECTIVA':
                    self.start_date_productive_stage = self.end_date_stage_lective + relativedelta(days=1)

                config = self.env['hr.payroll.config'].search(
                    [('state', '=', 'done'), ('start_date', '<=', date.today()), ('end_date', '>=', date.today())])
                if config:
                    for line in config.config_line_ids:
                        if line.name == 'Apoyo Sostenimiento':
                            self.new_salary = line.value
                else:
                    raise exceptions.ValidationError(_('No payroll setup for this year'))

    @api.onchange('end_date_productive_stage')
    def onchange_end_date_productive(self):
        if self.start_date_productive_stage and self.end_date_productive_stage:
            if self.start_date_productive_stage > self.end_date_productive_stage:
                raise exceptions.ValidationError(_('The start date cannot be greater than the end date.'))

    @api.depends('salary_percent')
    @api.onchange('salary_percent')
    def onchange_salary_percent(self):
        if self.salary_percent != 0:
            salary = (self.current_salary * self.salary_percent) / 100
            self.new_salary = self.current_salary + salary

    @api.onchange('contract_type_id')
    def onchange_contract_type_id(self):
        if self.check_change_contract:
            if not self.current_contract_type.date_end_required and self.contract_type_id.date_end_required:
                raise exceptions.ValidationError(_('You cannot go from a permanent contract to a contract permanent'))

    @api.onchange('start_date', 'final_date')
    def _check_duration_change_contract(self):
        if self.start_date and self.final_date:
            if self.check_change_contract and self.contract_type_id.date_end_required:
                duration = self.final_date - self.start_date
                days = abs(duration.days)

                if days > 365:
                    raise exceptions.ValidationError(_('There can be no fixed contracts for more than one year'))

            if self.start_date > self.final_date:
                raise exceptions.ValidationError(_('The start date must be less than the final date.'))

    @api.onchange('new_salary')
    def onchange_new_salary(self):
        if self.check_salary:
            config = self.env['hr.payroll.config'].search(
                [('start_date', '<=', date.today()), ('end_date', '>=', date.today()), ('state', '=', 'done')])

            if config:
                integral_salary = self.env['hr.payroll.config.lines'].search(
                    [('hr_payroll_config_id', '=', config.id), ('variable.name', '=', 'Salario Integral')])

                sustain_support = self.env['hr.payroll.config.lines'].search(
                    [('hr_payroll_config_id', '=', config.id), ('variable.name', '=', 'Apoyo Sostenimiento')])

                if self.salary_type == 'integral_salary':
                    if self.new_salary < integral_salary.value:
                        raise exceptions.ValidationError(_('The new salary cannot be lower than the integral salary.'))

                if self.salary_type == 'support_sustainability':
                    if not self.new_salary == sustain_support.value:
                        raise exceptions.ValidationError(
                            _('The new salary must be equal to the sustainability support.'))
            else:
                raise exceptions.ValidationError(_('There is no payroll configuration for this year'))

            if self.current_salary > self.new_salary:
                raise exceptions.ValidationError(_('The new salary cannot be lower than the current salary.'))

    @api.onchange('current_center_cost_id')
    def onchange_center_cost_ids(self):
        if self.current_center_cost_id:
            percent = 0
            for line in self.current_center_cost_id:
                percent += line.percent
                if percent > 100:
                    raise exceptions.ValidationError(_('The cost center distribution cannot be more than 100 percent'))

    @api.onchange('new_center_cost_id')
    def onchange_new_center_cost_ids(self):
        if self.new_center_cost_id:
            percent = 0
            for line in self.new_center_cost_id:
                percent += line.percent
                if percent > 100:
                    raise exceptions.ValidationError(_('The cost center distribution cannot be more than 100 percent'))

    @api.onchange('new_position')
    def onchange_new_position(self):
        if self.new_position:
            self.new_salary = self.new_position.position_wage

    @api.onchange('destination_entity')
    def onchange_destination_entity(self):
        if self.process == 'transfers' and self.destination_entity:
            return {
                'warning': {
                    'title': 'Warning!',
                    'message': _("Are you sure that " + self.destination_entity.name + " is the destination entity?")}
            }

    @api.onchange('model')
    def clear_fields(self):
        self.process = None
        self.type_novelty = None
        self.salary_type = None
        self.subsystem = None
        self.employee_id = None
        self.related_contract = None
        self.current_salary = None
        self.organization_unit_actual = None

    @api.onchange('check_cost_center')
    def onchange_check_cost_center(self):
        for rec in self:
            if rec.check_cost_center:
                if rec.employee_id:
                    contract = self.env['hr.contract'].search(
                        [('employee_id', '=', rec.employee_id.id), ('active', '=', True), ('state', '=', 'open')])
                    self.current_center_cost_id = contract.center_cost_ids

    @api.depends('employee_id')
    @api.onchange('employee_id')
    def contract_information(self):
        if self.employee_id:
            self.current_labor_relation_emp = self.employee_id.relacion_laboral_emp
            self.current_city_id = self.employee_id.ciudad_requi.id
            self.check_extend_number = False
            self.current_cotizante_subtype_id = self.employee_id.subtipo_cotizante_emp.id if self.employee_id.subtipo_cotizante_emp else False

            if self.model == 'contract':
                contract = self.env['hr.contract'].search(
                    [('employee_id', '=', self.employee_id.id), ('active', '=', True), ('state', '=', 'open')])
                if contract:
                    self.related_contract = contract.name
                    self.current_salary = contract.wage
                    self.department = contract.department_id.name
                    self.position = contract.job_id.name
                    self.organization_unit_actual = contract.unidad_organizativa_requi.nombre_unidad_org
                    self.date_start_current_contract = contract.date_start
                    self.date_end_current_contract = contract.date_end
                    self.current_contract_type = contract.contract_type_id.id
                    self.current_contract_client_work = contract.contract_client_work
                    self.current_apprentice_type = contract.tipo_aprendiz if contract.tipo_aprendiz else False
                    self.end_date_stage_lective = contract.fecha_fin_etapa_lectiva if contract.fecha_fin_etapa_lectiva else False

                    self.current_extension_number = contract.number_extend + 1

                    type_salary = False
                    if contract.tipo_de_salario_contrato == 'sueldo_basico':
                        type_salary = 'basic_salary'

                    if contract.tipo_de_salario_contrato == 'salario_integral':
                        type_salary = 'integral_salary'

                    if contract.tipo_de_salario_contrato == 'apoyo_sostenimiento':
                        type_salary = 'support_sustainability'

                    self.current_salary_type = type_salary

                else:
                    raise exceptions.ValidationError(_('The employee does not have an active contract'))

    @api.onchange('process')
    def clear_entity(self):
        self.source_entity = None
        self.destination_entity = None
        self.subsystem = None

    @api.onchange('subsystem')
    def charge_entity(self):
        """
        Function that loads the entity fields according to the employee and the selected field,
        additional changes dynamically the domain of the destination_entity field according to the selected subsystem
        """

        domain = {'destination_entity': []}
        if self.process == 'transfers':
            if self.subsystem == 'eps':
                if self.employee_id.eps_id:
                    self.source_entity = self.employee_id.eps_id
                    domain = {'destination_entity': [('is_eps', '=', True)]}
                else:
                    self.source_entity = None

            if self.subsystem == 'arl':
                if self.employee_id.arl_id:
                    self.source_entity = self.employee_id.arl_id
                    domain = {'destination_entity': [('is_arl', '=', True)]}
                else:
                    self.source_entity = None

            if self.subsystem == 'afp':
                if self.employee_id.pension_fund_id:
                    self.source_entity = self.employee_id.pension_fund_id
                    domain = {'destination_entity': [('is_afp', '=', True)]}
                else:
                    self.source_entity = None

            if self.subsystem == 'afc':
                if self.employee_id.afc_id:
                    self.source_entity = self.employee_id.afc_id
                    domain = {'destination_entity': [('is_afc', '=', True)]}
                else:
                    self.source_entity = None

            return {'domain': domain}

        else:
            domain = {'destination_entity': []}
            if self.subsystem == 'eps':
                if self.employee_id.eps_id:
                    self.destination_entity = self.employee_id.eps_id
                    domain = {'destination_entity': [('is_eps', '=', True)]}
                else:
                    self.destination_entity = None

            if self.subsystem == 'arl':
                if self.employee_id.arl_id:
                    self.destination_entity = self.employee_id.arl_id
                    domain = {'destination_entity': [('is_arl', '=', True)]}
                else:
                    self.destination_entity = None

            if self.subsystem == 'afp':
                if self.employee_id.pension_fund_id:
                    self.destination_entity = self.employee_id.pension_fund_id
                    domain = {'destination_entity': [('is_afp', '=', True)]}
                else:
                    self.destination_entity = None

            if self.subsystem == 'afc':
                if self.employee_id.afc_id:
                    self.destination_entity = self.employee_id.afc_id
                    domain = {'destination_entity': [('is_afc', '=', True)]}
                else:
                    self.destination_entity = None

            return {'domain': domain}

    @api.onchange('duration_day', 'duration_month', 'duration_year')
    def create_date_final(self):

        if self.model:
            if self.check_contract_term and self.start_date:
                year = self.duration_year
                month = self.duration_month
                day = self.duration_day

                self.final_date = self.start_date + relativedelta(years=year, months=month, days=day)

            if self.check_extend and self.date_start_extend:
                year = self.duration_year
                month = self.duration_month
                day = self.duration_day

                self.date_end_extend = self.date_start_extend + relativedelta(years=year, months=month, days=day)

    @api.onchange('current_extension_number')
    def onchange_current_extension(self):
        if self.current_extension_number == 4:
            self.check_extend_number = True

    @api.onchange('date_start_extend', 'date_end_extend')
    def onchange_date_extend(self):

        self.start_date = self.date_start_extend
        self.final_date = self.date_end_extend

        if self.date_start_extend:
            if self.date_start_extend < self.date_start_current_contract:
                raise exceptions.ValidationError(
                    _('The initial date of the extension cannot be less than the initial date of the contract'))

            if not self.date_end_current_contract and self.date_end_extend:
                raise exceptions.ValidationError(
                    _('No puede pasar de contrato termino indefinido a contrato de termino fijo'))

        if self.date_start_extend and self.date_end_extend:
            date_contract = self.date_end_extend - self.date_start_extend
            duration_current_contract = self.date_end_current_contract - self.date_start_current_contract

            if self.current_extension_number >= 4:
                if date_contract.days < 365:
                    raise exceptions.ValidationError(_('The contract cannot be less than one year'))
            else:
                if date_contract.days - 1 > duration_current_contract.days:
                    raise exceptions.ValidationError(_('Cannot be extended beyond the initial contract'))

            if duration_current_contract.days > 365 and date_contract.days < 365:
                raise exceptions.ValidationError(_(('The contract cannot be less than one year')))

            if date_contract.days > 1095:
                raise exceptions.ValidationError(_('The contract cannot be longer than three years'))

            date_final = relativedelta(self.date_end_extend, self.date_start_extend)

            self.duration_year = date_final.years
            self.duration_month = date_final.months
            self.duration_day = date_final.days

    @api.onchange('current_labor_relation_emp', 'new_labor_relation_emp')
    def onchange_method(self):
        if self.current_labor_relation_emp and self.new_labor_relation_emp:

            if self.current_labor_relation_emp in ['01 LEY 50', '03 INTEGRAL',
                                                   '02 REG ANTERIOR'] and self.new_labor_relation_emp in ['01 LEY 50',
                                                                                                          '03 INTEGRAL',
                                                                                                          '02 REG ANTERIOR']:
                pass
            else:
                raise exceptions.ValidationError(_('It is not a permitted change of labor relation'))

    @api.onchange('final_date')
    def reverse_date_final(self):
        if self.final_date:
            date_final = relativedelta(self.final_date, self.start_date)
            self.duration_year = date_final.years
            self.duration_month = date_final.months
            self.duration_day = date_final.days

    @api.onchange('state')
    @api.depends('state')
    def change_state(self):
        if self.state == 'finalized':
            if self.employee_id and self.filed_date:
                self.employee_id.write({'end_date_eps': self.filed_date})

            if not self.check_extend:

                if self.model == 'contract':

                    contract = self.env['hr.contract'].search(
                        [('employee_id', '=', self.employee_id.id), ('active', '=', True), ('state', '=', 'open')])

                    new_contract = {}

                    if self.check_apprentice:
                        self.employee_id.update({
                            'nivel_riesgo': self.risk_level,
                            'arl_emp': self.arl_id.id,
                        })
                        contract.update({
                            'tipo_aprendiz': self.new_apprentice_type,
                            'fecha_inicio_etapa_productiva': self.start_date_productive_stage,
                            'fecha_fin_etapa_productiva': self.end_date_productive_stage,
                            'wage': self.new_salary
                        })

                    if self.check_cotizante_subtype:
                        self.employee_id.update({
                            'subtipo_cotizante_emp': self.new_cotizante_subtype_id.id
                        })

                    if self.check_city:
                        contract.write({'ciudad_requi': self.new_city_id.id})
                        self.employee_id.write({'ciudad_requi': self.new_city_id.id})

                    if self.type_novelty.is_type_salary:

                        type_salary = False
                        if self.salary_type == 'basic_salary':
                            type_salary = 'sueldo_basico'

                        if self.salary_type == 'integral_salary':
                            type_salary = 'salario_integral'

                        if self.salary_type == 'support_sustainability':
                            type_salary = 'apoyo_sostenimiento'

                        contract.update({
                            'tipo_de_salario_contrato': type_salary,
                            'wage': self.new_salary
                        })

                    if self.check_cost_center:

                        if self.check_cost_center_distribution:
                            contract.center_cost_ids = self.current_center_cost_id
                        else:
                            for rec in contract.center_cost_ids:
                                rec.update({
                                    'contract_id': None,
                                })
                            for line in self.new_center_cost_id:
                                vals = {
                                    'name': line.name,
                                    'employee_id': self.employee_id.id,
                                    'contract_id': contract.id,
                                    'percent': line.percent,
                                    'account_analytic_id': line.account_analytic_id.id,
                                }
                                self.env['hr.center.cost'].create(vals)

                    if self.type_novelty.is_type_promotion:
                        new_contract['wage'] = self.new_salary

                        if self.contract_type_id:
                            new_contract['contract_type_id'] = self.contract_type_id.id

                        if self.new_position:
                            new_contract['job_id'] = self.new_position.id
                            self.employee_id.job_id = self.new_position.id

                        if self.check_change_organizational_unit:
                            new_contract['organization_unit_id'] = self.new_organization_unit.id

                        if self.new_contract_client_work:
                            new_contract['contract_client_work'] = self.new_contract_client_work

                    if self.check_change_organizational_unit:
                        new_contract['unidad_organizativa_requi'] = self.new_organization_unit.id
                        self.employee_id.write({
                            'unidad_organizativa_requi': self.new_organization_unit.id
                        })

                    if self.employee_id and self.generate_retroactive:
                        dif_month = self.start_date.month - self.retroactive_initial_date.month
                        retroactive_amount = self.new_salary - self.current_salary
                        vals = {
                            'employee_id': self.employee_id.id,
                            'event_id': self.retroactive_event.id,
                            'start_date': self.start_date,
                            'end_date': self.start_date,
                            'type_id': self.retroactive_event.type_id.id,
                            'subtype_id': self.retroactive_event.subtype_id.id,
                            'is_generated_retroactive': True,
                            'amount': retroactive_amount * dif_month,
                        }
                        retroactive_id = self.env['hr.pv'].create(vals)
                        self.pv_id = retroactive_id.id
                        retroactive_id.write({
                            'state': 'approved'
                        })

                    if self.check_labor_relation:
                        self.employee_id.update({
                            'relacion_laboral_emp': self.new_labor_relation_emp
                        })

                    contract.update(new_contract)

                    return new_contract

            if self.model == 'employee':

                if self.status_procedure == 'accepted':

                    if self.process == 'transfers':
                        if self.subsystem == 'eps':
                            self.employee_id.update({
                                'eps_id': self.destination_entity.id
                            })

                        if self.subsystem == 'afp':
                            self.employee_id.update({
                                'pension_fund_id': self.destination_entity.id
                            })

                        if self.subsystem == 'arl':
                            self.employee_id.update({
                                'arl_id': self.destination_entity.id
                            })
                        if self.subsystem == 'afc':
                            self.employee_id.update({
                                'afc_id': self.destination_entity.id
                            })

                    if self.process == 'inclusions':
                        for beneficiary in self.beneficiary_line_ids:
                            vals = {
                                'employee_id': self.employee_id.id,
                                'request_news': self.id,
                                'first_name': beneficiary.first_name,
                                'second_name': beneficiary.second_name,
                                'first_surname': beneficiary.first_surname,
                                'second_surname': beneficiary.second_surname,
                                'type_document': beneficiary.type_document,
                                'document': beneficiary.document,
                                'date_birth': beneficiary.date_birth,
                                'age': beneficiary.age,
                                'relationship_id': beneficiary.relationship_id.id,
                                'additional_upc': beneficiary.additional_upc,
                                'destination_entity': beneficiary.destination_entity.id,
                                'subsystem': beneficiary.subsystem,
                            }
                            self.employee_id.beneficiary_line_id.create(vals)

        if self.state == 'in_process':
            if self.check_extend:
                sequence = self.type_novelty.sequence_id
                if sequence:
                    name = sequence.next_by_id(sequence_date=date.today())
                    self.update({
                        'name': name,
                    })

                else:
                    raise exceptions.UserError(_('The type of novelty does not have a sequence'))

    """Buttons"""

    def create_sub_contract(self):
        """Create Subcontract."""

        for rec in self:
            if rec.type_novelty.sub_contract_check:
                contract = rec.env['hr.contract'].search(
                    [('employee_id', '=', rec.employee_id.id), ('active', '=', True), ('state', '=', 'open')])

                if contract:
                    new_subcontract_id = contract.copy()
                    contract.write({
                        'state': 'close', 'subcontract': False, })

                    if rec.check_extend:
                        extend = rec.env['hr.history.extend'].search([('employee_id', '=', rec.employee_id.id)])
                        new_subcontract_id.write({
                            'name': self.name,
                            'subcontract': True,
                            'father_contract_id': contract.id,
                            'date_start': rec.date_start_extend,
                            'date_end': rec.date_end_extend,
                            'number_extend': rec.current_extension_number,
                            'check_extend': True,
                            'contract_type_id': rec.contract_type_id.id,
                            'state': 'draft'})

                        rec.env['hr.history.extend'].create({
                            'employee_id': rec.employee_id.id,
                            'contract_id': new_subcontract_id.id,
                            'start_date': rec.date_start_extend,
                            'end_date': rec.date_end_extend,
                            'number_extend': rec.current_extension_number,
                            'duration_year': rec.duration_year,
                            'duration_month': rec.duration_month,
                            'duration_day': rec.duration_day,
                        })

                    else:
                        new_subcontract_id.write({
                            'subcontract': True,
                            'father_contract_id': contract.id,
                            'date_start': rec.start_date,
                            'wage': rec.new_salary,
                            'contract_type_id': rec.contract_type_id.id,
                            'job_id': rec.new_position.id,
                            'contract_client_work': rec.new_contract_client_work,
                            'date_end': rec.final_date,
                            'state': 'draft'})

                        if rec.new_position:
                            self.employee_id.write({
                                'job_id': rec.new_position.id,
                            })

                    if rec.check_cost_center:

                        if rec.check_cost_center_distribution:
                            new_subcontract_id.center_cost_ids = rec.current_center_cost_id
                        else:
                            for line in rec.new_center_cost_id:
                                vals = {
                                    'name': line.name,
                                    'employee_id': rec.employee_id.id,
                                    'contract_id': new_subcontract_id.id,
                                    'percent': line.percent,
                                    'account_analytic_id': line.account_analytic_id.id,
                                }
                                self.env['hr.center.cost'].create(vals)

                    if not contract.date_end:
                        contract.write({
                            'date_end':
                                new_subcontract_id.date_start + datetime.timedelta(
                                    days=-1)})

                    if contract.date_end and \
                            contract.date_end > fields.Date.today():
                        contract.write({
                            'date_end':
                                new_subcontract_id.date_start + datetime.timedelta(
                                    days=-1)})
                    rec.state = 'finalized'

    def validate_document(self):
        self.state = 'finalized'

    @api.model
    def create(self, vals):
        employee_id = self.env['hr.employee'].search([('id', '=', vals['employee_id'])])
        vals['name'] = employee_id.name
        request_new = super(RequestForNews, self).create(vals)

        if request_new.new_center_cost_id:
            total_percentage = 0
            for line in request_new.new_center_cost_id:
                total_percentage += line.percent

            if total_percentage < 100:
                raise exceptions.ValidationError(_('The cost center distribution must be 100 percent'))

        return request_new

    def write(self, vals):

        request_new = super(RequestForNews, self).write(vals)
        total_percentage = 0
        if self.new_center_cost_id:
            for line in self.new_center_cost_id:
                total_percentage += line.percent

            if total_percentage < 100:
                raise exceptions.ValidationError(_('The cost center distribution must be 100 percent'))

        return request_new


class CenterCost(models.Model):
    _name = 'hr.center.cost'

    _rec_name = "account_analytic_id"
    name = fields.Char('Name')
    contract_id = fields.Many2one('hr.contract')
    employee_id = fields.Many2one('hr.employee')
    percent = fields.Float('Percent')
    account_analytic_id = fields.Many2one('account.analytic.account')
    request_news_id = fields.Many2one('hr.request.for.news')
    direct_indirect = fields.Selection(selection=[('direct', 'Direct'), ('indirect', 'Indirect')],
                                       string='Direct/Indirect', related='account_analytic_id.direct_indirect')

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id:
            contract = self.env['hr.contract'].search(
                [('employee_id', '=', self.employee_id.id), ('active', '=', True), ('state', '=', 'open')])
            if contract:
                self.contract_id = contract.id


class NewCenterCost(models.Model):
    _name = 'hr.new.center.cost'

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    name = fields.Char('Name')
    percent = fields.Float('Percent')
    account_analytic_id = fields.Many2one('account.analytic.account')
    request_news_id = fields.Many2one('hr.request.for.news')
    direct_indirect = fields.Selection(selection=[('direct', 'Direct'), ('indirect', 'Indirect')],
                                       string='Direct/Indirect', related='account_analytic_id.direct_indirect')


class Beneficiary(models.Model):
    _name = 'beneficiary'
    _description = 'beneficiary for employee'
    _rec_name = 'document'

    @api.depends('date_birth')
    def _compute_age(self):
        for rec in self:
            rec.age = 0
            if rec.date_birth:
                rec.age = relativedelta(
                    fields.Date.today(), rec.date_birth).years

    name = fields.Char('Beneficiary name')

    request_news = fields.Many2one('hr.request.for.news')
    employee_id = fields.Many2one('hr.employee')
    first_name = fields.Char('First name')
    second_name = fields.Char('Second name')
    first_surname = fields.Char('First surname')
    second_surname = fields.Char('Second surname')
    type_document = fields.Selection(TYPE_DOCUMENT, string='Type document')
    document = fields.Char('N° document')
    date_birth = fields.Date('Date birth')
    age = fields.Integer(compute='_compute_age', string='Age')
    relationship_id = fields.Many2one('relationship', string='Relationship')

    subsystem = fields.Selection(string='Subsystem',
                                 selection=[('eps', 'EPS'), ('afp', 'AFP'), ('afc', 'AFC'), ('ccf', 'CCF'),
                                            ('arl', 'ARL')])

    destination_entity = fields.Many2one('res.partner', string='Destination entity')

    """Boolean Fields"""
    additional_upc = fields.Boolean('Additional UPC')

    _sql_constraints = [
        ('subsystem_uniq', 'unique(employee_id,document,subsystem,destination_entity)',
         'Cannot have the same beneficiary for the same subsystem!')
    ]

    @api.onchange('date_birth')
    def onchange_date_birth(self):
        if self.date_birth:
            date_today = date.today()
            age = date_today.year - self.date_birth.year
            age -= ((date_today.month, date_today.day) < (self.date_birth.month, self.date_birth.day))
            self.age = age

    @api.onchange('first_name', 'second_name', 'first_surname', 'second_surname', 'type_document', 'document',
                  'relationship_id')
    def default_subsystem(self):
        self.subsystem = self.request_news.subsystem
        self.destination_entity = self.request_news.destination_entity


class Relationship(models.Model):
    _name = 'relationship'
    _description = 'relationship with employee'

    name = fields.Char('Relationship')


class TypeNovelty(models.Model):
    _name = 'type.novelty'
    _description = 'Type novelty for request'

    name = fields.Char()
    sub_contract_check = fields.Boolean('Generate subcontract?')
    is_type_promotion = fields.Boolean('is a promotional type?')
    is_type_salary = fields.Boolean('is a salary type?')
    is_type_extend = fields.Boolean('is a extend?')
    is_cost_center = fields.Boolean('is change in center cost?')
    is_cost_center_distribution = fields.Boolean('is change cost center distribution?')
    is_change_contract = fields.Boolean('is change contract?')
    is_change_organization_unit = fields.Boolean('is change organization unit?')
    is_change_city = fields.Boolean('is change city?')
    is_labor_relation = fields.Boolean('is change labor relation?')
    is_change_cotizante_subtype = fields.Boolean('is change cotizante subtype?')
    is_change_stage_apprentice = fields.Boolean('is change stage apprentice?')

    sequence_id = fields.Many2one(comodel_name='ir.sequence', string='Sequence')
