# -*- coding: utf-8 -*-


from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, Warning

PARTNER_TYPES = [
    ('employee', 'Employee'),
    ('layoffs', 'Found Layoffs'),
    ('eps', 'EPS'),
    ('afp', 'AFP'),
    ('unemployment', 'Unemployment Fund'),
    ('arl', 'ARL'),
    ('pre_medicine', 'Prepaid Medicine'),
    ('pre_medicine2', 'Prepaid Medicine 2'),
    ('afc', 'AFC'),
    ('compensation', 'Compensation'),
    ('voluntary', 'Voluntary Contribution'),
    ('voluntary2', 'Voluntary Contribution 2')
]


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    partner_type = fields.Selection(selection=PARTNER_TYPES, string='Accounting partner')

#
