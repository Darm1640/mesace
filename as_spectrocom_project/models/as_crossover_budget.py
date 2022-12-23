# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import api, fields, models, _
from datetime import datetime, timedelta, date
import calendar
from pandas import Timestamp, date_range, bdate_range
from pandas.tseries.offsets import MonthBegin, MonthEnd, Day
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY, YEARLY

class AScrossovered_budget(models.Model):
    _inherit = "crossovered.budget"

    as_plantilla = fields.Many2one('as.plantillas.template', string="Plantilla")
    as_project_id = fields.Many2one('project.task', string="Proyecto")

    @api.onchange('as_plantilla')
    def onchange_plantilla_lines(self):
        data = {}
        line_cost = [(5, 0, 0)]
        
        mes = datetime.strptime(str(self.date_to), '%Y-%m-%d').strftime('%m')
        dia = datetime.strptime(str(self.date_to), '%Y-%m-%d').strftime('%d')
        year = datetime.strptime(str(self.date_to), '%Y-%m-%d').strftime('%Y')

        if self.as_project_id.as_frecuencia == 'Trimestral':
            # aux = 0
            
            # for num in range(1,5):
            start_ts, end_ts = Timestamp(self.date_from), Timestamp(self.date_to)
            dia = start_ts.day
            dia_fin = start_ts.days_in_month
            dias = int(dia_fin) - int(dia)
            diax = end_ts.day
            dia_finx = end_ts.days_in_month
            diasx = int(dia_finx) - int(diax)
            starts = bdate_range(start_ts, end_ts, freq='3M') + Day(-int(dias))
            ends = date_range(start_ts + MonthBegin(3), end_ts + MonthBegin(3), freq='3M') + Day(-int(diasx)) 
            # self.crossovered_budget_line = list(zip(starts, ends))
            for num in list(zip(starts, ends)):
                for lines in self.as_plantilla.template_cost_lines:
                    data = {
                        'general_budget_id': lines.general_budget_id.id,
                        'date_from': num[0]._date_repr,
                        'date_to': num[1]._date_repr,
                        'planned_amount': lines.price_unit
                    }
                    line_cost.append((0, 0, data))
                    
                # x = int(num)+aux
                
                # date_from = str(year)+'-'+str(x)+'-'+'01'
                # aux += 2
                # y = int(num)+aux
                # periodo = calendar.monthrange(int(year),y)
                # date_to = str(year)+'-'+str(y)+'-'+str(periodo[1])
                # for lines in self.as_plantilla.template_cost_lines:
                #     data = {
                #         'general_budget_id': lines.general_budget_id.id,
                #         'date_from': date_from,
                #         'date_to': date_to,
                #         'planned_amount': lines.price_unit
                #     }
                #     line_cost.append((0, 0, data))
        else:
            start_ts, end_ts = Timestamp(self.date_from), Timestamp(self.date_to)
            
            starts = [i.strftime('%m/%d/%Y') for i in date_range(start=start_ts, end=end_ts, freq='MS')] 
            ends = [i.strftime('%m/%d/%Y') for i in date_range(start=start_ts, end=end_ts, freq='MS')+ MonthEnd(+1)]
            
            d = []
            fi = start_ts + relativedelta(months=1)
            meses = 0
            for period in rrule(freq=MONTHLY, bymonth=(), dtstart=self.date_from, until=self.date_to):
                meses+=1

            flag = False
            cont = 0
            for i in range(0,meses):
                cont += 1
                if not flag:
                    fecha_inicial = self.date_from
                    fecha_final = fecha_inicial + relativedelta(months=1) 
                    fecha_final_d = fecha_final - relativedelta(days=1) 
                    flag = True
                    aux = {
                        'f_i':fecha_inicial,
                        'f_f':fecha_final_d
                    }
                    d.append(aux)
                else:
                    fecha_inicial = fecha_final
                    fecha_final = fecha_inicial + relativedelta(months=1) 
                    fecha_final_d = fecha_final - relativedelta(days=1) 
                    # if cont == meses:
                    #     fecha_final_d = self.date_to
                    aux = {
                        'f_i':fecha_inicial,
                        'f_f':fecha_final_d
                    }
                    d.append(aux)

            for num in d:
                for lines in self.as_plantilla.template_cost_lines:
                    data = {
                        'general_budget_id': lines.general_budget_id.id,
                        'date_from': num['f_i'],
                        'date_to': num['f_f'],
                        'planned_amount': lines.price_unit
                    }
                    line_cost.append((0, 0, data))
            # for num in range(1,int(mes)+1):
               
            #     periodo = calendar.monthrange(int(year),int(num))
            #     date_from = str(year)+'-'+str(num)+'-'+'01'
            #     date_to = str(year)+'-'+str(num)+'-'+str(periodo[1])
            #     for lines in self.as_plantilla.template_cost_lines:
            #         data = {
            #             'general_budget_id': lines.general_budget_id.id,
            #             'date_from': date_from,
            #             'date_to': date_to,
            #             'planned_amount': lines.price_unit
            #         }
            #         line_cost.append((0, 0, data))
        self.crossovered_budget_line = line_cost

class AScrossovered_budget_lines(models.Model):
    _inherit = "crossovered.budget.lines"

    general_budget_id = fields.Many2one(string='Your preferred label')