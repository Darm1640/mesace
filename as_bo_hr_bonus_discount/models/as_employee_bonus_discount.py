
from odoo import models, fields, api, _
from datetime import datetime
import time

class BonusReason(models.Model):
    _name = 'as.bonus.reason'
    _description = 'Bonus Reason'
    
    name = fields.Char(
        string="Name",
        required=True,
    )
    
class EmployeeBonus(models.Model):
    _name = 'as.employee.bonus'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Employee Bonus'
    _rec_name = 'employee_id'
    _order = 'id desc'
    
    @api.onchange('employee_id')
    def get_department(self):
        for line in self:
            line.department_id = line.employee_id.department_id.id
            line.job_id = line.employee_id.job_id.id
            line.manager_id = line.employee_id.parent_id.id
    
    @api.model
    def get_currency(self):
        return self.env.user.company_id.currency_id
    
    name = fields.Char(
        string="Numero",
        default='NEW',
        readonly=True,
        copy=False
    )
    employee_id = fields.Many2one(
        'hr.employee', 
        'Empleado', 
        required=True,
    )
    as_generator = fields.Many2one(
        'as.generate.bonus.discount', 
        'Generador',
    )
    date = fields.Date(
        'Fecha',
        default=fields.date.today(),
        required=True,
    )
#     payroll_date = fields.Date(
#         'Payroll Date',
#     )
    job_id = fields.Many2one(
        'hr.job', 
        string='Puesto de trabajo',
    )
    reason_id = fields.Many2one(
        'as.bonus.reason', 
        string='Motivo de bonificación',
        required=True
    )
    manager_id = fields.Many2one(
        'hr.employee', 
        string='Gerente',
    )
    department_id = fields.Many2one(
        'hr.department', 
        string='Departmento',
    )
    bonus_amount = fields.Float(
        string='Importe de la bonificación',
        required=True,
    )
#     inculde_in_payroll = fields.Boolean(
#         string='Include In Payroll',
#         default=True,
#         track_visibility='onchange',
#     )
    currency_id = fields.Many2one(
        'res.currency',
        default=get_currency,
        string='Moneda',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Compañia',
        default=lambda self: self.env.user.company_id, 
        readonly=True
    )
    state = fields.Selection([
        ('adraft', 'Borrador'),
        ('bconfirm', 'Confirmado'),
        ('capproved_dept_manager', 'Aprobado por Departamento'),
        ('dapproved_hr_manager', 'Aprobado por RRHH'),
        ('edone', 'Hecho'),
        ('cancel', 'Cancelado'),
        ('reject', 'Rechazado')], 'Status', 
        readonly=True, 
        track_visibility='onchange', 
        default='adraft',
        help="Gives the status of Employee Bonus.", 
    )
    notes = fields.Text(
        'Notas',
    )
    emp_user_id = fields.Many2one(
        related='employee_id.user_id', 
        store=True, 
        string='Usuario empleado', 
        readonly=True
    )
    confirm_uid = fields.Many2one(
        'res.users', 
        'Confirmado por', 
        readonly=True
    )
    confirm_date = fields.Date(
        'Fecha confirmada', 
        readonly=True
    )
    approved_manager_uid = fields.Many2one(
        'res.users', 
        'usuario empleado', 
        readonly=True
    )
    approved_manager_date = fields.Date(
        'Gerente aprobado Fecha', 
        readonly=True
    )
    approved_date = fields.Date(
        'Departamento aprobado Fecha', 
        readonly=True
    )
    approved_by = fields.Many2one(
        'res.users', 
        'Aprobado por Departamento', 
        readonly=True
    )
    as_date_start = fields.Date('Fecha Inicio')
    as_date_end = fields.Date('Fecha Fin')
    as_tipo = fields.Selection([
        ('bonus', 'Abono'),
        ('discount', 'Descuento'),
       ], 'Tipo', 
        default='bonus')
    as_modalidad = fields.Selection([
        ('manual', 'Manual'),
        ('auto', 'Automatico'),
       ], 'Tipo', 
        default='manual')
    as_state_payroll = fields.Selection([
        ('draft', 'PENDIENTE'),
        ('asign', 'ASIGNADO'),
        ('done', 'APLICADO'),
       ], 'Estado en Nomina', 
        default='draft')
    

    def get_confirm(self):
        self.state = 'bconfirm'
        self.confirm_date = time.strftime('%Y-%m-%d')
        self.confirm_uid = self.env.user.id
        if self.name == 'NEW':
            if self.as_tipo == 'bonus':
                self.name = self.env['ir.sequence'].next_by_code('emp.bonus')
            else:
                self.name = self.env['ir.sequence'].next_by_code('emp.discount')
    
    def get_apprv_dept_manager(self):
        self.state = 'capproved_dept_manager'
        self.approved_date = time.strftime('%Y-%m-%d')
        self.approved_by = self.env.user.id
       
    def get_apprv_hr_manager(self):
        self.state = 'dapproved_hr_manager'
        self.approved_manager_date = time.strftime('%Y-%m-%d')
        #self.payroll_date = time.strftime('%Y-%m-%d')
        self.approved_manager_uid = self.env.user.id
    
    def get_done(self):
        self.state = 'edone'
    
    def get_reset(self):
        self.state = 'adraft'
    
    def get_cancel(self):
        self.state = 'cancel'
        
    def get_reject(self):
        self.state = 'reject'