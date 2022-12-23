# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class AsSurveyCuadrante(models.Model):
    _name = "as.survey.consolidate"
    _description = "Evaluacion Consolidada"


    name = fields.Char(string="Nombre Talento", required=True)
    as_survey_ids = fields.Many2many('survey.survey', string='Encuestas')
    lines_ids = fields.One2many('as.survey.consolidate.line','as_consolidate_id')
    lines_summary_ids = fields.One2many('as.survey.consolidate.summary','as_consolidate_id')
    state = fields.Selection([
        ('draft','Borrador'),
        ('done','Validado'),
        ('cancel','Cancelado'),
        ], string=u'Estado', readonly=True, default='draft',ondelete={'draft': 'cascade'})
    answer_done_count = fields.Integer("Cantidad", compute="_compute_survey_statistic")
    employer_id = fields.Many2one('as.survey.employer', string='Empleador')

    @api.depends('lines_ids.as_survey_1')
    def _compute_survey_statistic(self):
        self.answer_done_count = len(self.lines_ids)

    def as_action_cancel(self):
        for input in self.lines_ids:
            for input_lien in input.user_input_id:
                input_lien.as_extraido = False
        self.lines_ids.unlink()
        self.state = 'cancel'

    def action_survey_user_input(self):
        return {
            'name': _('Lineas de encuestas'),
            'view_mode': 'tree',
            'res_model': 'as.survey.consolidate.line',
            'views': [(self.env.ref('as_rapport_hr.as_survey_consolidateline_tree').id, 'tree'), (False, 'form')],
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', tuple(self.lines_ids.ids))],
            'context': dict(self._context, create=False),
        }


    def action_survey_user_input_completed(self):
        self.as_action_cancel()
        amount_1=0
        porcentaje_1=0
        amount_2=0
        porcentaje_2=0
        amount_3=0
        porcentaje_3=0
        parent = []
        chields = []
        partner = self.env['res.partner'].search([])
        self.state='draft'
        for survey in self.as_survey_ids:
            if not survey.as_parent_id:
                chields.append(survey.id)
            else:
                parent.append(survey.id)
        for partner in partner:
            as_personalidad = 0
            as_cargo_1 = 0
            as_note = ''
            participaciones =  self.env['survey.user_input'].search([('survey_id','in',self.as_survey_ids.ids),('state','=','done'),('as_extraido','=',False),('partner_id','=',partner.id),('employer_id','=',self.employer_id.id)])
            user_id = self.env['res.users'].search([('partner_id','=',partner.id)],limit=1)
            employee = self.env['hr.employee'].search([('userp_id','=',user_id.id)],limit=1)
            if participaciones:
                for part in participaciones:
                    if part.as_observaciones:
                        as_cargo_1 = part.as_cargo_1.id
                        as_note = part.as_note
                        as_personalidad = part.as_personalidad.id
                vals={
                    'name': 'Encuesta a '+str(partner.name),
                    'partner_id': partner.id,
                    'as_consolidate_id': self.id,
                    'as_personalidad': as_personalidad,
                    'as_cargo_1': as_cargo_1,
                    'as_note': as_note,
                
                    'as_edad': employee.as_edad,
                    'user_input_id': participaciones.ids,
                    # 'as_situacion': situacion,
                    'as_cargo': employee.contract_id.as_anio,
                    'as_year': employee.as_anio,
                    'superior_id': employee.parent_id.id,
                    'as_survey_colr_1': '',
                    'as_survey_colr_2': '',
                    'as_survey_colr_3': '',
                    'as_survey_colr_4': '',
                    'as_total': 0,
                    'as_total_rango': 0,
                }
                if employee.job_title:
                    vals['job_title'] = employee.job_title
                cont_comp = 0
                cont_hab = 0
                edad = 0.0
                total_rango = 0.0
                situacion = 0.0
                compromiso = 0.0
                habilidades = 0.0
                consolidate_line_id = self.env['as.survey.consolidate.line']
                for input in participaciones:
                    input.as_extraido = True
                    for line in input.user_input_line_ids:
                        if line.question_id.as_secuencia == 1:
                            if line.value_numerical_box > 0.0:  
                                compromiso += line.value_numerical_box
                            else:
                                if line.answer_score > 0:
                                    compromiso += line.answer_score
                                    cont_comp+=1
                            total_rango += line.as_total
                        elif line.question_id.as_secuencia == 2:
                            if line.value_numerical_box > 0.0:  
                                habilidades += line.value_numerical_box
                            else:
                                if line.answer_score > 0:
                                    habilidades += line.answer_score
                                    cont_hab+=1
                            total_rango += line.as_total
                        elif line.question_id.as_secuencia == 3:
                            if line.value_numerical_box > 0.0:  
                                edad = line.value_numerical_box
                            else:
                                edad = line.answer_score
                            total_rango += line.as_total
                        elif line.question_id.as_secuencia == 4:
                            if line.value_numerical_box > 0.0:  
                                situacion = line.value_numerical_box
                            else:
                                situacion = line.answer_score
                            total_rango += line.as_total
                    if int(input.survey_id.as_sequence) == 1 or int(input.survey_id.as_parent_id.as_sequence) == 1:
                        if input.survey_id.as_parent_id:
                            amount_1=input.as_total_survery
                            porcentaje_1=input.survey_id.as_porcentaje/100
                            vals['as_survey_1']=input.as_total_survery
                            vals['as_survey_colr_1']= str(self._compute_simulador_color(input.as_total_survery))
                        else:
                            amount_1=input.as_total_survery
                            porcentaje_1=input.survey_id.as_porcentaje/100
                            vals['as_survey_1']=input.as_total_survery
                            vals['as_survey_colr_1']= str(self._compute_simulador_color(input.as_total_survery))
                    if int(input.survey_id.as_sequence) == 2 or int(input.survey_id.as_parent_id.as_sequence) == 2:
                        if input.survey_id.as_parent_id:
                            amount_2=input.as_total_survery
                            porcentaje_2=input.survey_id.as_porcentaje/100
                            vals['as_survey_2']=input.as_total_survery
                            vals['as_survey_colr_2']= str(self._compute_simulador_color(input.as_total_survery))
                        else:
                            amount_2=input.as_total_survery
                            porcentaje_2=input.survey_id.as_porcentaje/100
                            vals['as_survey_2']=input.as_total_survery
                            vals['as_survey_colr_2']= str(self._compute_simulador_color(input.as_total_survery))
                    if int(input.survey_id.as_sequence) == 3 or int(input.survey_id.as_parent_id.as_sequence) == 3:
                        if input.survey_id.as_parent_id:
                            amount_3=input.as_total_survery
                            porcentaje_3=input.survey_id.as_porcentaje/100
                            vals['as_survey_3']=input.as_total_survery
                            vals['as_survey_colr_3']= str(self._compute_simulador_color(input.as_total_survery))
                        else:
                            amount_3=input.as_total_survery
                            porcentaje_3=input.survey_id.as_porcentaje/100
                            vals['as_survey_3']=input.as_total_survery
                            vals['as_survey_colr_3']= str(self._compute_simulador_color(input.as_total_survery))
                if cont_comp > 0:
                    vals['as_compromiso']=compromiso/cont_comp
                else:
                    vals['as_compromiso']=compromiso
                if cont_hab > 0:
                    vals['as_habilidades']=habilidades/cont_hab
                else:
                    vals['as_habilidades']=habilidades

                # vals['as_total']= float(compromiso+habilidades)/2,
                # vals['as_total_rango']=float(total_rango),
                vals['as_total_general']=(amount_1*porcentaje_1)+(amount_2*porcentaje_2)+(amount_3*porcentaje_3)
                vals['as_survey_colr_5']= str(self._compute_simulador_color((amount_1*porcentaje_1)+(amount_2*porcentaje_2)+(amount_3*porcentaje_3)))
                consolidate_line_id.create(vals)
                self.state = 'done'
        self._compute_consolidado_summary()

    def get_chield_amount(self,parent,partner):
        include = False
        total_rango = 0.0
        habilidades = 0.0
        for survey in parent:
            participaciones =  self.env['survey.user_input'].search([('survey_id','in',survey.id),('state','=','done'),('as_extraido','=',False),('partner_id','=',partner.id),('employer_id','=',self.employer_id.id)],limit=1)
            if participaciones:
                include = True
                total_rango = participaciones.as_total
                habilidades = participaciones.as_total
                if participaciones.value_numerical_box > 0.0:  
                    habilidades = participaciones.value_numerical_box
                else:
                    if participaciones.answer_score > 0:
                        habilidades = participaciones.answer_score
        return include,total_rango,habilidades
        

    def _compute_consolidado_summary(self):
        self.lines_summary_ids.sudo().unlink()
        consolidate_summary_id = self.env['as.survey.consolidate.summary']
        get_consolidate = ("""
                SELECT
                    superior_id,
                    avg(as_survey_1),
                    avg(as_survey_2),
                    avg(as_survey_3),
                    avg(as_total_general),
                    avg(as_compromiso)
                FROM
                    as_survey_consolidate_line
            WHERE
            as_consolidate_id = """+str(self.id)+"""
            group by 1 
        """)
        self.env.cr.execute(get_consolidate)
        for val in self.env.cr.fetchall():
            val1= 0
            val2= 0
            val3= 0
            val4= 0
            val5= 0
            if val[1] != None:
                val1= round(val[1],2)
            if val[2] != None:
                val2= round(val[2],2)
            if val[3] != None:
                val3= round(val[3],2)
            if val[4] != None:
                val4= round(val[4],2)
            if val[5] != None:
                val5= round(val[5],2)
            vals={
                'name': 'Obtenido',
                'as_consolidate_id': self.id,
                'superior_id': val[0],
                'as_survey_1': val1,
                'as_survey_2': val2,
                'as_survey_3': val3,
                'as_total_general': val4,
                'as_compromiso': val5,
            }
            if val[1] != None:
                vals['as_survey_colr_1']= str(self._compute_simulador_color(val1))
            if val[2] != None:
                vals['as_survey_colr_2']= str(self._compute_simulador_color(val2))
            if val[3] != None:
                vals['as_survey_colr_3']= str(self._compute_simulador_color(val3))
            if val[4] != None:
                vals['as_survey_colr_5']= str(self._compute_simulador_color(val4))

            consolidate_summary_id.create(vals)
        return True
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
        return color

