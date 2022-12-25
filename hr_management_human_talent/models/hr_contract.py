from odoo import api, fields, models, exceptions, _
import locale, datetime
from datetime import date


class Contract(models.Model):
    _inherit = 'hr.contract'

    job_id = fields.Many2one('hr.job', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                             string='Job Position', tracking=True)

    contract_type_id = fields.Many2one('hr.contract.type', related='', string='Contract Type', tracking=True)
    unidad_organizativa_requi = fields.Many2one('unidades', string='Organization unity', tracking=True)
    center_cost_ids = fields.One2many('hr.center.cost', 'contract_id', string='Center Cost', copy=True)

    minimum_wage = fields.Float(compute='_compute_minimum_wage')
    check_min_wage = fields.Boolean(tracking=True)

    evaluation_date = fields.Date('Evaluation Date', tracking=True)
    evaluation_result = fields.Float('Trial Period Evaluation Result', tracking=True)

    """Extend Fields"""
    check_extend = fields.Boolean(tracking=True)
    number_extend = fields.Integer('No. Extend', tracking=True)
    date_now = fields.Text(compute="set_date_now", tracking=True)

    @api.onchange('center_cost_ids')
    def onchange_center_cost_ids(self):
        if self.center_cost_ids:
            percent = 0
            for line in self.center_cost_ids:
                percent += line.percent
                if percent > 100:
                    raise exceptions.ValidationError(_('The cost center distribution cannot be more than 100 percent'))

    @api.model
    @api.onchange('wage')
    def _compute_minimum_wage(self):

        today = fields.Date.today()

        config = self.env['hr.payroll.config'].search(
            [('start_date', '<=', today), ('end_date', '>=', today), ('state', '=', 'done')])
        min_wage = self.env['hr.payroll.config.lines'].search(
            [('hr_payroll_config_id', '=', config.id), ('variable.name', '=', 'Salario Minimo')])

        for contract in self:
            contract.minimum_wage = min_wage.value
            if contract.minimum_wage == contract.wage:
                contract.check_min_wage = True
            else:
                contract.check_min_wage = False

    def set_date_now(self):
        """
        Método llamado por la declaración del atributo date_now como campo calculado, que almacena la fecha actual con formato colombiano en el campo.
        """
        now = datetime.datetime.now()
        for employee in self:
            employee.date_now = now.strftime('%B %d de %Y').capitalize()

    def set_date(self, date):
        return date.strftime('%d de %B de %Y').capitalize()

    def write(self, vals):
        contract = super(Contract, self).write(vals)
        if vals.get('job_id', False):
            history_labor = {
                'employee_id': self.employee_id.id,
                'position_id': self.job_id.id,
                'salary': self.wage,
                'start_date': self.date_start,
                'end_date': self.date_end,
            }
            self.env['hr.history.promotion'].create(history_labor)
        return contract

    def get_date_contract_principal(self):
        contract_principal = self.father_contract_id
        date_contract = self.date_start

        if contract_principal:
            while contract_principal:
                if not contract_principal.father_contract_id:
                    date_contract = contract_principal.date_start
                contract_principal = contract_principal.father_contract_id

        return date_contract


class OrganizationUnit(models.Model):
    _name = 'unidades'
    _description = 'Organization unit'
    _rec_name = 'nombre_unidad_org'

    nombre_unidad_org = fields.Char('Name')
    company_id = fields.Many2one('res.company')
