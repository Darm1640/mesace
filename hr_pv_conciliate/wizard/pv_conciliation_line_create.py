from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class WizardHrPvLine(models.TransientModel):
    _name = 'wizard.hr.pv.line'
    _description = 'wizard.hr.pv.line'

    event_id = fields.Many2one('hr.pv.event', 'Pv Event')

    def confirm(self):
        hr_pv_conciliation_line_id = self.env[self.env.context.get(
            'active_model')].browse(
            self.env.context.get('active_id'))
        hr_pv_conciliation_id = hr_pv_conciliation_line_id.hr_pv_conciliation_id
        if hr_pv_conciliation_id:
            if hr_pv_conciliation_id.different_amount == 0.0 and self.event_id:
                raise ValidationError(_(
                    "Different Amount should not be 0 in Conciliate"))
            different_amount = hr_pv_conciliation_id.different_amount
            if different_amount < 0:
                different_amount = hr_pv_conciliation_id.different_amount * -1
            if hr_pv_conciliation_id.state != 'conciliate':
                hr_pv_rec = self.env['hr.pv'].create(
                    {'conciliate_id': hr_pv_conciliation_id.id,
                     'start_date': hr_pv_conciliation_line_id.date_process,
                     'type_id': self.event_id.type_id.id,
                     'subtype_id': self.event_id.subtype_id.id,
                     'code': self.event_id.code,
                     'event_id': self.event_id.id,
                     'amount': different_amount,
                     'employee_id': hr_pv_conciliation_id.employee_id.id,
                     'identification_id':
                         hr_pv_conciliation_id.employee_id.identification_id,
                     'real_start_date': hr_pv_conciliation_line_id.date_process,
                     'conciliate_pv_id': hr_pv_conciliation_id.id})
                hr_pv_conciliation_line_id.write({
                    'pv_id': hr_pv_rec.id, 'state': 'conciliate'})
                return {
                    "name": "Hr Pv",
                    "view_mode": "form",
                    "view_type": "form",
                    "res_model": "hr.pv",
                    "type": "ir.actions.act_window",
                    "res_id": hr_pv_rec.id,
                }
            if hr_pv_conciliation_id.state == 'conciliate':
                if not hr_pv_conciliation_id.pv_id.event_id.event_conciliate_id:
                    raise ValidationError(_(
                        "Please add Event Conciliate contraparted"))
                hr_pv_rec = self.env['hr.pv'].create(
                    {'conciliate_id': hr_pv_conciliation_id.id,
                     'start_date': hr_pv_conciliation_line_id.date_process,
                     'type_id': hr_pv_conciliation_id.pv_id.event_id.event_conciliate_id.type_id.id,
                     'subtype_id': hr_pv_conciliation_id.pv_id.event_id.event_conciliate_id.subtype_id.id,
                     'code': hr_pv_conciliation_id.pv_id.event_id.event_conciliate_id.code,
                     'event_id': hr_pv_conciliation_id.pv_id.event_id.event_conciliate_id.id,
                     'employee_id': hr_pv_conciliation_id.employee_id.id,
                     'identification_id':
                         hr_pv_conciliation_id.employee_id.identification_id,
                     'real_start_date': hr_pv_conciliation_line_id.date_process,
                     'amount': hr_pv_conciliation_id.summatory_amount,
                     'conciliate_pv_id': hr_pv_conciliation_id.id})
                hr_pv_conciliation_line_id.write({
                    'pv_id': hr_pv_rec.id, 'state': 'conciliate'})
                # if hr_pv_rec:
                #    if self.event_id and not self.event_id.event_conciliate_id:
                #        hr_pv_rec.write({'event_id': self.event_id.id})
                return {
                    "name": "Hr Pv",
                    "view_mode": "form",
                    "view_type": "form",
                    "res_model": "hr.pv",
                    "type": "ir.actions.act_window",
                    "res_id": hr_pv_rec.id,
                }
