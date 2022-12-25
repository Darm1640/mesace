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


class TypeSettlement(models.Model):
    _name = 'type.settlement'
    _description = 'Type Settlement'

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
    pay_type = fields.Selection(string="Type",
                                selection=[('annual', 'Annual'),
                                           ('biannual', 'Biannual')],
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
    days_assign = fields.Integer(string="Days", required=False)
    assign_month_ids = fields.One2many(comodel_name="assign.month",
                                       inverse_name="type_settlement_id",
                                       string="Assign Month", required=False)
