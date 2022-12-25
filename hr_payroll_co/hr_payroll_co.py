# -*- coding = utf-8 -*-
#/#############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2004-TODAY Tech-Receptives(<http =//www.techreceptives.com>)
#    Special Credit and Thanks to Thymbra Latinoamericana S.A.
#
#    This program is free software = you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http =//www.gnu.org/licenses/>.
#
#/#############################################################################

from odoo import api, fields, models, _

class hr_payslip_run (models.Model):
    _inherit = 'hr.payslip.run'

    liquida =  fields.Boolean('Liquidación', help="Indica si se ejecuta una estructura para liquidacion de contratos y vacaciones")
    struct_id =fields.Many2one('hr.payroll.structure', 'Estructura salarial', help="Defina la estructura salarial que se usará para la liquidacion de contratos y vacaciones") 
    date_prima = fields.Date ('Fecha de liquidación de prima')
    date_cesantias  = fields.Date ('Fecha de liquidación de cesantías')
    date_vacaciones  = fields.Date ('Fecha de liquidación de vacaciones')
    dias_vacaciones = fields.Float('Días tomados de vacaciones', digits=('Payroll'))
    date_intereses  = fields.Date ('Fecha de liquidación de intereses a las cesantías')
    date_liquidacion  = fields.Date ('Fecha de liquidación contrato')


class hr_contract_setting (models.Model):
    _name= 'hr.contract.setting'
    _description = 'Configuracion nomina'


    contrib_id  = fields.Many2one ('hr.contribution.register','Concepto', help="Concepto de aporte")
    partner_id  = fields.Many2one ('res.partner','Entidad', help="Entidad relacionada")
    account_debit_id  = fields.Many2one('account.account', 'Cuenta deudora')
    account_credit_id  = fields.Many2one('account.account', 'Cuenta acreedora')
    contract_id  = fields.Many2one('hr.contract', 'Riesgos', required=True, ondelete='cascade', )      


class hr_employee (models.Model):
    _inherit = 'hr.employee' 
    
    _sql_constraints = [('emp_identification_uniq', 'unique(identification_id)', 'La cedula debe ser unica. La cedula ingresada ya existe')
                       ]

class hr_department_salary_rule (models.Model):
    _name = 'hr.department.salary.rule'
    _description = 'Cuentas contables por departamento'

    department_id  = fields.Many2one('hr.department', 'Departamento', required=True, ondelete='cascade', )
    salary_rule_id  = fields.Many2one('hr.salary.rule', 'Regla salarial', required=True)
    account_debit_id = fields.Many2one('account.account', 'Cuenta deudora')
    account_credit_id  = fields.Many2one('account.account', 'Cuenta acreedora')       

    _sql_constraints = [('department_rule_uniq', 'unique(department_id, salary_rule_id)', 'La regla debe ser unica por departamento. La regla ingresada ya existe'),
                       ]   

class hr_department (models.Model):
    _inherit = 'hr.department'


    account_analytic_id = fields.Many2one('account.analytic.account','Cuenta analítica',required=True)  
    salary_rule_ids = fields.One2many('hr.department.salary.rule', 'department_id', 'Reglas salariales')

class hr_salary_rule (models.Model):
    _inherit = 'hr.salary.rule'

    
    acumula =  fields.Boolean('Acumula', help="Indica si el valor se acumula para liquidación de contratos")
    type_distri  = fields.Selection([('na','No aplica'), ('hora','Horas reportadas'),('dpto','Por contrato'),('novedad','Por novedades')],'Tipo distribución', required=True)
    register_credit_id =fields.Many2one('hr.contribution.register', 'Registro contribución crédito', help="Identificación del movimiento cédito de la regla salarial")  


class hr_salary_rule_category (models.Model):
    _inherit = 'hr.salary.rule.category'

    type  = fields.Selection([('Devengado','Devengado'),('Deducción','Deducción')],'Tipo')


