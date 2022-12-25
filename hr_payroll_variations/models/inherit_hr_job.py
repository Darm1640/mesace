from odoo import api, fields, models


class HrJob(models.Model):
    _inherit = 'hr.job'

    position_wage = fields.Float('Position wage')
    monetization_sena_id = fields.Many2one(comodel_name='hr.employee.sena', string='Monetization Sena', required=False)
