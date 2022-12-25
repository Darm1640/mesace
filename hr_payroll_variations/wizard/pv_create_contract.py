# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class pvCreateContract(models.TransientModel):
    _name = 'pv.create.contract'
    _description = 'pv Create Contract'

    @api.model
    def default_get(self, lst_fields):
        """Add wage_assign and Fix_wage_assing."""
        result = super(pvCreateContract, self).default_get(lst_fields)
        active_id = self.env.context.get('active_id')
        pv_id = self.env['hr.pv'].browse(active_id)
        if pv_id.wage_assign:
            result['wage_assign'] = pv_id.wage_assign
        if pv_id.Fix_wage_assing:
            result['Fix_wage_assing'] = pv_id.Fix_wage_assing
        struct_id = self.env['hr.payroll.structure'].search([
            ('type_id.name', '=', 'Nuevo Flex')], limit=1)
        if struct_id:
            result['struct_id'] = struct_id.id
        return result

    struct_id = fields.Many2one('hr.payroll.structure', 'Salary Structures')
    wage_assign = fields.Float()
    Fix_wage_assing = fields.Float()

    @api.constrains('wage_assign', 'Fix_wage_assing')
    def _check_wage(self):
        if self.wage_assign <= 0.0:
            raise ValidationError(_('Wage Assign should be positive.'))
        if self.Fix_wage_assing <= 0.0:
            raise ValidationError(_('Fix Wage Assign should be positive.'))

    
    def confirm(self):
        """Create Contract."""
        active_id = self.env.context.get('active_id')
        pv_id = self.env['hr.pv'].browse(active_id)
        if self.struct_id and self.wage_assign and self.Fix_wage_assing and\
           pv_id.employee_id:
            contract = self.env['hr.contract'].with_context(
                from_pv=True).create({
                    'name': pv_id.employee_id.name + ' Contract',
                    'employee_id': pv_id.employee_id.id,
                    'date_start': fields.Date.today(),
                    'wage': self.wage_assign,
                    'fix_wage_amount': self.Fix_wage_assing,
                    'struct_id': self.struct_id.id,
                    'recruitment_reason_id':
                    pv_id.recruitment_reason_id.id})
            # struct_id = self.env['hr.payroll.structure'].search([
            #     ('type_id.name', '=', 'Nuevo Flex')], limit=1)
            # if struct_id:
            # contract.write({'struct_id': struct_id.id})
            contract.onchange_struct_id()
            contract.onchange_fix_wage_amount()
            contract._onchange_employee_id()
            pv_id.write({
                'contract_id': contract.id})
