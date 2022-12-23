# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class AsQuestion(models.Model):
    _inherit = "survey.question"

    as_factor = fields.Float(string="Factor %")
    as_secuencia = fields.Integer(string="Secuencia")

class AsInput(models.Model):
    _inherit = "survey.user_input"

    def as_get_lines_survey(self,valor):
        as_valor = float(valor)
        as_cant_line = len(self.survey_id.question_and_page_ids.filtered(lambda question: question.question_type != False))
        as_value_individual = as_valor
        if as_cant_line > 0:
            as_value_individual = as_valor/as_cant_line
        for line_question in self.survey_id.question_and_page_ids.filtered(lambda question: question.question_type != False):
            as_answer_score = as_value_individual
            if line_question.as_factor > 0:
                as_answer_score = as_value_individual / line_question.as_factor
            line = self.env['survey.user_input.line'].create(
                {'question_id': line_question.id, 
                'answer_type': 'numerical_box', 
                'answer_score': as_answer_score, 
                'as_factor': line_question.as_factor, 
                'as_total': as_value_individual, 
                'user_input_id': self.id
                })


    @api.depends('user_input_line_ids','as_note','as_cargo_1','as_personalidad','as_color_id')
    def _compute_amount_total(self):
        for input in self:
            total = 0.0
            input.as_total_old = 0.0 
            input.as_total_age = 0.0
            input.as_point_age = 0.0
            for line in input.user_input_line_ids:
                valor = line.answer_score
                line.as_factor = line.question_id.as_factor
                line.as_total = line.as_factor* valor
                total += line.as_total
                line.answer_score = valor
            input.as_total_survery = total
            # se calcula Edad y Antiguedad
            user_id = self.env['res.users'].search([('partner_id','=',input.partner_id.id)],limit=1)
            employee = self.env['hr.employee'].search([('userp_id','=',user_id.id)],limit=1)
            range_model = input.survey_id.as_range_age_id
            range_old = input.survey_id.as_range_old_id
            if range_model and employee:
                edad = employee.as_edad
                for line in range_model.as_range_lines:
                    if edad >= line.as_from and edad <= line.as_to:
                        input.as_total_age = input.survey_id.as_range_age_id.as_factor * line.as_value
                        input.as_point_age = line.as_value
            else:
                input.as_total_age = 0.0
                input.as_point_age = 0.0
            if range_old and employee:
                antiguedad = employee.as_anio
                for line in range_old.as_range_lines:
                    if antiguedad >= line.as_from and antiguedad <= line.as_to:
                        input.as_total_old = input.survey_id.as_range_old_id.as_factor * line.as_value
                        input.as_point_old = line.as_value
            else:
                input.as_total_old = 0.0
                input.as_point_old = 0.0
            input.as_total_survery+= input.as_total_old
            input.as_total_survery+= input.as_total_age


    as_color_id = fields.Many2one('as.survey.color', store=True,string='Color',compute='_compute_simulador')
    as_cuadrante_id = fields.Many2one('as.survey.cuadrante', store=True,string='Cuadrante',compute='_compute_simulador')
    as_total_survery = fields.Float(string='Total Obtenido', store=True, readonly=True, compute='_compute_amount_total')
    as_total_age = fields.Float(string='Edad', store=True, readonly=True, compute='_compute_amount_total')
    as_total_old = fields.Float(string='Antiguedad', store=True, readonly=True, compute='_compute_amount_total')
    as_point_age = fields.Float(string='Edad Puntos', store=True, readonly=True, compute='_compute_amount_total')
    as_point_old = fields.Float(string='Antiguedad Puntos', store=True, readonly=True, compute='_compute_amount_total')
    as_extraido = fields.Boolean(string='Obtenido')
    partner_id = fields.Many2one('res.partner', string='Partner',readonly=False)
    survey_id = fields.Many2one('survey.survey', string='Survey', required=True,readonly=False, ondelete='cascade')
    state = fields.Selection([
        ('new', 'Not started yet'),
        ('in_progress', 'In Progress'),
        ('done', 'Completed')], string='Status', default='new', readonly=False)
    email = fields.Char('Email', readonly=False)
    as_personalidad = fields.Many2one('as.personalidad', string='Personalidad')
    as_cargo_1 = fields.Many2one('as.cargo', string='Cargo')
    as_note = fields.Char(string='Observaciones')
    as_observaciones = fields.Boolean(string='Llevar observaciones a Consolidado')
    employer_id = fields.Many2one('as.survey.employer', string='Empleador')


    @api.depends('partner_id','user_input_line_ids','as_observaciones','as_cargo_1')
    def _compute_obtener_employer(self):
        for input in self:
            user_id = self.env['res.users'].search([('partner_id','=',input.partner_id.id)],limit=1)
            employee = self.env['hr.employee'].search([('userp_id','=',user_id.id)],limit=1)
            input.employer_id = employee.employer_id
        
    
    @api.depends('user_input_line_ids')
    def _compute_simulador(self):
        cuadrante = 0.0
        for input in self:
            # input.as_total_survery = 0.0
            # for line in input.user_input_line_ids:
            #     cuadrante += line.as_total
            # input.as_total_survery = cuadrante
            get_color = ("""
                SELECT
                    ascu.id,
                    ascu.as_color_id
                FROM
                    as_survey_cuadrante ascu
                WHERE
                """+str(input.as_total_survery)+""" BETWEEN ascu.as_range_start AND ascu.as_range_end
            """)
            self.env.cr.execute(get_color)
            color = False
            cuadrante = False
            for val in self.env.cr.fetchall():
                color=val[1]
                cuadrante=val[0]
            input.as_color_id = color
            input.as_cuadrante_id = cuadrante
            input._compute_obtener_employer()

