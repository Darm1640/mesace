# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError
from odoo import models,fields
from datetime import datetime, timedelta

class ReportTax(models.AbstractModel):
    _name = 'report.as_bo_hr.as_planilla_sueldo_pdf'

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        if data['form']['as_filtro_dep'] == True:
            lineas = self.lines_nomina_departamento(data['form']['payslip_run_id'][0])
        else:
            lineas = self.lines_nomina(data['form']['payslip_run_id'][0])
        return {
            'data': data['form'],
            'agrupado': data['form']['as_filtro_dep'],
            'afp': data['form']['as_name_afp'],
            'info': self.info_sucursal(),
            'fechas': self.fechas(data['form']['payslip_run_id'][0]),
            'info': self.info_sucursal(),
            'nomina': data['form']['payslip_run_id'][1],
            'lines': lineas,
            'anio': self.fechas(data['form']['payslip_run_id'][0])['date_end'].strftime('%Y'),
            'mes': self.get_mes(self.fechas(data['form']['payslip_run_id'][0])['date_end'].strftime('%m')),
        }

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

    def info_sucursal(self):
        info = ''
        diccionario_dosificacion= {}
        diccionario_dosificacion = {
            'nombre_empresa' : self.env.user.company_id.name or '',
            'nit' : self.env.user.company_id.vat or '',
            'as_numero_patronal' : self.env.user.company_id.as_numero_patronal or '',
            'as_patronal_municipal' : self.env.user.company_id.as_patronal_municipal or '',
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

    def lines_nomina(self,nomina_id):
        nomina = self.env['hr.payslip.run'].sudo().search([('id', '=', nomina_id)])
        items=[]
        cont = 0
        TBASIC = 0.0
        TMBA = 0.0
        TBOPRO = 0.0
        TBOFRON = 0.0
        THOURS100 = 0.0
        TDOMIN100 = 0.0
        TOTING = 0.0
        TSUBT = 0.0
        TAFP = 0.0
        TIMRCR = 0.0
        TOTDES = 0.0
        TSUBTDED = 0.0
        TTOTAL = 0.0
        for nomina in nomina.slip_ids:
            cont +=1
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
            BASIC = self.get_total_rules(nomina.id,'BASIC',nomina.employee_id.id,nomina.contract_id.id)
            MBA = self.get_total_rules(nomina.id,'MBA',nomina.employee_id.id,nomina.contract_id.id)
            BOPRO = self.get_total_rules(nomina.id,'BOPRO',nomina.employee_id.id,nomina.contract_id.id)
            BOFRON = self.get_total_rules(nomina.id,'BOFRON',nomina.employee_id.id,nomina.contract_id.id)
            HOURS100 = self.get_total_rules(nomina.id,'HOURS100',nomina.employee_id.id,nomina.contract_id.id)
            DOMIN100 = self.get_total_rules(nomina.id,'DOMIN100',nomina.employee_id.id,nomina.contract_id.id)
            OTING = self.get_total_rules(nomina.id,'OTING',nomina.employee_id.id,nomina.contract_id.id)
            SUBT = self.get_total_rules(nomina.id,'SUBT',nomina.employee_id.id,nomina.contract_id.id)
            AFP = self.get_total_rules(nomina.id,'AFP',nomina.employee_id.id,nomina.contract_id.id)
            IMRCR = self.get_total_rules(nomina.id,'IMRCR',nomina.employee_id.id,nomina.contract_id.id)
            OTDES = self.get_total_rules(nomina.id,'OTDES',nomina.employee_id.id,nomina.contract_id.id)
            SUBTDED = self.get_total_rules(nomina.id,'SUBTDED',nomina.employee_id.id,nomina.contract_id.id)
            TOTAL = self.get_total_rules(nomina.id,'TOTAL',nomina.employee_id.id,nomina.contract_id.id)
            TBASIC += BASIC
            TMBA += MBA
            TBOPRO += BOPRO
            TBOFRON += BOFRON
            THOURS100 += HOURS100
            TDOMIN100 += DOMIN100
            TOTING += OTING
            TSUBT += SUBT
            TAFP += AFP
            TIMRCR += IMRCR
            TOTDES += OTDES
            TSUBTDED += SUBTDED
            TTOTAL += TOTAL
            birthday = ''
            if nomina.employee_id.birthday:
                birthday = nomina.employee_id.birthday.strftime('%d/%m/%Y')
            vals ={
                'num':cont,
                'identification_id':nomina.employee_id.identification_id,
                'name':nomina.employee_id.name,
                'country_id':nomina.employee_id.country_id.name,
                'birthday': birthday,
                'genero':genero,
                'ocupacion':nomina.employee_id.job_id.name,
                'fecha_ingreso':nomina.employee_id.as_fecha_ingreso.strftime('%d/%m/%Y'),
                'total_dias':total_dias,
                'total_horas':nomina.employee_id.resource_calendar_id.hours_per_day,
                'BASIC':BASIC,
                'MBA':MBA,
                'BOPRO':BOPRO,
                'BOFRON':BOFRON,
                'HOURS100':HOURS100,
                'DOMIN100':DOMIN100,
                'OTING':OTING,
                'SUBT':SUBT,
                'AFP':AFP,
                'IMRCR':IMRCR,
                'OTDES':OTDES,
                'SUBTDED':SUBTDED,
                'TOTAL':TOTAL,
            }
            items.append(vals)
        vals_total = {
            'num':-1,
            'name':'total',
            'BASIC':TBASIC,
            'MBA':TMBA,
            'BOPRO':TBOPRO,
            'BOFRON':TBOFRON,
            'HOURS100':THOURS100,
            'DOMIN100':TDOMIN100,
            'OTING':OTING,
            'SUBT':TSUBT,
            'AFP':TAFP,
            'IMRCR':TIMRCR,
            'OTDES':TOTDES,
            'SUBTDED':TSUBTDED,
            'TOTAL':TTOTAL,

        }
        items.append(vals_total)
        return items

    def get_total_rules(self,slip_id,code,employee_id,contract_id): 
        slip_line=self.env['hr.payslip.line'].sudo().search([('slip_id', '=', slip_id),('code', '=',code),('contract_id', '=',contract_id)],limit=1)
        if slip_line:
            return slip_line.total
        else:
            return 0.0    

    def lines_nomina_departamento(self,nomina_id):
        departamentos = self.env['hr.department'].sudo().search([])
        items=[]
        cont = 0
        TBASIC = 0.0
        TMBA = 0.0
        TBOPRO = 0.0
        TBOFRON = 0.0
        THOURS100 = 0.0
        TDOMIN100 = 0.0
        TOTING = 0.0
        TSUBT = 0.0
        TAFP = 0.0
        TIMRCR = 0.0
        TOTDES = 0.0
        TSUBTDED = 0.0
        TTOTAL = 0.0
        cont = 0
        for depa in departamentos:
            vals ={
                'num':0,
                'name':depa.name,
            }
            consulta_employee = ("""
                SELECT 
                hp.id from hr_payslip hp
                inner join hr_employee he on hp.employee_id = he.id 
                left join hr_department hd on he.department_id = hd.id 
                where
                hd.id = """ + str(depa.id) + """ and 
                hp.payslip_run_id = """ + str(nomina_id) + """ 
            """)
            self.env.cr.execute(consulta_employee)
            employee = [k for k in self.env.cr.fetchall()]
            nomina = self.env['hr.payslip'].sudo().search([('id', 'in', employee)])
            if nomina:
                items.append(vals)
            for nomina in nomina:
                cont +=1
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
                BASIC = self.get_total_rules(nomina.id,'BASIC',nomina.employee_id.id,nomina.contract_id.id)
                MBA = self.get_total_rules(nomina.id,'MBA',nomina.employee_id.id,nomina.contract_id.id)
                BOPRO = self.get_total_rules(nomina.id,'BOPRO',nomina.employee_id.id,nomina.contract_id.id)
                BOFRON = self.get_total_rules(nomina.id,'BOFRON',nomina.employee_id.id,nomina.contract_id.id)
                HOURS100 = self.get_total_rules(nomina.id,'HOURS100',nomina.employee_id.id,nomina.contract_id.id)
                DOMIN100 = self.get_total_rules(nomina.id,'DOMIN100',nomina.employee_id.id,nomina.contract_id.id)
                OTING = self.get_total_rules(nomina.id,'OTING',nomina.employee_id.id,nomina.contract_id.id)
                SUBT = self.get_total_rules(nomina.id,'SUBT',nomina.employee_id.id,nomina.contract_id.id)
                AFP = self.get_total_rules(nomina.id,'AFP',nomina.employee_id.id,nomina.contract_id.id)
                IMRCR = self.get_total_rules(nomina.id,'IMRCR',nomina.employee_id.id,nomina.contract_id.id)
                OTDES = self.get_total_rules(nomina.id,'OTDES',nomina.employee_id.id,nomina.contract_id.id)
                SUBTDED = self.get_total_rules(nomina.id,'SUBTDED',nomina.employee_id.id,nomina.contract_id.id)
                TOTAL = self.get_total_rules(nomina.id,'TOTAL',nomina.employee_id.id,nomina.contract_id.id)
                TBASIC += BASIC
                TMBA += MBA
                TBOPRO += BOPRO
                TBOFRON += BOFRON
                THOURS100 += HOURS100
                TDOMIN100 += DOMIN100
                TOTING += OTING
                TSUBT += SUBT
                TAFP += AFP
                TIMRCR += IMRCR
                TOTDES += OTDES
                TSUBTDED += SUBTDED
                TTOTAL += TOTAL
                birthday = ''
                if nomina.employee_id.birthday:
                    birthday = nomina.employee_id.birthday.strftime('%d/%m/%Y')
                vals ={
                    'num':cont,
                    'identification_id':nomina.employee_id.identification_id,
                    'name':nomina.employee_id.name,
                    'country_id':nomina.employee_id.country_id.name,
                    'birthday': birthday,
                    'genero':genero,
                    'ocupacion':nomina.employee_id.job_id.name,
                    'fecha_ingreso':nomina.employee_id.as_fecha_ingreso.strftime('%d/%m/%Y'),
                    'total_dias':total_dias,
                    'total_horas':nomina.employee_id.resource_calendar_id.hours_per_day,
                    'BASIC':BASIC,
                    'MBA':MBA,
                    'BOPRO':BOPRO,
                    'BOFRON':BOFRON,
                    'HOURS100':HOURS100,
                    'DOMIN100':DOMIN100,
                    'OTING':OTING,
                    'SUBT':SUBT,
                    'AFP':AFP,
                    'IMRCR':IMRCR,
                    'OTDES':OTDES,
                    'SUBTDED':SUBTDED,
                    'TOTAL':TOTAL,
                }
                items.append(vals)
        vals_total = {
            'num':-1,
            'name':'total',
            'BASIC':TBASIC,
            'MBA':TMBA,
            'BOPRO':TBOPRO,
            'BOFRON':TBOFRON,
            'HOURS100':THOURS100,
            'DOMIN100':TDOMIN100,
            'OTING':OTING,
            'SUBT':TSUBT,
            'AFP':TAFP,
            'IMRCR':TIMRCR,
            'OTDES':TOTDES,
            'SUBTDED':TSUBTDED,
            'TOTAL':TTOTAL,

        }
        items.append(vals_total)
        return items
    
