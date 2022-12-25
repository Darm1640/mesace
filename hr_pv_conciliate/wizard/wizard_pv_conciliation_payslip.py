from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class WizardPvConciliationPayslip(models.TransientModel):
    _name = 'wizard.pv.conciliation.payslip'
    _description = 'wizard.pv.conciliation.payslip'

    date_from = fields.Date()
    date_to = fields.Date()
    struct_id = fields.Many2one('hr.payroll.structure', 'Salary Structure')

    def confirm(self):
        hr_pv_conciliation_id = self.env[self.env.context.get(
            'active_model')].browse(
            self.env.context.get('active_id'))
        if hr_pv_conciliation_id:
            hr_contract_rec = self.env['hr.contract'].create({
                'name': hr_pv_conciliation_id.employee_id.display_name +
                        ' Contract',
                'employee_id': hr_pv_conciliation_id.employee_id.id,
                'date_start': self.date_from,
                'date_end': self.date_to,
                'wage': hr_pv_conciliation_id.summatory_amount,
                'struct_id': self.struct_id.id,
                'state': 'open'})
            payslip = self.env['hr.payslip'].with_context({
                'contract_completion': True}).create({
                'employee_id': hr_contract_rec.employee_id.id,
                'date_from': hr_contract_rec.date_start,
                'date_to': hr_contract_rec.date_end,
                'name':
                    "Contract Completion for %s" % hr_pv_conciliation_id.employee_id.name,
                'contract_id': hr_contract_rec.id,
            })
            payslip._onchange_employee()
            hr_contract_rec.write({'state': 'close'})