class hr_contract_deduction (models.Model):
    _name= 'hr.contract.deduction'
    _description = 'Deducciones o pagos periodicas'

    
    input_id  =fields.Many2one ('hr.rule.input','Entrada', required=True, help="Entrada o parametro asociada a la regla salarial")
    type  = fields.Selection([('P','Prestamo empresa'),('A','Ahorro'),('S','Seguro'),('L','Libranza'),('E','Embargo'),('R','Retencion'),('O','Otros')],'Tipo deduccion', required=True)
    period  = fields.Selection([('limited','Limitado'),('indefinite','Indefinido')],'Periodo', required=True)
    amount  = fields.Float('Valor', help="Valor de la cuota o porcentaje segun formula de la regla salarial", required=True)
    total_deduction  = fields.Float('Total', help="Total a descontar")
    total_accumulated  = fields.Float('Acumulado', help="Total pagado o acumulado del concepto")
    date  = fields.Date('Fecha', help="Fecha del prestamo u obligacion")
    show_voucher =  fields.Boolean('Mostrar', help="Indica si se muestra o no en el comprobante de nomina")
    contract_id  = fields.Many2one('hr.contract', 'Deduciones', required=True, ondelete='cascade', )
    

class hr_contract_risk (models.Model):
    _name= 'hr.contract.risk'
    _description = 'Riesgos profesionales'
    

    code = fields.Char ('Codigo', size=10, required = True)
    name  = fields.Char ('Nombre', size=100, required = True)
    percent = fields.Float('Porcentaje', required = True, help="porcentaje del riesgo profesional")
    date  = fields.Date ('Fecha vigencia')

    

class hr_payslip_deduction_line (models.Model):
    '''
    Detail of deduction
    '''
    _name = 'hr.payslip.deduction.line'
    _description = 'Detalle de deducciones'
    _order = 'employee_id, contract_id, deduction_id'


    slip_id = fields.Many2one('hr.payslip', 'Pay Slip', required=True, ondelete='cascade')
    deduction_id =fields.Many2one('hr.contract.deduction', 'Deducciones', required=True)
    employee_id =fields.Many2one('hr.employee', 'Employee', required=True)
    contract_id =fields.Many2one('hr.contract', 'Contract', required=True, )
    amount = fields.Float('Valor', digits=('Payroll'))
    total_deduction  = fields.Float('Total', digits=('Payroll'), help="Total a descontar")
    total_accumulated  = fields.Float('Acumulado', digits=('Payroll'), help="Total pagado o acumulado del concepto", readonly=True)
    date  = fields.Date('Fecha',  digits=('Payroll'), help="Fecha del prestamo u obligacion")
    show_voucher =  fields.Boolean('Mostrar', digits=('Payroll'), help="Indica si se muestra o no en el comprobante de nomina")
    
class hr_contract_acumulados (models.Model):
    '''
    Detalle acumulados del contrato
    '''
    _name = 'hr.contract.acumulados'
    _description = 'Acumulados del contrato'
    _order = 'period_id, salary_rule_id'


    period_id  = fields.Many2one('account.period', required=True, string='Periodo')     
    salary_rule_id  = fields.Many2one('hr.salary.rule', required=True, string='Regla salarial')       
    amount = fields.Float('Valor', required=True)
    contract_id  = fields.Many2one('hr.contract', 'Liquidacion', required=True, ondelete='cascade', )

    


class hr_contract_liquidacion (models.Model):
    '''
    Detalle liquidacion de contrato
    '''
    _name = 'hr.contract.liquidacion'
    _description = 'Detalle liquidacion de contrato'
    _order = 'contract_id, sequence'


    sequence = fields.Integer('Secuencia', required=True)
    type  = fields.Selection([('P','Pago'),('D','Descuento')],'Tipo', required=True)
    name  = fields.Char ('Concepto', size=100, required = True)
    dias = fields.Float('Días', required = True)
    amount  = fields.Float('Valor', required=True)
    contract_id = fields.Many2one('hr.contract', 'Liquidacion', required=True, ondelete='cascade', )

class hr_contract_analytic(models.Model):
    _name= 'hr.contract.analytic'
    _description = 'Distribucion por cuenta analitica'


    percent  = fields.Float('Porcentaje', required=True)
    account_analytic_id = fields.Many2one('account.analytic.account','Cuenta analítica',required=True) 
    contract_id  = fields.Many2one('hr.contract', 'Cuenta analitica', required=True, ondelete='cascade', )        

    

    
