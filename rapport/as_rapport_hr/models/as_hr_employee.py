# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class AsEmployee(models.Model):
    _inherit = "hr.employee"
    
    # def _get_employer(self):
    #     employer = []
    #     for employee in self:
    #         for contract in employee.contract_ids:
    #             employer.append(contract.employer_id.id)
    #         employee.employer_ids = employer
    # employer_ids = fields.Many2many('as.survey.employer', string='Empleadores', readonly=True,compute='_get_employer')

    as_subgerente_id = fields.Many2one('hr.employee',string="Sub Gerente")
    as_date_start = fields.Date(string='Fecha inicio empresa', default=fields.Datetime.now)
    as_edad = fields.Integer(string='Edad')
    as_anio = fields.Integer(string='Años Antiguedad Cargo')
    as_mes = fields.Integer(string='Meses Antiguedad Cargo')
    as_dias = fields.Integer(string='Dias Antiguedad Cargo')
    userp_id = fields.Many2one('res.users', string='Usuario Encuesta')
    user_id = fields.Many2one('res.users', 'Usuario', store=True)
    employer_id = fields.Many2one('as.survey.employer', string='Empleador')

    @api.onchange('as_date_start')
    def _compute_contract_id(self):
        if self.as_date_start:
            tiempo = fields.Date.context_today(self) - self.as_date_start
            self.as_mes = int((tiempo.days/30/12 - int(tiempo.days/30/12))*12)
            self.as_dias = int((tiempo.days/30/12 - int(tiempo.days/30/12))*30)
            if int(tiempo.days/30/12) >= 1:
                self.as_anio = int(tiempo.days/30/12)
            else:
                self.as_anio = 0


    @api.onchange('birthday')
    def as_get_date_birthday(self):
        if self.birthday:
            edad = self.birthday-fields.Date.context_today(self)
            self.as_edad = (edad.days/365)*-1


class AsResUsers(models.Model):
    _inherit = "res.users"

    @api.model_create_multi
    def create(self, vals_list):
        users = super(AsResUsers, self).create(vals_list)
        employee = self.env['hr.employee'].create({
            'name': vals_list[0]['name'],
            'user_id': users.id,
            'userp_id': users.id,
        })
        return users

class HrPartner(models.Model):
    _inherit = "hr.employee.public"

    as_subgerente_id = fields.Many2one('hr.employee',string="Sub Gerente")
    as_date_start = fields.Date(string='Fecha inicio empresa', default=fields.Datetime.now)
    as_edad = fields.Integer(string='Edad')
    as_anio = fields.Integer(string='Años Antiguedad Cargo')
    as_mes = fields.Integer(string='Meses Antiguedad Cargo')
    as_dias = fields.Integer(string='Dias Antiguedad Cargo')
    userp_id = fields.Many2one('res.users', string='Usuario Encuesta')

