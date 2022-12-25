from odoo import api, fields, models
from datetime import date


class AssigmentCancelWizard(models.TransientModel):
    _name = 'hr.assignment.cancel.wizard'
    _description = 'pv Cancel Assignment Wizard'

    date = fields.Datetime(string="Date Cancel", default=date.today())

    def confirm(self):
        active_id = self.env.context.get('active_id')
        assignment_id = self.env['hr.assignment.employee'].browse(active_id)
        if assignment_id:
            for line in assignment_id.pv_ids:
                line.write({
                    'cancel_date': self.date,
                    'state': 'cancel'})

            assignment_id.write({
                'state': 'canceled'
            })
