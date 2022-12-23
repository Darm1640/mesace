# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime, timedelta
from time import mktime
from odoo.exceptions import UserError, RedirectWarning, ValidationError, MissingError
import time
from . import as_taxes_requests
import calendar
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from datetime import datetime, timedelta

class HrEmployeeSmn(models.Model):
    _name = 'as.hr.finiquito'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description="Calculo d eindemnizacion y finiquito de empleados"

    employee_id = fields.Many2one('hr.employee', string="Empleado")
    contract_id = fields.Many2one('hr.contract', compute='_compute_contract_id', string='Contrato',store=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True, default=lambda self: self.env.company)
    as_date_start = fields.Date('Fecha Ingreso', default=fields.Date.context_today)
    as_date_end = fields.Date('Fecha Retiro/Indemnización', default=fields.Date.context_today)
    as_dias = fields.Float('Dias')
    as_meses = fields.Float('Meses')
    as_años = fields.Float('Años')
    as_motivo = fields.Text(string='Motivo de retiro')
    as_tipo = fields.Selection([ ('Indemnización', 'Indemnización'),('Finiquito', 'Finiquito')], default='Indemnización',string='Tipo')
    as_gerente = fields.Many2one('hr.employee', string="Gerente General")
    as_deducciones_ids = fields.One2many('as.hr.finiquito.lines', 'as_finiquito_id', string='Deduacciones')
    as_remuneraciones_ids = fields.One2many('as.hr.remuneracion', 'as_finiquito_id', string='Remuneraciones')
    as_indemnizaciones_ids = fields.One2many('as.hr.indemnizacion', 'as_finiquito_id', string='Indemnizaciones')
    state = fields.Selection([('draft', 'Borrador'),('to_approval', 'A Aprobar'), ('approval', 'Aprobado'),('paid', 'Pagado')], default='draft',string='Estado')
    as_total_promedio = fields.Float('Total Ganado Promedio')
    as_total_vacaciones = fields.Float('Vacaciones')
    as_total_indemnizacion = fields.Float('Total Indemnización',compute="as_compute_deducciones")
    as_total_deducciones = fields.Float('Total Deducciones',compute="as_compute_deducciones")
    as_total = fields.Float('Total',compute="as_compute_deducciones")
    as_approval = fields.Boolean(string="Permitido aprobar",compute="_get_approvals")
    as_sueldo_promedio = fields.Float(string='Sueldo Promedio')
    as_caja_line_id = fields.Many2many('as.payment.multi', string="Linea de Caja")

    def as_get_bonus_payment(self):
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'as.payment.finiquito',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': {'default_as_generador_id': self.id },
            }

    def as_action_confirm(self):
        self.state = 'approval'    
        
    def as_get_to_approval(self):
        self.state = 'to_approval'

    def as_get_draft(self):
        for order in self:
            order.state =  'draft'

    @api.depends('state')
    def _get_approvals(self):
        for order in self:
            aprobar = False
            usuario = order.env.user.id
            if usuario == order.as_gerente.user_id.id:
                aprobar = True 
            order.as_approval = aprobar

    @api.depends('as_deducciones_ids.as_amount','as_indemnizaciones_ids.as_total')
    def as_compute_deducciones(self):
        total_indemnizaciones= 0.0
        deducciones = 0.0
        for line in self.as_indemnizaciones_ids:
            total_indemnizaciones+= line.as_total
        for line in self.as_deducciones_ids:
            deducciones+= line.as_amount
        self.as_total_deducciones = deducciones
        self.as_total_indemnizacion = total_indemnizaciones
        self.as_total = total_indemnizaciones - deducciones


    @api.onchange('employee_id','as_date_start','as_date_end')
    def _compute_contract_id(self):
        Contract = self.env['hr.contract']
        for employee in self.employee_id:
            self.contract_id = Contract.search([('employee_id', '=', employee.id)], order='date_start desc', limit=1)
            self.as_date_start= self.contract_id.date_start
            if self.contract_id.date_start:
                tiempo = self.as_date_end - self.contract_id.date_start
                self.as_meses = int((tiempo.days/30/12 - int(tiempo.days/30/12))*12)
                self.as_dias = int((tiempo.days/30/12 - int(tiempo.days/30/12))*30)
                if int(tiempo.days/30/12) >= 1:
                    self.as_años = int(tiempo.days/30/12)
                else:
                    self.as_años = 0

    def as_compute_finiquito(self):
        for finiquito in self:
            #REMUNERACIONES
            total_ganado = 0.0
            ganado = self.env['as.hr.remuneracion']
            finiquito.as_remuneraciones_ids.unlink()
            mes1= (datetime.strptime(str(self.as_date_end), '%Y-%m-%d') - relativedelta(months=+0)).strftime('%m')
            mes2= (datetime.strptime(str(self.as_date_end), '%Y-%m-%d') - relativedelta(months=+1)).strftime('%m')
            mes3= (datetime.strptime(str(self.as_date_end), '%Y-%m-%d') - relativedelta(months=+2)).strftime('%m')
            year1= (datetime.strptime(str(self.as_date_end), '%Y-%m-%d') - relativedelta(months=+0)).strftime('%Y')
            year2= (datetime.strptime(str(self.as_date_end), '%Y-%m-%d') - relativedelta(months=+1)).strftime('%Y')
            year3= (datetime.strptime(str(self.as_date_end), '%Y-%m-%d') - relativedelta(months=+2)).strftime('%Y')
            vals ={
                'as_años': year1,
                'as_meses': self.get_mes(str(mes1)),
                'as_amount': self.get_periodo_salary(str(mes1),year1),
                'as_finiquito_id': finiquito.id,
            }
            total_ganado += self.get_periodo_salary(str(mes1),year1)
            ganado += self.env['as.hr.remuneracion'].create(vals)
            vals ={
                'as_años': year2,
                'as_meses': self.get_mes(str(mes2)),
                'as_amount': self.get_periodo_salary(str(mes2),year2),
                'as_finiquito_id': finiquito.id,
            }
            total_ganado += self.get_periodo_salary(str(mes2),year2)
            ganado += self.env['as.hr.remuneracion'].create(vals) 
            vals ={
                'as_años': year3,
                'as_meses': self.get_mes(str(mes3)),
                'as_amount': self.get_periodo_salary(str(mes3),year3),
                'as_finiquito_id': finiquito.id,
            }
            total_ganado += self.get_periodo_salary(str(mes3),year3)
            ganado += self.env['as.hr.remuneracion'].create(vals) 
            for line in ganado:
                if line.as_amount <= 0:
                    line.as_amount = finiquito.contract_id.wage
                    total_ganado+=finiquito.contract_id.wage
            finiquito.as_total_promedio = total_ganado/3
            #INDEMNIZACION
            total_indemnizacion = 0.0
            date_start = finiquito.as_date_start
            if finiquito.get_last_indemnizacion():
                date_start = fields.Date.from_string(finiquito.get_last_indemnizacion()) + relativedelta(days=+1)
            fechas = self.as_get_compute_time(date_start,finiquito.as_date_end)
            finiquito.as_indemnizaciones_ids.unlink()
            #años
            anio = int(fechas[0])*(finiquito.as_total_promedio)
            if anio > 0:
                vals ={
                    'as_concepto': 'Indemnización '+str(date_start.strftime('%d-%m-%y'))+'/'+str(finiquito.as_date_end.strftime('%d-%m-%y')),
                    'as_años': fechas[0],
                    'as_meses': '',
                    'as_dias': 0,
                    'as_amount': finiquito.as_total_promedio,
                    'as_total': anio,
                    'as_finiquito_id': finiquito.id,
                }
                total_indemnizacion += anio
                self.env['as.hr.indemnizacion'].create(vals)  
            #meses
            mes = int(fechas[1])*(finiquito.as_total_promedio/12)
            if mes > 0:
                vals ={
                    'as_concepto': 'Indemnización '+str(date_start.strftime('%d-%m-%y'))+'/'+str(finiquito.as_date_end.strftime('%d-%m-%y')),
                    'as_años': 0,
                    'as_meses': str(fechas[1]),
                    'as_dias': 0,
                    'as_amount': finiquito.as_total_promedio/12,
                    'as_total': mes,
                    'as_finiquito_id': finiquito.id,
                }
                total_indemnizacion += mes
                self.env['as.hr.indemnizacion'].create(vals)  
            #Dias
            dias = int(fechas[2])*(finiquito.as_total_promedio/360)
            if dias > 0:
                vals ={
                    'as_concepto': 'Indemnización '+str(date_start.strftime('%d-%m-%y'))+'/'+str(finiquito.as_date_end.strftime('%d-%m-%y')),
                    'as_años': 0,
                    'as_meses': '',
                    'as_dias': fechas[2],
                    'as_amount': finiquito.as_total_promedio/360,
                    'as_total': dias,
                    'as_finiquito_id': finiquito.id,
                }
                total_indemnizacion += dias
                self.env['as.hr.indemnizacion'].create(vals)  
            if finiquito.as_tipo == 'Finiquito':
                #AGUINALDO
                date_start = fields.Date.from_string(year1+'-01-01')
                fechas = self.as_get_compute_time(date_start,finiquito.as_date_end)
                #años
                anio = int(fechas[0])*(finiquito.as_total_promedio)
                if anio > 0:
                    vals ={
                        'as_concepto': 'Aguinaldo de Navidad '+str(date_start.strftime('%d-%m-%y'))+'/'+str(finiquito.as_date_end.strftime('%d-%m-%y')),
                        'as_años': fechas[0],
                        'as_meses': '',
                        'as_dias': 0,
                        'as_amount': finiquito.as_total_promedio,
                        'as_total': anio,
                        'as_finiquito_id': finiquito.id,
                    }
                    total_indemnizacion += anio
                    self.env['as.hr.indemnizacion'].create(vals)  
                #meses
                mes = int(fechas[1])*(finiquito.as_total_promedio/12)
                if mes > 0:
                    vals ={
                        'as_concepto': 'Aguinaldo de Navidad '+str(date_start.strftime('%d-%m-%y'))+'/'+str(finiquito.as_date_end.strftime('%d-%m-%y')),
                        'as_años': 0,
                        'as_meses': str(fechas[1]),
                        'as_dias': 0,
                        'as_amount': finiquito.as_total_promedio/12,
                        'as_total': mes,
                        'as_finiquito_id': finiquito.id,
                    }
                    total_indemnizacion += mes
                    self.env['as.hr.indemnizacion'].create(vals)  
                #Dias
                dias = int(fechas[2])*(finiquito.as_total_promedio/360)
                if dias > 0:
                    vals ={
                        'as_concepto': 'Aguinaldo de Navidad '+str(date_start.strftime('%d-%m-%y'))+'/'+str(finiquito.as_date_end.strftime('%d-%m-%y')),
                        'as_años': 0,
                        'as_meses': '',
                        'as_dias': fechas[2],
                        'as_amount': finiquito.as_total_promedio/360,
                        'as_total': dias,
                        'as_finiquito_id': finiquito.id,
                    }
                    total_indemnizacion += dias
                    self.env['as.hr.indemnizacion'].create(vals)  
                #VACACIONES
                date_start = finiquito.as_date_start
                fechas = self.as_get_compute_vacaciones()
                #Dias
                vacaciones = 0.0
                dias = int(fechas)*(finiquito.as_total_promedio/30)
                if dias > 0:
                    vals ={
                        'as_concepto': 'Vacaciones '+str(date_start.strftime('%d-%m-%y'))+'/'+str(finiquito.as_date_end.strftime('%d-%m-%y')),
                        'as_años': 0,
                        'as_meses': '',
                        'as_dias': fechas,
                        'as_amount': finiquito.as_total_promedio/360,
                        'as_total': dias,
                        'as_finiquito_id': finiquito.id,
                    }
                    total_indemnizacion += dias
                    vacaciones = dias
                    self.env['as.hr.indemnizacion'].create(vals)  
                finiquito.as_total_indemnizacion = total_indemnizacion
                finiquito.as_total_vacaciones = vacaciones
                finiquito.as_deducciones_ids.unlink()
                vals ={
                    'as_concepto': 'Vacación de  Descuento por  RC-IVA  13%',
                    'as_amount': finiquito.as_total_vacaciones*0.13,
                    'as_finiquito_id': finiquito.id,
                }
                finiquito.as_total_deducciones=finiquito.as_total_vacaciones*0.13
                self.env['as.hr.finiquito.lines'].create(vals)  

    def as_get_compute_vacaciones(self):
        total_dias = 0.0
        dias_fraccion = 0
        if self.as_años > 0: 
            for i in range(1,int(self.as_años)+1):
                if i < 5:
                    total_dias+=15
                else:
                    total_dias+=20
        if (total_dias+1) < 5:
            dias_fraccion =15
        else:
            dias_fraccion =20
        total_dias += int(self.as_meses) * (dias_fraccion/12)
        total_dias += int(self.as_dias) * (dias_fraccion/360)
        dias_usados = 0.0
        solicitudes = self.env['hr.leave'].sudo().search([('employee_id','=',self.employee_id.id),('state','=','validate'),'|',('as_vaca','=',True),('as_vaca_permiso','=',True)])
        for day in solicitudes:
            dias_usados += day.number_of_days
        return total_dias-dias_usados

    def as_get_compute_time(self,date_start,date_end):
        Contract = self.env['hr.contract']
        tiempo = date_end - date_start
        as_meses = int((tiempo.days/30/12 - int(tiempo.days/30/12))*12)
        as_dias = int((tiempo.days/30/12 - int(tiempo.days/30/12))*30)
        if int(tiempo.days/30/12) >= 1:
            as_años = int(tiempo.days/30/12)
        else:
            as_años = 0
        return as_años,as_meses,as_dias

    def get_last_indemnizacion(self):
        self.env.cr.execute("""
            SELECT
                sl.as_date_end
            FROM
                as_hr_finiquito sl
            WHERE
                employee_id= """+str(self.employee_id.id)+""" and 
                contract_id= """+str(self.contract_id.id)+""" and 
                as_tipo = 'Indemnización' and 
                state = 'paid'
                order by sl.as_date_end desc
                limit 1
        """)
        ubicaciones_ids = [i[0] for i in self.env.cr.fetchall()]
        monto = 0.0
        if ubicaciones_ids != []:
            return ubicaciones_ids[0]
        else:
            return False
        return False

    def get_date_complet(self):
        ciudad = self.info_sucursal_2('ciudad')
        semana = (datetime.now() - timedelta(hours = 4)).strftime('%w')
        dia = (datetime.now() - timedelta(hours = 4)).strftime('%d')
        mes = (datetime.now() - timedelta(hours = 4)).strftime('%m')
        year = (datetime.now() - timedelta(hours = 4)).strftime('%Y')
        return str(ciudad)+' '+self.get_week(str(semana)) +' '+dia+' de '+self.get_mes(mes)+' de '+year

    def sumar_deducciones(self):
        monto =0.0
        if self.as_deducciones_ids:
            for field in self.as_deducciones_ids:
                if field.as_amount:
                    monto += field.as_amount 
                return monto
        else:
            monto += 0.0
        return monto

    def report_pdf_finiquito(self):
        self.ensure_one()
        context = self._context
        data = {'ids': self.env.context.get('active_ids', [])}
        res = self.read()
        res = res and res[0] or {}
        data.update({'form': res})
        return self.env.ref('as_hr.as_hr_report_finiquito').report_action(self, data=data)

    def info_sucursal(self, requerido):
        info = ''
        diccionario_dosificacion= {}
        qr_code_id = self.env['qr.code'].search([('id', 'in', self.env['res.users'].browse(self._context.get('uid')).dosificaciones.ids),('activo', '=', True)],limit=1)
        user_id = self.env['res.users'].browse(self._context.get('uid'))
        if qr_code_id:
            diccionario_dosificacion = {
                'nombre_empresa' : qr_code_id.nombre_empresa or '',
                'nit' : qr_code_id.nit_empresa or '',
                'direccion1' : qr_code_id.direccion1 or '',
                'telefono' : qr_code_id.telefono or '',
                'ciudad' : qr_code_id.ciudad or '',
                'pais' : user_id.company_id.country_id.name or '',
                'actividad' : qr_code_id.descripcion_actividad or '',
                'sucursal' : qr_code_id.sucursal or '',
                'fechal' : qr_code_id.fecha_limite_emision or '',
            }
        else:
            diccionario_dosificacion = {
                'nombre_empresa' : self.company_id.name or '',
                'nit' : self.company_id.vat or '',
                'direccion1' : self.company_id.street or '',
                'telefono' : self.company_id.phone or '',
                'ciudad' : self.company_id.city or '',
                'sucursal' : self.company_id.city or '',
                'pais' : self.company_id.country_id.name or '',
                'actividad' :  self.company_id.name or '',
                'fechal' : self.company_id.phone or '',

            }
        info = diccionario_dosificacion[str(requerido)]
        return info
    
    def info_sucursal_2(self, requerido):
        info = ''
        diccionario_dosificacion= {}
        diccionario_dosificacion = {
            'nombre_empresa' : self.company_id.name or '',
            'nit' : self.company_id.vat or '',
            'direccion1' : self.company_id.street or '',
            'telefono' : self.company_id.phone or '',
            'ciudad' : self.company_id.city or '',
            'sucursal' : self.company_id.city or '',
            'pais' : self.company_id.country_id.name or '',
            'actividad' :  self.company_id.name or '',
            'fechal' : self.company_id.phone or '',

        }
        info = diccionario_dosificacion[str(requerido)]
        return info

    def dias_totales(self):
        sueldo = 0.0
        for sal in self:
            yaars= self.as_años * (self.contract_id.wage)
            month= self.as_meses * (self.contract_id.wage/12)
            days= self.as_dias * (self.contract_id.wage/30)
            sueldo = yaars + month + days
        return sueldo    
    
    def dias_totales_aguinaldo(self):
        sueldo = 0.0
        yaars= self.as_aguinaldo_m * (self.contract_id.wage/12)
        yaars2= (self.as_aguinaldo_d * (self.contract_id.wage/12))/30
        sueldo = yaars + yaars2
        return sueldo

    def dias_totales_vaca(self):
        sueldo= self.as_total_vacaciones * (self.contract_id.wage/30)
        return sueldo

    def convertir_numero_a_literal(self, amount):
        amt_en = as_taxes_requests.amount_to_text(amount, 'BOLIVIANOS')
        return amt_en
    
    def as_get_date_literal(self,fecha):
        dia = datetime.strptime(str(fecha), '%Y-%m-%d').strftime('%d')
        mes = self.get_mes(datetime.strptime(str(fecha), '%Y-%m-%d').strftime('%m'))
        ano = datetime.strptime(str(fecha), '%Y-%m-%d').strftime('%Y')
        return str(dia)+' de '+ str(mes)+' de '+str(ano)
    
    def extraer_firma_solicitante(self):
        if self.employee_id:
            hr_employee = self.env['hr.employee'].sudo().search([('id', '=', self.employee_id.id)])
            return hr_employee.id
    
    def total_asignaciones(self):
        # return float(self.dias_totales())+float(self.dias_totales_aguinaldo())+float(self.dias_totales_vaca())
        return float(self.dias_totales())+float(self.dias_totales_vaca())

    def obtener_deducciones(self,requerido):
        for a in self:
            años = ''
            dic = {}
            cont = 0
            sumita = 0.0
            if a.as_deducciones_ids:
                for b in a.as_deducciones_ids:
                    lineas = self.env['as.hr.finiquito.lines'].sudo().search([('id', '=', b.id)])
                    if lineas:
                        if lineas.as_amount > 0 and cont <= 1:
                            dic['monto'] = lineas.as_amount
                            sumita += lineas.as_amount
                        cont += 1
                        dic['sumita'] = sumita
                años = dic[str(requerido)]
                return años
    
    def obtener_indeminizacion_anio(self,requerido):
        for a in self:
            años = ''
            dic = {}
            cont = 0
            sumita = 0.0
            if a.as_indemnizaciones_ids:
                for b in a.as_indemnizaciones_ids:
                    lineas = self.env['as.hr.indemnizacion'].sudo().search([('id', '=', b.id)])
                    if lineas:
                        if lineas.as_años > 0 and cont <= 2:
                            dic['años'] = lineas.as_años
                            dic['monto_año'] = lineas.as_total
                            sumita += lineas.as_total
                        if lineas.as_meses > 0 and cont <= 2:
                            dic['meses'] = lineas.as_meses
                            dic['monto_mes'] = lineas.as_total
                            sumita += lineas.as_total
                        if lineas.as_dias > 0 and cont <= 2:
                            dic['dias'] = lineas.as_dias
                            dic['monto_dia'] = lineas.as_total
                            sumita += lineas.as_total
                        cont += 1
                        dic['sumita'] = sumita
                años = dic[str(requerido)]
                return años
        
    def obtener_aguinaldos(self,requerido):
        for a in self:
            años = ''
            dic = {}
            cont = 0
            sumita = 0.0
            if a.as_indemnizaciones_ids:
                for b in a.as_indemnizaciones_ids:
                    lineas = self.env['as.hr.indemnizacion'].sudo().search([('id', '=', b.id)])
                    if lineas:
                        if lineas.as_meses > 0 and cont == 3:
                            dic['meses'] = lineas.as_meses
                            dic['monto_mes'] = lineas.as_total
                            sumita += lineas.as_total
                        if lineas.as_dias > 0 and cont == 4:
                            dic['dias'] = lineas.as_dias
                            dic['monto_dia'] = lineas.as_total
                            sumita += lineas.as_total
                        cont += 1
                        dic['sumita'] = sumita
                años = dic[str(requerido)]
                return años
        
    def obtener_vacacion_valores(self,requerido):
        for a in self:
            años = ''
            dic = {}
            cont = 0
            sumita = 0.0
            if a.as_indemnizaciones_ids:
                for b in a.as_indemnizaciones_ids:
                    lineas = self.env['as.hr.indemnizacion'].sudo().search([('id', '=', b.id)])
                    if lineas:
                        if lineas.as_dias > 0 and cont >= 5:
                            dic['dias'] = lineas.as_dias
                            dic['monto_mes'] = lineas.as_total
                            sumita += lineas.as_total
                        cont += 1
                        dic['sumita'] = sumita
                años = dic[str(requerido)]
                return años
        

    def obtener_nombre_anio(self):
        for i in self:
            lines_salary=''
            cont = 0
            if i.as_remuneraciones_ids:
                for n in  i.as_remuneraciones_ids:
                    lineas = self.env['as.hr.remuneracion'].sudo().search([('id', '=', n.id)])
                    if lineas and cont == 0:
                        mes_uno= lineas.as_meses
                        m = lineas.as_años
                        lines_salary = str(mes_uno) +' '+ str(m)
                    cont +=1
                return lines_salary
    
    def obtener_anio_monto_uno(self):
        for i in self:
            lines_salary=''
            cont = 0
            if i.as_remuneraciones_ids:
                for n in  i.as_remuneraciones_ids:
                    lineas = self.env['as.hr.remuneracion'].sudo().search([('id', '=', n.id)])
                    if lineas and cont == 0:
                        mes_uno= lineas.as_amount
                        lines_salary = mes_uno
                    cont +=1
                return lines_salary
    
    def obtener_nombre_anio_dos(self):
        for i in self:
            lines_salary=''
            cont = 0
            if i.as_remuneraciones_ids:
                for n in  i.as_remuneraciones_ids:
                    lineas = self.env['as.hr.remuneracion'].sudo().search([('id', '=', n.id)])
                    if lineas and cont == 0:
                        mes_uno= lineas.as_meses
                         
                    if lineas and cont == 1:
                        mes_uno= lineas.as_meses
                        m = lineas.as_años
                        lines_salary = str(mes_uno) +' '+ str(m)   
                    cont += 1 
                return lines_salary
    
    def obtener_anio_monto_dos(self):
        for i in self:
            lines_salary=''
            cont = 0
            if i.as_remuneraciones_ids:
                for n in  i.as_remuneraciones_ids:
                    lineas = self.env['as.hr.remuneracion'].sudo().search([('id', '=', n.id)])
                    if lineas and cont == 0:
                        mes_uno= lineas.as_amount
                    if lineas and cont == 1:
                        mes_uno= lineas.as_amount
                        lines_salary = mes_uno
                    cont += 1 
                return lines_salary
    
    def obtener_nombre_anio_tres(self):
        for i in self:
            lines_salary=''
            cont = 0
            if i.as_remuneraciones_ids:
                for n in  i.as_remuneraciones_ids:
                    lineas = self.env['as.hr.remuneracion'].sudo().search([('id', '=', n.id)])
                    if lineas and cont == 2:
                        mes_uno= lineas.as_meses
                        m = lineas.as_años
                        lines_salary = str(mes_uno) +' '+ str(m)
                    cont += 1 
                return lines_salary
        
    def obtener_anio_monto_tres(self):
        for i in self:
            lines_salary=''
            cont = 0
            if i.as_remuneraciones_ids:
                for n in  i.as_remuneraciones_ids:
                    lineas = self.env['as.hr.remuneracion'].sudo().search([('id', '=', n.id)])
                    if lineas and cont == 2:
                        mes_uno= lineas.as_amount
                        lines_salary = mes_uno
                    cont += 1 
                return lines_salary
    
    
    def get_lines_salary(self):  
        lines_salary=[]  
        mes1= (datetime.strptime(str(self.as_date_end), '%Y-%m-%d') - relativedelta(months=+1)).strftime('%m')
        mes2= (datetime.strptime(str(self.as_date_end), '%Y-%m-%d') - relativedelta(months=+2)).strftime('%m')
        mes3= (datetime.strptime(str(self.as_date_end), '%Y-%m-%d') - relativedelta(months=+3)).strftime('%m')
        year= datetime.strptime(str(self.as_date_end), '%Y-%m-%d').strftime('%Y')
        mes11= str(mes1)+'-'+ self.get_mes(str(mes1))
        mes22= str(mes2)+'-'+ self.get_mes(str(mes2))
        mes33= str(mes3)+'-'+ self.get_mes(str(mes3))
        vals ={
            '1': mes33,
            '2': mes22,
            '3': mes11,
        }
        lines_salary.append(vals)
        vals2={}
        vals3={}
        salario_ganado = 0.0
        salario1= self.get_periodo_salary(str(mes3),year)
        cont=0
        if salario1:
            vals2['1']= salario1
            salario_ganado += salario1
            cont+=1
        else:
            vals2['1']= 0.0
        salario2= self.get_periodo_salary(str(mes2),year)
        if salario2:
            vals2['2']= salario2
            salario_ganado += salario2
            cont+=1
        else:
            vals2['2']= 0.0
        salario3= self.get_periodo_salary(str(mes1),year)
        if salario3:
            vals2['3']= salario3
            salario_ganado += salario3
            cont+=1
        else:
            vals2['3']= 0.0
        lines_salary.append(vals2)
        if cont > 0:
            self.contract_id.wage= salario_ganado/cont
        else:
            self.contract_id.wage= 0.0
        return lines_salary
    


    def get_periodo_salary(self,mes,year):
        periodo = calendar.monthrange(int(year),int(mes))
        date_from = str(year)+'-'+str(mes)+'-'+'01'
        date_to = str(year)+'-'+str(mes)+'-'+str(periodo[1])
        self.env.cr.execute("""
            SELECT
                sl.id
            FROM
                hr_payslip sl
            WHERE
                employee_id= """+str(self.employee_id.id)+""" and 
                contract_id= """+str(self.contract_id.id)+""" and 
                (date_from = '"""+str(date_from)+"""' or
                date_to = '"""+str(date_to)+"""' )
                limit 1
        """)
        ubicaciones_ids = [i[0] for i in self.env.cr.fetchall()]
        monto = 0.0
        if ubicaciones_ids != []:
            slip = self.env['hr.payslip'].search([('id', '=', ubicaciones_ids[0])], limit=1)
            monto = slip._get_salary_line_total('SUBT')
        else:
            monto = 0.0
        return monto

    def get_mes(self,mes):
        mesesDic = {
            "01":'Enero',
            "02":'Febrero',
            "03":'Marzo',
            "04":'Abril',
            "05":'Mayo',
            "06":'Junio',
            "07":'Julio',
            "08":'Agosto',
            "09":'Septiembre',
            "10":'Octubre',
            "11":'Noviembre',
            "12":'Diciembre'
        }
        return mesesDic[str(mes)]

    def get_week(self,semana):
        semanaesDic = {
            "1":'Lunes',
            "2":'Martes',
            "3":'Miercoles',
            "4":'Jueves',
            "5":'Viernes',
            "6":'Sabado',
            "7":'Domingo',
          
        }
        return semanaesDic[str(semana)]

    def date_birthday(self):
        birthday =0
        hoy = fields.Date.context_today(self)
        date_birthday = self.employee_id.birthday
        if date_birthday:
            anos = hoy - date_birthday
            birthday = int(anos.days/30/12)
        else:
            birthday = 0
        return birthday
    def estado_civil(self):
        estado = self.employee_id.marital
        if estado == 'single':
            estado_civil = 'Soltero(a)'
        if estado == 'married':
            estado_civil = 'Casado(a)'
        if estado == 'cohabitant':
            estado_civil = 'Cohabitante legal'
        if estado == 'widower':
            estado_civil = 'Viudo(a)'
        if estado == 'divorced':
            estado_civil = 'divorciado(a)'
        return estado_civil

class HrEmployeeSmn(models.Model):
    _name = 'as.hr.finiquito.lines'

    as_concepto = fields.Char(string='Concepto')
    as_amount = fields.Float('Monto')
    as_finiquito_id = fields.Many2one('as.hr.finiquito', string='Finiquito')

class AsHrIdemnLines(models.Model):
    _name = 'as.hr.remuneracion'

    as_años = fields.Integer('Años')
    as_meses = fields.Char('Meses')
    as_amount = fields.Float('Monto')
    as_finiquito_id = fields.Many2one('as.hr.finiquito', string='Finiquito')
    

class AsHrIdemnLines(models.Model):
    _name = 'as.hr.indemnizacion'

    as_concepto = fields.Char(string='Concepto')
    as_años = fields.Integer('Años')
    as_meses = fields.Integer('Meses')
    as_dias = fields.Float('Dias')
    as_amount = fields.Float('Subtotal')
    as_total = fields.Float('Total')
    as_state = fields.Selection([('Pendiente', 'Pendiente'), ('Pagado', 'Pagado')], default='Pendiente',string='Estado')
    as_finiquito_id = fields.Many2one('as.hr.finiquito', string='Finiquito')