class hr_contract  (models.Model):
    _inherit = "hr.contract"

    analytic_ids  = fields.One2many('hr.contract.analytic', 'contract_id', 'Cuentas analíticas')
    setting_ids  = fields.One2many('hr.contract.setting', 'contract_id', 'Configuración')
    deduction_ids  = fields.One2many('hr.contract.deduction', 'contract_id', 'Deducciones'),
    liquidacion_ids  = fields.One2many('hr.contract.liquidacion', 'contract_id', 'Liquidación')
    acumulado_ids  = fields.One2many('hr.contract.acumulados', 'contract_id', 'Acumulados')
    risk_id  = fields.Many2one('hr.contract.risk', required=True, string='Riesgo profesional')
    date_prima = fields.Date ('Fecha de liquidación de prima')
    date_cesantias  = fields.Date ('Fecha de liquidación de cesantías')
    date_vacaciones  = fields.Date ('Fecha de liquidación de vacaciones')
    dias_vacaciones = fields.Float('Días tomados de vacaciones', digits=('Payroll'))
    date_intereses  = fields.Date ('Fecha de liquidación de intereses a las cesantías')
    date_liquidacion  = fields.Date ('Fecha de liquidación contrato')
    dias_sancion = fields.Float('Sansiones en días', digits=('Payroll'))
    prestamos = fields.Float('Préstamos y anticipos', digits=('Payroll'))
    distribuir =  fields.Boolean('Distribuir por cuenta analítica', help="Indica si al calcula la nómina del contrato se distribuye por centro de costo")
    factor = fields.Float('Factor salarial', required=True)
    parcial = fields.Boolean('Tiempo parcial')
    pensionado = fields.Boolean('Pensionado')
    condicion = fields.Float('Condición anterior', digits=('Payroll'))
    compensacion = fields.Float('Compensación', digits=('Payroll'))

class hr_payslip_analytic (models.Model):
    _name= 'hr.payslip.analytic'
    _description = 'Distribucion regla por cuenta analitica'
    _order = 'salary_rule_id'

    salary_rule_id = fields.Many2one('hr.salary.rule','Regla salarial',required=True)
    account_analytic_id = fields.Many2one('account.analytic.account','Cuenta analítica',required=True)   
    percent  = fields.Float('Porcentaje', required=True)
    slip_id  = fields.Many2one('hr.payslip', 'Nómina', required=True, ondelete='cascade', )

class hr_payslip(models.Model):
    _inherit = "hr.payslip"
    

    liquida =  fields.Boolean('Liquidación', help="Indica si se ejecuta una estructura para liquidacion de contratos y vacaciones")
    deduction_line_ids = fields.One2many('hr.payslip.deduction.line', 'slip_id', 'Detalle deducciones', readonly=True)
    analytic_ids = fields.One2many('hr.payslip.analytic', 'slip_id', 'Distribucion cuentas analiticas')
    date_prima  = fields.Date ('Fecha de liquidación de prima')
    date_cesantias  = fields.Date ('Fecha de liquidación de cesantías')
    date_vacaciones  = fields.Date ('Fecha de liquidación de vacaciones')
    dias_vacaciones = fields.Float('Días tomados de vacaciones', digits=('Payroll'))
    date_intereses  = fields.Date ('Fecha de liquidación de intereses a las cesantías')
    date_liquidacion  = fields.Date ('Fecha de liquidación contrato')

class hr_novedades(models.Model):
    _name= 'hr.novedades'
    _description = 'Novedades de nómina'


    input_id  = fields.Many2one ('hr.rule.input','Novedad', required=False, help="Código o nombre de la novedad")
    code = fields.Char ('Codigo', required = True)
    date_from  = fields.Date ('Fecha desde', required = True)
    date_to  = fields.Date ('Fecha hasta', required = True)
    employee_id  = fields.Many2one ('hr.employee','Empleado', required=False, domain=[('active','=','true')],help="Cédula o nombre completo del empleado")
    identification_id  = fields.Char ('Cédula',required = True)
    value = fields.Float('Valor', required = True)
    account_analytic_id = fields.Many2one('account.analytic.account','Cuenta analítica')   
    