class AsInputLine(models.Model):
    _inherit = "survey.user_input.line"

    as_factor = fields.Float(string="Factor %", store=True,readonly=False,compute='_compute_simulador')
    as_total = fields.Float(string="Rango",store=True,readonly=False,compute='_compute_simulador')

    @api.depends('value_numerical_box','answer_score','as_factor')
    @api.onchange('value_numerical_box','answer_score','as_factor')
    def _compute_simulador(self):
        for input in self:
            valor = 0.0
            if input.value_numerical_box > 0.0:
                valor = input.value_numerical_box
            else:
                valor = input.answer_score
            input.as_factor = input.question_id.as_factor
            input.as_total = input.as_factor* valor

    @api.model
    def _get_answer_score_values(self, vals, compute_speed_score=True):
        """ Get values for: answer_is_correct and associated answer_score.

        Requires vals to contain 'answer_type', 'question_id', and 'user_input_id'.
        Depending on 'answer_type' additional value of 'suggested_answer_id' may also be
        required.

        Calculates whether an answer_is_correct and its score based on 'answer_type' and
        corresponding question. Handles choice (answer_type == 'suggestion') questions
        separately from other question types. Each selected choice answer is handled as an
        individual answer.

        If score depends on the speed of the answer, it is adjusted as follows:
         - If the user answers in less than 2 seconds, they receive 100% of the possible points.
         - If user answers after that, they receive 50% of the possible points + the remaining
            50% scaled by the time limit and time taken to answer [i.e. a minimum of 50% of the
            possible points is given to all correct answers]

        Example of returned values:
            * {'answer_is_correct': False, 'answer_score': 0} (default)
            * {'answer_is_correct': True, 'answer_score': 2.0}
        """
        user_input_id = vals.get('user_input_id')
        answer_type = vals.get('answer_type')
        question_id = vals.get('question_id') or self.question_id
        if not question_id and not self.question_id:
            raise ValueError(_('Computing score requires a question in arguments.'))
        question = self.env['survey.question'].browse(int(question_id))

        # default and non-scored questions
        answer_is_correct = False
        answer_score = 0

        # record selected suggested choice answer_score (can be: pos, neg, or 0)
        if question.question_type in ['simple_choice', 'multiple_choice']:
            if answer_type == 'suggestion':
                suggested_answer_id = vals.get('suggested_answer_id')
                if suggested_answer_id:
                    question_answer = self.env['survey.question.answer'].browse(int(suggested_answer_id))
                    answer_score = question_answer.answer_score
                    answer_is_correct = question_answer.is_correct
        # for all other scored question cases, record question answer_score (can be: pos or 0)
        elif question.is_scored_question:
            answer = vals.get('value_%s' % answer_type)
            if answer_type == 'numerical_box':
                answer = float(answer)
            elif answer_type == 'date':
                answer = fields.Date.from_string(answer)
            elif answer_type == 'datetime':
                answer = fields.Datetime.from_string(answer)
            if answer and answer == question['answer_%s' % answer_type]:
                answer_is_correct = True
                answer_score = question.answer_score

        if compute_speed_score and answer_score > 0:
            user_input = self.env['survey.user_input'].browse(user_input_id)
            session_speed_rating = user_input.exists() and user_input.is_session_answer and user_input.survey_id.session_speed_rating
            if session_speed_rating:
                max_score_delay = 2
                time_limit = question.time_limit
                now = fields.Datetime.now()
                seconds_to_answer = (now - user_input.survey_id.session_question_start_time).total_seconds()
                question_remaining_time = time_limit - seconds_to_answer
                # if answered within the max_score_delay => leave score as is
                if question_remaining_time < 0:  # if no time left
                    answer_score /= 2
                elif seconds_to_answer > max_score_delay:
                    time_limit -= max_score_delay  # we remove the max_score_delay to have all possible values
                    score_proportion = (time_limit - seconds_to_answer) / time_limit
                    answer_score = (answer_score / 2) * (1 + score_proportion)

        return {
            'answer_is_correct': answer_is_correct,
            'answer_score': answer_score
        }
