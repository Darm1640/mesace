import pytz
from odoo import http, api, fields, models, _
from datetime import datetime, timedelta  
from odoo.http import request
import json
import logging
_logger = logging.getLogger(__name__)
from odoo import models, fields, api
import datetime
import sys
import importlib

    
class VisitP(models.Model):
    _name = 'hr.employee.test'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'evaluacion empleados Prueba'
    _rec_name = 'as_cliente'

    as_cliente = fields.Char(string='Nombre',required=True)
    as_email = fields.Char(string='Correo',required=True)
    as_mobile = fields.Char(string='Célular',required=True)
    as_empresa = fields.Char(string='Empresa',required=True)
    # as_antiguedad_cargo = fields.Integer(string='Antiguedad en el cargo',required=True)
    as_date = fields.Datetime(string='Fecha',required=True, default=lambda self: fields.Datetime.now())
    user_id = fields.Many2one('res.users', string='Responsible', required=False, default=lambda self: self.env.user)
    as_cuadrante_id = fields.Many2one('as.survey.cuadrante', string='Cuadrante')

    as_compromiso = fields.Selection(selection=[
            ('10','NINGUNO/A'),
            ('20','DEMASIADO BAJO'),
            ('30','UN POCO BAJO'),
            ('40','BAJO'),
            ('50','MEDIO/BAJO'),
            ('60','MEDIO'),
            ('70','MEDIO/ALTO'),
            ('80','ALTO'),
            ('90','MUY ALTO'),
            ('100','DESTACADO'),
        ],
        string="Compromiso")
    as_habilidades = fields.Selection(selection=[
            ('10','NINGUNO/A'),
            ('20','DEMASIADO BAJO'),
            ('30','UN POCO BAJO'),
            ('40','BAJO'),
            ('50','MEDIO/BAJO'),
            ('60','MEDIO'),
            ('70','MEDIO/ALTO'),
            ('80','ALTO'),
            ('90','MUY ALTO'),
            ('100','DESTACADO'),
        ],
        string="Habilidades")
    as_antiguedad = fields.Selection(selection=[
            ('5','MENOS 1 A 2'),
            ('90','2.1 A 4'),
            ('100','4.1 A 5'),
            ('80','5.1 A 6'),
            ('70','6.1 A 6.5'),
            ('60','6.6 A 7'),
            ('50','7.1 A 7.5'),
            ('40','7.6 A 8'),
            ('30','8.1 A 10'),
            ('20','10.1 A 13'),
            ('10','13.1 O MAS'),
        ],
        string="Antiguedada")
    as_edad = fields.Selection(selection=[
            ('10','60 O MAS'),
            ('20','56 Y 59'),
            ('30','52 A 55'),
            ('40','49 Y 51'),
            ('50','46 Y 48'),
            ('60','43 Y 45'),
            ('70','40 Y 42'),
            ('80','38 y 39'),
            ('90','34 y 37'),
            ('100','27 y 33'),
        ],
        string="Edad")
    as_rango_1 = fields.Float(string='as_rango_1')
    as_rango_2 = fields.Float(string='as_rango_2')
    as_rango_3 = fields.Float(string='as_rango_3')
    as_rango_4 = fields.Float(string='as_rango_4')
    as_simulador_1 = fields.Float(string='as_simulador_1')
    as_simulador_2 = fields.Float(string='as_simulador_2')
    as_simulador_3 = fields.Float(string='as_simulador_3')
    as_simulador_4 = fields.Float(string='as_simulador_4')
    as_factor_1 = fields.Float(string='as_factor_1',default=20.0)
    as_factor_2 = fields.Float(string='as_factor_2',default=60.0)
    as_factor_3 = fields.Float(string='as_factor_3',default=10.0)
    as_factor_4 = fields.Float(string='as_factor_4',default=10.0)
    as_total = fields.Float(string='as_factor_4')
    as_total_factor = fields.Float(string='as_factor_4')
    as_features_ids = fields.Many2many('as.survey.features', string='Tag Características')

    @api.onchange('as_compromiso','as_habilidades','as_antiguedad','as_edad')
    def as_get_compromiso(self):
        for line in self:
            line.as_simulador_1 = float(line.as_compromiso)
            line.as_simulador_2 = float(line.as_habilidades)
            line.as_simulador_3 = float(line.as_antiguedad)
            line.as_simulador_4 = float(line.as_edad)

            line.as_rango_1 = float(line.as_compromiso)*line.as_factor_1
            line.as_rango_2 = float(line.as_habilidades)*line.as_factor_2
            line.as_rango_3 = float(line.as_antiguedad)*line.as_factor_3
            line.as_rango_4 = float(line.as_edad)*line.as_factor_4

            line.as_total = line.as_rango_1+ line.as_rango_2+line.as_rango_3+line.as_rango_4
            line.as_total_factor = line.as_factor_1+ line.as_factor_2+line.as_factor_3+line.as_factor_4
            line._compute_simulador_color(line.as_total)[0]
            cuadrant_id = line._compute_simulador_color(line.as_total)[1]
            if cuadrant_id:
                active_id = self.env['as.survey.cuadrante'].search([('id','=',cuadrant_id)])
                line.as_cuadrante_id = active_id
                line.as_features_ids = active_id.as_features_ids.ids
            

    def _compute_simulador_color(self,valor):
        cuadrante = 0
        color = 0
        get_color = ("""
                SELECT
                    ascu.id,
                    asci.as_color
                FROM
                    as_survey_cuadrante ascu
                    join as_survey_color asci on asci.id=ascu.as_color_id
            WHERE
            """+str(valor)+""" BETWEEN ascu.as_range_start AND ascu.as_range_end
        """)
        self.env.cr.execute(get_color)
        color = False
        cuadrante = False
        for val in self.env.cr.fetchall():
            color=val[1]
            cuadrante=val[0]
        return (color,cuadrante)