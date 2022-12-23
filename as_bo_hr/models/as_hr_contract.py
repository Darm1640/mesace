# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime, timedelta
from time import mktime
import time
from datetime import datetime, timedelta


class HrContract(models.Model):
    _inherit= 'hr.contract'

    as_aumento_type = fields.Selection([('P','Porcentaje'),('M','Monto')], default='P',string='Novedades')
    as_aumento = fields.Float('Aumento Salarial Acordado', default=0.00)
    as_motivo_retiro = fields.Selection(selection=[('1','Retiro voluntario del trabajador'),('2','Vencimiento del contrato'),('3','Conclusion de obra'),('4','Perjuicio material causado con intencion en los instrumentos de trabajo'),('5','Revelacion de secretos industriales'),('6','Omision o imprudencias que afecten a la seguridad o higiene industrial'),('7','Inasistencia injustificada o mas de 6 dias continuos'),('8','Incumplimiento total o parcial del convenio'),('9','Robo o hurto por el trabajador'),('10','Retiro forzoso'),('11','Segun Articulo 41 de la ley N° 2027'),('12','Segun reglamento interno')], string="Motivo de Retiro")
    as_modalidad_contrato = fields.Selection(selection=[('1','Tiempo indefinido.'),('2','Aplazo fijo.'),('3','Por temporada.'),('4','Por realizacion de obra o servicio.'),('5','Condicional o eventual')], string="Modalidad de contrato", default="1", required=True)
    as_tipo_contrato = fields.Selection(selection=[('1','Escrito.'),('2','Verbal.')], string="Tipo de contrato", default="1", required=True)