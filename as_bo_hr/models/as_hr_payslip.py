# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime, timedelta
from time import mktime
import time
from datetime import datetime, timedelta
from odoo.exceptions import UserError, RedirectWarning, ValidationError, MissingError
from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round, float_is_zero
from odoo.tools.float_utils import float_round, float_compare
from itertools import groupby
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import format_date
from odoo.tools.safe_eval import safe_eval
import base64

class HrEmployee(models.Model):
    _inherit = 'hr.payslip'
    
    as_sequence = fields.Integer(string='N°', help="Otorga la secuencia de nomina")
    as_antiguedad_payslib = fields.Integer(string='Años de Antiguedad',compute="_compute_calcular_antiguedad")
    as_neto_wage = fields.Monetary(compute='_compute_neto_net',string="Monto Neto")
    as_base_wage = fields.Monetary(compute='_compute_basic_pay',string="Sueldo Base")
    as_days_work= fields.Monetary(compute='_compute_basic_pay',string="Dias trabajados")

    def _compute_neto_net(self):
        for payslip in self:
            payslip.as_neto_wage = float(self.get_total_rules(payslip.id,'TOTAL',payslip.employee_id.id,payslip.contract_id.id))

    def _compute_basic_pay(self):
        for payslip in self:
            payslip.as_base_wage = 0.0
            dias = 0.0
            amount = 0.0
            worked_days = payslip.worked_days_line_ids.filtered(lambda p: p.work_entry_type_id.code == 'WORK100')
            if not worked_days:
                dias = payslip.as_get_days(30)
            else:
                dias = worked_days.number_of_days
            payslip.as_days_work = dias
            if not payslip.contract_id:
                amount = 0
                result = 0.0
            else:
                smn = float(payslip.as_smn_id.amount)
                if float(payslip.contract_id.wage) <= smn:
                    result = smn
                else:
                    valor = payslip.contract_id.wage* (int(payslip.as_smn_id.porcentaje)/100)
                    result = payslip.contract_id.wage + valor
            sueldo = result/30
            amount = sueldo * dias
            payslip.as_base_wage = amount

    # @api.onchange('worked_days_line_ids')
    def _compute_calcular_antiguedad(self):
        for payslip in self:
            #now = payslip.date_from
            now = payslip.date_to
            fecha_ingreso = fields.Date.from_string(payslip.employee_id.as_fecha_ingreso.strftime('%Y-%m-%d'))
            antiguedad = fecha_ingreso - now
            payslip.as_antiguedad_payslib = int(antiguedad.days/30/12)*-1

    def _action_create_account_move(self):
        precision = self.env['decimal.precision'].precision_get('Payroll')

        # Add payslip without run
        payslips_to_post = self.filtered(lambda slip: not slip.payslip_run_id)

        # Adding pay slips from a batch and deleting pay slips with a batch that is not ready for validation.
        payslip_runs = (self - payslips_to_post).mapped('payslip_run_id')
        for run in payslip_runs:
            if run._are_payslips_ready():
                payslips_to_post |= run.slip_ids

        # A payslip need to have a done state and not an accounting move.
        payslips_to_post = payslips_to_post.filtered(lambda slip: slip.state == 'done' and not slip.move_id)

        # Check that a journal exists on all the structures
        if any(not payslip.struct_id for payslip in payslips_to_post):
            raise ValidationError(_('One of the contract for these payslips has no structure type.'))
        if any(not structure.journal_id for structure in payslips_to_post.mapped('struct_id')):
            raise ValidationError(_('One of the payroll structures has no account journal defined on it.'))

        # Map all payslips by structure journal and pay slips month.
        # {'journal_id': {'month': [slip_ids]}}
        slip_mapped_data = {slip.struct_id.journal_id.id: {fields.Date().end_of(slip.date_to, 'month'): self.env['hr.payslip']} for slip in payslips_to_post}
        for slip in payslips_to_post:
            slip_mapped_data[slip.struct_id.journal_id.id][fields.Date().end_of(slip.date_to, 'month')] |= slip

        for journal_id in slip_mapped_data: # For each journal_id.
            for slip_date in slip_mapped_data[journal_id]: # For each month.
                line_ids = []
                debit_sum = 0.0
                credit_sum = 0.0
                date = slip_date
                move_dict = {
                    'narration': '',
                    'ref': date.strftime('%B %Y'),
                    'journal_id': journal_id,
                    'date': date,
                }
                #agrupacion por categoria
                categories = []
                vals = {
                    'categ':'Costo',
                    'slips':self.env['hr.payslip'].sudo(),
                }
                categories.append(vals)
                vals = {
                    'categ':'Gasto',
                    'slips':self.env['hr.payslip'].sudo(),
                }
                categories.append(vals)


                for lista in categories:
                    for slip in slip_mapped_data[journal_id][slip_date]:
                        for categ in slip.employee_id.category_ids:
                            if categ.as_tipo == lista['categ']:
                                lista['slips']+=slip
                    # categories.append(vals)
                categs = []
                for categ in categories:
                    line_ids = []
                    for slip in categ['slips']:
                        move_dict['narration'] += slip.number or '' + ' - ' + slip.employee_id.name or ''
                        move_dict['narration'] += '\n'
                        slip_lines = slip._prepare_slip_lines(date, line_ids,categ['categ'])
                        line_ids.extend(slip_lines)
                        # for line in line_ids:
                        #     line['name'] = line['name']+' Categoría: '+str(categ['categ'])
                    if line_ids != []:
                        categs.append({
                            'name': categ['categ'],
                            'display_type': 'line_note',
                            'debit': 0.0,
                            'credit': 0.0,
                        })
                    categs+=line_ids

                for line_id in categs: # Get the debit and credit sum.
                    debit_sum += line_id['debit']
                    credit_sum += line_id['credit']

                # The code below is called if there is an error in the balance between credit and debit sum.
                if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
                    slip._prepare_adjust_line(line_ids, 'credit', debit_sum, credit_sum, date)
                elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
                    slip._prepare_adjust_line(line_ids, 'debit', debit_sum, credit_sum, date)
                for line_pay in categs:
                    line_pay['name']=line_pay['name']+' - '+str(self.payslip_run_id.name)
                # Add accounting lines in the move
                move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in categs]
                move = self._create_account_move(move_dict)
                for slip in slip_mapped_data[journal_id][slip_date]:
                    slip.write({'move_id': move.id, 'date': date})
        return True

    def _prepare_slip_lines(self, date, line_ids,typ):
        self.ensure_one()
        precision = self.env['decimal.precision'].precision_get('Payroll')
        new_lines = []
        for line in self.line_ids.filtered(lambda line: line.category_id):
            amount = -line.total if self.credit_note else line.total
            if line.code == 'NET': # Check if the line is the 'Net Salary'.
                for tmp_line in self.line_ids.filtered(lambda line: line.category_id):
                    if tmp_line.salary_rule_id.not_computed_in_net: # Check if the rule must be computed in the 'Net Salary' or not.
                        if amount > 0:
                            amount -= abs(tmp_line.total)
                        elif amount < 0:
                            amount += abs(tmp_line.total)
            if float_is_zero(amount, precision_digits=precision):
                continue
            debit_account_id = line.salary_rule_id.account_debit.id
            credit_account_id = line.salary_rule_id.account_credit.id
            if typ == 'Costo' and line.salary_rule_id.as_account_debit_cost:
                debit_account_id = line.salary_rule_id.as_account_debit_cost.id
            if typ == 'Costo' and line.salary_rule_id.as_account_credit_cost:
                credit_account_id = line.salary_rule_id.as_account_credit_cost.id
            print(type)
            if debit_account_id: # If the rule has a debit account.
                debit = amount if amount > 0.0 else 0.0
                credit = -amount if amount < 0.0 else 0.0

                debit_line = self._get_existing_lines(
                    line_ids + new_lines, line, debit_account_id, debit, credit)

                if not debit_line:
                    debit_line = self._prepare_line_values(line, debit_account_id, date, debit, credit)
                    new_lines.append(debit_line)
                else:
                    debit_line['debit'] += debit
                    debit_line['credit'] += credit

            if credit_account_id: # If the rule has a credit account.
                debit = -amount if amount < 0.0 else 0.0
                credit = amount if amount > 0.0 else 0.0
                credit_line = self._get_existing_lines(
                    line_ids + new_lines, line, credit_account_id, debit, credit)

                if not credit_line:
                    credit_line = self._prepare_line_values(line, credit_account_id, date, debit, credit)
                    new_lines.append(credit_line)
                else:
                    credit_line['debit'] += debit
                    credit_line['credit'] += credit
        return new_lines

    def get_date_employee(self,fecha):
        fecha_def = ''
        if fecha:
            dia = datetime.strptime(str(fecha), '%Y-%m-%d').strftime('%d')
            mes = datetime.strptime(str(fecha), '%Y-%m-%d').strftime('%m')
            ano = datetime.strptime(str(fecha), '%Y-%m-%d').strftime('%Y')
            fecha_def = str(dia)+'/'+ str(mes)+'/'+str(ano)
        return fecha_def

    def _as_get_saldo_anterior(self):
        saldo_anterior = 0.0
        for payslip in self:
            if payslip.as_saldo_monto > 0.0:
                saldo_anterior = payslip.as_saldo_monto
            fecha = self.date_from - relativedelta(months=1)
            payslip_anterior = self.env['hr.payslip'].sudo().search([('date_from', '=', fecha),('employee_id','=',payslip.employee_id.id),('state','=','done')],limit=1)
            if payslip_anterior:
                saldo_anterior = float(self.get_total_rules(payslip_anterior.id,'SALDOSN',payslip_anterior.employee_id.id,payslip_anterior.contract_id.id))
            payslip.as_saldo_anterior = saldo_anterior

    as_indicadores_id = fields.Many2one('hr.indicadores', string='Indicadores')
    as_smn_id = fields.Many2one('as.hr.smn', string='Sueldo Minimo Nacional',readonly=True)
    as_saldo_anterior = fields.Float('Saldo Anterior',compute='_as_get_saldo_anterior')
    as_saldo_monto = fields.Float('Saldo Anterior Manual')

    def testeo_formulas(self):
        payslip = self
        ganado = 56153.85
        BASIC = 50000
        valor = 0.0
        bandera = False
        total = 0.0
        cantidad = len(payslip.as_indicadores_id.as_value_afp_ids)
        cont = 0
        desde = 0.0
        for item in payslip.as_indicadores_id.as_value_afp_ids:
            cont+=1
            if cont == cantidad:
                desde =item.as_desde
            else:
                desde =item.as_hasta
            if (BASIC-float(desde)) > 0.0:
                if not bandera:
                    valor = BASIC-float(item.as_hasta)
                    total += float(item.as_hasta)*float(item.as_valor/100)
                    bandera = True
                else:
                    total += valor * float(item.as_valor/100)
                    valor = BASIC-float(item.as_hasta)
            else:
                total += BASIC * float(item.as_valor/100)
                break
        total_10 = ganado*0.10
        total_171 = ganado*0.0171
        total_050 = ganado*0.005
        result = total 
        self._as_get_saldo_anterior()



    def get_total_rules(self,slip_id,code,employee_id,contract_id): 
        slip_line=self.env['hr.payslip.line'].sudo().search([('slip_id', '=', slip_id),('code', '=',code),('contract_id', '=',contract_id)],limit=1)
        if slip_line:
            return slip_line.total
        else:
            return 0.0    
    def get_mes_date(self,date):
        mes = self.get_mes(datetime.strptime(str(date), '%Y-%m-%d').strftime('%m'))
        return mes


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

    def _get_worked_day_lines_values(self, domain=None):
        self.ensure_one()
        res = []
        hours_per_day = self._get_worked_day_lines_hours_per_day()
        work_hours = self.contract_id._get_work_hours(self.date_from, self.date_to, domain=domain)
        work_hours_ordered = sorted(work_hours.items(), key=lambda x: x[1])
        biggest_work = work_hours_ordered[-1][0] if work_hours_ordered else 0
        add_days_rounding = 0
        for work_entry_type_id, hours in work_hours_ordered:
            work_entry_type = self.env['hr.work.entry.type'].browse(work_entry_type_id)
            days = round(hours / hours_per_day, 5) if hours_per_day else 0
            if work_entry_type_id == biggest_work:
                days += add_days_rounding
            day_rounded = self._round_days(work_entry_type, days)
            add_days_rounding += (days - day_rounded)
            if self.employee_id.resource_calendar_id.as_modalidad and work_entry_type.code == 'WORK100':
                dias = self.employee_id.resource_calendar_id.as_total_days
                dias = self.as_get_days(dias)
                attendance_line = {
                    'sequence': work_entry_type.sequence,
                    'work_entry_type_id': work_entry_type_id,
                    'number_of_days': dias,
                    'number_of_hours': dias*hours_per_day,
                }
                res.append(attendance_line)
            else:
                attendance_line = {
                    'sequence': work_entry_type.sequence,
                    'work_entry_type_id': work_entry_type_id,
                    'number_of_days': day_rounded,
                    'number_of_hours': hours,
                }
                res.append(attendance_line)
        return res

    def as_get_days(self,dias):
        for payslip in self:
            contrato = payslip.contract_id
            fic = contrato.date_start
            ffc = contrato.date_end
            fin = payslip.date_from
            ffn = payslip.date_to
            dias_mes = int(payslip.date_to.strftime('%d'))
            dias_fic = 0.0
            dias_ffc = 0.0
            bandera = False
            if fic:
                if fic > fin and fic <= ffn:
                    dias_fic = dias_mes-(float(fic.strftime('%d'))-1)
                    bandera = True
            if ffc:
                if ffc > fin and ffc <= ffn:
                    dias_ffc = float(ffc.strftime('%d'))-1
                    bandera = True
            if bandera:
                dias = abs(dias_fic-dias_ffc)
            return dias
			
			
    def get_slip_employee(self):
        return {
            'name': _('Nomina de Empleado'+str(self.employee_id.name)),
            'view_mode': 'form',
            'res_model': 'hr.payslip',
            'views': [(self.env.ref('hr_payroll.view_hr_payslip_form').id, 'form'), (False, 'tree')],
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'context': dict(self._context, create=False),
            'target': 'current',
        }

    @api.model
    def create(self,vals):
        smnv =self.env['as.hr.smn'].sudo().search([('state', '=', 'V')])
        if 'payslip_run_id' in vals:
            payslip_run_id =self.env['hr.payslip.run'].sudo().search([('id', '=', vals['payslip_run_id'])])
            if not smnv:
                raise UserError(_('No existe SMN en Vigencia, por favor cree al menos un en Vigencia'))
            else:
                vals['as_smn_id'] = smnv.id
            if payslip_run_id:
                vals['as_indicadores_id'] = payslip_run_id.as_indicadores_id.id
        res = super(HrEmployee, self).create(vals)
        return res

    def write(self, vals):
        smnv =self.env['as.hr.smn'].sudo().search([('state', '=', 'V')],limit=1)
        if not self.as_smn_id:
            vals['as_smn_id'] = smnv.id
        res = super(HrEmployee, self).write(vals)
        return res

    def compute_sheet(self):
        for pay in self:
            pay._as_get_saldo_anterior()
        res = super(HrEmployee, self).compute_sheet()
        return res


    def datos_employee(self):
        sueldo_basico = 0.0
        total_dias =0.0
        total_horas =0.0
        for rules in self.line_ids:
            if rules.code == 'BASIC':
                sueldo_basico = rules.total
        for line in self.worked_days_line_ids:
            total_dias += line.number_of_days
            total_horas += line.number_of_hours
        res = {
            'sueldo_basico': sueldo_basico,
            'dias_trabajo': total_dias,
            'horas_trabajo': total_horas,
        }
        return res

    def datos_asignacion(self):
        asignacion =0.0
        deduccion =0.0
        res = []
        for line in self.line_ids:
            if line.code == 'SALGAN':
                res.append({'monto': line.total,'name':line.name})        
            elif line.code == 'MBA':
                res.append({'monto': line.total,'name':line.name})    
            elif line.code == 'OTING':
                res.append({'monto': line.total,'name':line.name})    
            elif line.code == 'SUBT':
                res.append({'monto': line.total,'name':line.name})        
            elif line.code == 'TOTAL':
                res.append({'monto': line.total,'name':line.name})    
        return res

    def datos_deduccion(self):
        asignacion =0.0
        deduccion =0.0
        res = []
        for line in self.line_ids:    
            if line.code == 'AFP':
                res.append({'monto': line.total,'name':line.name})    
            elif line.code == 'ASOL':
                res.append({'monto': line.total,'name':line.name})    
            elif line.code == 'SUBTDED':
                res.append({'monto': line.total,'name':line.name})      
        return res
    def info_sucursal(self, requerido):
        info = ''
        diccionario_dosificacion= {}
        qr_code_id = self.env['qr.code'].search([('id', 'in', self.env['res.users'].browse(self._context.get('uid')).dosificaciones.ids),('activo', '=', True)],limit=1)
        if qr_code_id:
            diccionario_dosificacion = {
                'nombre_empresa' : qr_code_id.nombre_empresa or '',
                'nit' : qr_code_id.nit_empresa or '',
                'direccion1' : qr_code_id.direccion1 or '',
                'telefono' : qr_code_id.telefono or '',
                'ciudad' : qr_code_id.ciudad or '',
                'pais' : self.company_id.country_id.name or '',
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
        
    def logo(self):
        as_logo_cotizaciones_notas = bool(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_logo_cotizaciones_notas'))
        return as_logo_cotizaciones_notas or False

    def _get_salary_line_total(self, code):
        lines = self.line_ids.filtered(lambda line: line.code == code)
        return sum([line.total for line in lines])
    
    def devolver_logo(self):
        a=0
        valor = self.env.user.company_id.logo
        return valor
    
    def obtener_gestion(self, date):
        mes = datetime.strptime(str(date), '%Y-%m-%d').strftime('%Y')
        return mes
    
    def obtener_fecha_inicio(self, id_hr):
        val =self.env['hr.contract'].sudo().search([('employee_id', '=', id_hr), ('active', '=', True)])
        if val:
            m = datetime.strptime(str(val.date_start), '%Y-%m-%d').strftime('%d/%m/%Y')
            return m
        
    def obtner_total_codes(self):
        if self.line_ids:
            m = 0.00
            l_ = 0.00
            n = 0.00
            o = 0.00
            p = 0.00
            for line in self.line_ids:
                if line.code == 'BASIC':
                    m = line.total
                
                if line.code =='MBA':
                    l_ = line.total
                    
                if line.code =='TOTALDEI':
                    n = line.total
                    
                if line.code =='SUMAT':
                    o = line.total   
                    
                if line.code =='PSPA':
                    p = line.total                
            vals={
                    'RETRO': m,
                    'MBA': l_,
                    'TOTALDEI': n,
                    'suma': m + l_,
                    'SUMAT': o,
                    'PSPA': p,
                    'suma_desc': o - p,
                    'liquido': (m + l_) - (o - p),
            }
            return vals
    
    def obtner_firma_gerente(self):
        val =self.env['hr.employee'].sudo().search([('id', '=',267)])
        if val:
            devolver_firma = val.as_firma_archivo
            return devolver_firma
                

   

class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    as_type_id = fields.Many2one('as.hr.worked.days', string='Tipo')

    @api.depends('is_paid', 'number_of_hours', 'payslip_id', 'payslip_id.normal_wage', 'payslip_id.sum_worked_hours')
    def _compute_amount(self):
        for worked_days in self:
            if not worked_days.contract_id:
                worked_days.amount = 0
                continue
            if worked_days.payslip_id.wage_type == "hourly":
                worked_days.amount = worked_days.payslip_id.contract_id.hourly_wage * worked_days.number_of_hours if worked_days.is_paid else 0
            else:
                smn = float(worked_days.payslip_id.as_smn_id.amount)
                if float(worked_days.payslip_id.contract_id.wage) <= smn:
                    result = smn
                else:
                    valor = worked_days.payslip_id.contract_id.wage* (int(worked_days.payslip_id.as_smn_id.porcentaje)/100)
                    result = worked_days.payslip_id.contract_id.wage + valor
                sueldo = result/30
                worked_days.amount = sueldo * worked_days.number_of_days

    @api.onchange('as_type_id')
    def onchange_days(self):
        for work in self:
            work.name= work.as_type_id.name
            work.code= work.as_type_id.code
            if work.payslip_id.contract_id:
                work.contract_id=work.payslip_id.contract_id

    @api.onchange('number_of_days')
    def oncchange_number_days(self):
        self.ensure_one()
        self.number_of_hours= (self.number_of_days*24)

class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    as_type_id = fields.Many2one('as.hr.inputs', string='Tipo')

    @api.onchange('as_type_id')
    def onchange_days(self):
        for work in self:
            work.name= work.as_type_id.name
            work.code= work.as_type_id.code
            if work.payslip_id.contract_id:
                work.contract_id=work.payslip_id.contract_id