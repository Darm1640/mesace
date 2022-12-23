# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from urllib.request import urlopen
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import requests
import calendar
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY, SU, SA

_logger = logging.getLogger(__name__)
MONTH_LIST= [('1', 'Enero'), 
('2', 'Febrero'), ('3', 'Marzo'), 
('4', 'Abril'), ('5', 'Mayo'), 
('6', 'Junio'), ('7', 'Julio'), 
('8', 'Agosto'), ('9', 'Septiembre'), 
('10', 'Octubre'), ('11', 'Noviembre'),
('12', 'Diciembre')]


class hr_indicadores_previsionales(models.Model):

    _name = 'hr.indicadores'
    _description = 'Indicadores Provisionales'


    name = fields.Char('Nombre')
    month = fields.Selection(MONTH_LIST, string='Mes', required=True)
    year = fields.Integer('Año', required=True, default=datetime.now().strftime('%Y'))
    as_afp = fields.Char('Factor AFP')
    as_aumento_sueldo = fields.Char('Aumento de Sueldo %')
    as_antiguedad_ids = fields.Many2many('as.hr.antiguedad',string='Rangos de antiguedad y porcentaje')
    as_value_afp_ids = fields.Many2many('as.hr.afp',string='Rangos de AFP-Aporte Solidario')
    as_factor_3smn = fields.Float('Factor 3SMN')
    as_semanas = fields.Float('Semanas del Año')
    as_meses = fields.Float('Meses del Año')
    as_horas_mujer = fields.Float('Horas/semanas Mujer')
    as_dias_hombre = fields.Float('Dias/semanas Hombre')
    as_dias_mujer = fields.Float('Dias/semanas Mujer')
    as_horas_hombre = fields.Float('Horas/semanas Hombre')
    as_horas_mujer = fields.Float('Horas/semanas Mujer')
    as_semanas_meses = fields.Float('Semanas/Meses')
    as_dias_habiles = fields.Float('Dias Habiles')
    as_dias_inhabiles = fields.Float('Dias Inhabiles')
    as_UFV_inicial = fields.Float('UFV Inicial',digits=(5,5))
    as_UFV_final = fields.Float('UFV Final',digits=(5,5))

    @api.onchange('year','month')
    def as_dias_habiles_computo(self):
        for line in self:
            cont =0
            conti =0
            year = self.year
            mes = self.month
            if year and mes:
                date = fields.Date.context_today(self)
                periodo = calendar.monthrange(int(year),int(mes))
                inicio = datetime.strptime(str(periodo[1])+'/'+str(mes)+'/'+str(year), '%d/%m/%Y')
                fin = datetime.strptime(str('1')+'/'+str(mes)+'/'+str(year), '%d/%m/%Y')
                dt = rrule(freq=DAILY, byweekday=[6], dtstart=fin, until=inicio)
                dt2 = rrule(freq=DAILY, byweekday=[0,1,2,3,4,5], dtstart=fin, until=inicio)
                for day in dt2:
                    conti+=1      
                for day in dt:
                    cont+=1
            line.as_dias_habiles = conti
            line.as_dias_inhabiles = cont

            
    @api.onchange('as_semanas','as_meses')
    def as_onchange(self):
        for line in self:
            if line.as_meses > 0:
                line.as_semanas_meses = line.as_semanas /  line.as_meses
        

class as_hr_antiguedad(models.Model):
    
    _name = 'as.hr.antiguedad'
    _description = 'Indicadores Provisionales lineas de rango de antiguedad'

    as_desde = fields.Integer('Desde')
    as_hasta = fields.Integer('Hasta')
    as_valor = fields.Float('Valor')

class as_hr_afp(models.Model):
    
    _name = 'as.hr.afp'
    _description = 'Indicadores Provisionales lineas de rango de AFP'

    as_desde = fields.Integer('Desde')
    as_hasta = fields.Integer('Hasta')
    as_valor = fields.Float('Valor')
