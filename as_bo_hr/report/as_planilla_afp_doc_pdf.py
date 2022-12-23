# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError
import calendar
import datetime
from datetime import datetime
import pytz
from odoo import models,fields
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class ReportTax(models.AbstractModel):
    _name = 'report.as_bo_hr.as_planilla_pdf_afp'

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        lineas = self.lines_nomina(data['form']['payslip_run_id'][0])
        return {
            'data': data['form'],
            'info': self.info_sucursal(),
            'fechas': self.fechas(data['form']['payslip_run_id'][0]),
            'info': self.info_sucursal(),
            'nomina': data['form']['payslip_run_id'][1],
            'lines': lineas,
            'salarios': self.salarios(data['form']['payslip_run_id'][0]),
        }

    def info_sucursal(self):
        info = ''
        diccionario_dosificacion= {}
        diccionario_dosificacion = {
            'nombre_empresa' : self.env.user.company_id.name or '',
            'as_numero_patronal' : self.env.user.company_id.as_numero_patronal or '',
            'as_patronal_municipal' : self.env.user.company_id.as_patronal_municipal or '',
            'nit' : self.env.user.company_id.vat or '',
            'direccion1' : self.env.user.company_id.street or '',
            'telefono' : self.env.user.company_id.phone or '',
            'ciudad' : self.env.user.company_id.city or '',
            'sucursal' : self.env.user.company_id.city or '',
            'pais' : self.env.user.company_id.country_id.name or '',
            'actividad' :  self.env.user.company_id.name or '',
            'fechal' : self.env.user.company_id.phone or '',
            'email' : self.env.user.company_id.email or '',

        }
        return diccionario_dosificacion

    def fechas(self,nomina_id):
        fechas = {}
        nomina = self.env['hr.payslip.run'].sudo().search([('id', '=', nomina_id)])
        for nomina in nomina:
            vals = {
                'date_start': nomina.date_start,
                'date_end': nomina.date_end,
            }
            return vals

    def salarios(self,nomina_id):
        nomina = self.env['hr.payslip.run'].sudo().search([('id', '=', nomina_id)])
        smns =self.env['as.hr.smn'].sudo().search([('state', '=', 'V')])
        periodo = datetime.strptime(str(nomina.date_start), '%Y-%m-%d').strftime('%m')
        ano = datetime.strptime(str(nomina.date_start), '%Y-%m-%d').strftime('%Y')
        mes_anterior = datetime.strptime(str(nomina.date_start), '%Y-%m-%d') - relativedelta(months=1)
        mes_actual = datetime.strptime(str(nomina.date_start), '%Y-%m-%d')
        fecha = datetime.strptime(str(nomina.date_start), '%Y-%m-%d')
        fechai = str(ano) +'-'+str(mes_anterior.strftime('%m'))+'-'+str(calendar.monthrange(fecha.year,fecha.month-1)[1])
        fechaf = str(ano) +'-'+str(mes_actual.strftime('%m'))+'-'+str(calendar.monthrange(fecha.year,fecha.month)[1])
        consulta_rate = ("""
            select rcr.rate from res_currency_rate rcr
            inner join res_currency rc on rc.id = rcr.currency_id
            where 
            rc.name='UFV' and 
            rcr.name in ('""" + str(fechai) + """', '""" + str(fechaf) + """') order by rcr.name limit 2
            """)
        self.env.cr.execute(consulta_rate)
        rates = [k for k in self.env.cr.fetchall()]
        tasa_inicial = 0.0
        tasa_final = 0.0
        if len(rates)>0:
            tasa_inicial = rates[0][0]
        if len(rates)>1:
            tasa_final = rates[1][0]
        return {'fecha_i': tasa_inicial,'fecha_f': tasa_final,'smn': smns.amount}

    def lines_nomina(self,nomina_id):
        nominas = self.env['hr.payslip.run'].sudo().search([('id', '=', nomina_id)])
        items=[]
        cont = 0
        monto_sueldos = 0.0
        monto_afp = 0.0
        monto_ans = 0.0
        monto_otros = 0.0
        monto_neto = 0.0
        monto_dos_salarios = 0.0
        monto_base_imponible = 0.0
        monto_impuestorc = 0.0
        monto_smn = 0.0
        monto_neto_ec= 0.0
        monto_facturas= 0.0
        monto_fisco= 0.0
        monto_dependiente= 0.0
        monto_saldo_anterior= 0.0
        monto_saldo_anterior= 0.0
        monto_anterior_actualizado= 0.0
        monto_saldo_utilizado= 0.0
        monto_saldo_perido= 0.0
        monto_saldo_impuestorc= 0.0
        monto_mes_siguiente= 0.0
        for nomina in nominas.slip_ids:
            cont +=1
            total_asignacion = 0.0
            total_deduccion = 0.0
            total_fact = 0.0
            total_saldo = 0.0
            if nomina.employee_id.gender =='male':
                genero='M'
            elif nomina.employee_id.gender =='female':
                genero='F'
            else:
                genero='O'
            total_dias= 0
            total_horas= 0
            for line in nomina.worked_days_line_ids:
                total_dias += line.number_of_days
                total_horas += line.number_of_hours
            #asignaciones
            sueldo_basico= 0.0
            sueldo_ganado= 0.0
            mba= 0.0
            oting =0.0
            Subtotal_ganado= 0.0
            #deducciones
            afp = 0.0
            asol = 0.0
            subt = 0.0
            total_asignacion = 0.0
            subtotal_deducciones = 0.0
            #total liquido pagable
            sueldo_neto = 0.0
            for line in nomina.line_ids:
                if line.code == 'SUBT':
                    subt = line.total
                    total_asignacion += line.total
                    monto_sueldos += line.total    
                elif line.code == 'OTING':
                    oting = line.total
                    total_asignacion += line.total  
                    monto_otros +=  line.total  
                elif line.code == 'AFP':
                    afp = line.total 
                    total_deduccion += line.total 
                    monto_afp +=  line.total  
                elif line.code == 'ASOL':
                    asol = line.total 
                    total_deduccion += line.total 
                    monto_ans +=  line.total  
                elif line.code == 'FACT':
                    total_fact += line.total 
                elif line.code == 'SALFAV':
                    total_saldo += line.total 
            total_ingreso = total_asignacion - total_deduccion   
            monto_neto += total_ingreso
            total_sueldo = float(nomina.as_smn_id.amount)*2 
            monto_dos_salarios += total_sueldo
            if total_ingreso > total_sueldo:
                base_impuesto = total_ingreso - total_sueldo
            else:
                base_impuesto = 0
            monto_base_imponible +=base_impuesto
            base_impuesto_iva = base_impuesto*0.13
            monto_impuestorc += base_impuesto_iva
            base_sin = 0.0
            if base_impuesto_iva > 0.0:
                base_sin = base_impuesto_iva * 0.13
            monto_smn += base_sin
            monto_n = 0.0
            if base_impuesto_iva > base_sin:
                monto_n =base_impuesto_iva - base_sin
            monto_neto_ec +=  monto_n
            monto_facturas += total_fact
            fisco = 0.0
            if monto_n > total_fact:
                fisco = monto_n - total_fact
            monto_fisco += fisco
            dependiente = 0.0
            if total_fact > monto_n:
                dependiente = total_fact - monto_n
            monto_dependiente += dependiente
            monto_saldo_anterior += total_saldo
            monto_saldo_anterior += total_saldo
            monto_anterior =0
            tasa_final = float(self.salarios(nomina_id)['fecha_f'])
            tasa_inicial = float(self.salarios(nomina_id)['fecha_i'])
            if tasa_final > 0:
                monto_anterior = (tasa_inicial/tasa_final)*total_saldo
            monto_anterior_actualizado += monto_anterior
            anterior_actual = monto_anterior+total_saldo
            monto_saldo_utilizado += anterior_actual
            saldo_utilizado = 0.0
            if anterior_actual <= fisco:
                saldo_utilizado =  anterior_actual
            else:
                saldo_utilizado =  fisco
            monto_saldo_perido += saldo_utilizado
            impuestorc= 0
            if fisco > saldo_utilizado:
                impuestorc = fisco - saldo_utilizado
            monto_saldo_impuestorc +=impuestorc
            saldo_mes_siguiente = (dependiente + saldo_utilizado)- saldo_utilizado
            monto_mes_siguiente += saldo_mes_siguiente
            vals ={
                'num':cont,
                'as_documento': nomina.employee_id.as_documento,
                'identification_id': nomina.employee_id.identification_id,
                'as_expedito': nomina.employee_id.as_expedito,
                'apellido_1': nomina.employee_id.apellido_1,
                'apellido_2': nomina.employee_id.apellido_2,
                'apellido_3': nomina.employee_id.apellido_3,
                'name': nomina.employee_id.name,
                'ocupacion':nomina.employee_id.job_id.name,
                'as_novedades': nomina.employee_id.as_novedades,
                'total_dias':total_dias,
                # 'ano':datetime.strptime(str( nominas.date_start), '%Y-%m-%d').strftime('%Y'),
                # 'mes':datetime.strptime(str( nominas.date_start), '%Y-%m-%d').strftime('%m'),
                # 'as_code_iva': nomina.employee_id.as_code_iva,
                # 'nombre': nomina.employee_id.nombre,
                # 'afp': afp,
                # 'asol': asol,
                # 'oting': oting,
                # 'subt': subt,
                # 'total_ingreso': total_ingreso,
                # 'total_sueldo': total_sueldo,
                # 'base_impuesto': round(base_impuesto,0),
                # 'base_impuestorc': round(base_impuesto*0.13,3),
                # 'base_sin': base_sin,
                # 'monto_n': monto_n,
                # 'total_fact': total_fact,
                # 'fisco': fisco,
                # 'dependiente': dependiente,
                # 'total_saldo': total_saldo,
                # 'monto_anterior': monto_anterior,
                # 'anterior_actual': anterior_actual,
                # 'saldo_utilizado': saldo_utilizado,
                # 'impuestorc': impuestorc,
                # 'saldo_mes_siguiente': saldo_mes_siguiente,
        
            }
            items.append(vals)
        totales ={
            'num': 0,
            # 'afp': monto_afp,
            # 'asol': monto_ans,
            # 'oting': monto_otros,
            # 'subt': monto_sueldos,
            # 'total_ingreso': monto_neto,
            # 'total_sueldo': monto_dos_salarios,
            # 'base_impuesto' : monto_base_imponible,
            # 'base_impuestorc' : monto_impuestorc,
            # 'base_sin' : monto_smn,
            # 'monto_n' : monto_neto_ec,
            # 'total_fact' : monto_facturas,
            # 'fisco' : monto_fisco,
            # 'dependiente' : monto_dependiente,
            # 'total_saldo' : monto_saldo_anterior,
            # 'monto_anterior' : monto_anterior_actualizado,
            # 'anterior_actual' : monto_saldo_utilizado,
            # 'saldo_utilizado' : monto_saldo_perido,
            # 'impuestorc' : monto_saldo_impuestorc,
            # 'saldo_mes_siguiente' : monto_mes_siguiente,
        }
        items.append(totales)
        return items
    