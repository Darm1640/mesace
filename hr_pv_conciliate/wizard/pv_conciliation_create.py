from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class WizardHrPv(models.TransientModel):
    _name = 'wizard.hr.pv'
    _description = 'wizard.hr.pv'

    event_id = fields.Many2one('hr.pv.event', 'Pv Event', required=True)
    start_date = fields.Datetime(required=True)

    def confirm(self):
        hr_pv_conciliation_id = self.env[self.env.context.get(
            'active_model')].browse(
            self.env.context.get('active_id'))
        if hr_pv_conciliation_id:
            if self.env['hr.pv.conciliation.lines'].search_count([
                ('hr_pv_conciliation_id', '=', hr_pv_conciliation_id.id),
                ('state', '!=', 'conciliate')]) > 0:
                raise ValidationError(_(
                    "All lines must be Conciliate"))
            if hr_pv_conciliation_id.different_amount == 0.0 and self.event_id:
                raise ValidationError(_(
                    "Different Amount should not be 0 in Conciliate"))
            different_amount = hr_pv_conciliation_id.different_amount
            if different_amount < 0:
                different_amount = hr_pv_conciliation_id.different_amount * -1
            if hr_pv_conciliation_id.state != 'conciliate':
                hr_pv_rec = self.env['hr.pv'].create(
                    {'conciliate_id': hr_pv_conciliation_id.id,
                     'start_date': self.start_date,
                     'type_id': self.event_id.type_id.id,
                     'subtype_id': self.event_id.subtype_id.id,
                     'code': self.event_id.code,
                     'event_id': self.event_id.id,
                     'amount': different_amount,
                     'employee_id': hr_pv_conciliation_id.employee_id.id,
                     'identification_id':
                         hr_pv_conciliation_id.employee_id.identification_id,
                     'real_start_date': self.start_date,
                     'conciliate_pv_id': hr_pv_conciliation_id.id})
                hr_pv_conciliation_id.state = 'conciliate'
                return {
                    "name": "Hr Pv",
                    "view_mode": "form",
                    "view_type": "form",
                    "res_model": "hr.pv",
                    "type": "ir.actions.act_window",
                    "res_id": hr_pv_rec.id,
                }
            '''if hr_pv_conciliation_id.state == 'conciliate':
                if not hr_pv_conciliation_id.pv_id.event_id.event_conciliate_id:
                    raise ValidationError(_(
                        "Please add Event Conciliate contraparted"))
                hr_pv_rec = self.env['hr.pv'].create(
                    {'conciliate_id': hr_pv_conciliation_id.id,
                     'start_date': self.start_date,
                     'type_id': hr_pv_conciliation_id.pv_id.event_id.event_conciliate_id.type_id.id,
                     'subtype_id': hr_pv_conciliation_id.pv_id.event_id.event_conciliate_id.subtype_id.id,
                     'code': hr_pv_conciliation_id.pv_id.event_id.event_conciliate_id.code,
                     'event_id': hr_pv_conciliation_id.pv_id.event_id.event_conciliate_id.id,
                     'employee_id': hr_pv_conciliation_id.employee_id.id,
                     'identification_id':
                     hr_pv_conciliation_id.employee_id.identification_id,
                     'real_start_date': self.start_date,
                     'amount': hr_pv_conciliation_id.summatory_amount,
                     'conciliate_pv_id': hr_pv_conciliation_id.id})
                #if hr_pv_rec:
                #    if self.event_id and not self.event_id.event_conciliate_id:
                #        hr_pv_rec.write({'event_id': self.event_id.id})
                return {
                    "name": "Hr Pv",
                    "view_mode": "form",
                    "view_type": "form",
                    "res_model": "hr.pv",
                    "type": "ir.actions.act_window",
                    "res_id": hr_pv_rec.id,
                }'''
