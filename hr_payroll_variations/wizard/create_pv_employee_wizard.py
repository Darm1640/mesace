from odoo import api, fields, models, _


class CreatePv(models.TransientModel):
    _name = 'hr.create.pv.wizard'
    _description = 'Create PV Wizard'

    employee_id = fields.Many2one('hr.employee', required=True)

    def confirm(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Create Pv'),
                'res_model': 'hr.pv',
                'target': 'new',
                'view_id': self.env.ref('hr_payroll_variations.view_hr_pv_form').id,
                'view_mode': 'form',
                'context': {'default_employee_id': self.employee_id.id,'state':'draft'}
                }
