# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
import datetime


def get_months():
    months_choices = []
    for i in range(1, 13):
        months_choices.append((i, datetime.date(2019, i, 1).strftime('%B')))
    return months_choices


class AssignMonth(models.Model):
    _name = 'assign.month'
    _description = 'Assign Month'

    name = fields.Char(string="Name")
    active = fields.Boolean('Active', default=True)
    start_day = fields.Integer(string="Start Day")
    end_day = fields.Integer(string="End Day")
    start_month = fields.Selection([('1', 'January'),
                                    ('2', 'February'),
                                    ('3', 'March'),
                                    ('4', 'April'),
                                    ('5', 'May'),
                                    ('6', 'June'),
                                    ('7', 'July'),
                                    ('8', 'August'),
                                    ('9', 'September'),
                                    ('10', 'October'),
                                    ('11', 'November'),
                                    ('12', 'December')],
                                   string="Start Month",
                                   required=False)
    end_month = fields.Selection([('1', 'January'),
                                  ('2', 'February'),
                                  ('3', 'March'),
                                  ('4', 'April'),
                                  ('5', 'May'),
                                  ('6', 'June'),
                                  ('7', 'July'),
                                  ('8', 'August'),
                                  ('9', 'September'),
                                  ('10', 'October'),
                                  ('11', 'November'),
                                  ('12', 'December')],
                                 string="End Month",
                                 required=False)
    days_assign = fields.Integer(string="", required=False)
    type_settlement_id = fields.Many2one(comodel_name="type.settlement",
                                         string="Settlement")
