from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

class hr_novelties_independents(models.Model):
    _name = 'hr.novelties.independents'
    _description = 'Novedades Independientes'

    employee_id = fields.Many2one('hr.employee', string='Empleado', index=True)
    employee_identification = fields.Char('Identificación empleado')
    salary_rule_id = fields.Many2one('hr.salary.rule', string='Regla salarial', required=True)
    dev_or_ded = fields.Selection([('devengo', 'Devengo'),
                                   ('deduccion', 'Deducción')], 'Naturaleza', related='salary_rule_id.dev_or_ded',
                                  store=True, readonly=True)
    date = fields.Date('Fecha', required=True)
    amount = fields.Float('Valor', required=True)
    description = fields.Char('Descripción')

    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.dev_or_ded == 'deduccion' and record.amount > 0:
                raise UserError(_('La regla es de tipo deducción, el valor ingresado debe ser negativo'))
            if record.dev_or_ded == 'devengo' and record.amount < 0:
                raise UserError(_('La regla es de tipo devengo, el valor ingresado debe ser positivo'))

    @api.model
    def create(self, vals):
        if vals.get('employee_identification'):
            obj_employee = self.env['hr.employee'].search(
                [('identification_id', '=', vals.get('employee_identification'))])
            vals['employee_id'] = obj_employee.id
        if vals.get('employee_id'):
            obj_employee = self.env['hr.employee'].search([('id', '=', vals.get('employee_id'))])
            vals['employee_identification'] = obj_employee.identification_id

        res = super(hr_novelties_independents, self).create(vals)
        return res

class Hr_payslip(models.Model):
    _inherit = 'hr.payslip'    
    
    reason_retiro = fields.Text('Motivo retiro')
    have_compensation = fields.Boolean('Indemnización', default=False)
    settle_payroll_concepts = fields.Boolean('Liquida conceptos de nómina', default=True)
    novelties_payroll_concepts = fields.Boolean('Liquida conceptos de novedades', default=True)
class hr_work_entry_type(models.Model):
    _name = 'hr.work.entry.type'
    _inherit = ['hr.work.entry.type','mail.thread', 'mail.activity.mixin']

    code = fields.Char(tracking=True)
    sequence = fields.Integer(tracking=True)
    round_days = fields.Selection(tracking=True)
    round_days_type = fields.Selection(tracking=True)
    is_leave = fields.Boolean(tracking=True)
    is_unforeseen = fields.Boolean(tracking=True)

#Reglas Salariales - Herencia
class hr_salary_rule(models.Model):
    _name = 'hr.salary.rule'
    _inherit = ['hr.salary.rule','mail.thread', 'mail.activity.mixin']

    #Trazabilidad
    struct_id = fields.Many2one(tracking=True)
    active = fields.Boolean(tracking=True)
    sequence = fields.Integer(tracking=True)
    condition_select = fields.Selection(tracking=True)
    amount_select = fields.Selection(tracking=True)
    amount_python_compute = fields.Text(tracking=True)
    appears_on_payslip = fields.Boolean(tracking=True)
    #Campos lavish
    #types_employee = fields.Many2many('hr.types.employee',string='Tipos de Empleado', tracking=True)
    dev_or_ded = fields.Selection([('devengo', 'Devengo'),
                                     ('deduccion', 'Deducción')],'Naturaleza', tracking=True)
    type_concept = fields.Selection([('contrato', 'Fijo Contrato'),
                                     ('ley', 'Por Ley'),
                                     ('novedad', 'Novedad Variable'),
                                     ('prestacion', 'Prestación Social'),
                                     ('tributaria', 'Deducción Tributaria')],'Tipo', required=True, default='contrato', tracking=True)
    aplicar_cobro = fields.Selection([('15','Primera quincena'),
                                        ('30','Segunda quincena'),
                                        ('0','Siempre')],'Aplicar cobro', tracking=True)
    modality_value = fields.Selection([('fijo', 'Valor fijo'),
                                       ('diario', 'Valor diario'),
                                       ('diario_efectivo', 'Valor diario del día efectivamente laborado')],'Modalidad de valor', tracking=True)
    deduction_applies_bonus = fields.Boolean('Aplicar deducción en Prima', tracking=True)
    #Es incapacidad / deducciones
    is_leave = fields.Boolean('Es Ausencia', tracking=True)
    deduct_deductions = fields.Selection([('all', 'Todas las deducciones'),
                                          ('law', 'Solo las deducciones de ley')],'Tener en cuenta al descontar', default='all', tracking=True)    #Vacaciones
    #Base de prestaciones