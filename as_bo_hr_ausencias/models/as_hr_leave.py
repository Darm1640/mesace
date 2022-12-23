# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime, timedelta
from time import mktime
import time
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo.exceptions import UserError, RedirectWarning, ValidationError, MissingError
from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round, float_is_zero
from odoo.tools.float_utils import float_round, float_compare

class HrEmployee(models.Model):
    _inherit = 'hr.leave'

    as_disponible = fields.Integer(string="Dias Disponibles",copy=False)
    as_motivo = fields.Many2one('as.hr.leave.motive', string="Motivo de Permiso",copy=False)
    as_remunerada = fields.Boolean(string="Remunerada")
    as_aprobado_un_dia = fields.Boolean(string="Aprobar menos de un dia")
    as_periodos_ids = fields.One2many('as.hr.periodo', 'as_leave',string="Periodos",copy=False)
    as_vaca = fields.Boolean(string="Vacaciones",related="holiday_status_id.as_calculo_vaca")
    as_permisos = fields.Boolean(string="Permisos",related="holiday_status_id.as_motivo_permiso")
    as_vaca_permiso = fields.Boolean(string="Vacaciones",related="as_motivo.as_vaca")
    as_periodos = fields.Char(string="Periodos")
    as_saldo = fields.Char(string="Dias de saldo del periodo")

    @api.onchange('request_date_from','request_date_to','employee_id','holiday_status_id')
    def as_get_dias_disponibles(self):
        dias_acumulados = 0
        dias_usados = 0
        for ausencia in self:
            if ausencia.holiday_status_id.as_calculo_vaca or ausencia.as_vaca_permiso:
                now = datetime.now()
                if not ausencia.employee_id.as_fecha_ingreso:
                    raise UserError(_('Debe completar fecha de ingreso en empleado'))
                fecha_ingreso = ausencia.employee_id.as_fecha_ingreso
                antiguedad = fecha_ingreso - now
                dias = int(antiguedad.days/30/12)*-1
                for dia in range(1,dias):
                    if dia < 5:
                        dias_acumulados+= 15
                    else:
                        dias_acumulados+= 20
                solicitudes = self.env['hr.leave'].sudo().search([('employee_id','=',ausencia.employee_id.id),('state','=','validate'),'|',('as_vaca','=',True),('as_vaca_permiso','=',True)])
                for day in solicitudes:
                    dias_usados += day.number_of_days
                ausencia.as_disponible = dias_acumulados-dias_usados
    
    def as_get_periodos(self):
        dias_acumulados = 0
        dias_usados = 0
        for ausencia in self:
            if ausencia.holiday_status_id.as_calculo_vaca or ausencia.as_vaca_permiso:
                now = datetime.now()
                ausencia.as_periodos_ids.unlink()
                valores = []
                if not ausencia.employee_id.as_fecha_ingreso:
                    raise UserError(_('Debe completar fecha de ingreso en empleado'))
                fecha_ingreso = ausencia.employee_id.as_fecha_ingreso
                antiguedad = fecha_ingreso - now
                dias = int(antiguedad.days/30/12)*-1 # lolleva a años
                cont = 0
                fecha_i = ausencia.employee_id.as_fecha_ingreso
                for dia in range(1,dias): 
                    if dia < 5: #SI LOS AÑOS SON MENOR A 5 LOS AÑOS DISPONIBLES DE VACACIONES SON 15 DIAS
                        vals = {
                            'as_date_from': fecha_i.strftime('%Y-%m-%d'),
                            'as_disponible': 15,
                            'as_leave': ausencia.id,
                        }
                        fecha_i = fecha_i + relativedelta(years=1)
                        vals['as_date_to'] = fecha_i
                        valores.append(vals)
                        dias_acumulados+= 15
                    else:#SI LOS AÑOS SON MAYOR A 5 LOS AÑOS DISPONIBLES DE VACACIONES SON 20 DIAS
                        vals = {
                            'as_date_from': fecha_i.strftime('%Y-%m-%d'),
                            'as_disponible': 20,
                            'as_leave': ausencia.id,
                        }
                        fecha_i = fecha_i + relativedelta(years=1)
                        vals['as_date_to'] = fecha_i
                        valores.append(vals)
                        dias_acumulados+= 20
                lines = self.env['as.hr.periodo'].sudo().create(valores)
                solicitudes = self.env['hr.leave'].sudo().search([('employee_id','=',ausencia.employee_id.id),('state','=','validate'),'|',('as_vaca','=',True),('as_vaca_permiso','=',True)])
                for day in solicitudes:
                    dias_usados += day.number_of_days
                dias_utilizados = dias_usados
                for line in ausencia.as_periodos_ids:
                    if dias_utilizados >= line.as_disponible:
                        line.as_usados  = line.as_disponible
                        dias_utilizados -= line.as_disponible
                    else:
                        line.as_usados  = dias_utilizados
                        dias_utilizados -= dias_utilizados 
                for line in ausencia.as_periodos_ids:                     
                    line.as_saldo = line.as_disponible - line.as_usados
                dias_soli = ausencia.number_of_days
                periodos = ''
                var = 0
                bandera = False
                saldo = 0
                cont = 0
                # el unico problema es que no se mostrara nada en periodos si la solicitud de
                # vacaciones es menor a 15 o al saldo de la primera linea        
                for line in ausencia.as_periodos_ids:
                    if dias_soli < line.as_saldo and cont == 0:
                        dias_soli = dias_soli - line.as_saldo
                        var = dias_soli
                        periodos += line.as_date_from.strftime('%d-%m-%Y')+'/'+line.as_date_to.strftime('%d-%m-%Y')+', '
                        saldo = abs(var)
                    else:
                        if bandera == True:
                            periodos += line.as_date_from.strftime('%d-%m-%Y')+'/'+line.as_date_to.strftime('%d-%m-%Y')+', '
                            bandera = False
                            saldo = abs(var - line.as_saldo)
                        
                        if line.as_saldo <= dias_soli and line.as_saldo > 0:
                            dias_soli = dias_soli - line.as_saldo
                            periodos += line.as_date_from.strftime('%d-%m-%Y')+'/'+line.as_date_to.strftime('%d-%m-%Y')+', '
                            var = dias_soli
                            if var != 0 and var < line.as_saldo:
                                bandera = True
                            saldo = abs(var)
                    cont += 1
                        
                ausencia.as_periodos = periodos
                ausencia.as_saldo = int(saldo)


    @api.model
    def create(self,vals):
        res = super(HrEmployee, self).create(vals)
        if res.holiday_status_id.as_calculo_vaca or res.as_vaca_permiso:
            if res.number_of_days > res.as_disponible:
                raise UserError(_('No puede registrar con dias superiores a los disponibles'))
            res.as_get_periodos()
        return res
    
    def obtener_fecha_actual(self):
        fecha_actual = time.strftime('%d/%m/%Y')
        struct_time_convert = time.strptime(fecha_actual, '%d/%m/%Y')
        date_time_convert = datetime.fromtimestamp(mktime(struct_time_convert))
        date_time_convert = date_time_convert - timedelta(hours = 4)
        fecha_actual = date_time_convert.strftime('%d/%m/%Y')
        return fecha_actual
    
    def extraer_firma_solicitante(self):
        if self.employee_id:
            hr_employee = self.env['hr.employee'].sudo().search([('id', '=', self.employee_id.id)])
            return hr_employee.id
    
    def extraer_firma_responsable(self):
        if self.employee_id:
            hr_employee = self.env['hr.employee'].sudo().search([('id', '=', self.employee_id.parent_id.id)])
            return hr_employee.id
        
    def resta_fechas(self):
        if self.date_from and self.date_to:
            fecha_1 = self.date_from.strftime('%d/%m/%Y %H:%M:%S')
            fecha_2 = self.date_to.strftime('%d/%m/%Y %H:%M:%S')
            date_ini = datetime.strptime(fecha_1, '%d/%m/%Y %H:%M:%S')  
            date_fin = datetime.strptime(fecha_2, '%d/%m/%Y %H:%M:%S')
            tiempo = (date_fin - date_ini)
            return tiempo
        

class AsMotivoPermiso(models.Model):
    _name = 'as.hr.leave.motive'
    _description = "modelo para guardar motivos de permiso"

    name = fields.Char(string="Titulo")
    as_vaca = fields.Boolean(string="Vacaciones")

class Ashrperiodo(models.Model):
    _name = 'as.hr.periodo'
    _description = "modelo para guardar motivos de permiso"

    as_date_from = fields.Date(string="Desde")
    as_date_to = fields.Date(string="Hasta")
    as_disponible = fields.Integer(string="Dias Acumulados",copy=False)
    as_usados = fields.Integer(string="Dias Usados",copy=False)
    as_saldo = fields.Integer(string="Dias Disponibles",copy=False)
    as_leave = fields.Many2one('hr.leave', string="Permiso Vacaciones",copy=False)