class AsSurveyCuadranteLine(models.Model):
    _name = "as.survey.consolidate.line"
    _description = "Evaluacion Consolidada lineas"

    @api.depends('as_total_general')
    def _compute_simulador(self):
        cuadrante = 0.0
        for input in self:
            for line in input:
                cuadrante += line.as_total_general
            get_color = ("""
                SELECT
                    ascu.id,
                    asci.as_color
                FROM
                    as_survey_cuadrante ascu
                    join as_survey_color asci on asci.id=ascu.as_color_id
                WHERE
                """+str(cuadrante)+""" BETWEEN ascu.as_range_start AND ascu.as_range_end
            """)
            self.env.cr.execute(get_color)
            color = False
            cuadrante = False
            for val in self.env.cr.fetchall():
                color=val[1]
                cuadrante=val[0]
            if color:
                input.sudo().as_color_id = color 
                input.as_color = input.sudo().as_color_id.as_color
            else:
                input.sudo().as_color_id = False
                input.as_color = '0'

    name = fields.Char(string="Nombre Talento", required=True)
    partner_id = fields.Many2one('res.partner')
    job_id = fields.Many2one('hr.job')
    job_title = fields.Char('Cargo')
    as_consolidate_id = fields.Many2one('as.survey.consolidate')
    as_compromiso = fields.Float(string="Compromiso")
    as_habilidades = fields.Float(string="Habilidades")
    as_total = fields.Float(string="Total Habilidades Promedio")
    as_edad = fields.Float(string="Edad")
    as_total_rango = fields.Float(string="Total Rango")
    as_situacion = fields.Float(string="Situación")
    as_cargo = fields.Integer(string="Años en el Cargo")
    as_year = fields.Integer(string="Años en la Empresa")
    superior_id = fields.Many2one('hr.employee',string="Evaluación Jefe superior")
    user_input_id = fields.Many2many('survey.user_input', string='Certification attempts')
    as_total_general = fields.Float(string="Ranking Final")
    as_survey_1 = fields.Float(string="Auto Evaluación 30%")
    as_survey_2 = fields.Float(string="Evaluación Jefe Directo 40%")
    as_survey_3 = fields.Float(string="KPI 30%")
    as_survey_4 = fields.Float(string="quitado")
    as_survey_colr_1 = fields.Char(string='Color 1')
    as_survey_colr_2 = fields.Char(string='Color 2')
    as_survey_colr_3 = fields.Char(string='Color 3')
    as_survey_colr_4 = fields.Char(string='Color 4')
    as_survey_colr_5 = fields.Char(string='Color 5')
    as_color_id = fields.Many2one('as.survey.color', string='Color')
    as_color = fields.Selection(related="as_color_id.as_color")
    as_personalidad = fields.Many2one('as.personalidad', string='Personalidad')
    as_cargo_1 = fields.Many2one('as.cargo', string='Cargo')
    as_note = fields.Char(string='Observaciones')

class AsSurveyCuadranteSummary(models.Model):
    _name = "as.survey.consolidate.summary"
    _description = "Resumen de lineas de Consolidado"

    name = fields.Char(string="Nombre Resumen", required=True)
    as_consolidate_id = fields.Many2one('as.survey.consolidate')
    superior_id = fields.Many2one('hr.employee',string="Evaluación Jefe superior")
    as_compromiso = fields.Float(string="Compromiso")
    as_survey_1 = fields.Float(string="Auto Evaluación 30%")
    as_survey_2 = fields.Float(string="Evaluación Jefe Directo 40%")
    as_survey_3 = fields.Float(string="KPI 30%")
    as_total_general = fields.Float(string="Ranking Final")
    as_survey_colr_1 = fields.Char(string='Color 1')
    as_survey_colr_2 = fields.Char(string='Color 2')
    as_survey_colr_3 = fields.Char(string='Color 3')
    as_survey_colr_5 = fields.Char(string='Color 5')
