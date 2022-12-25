# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, Warning


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    fixed = fields.Boolean(help="is this rule fixed (it can't be modified)")
    is_flex = fields.Boolean('Flex')
    autocomplete_flex = fields.Boolean(copy=False)
    accumulate = fields.Boolean('Accumulate')
    print_payslip = fields.Boolean(copy=False)
    total_cost = fields.Boolean('Total Cost')
    projection_exempt = fields.Boolean('Projection Exempt')
    prepaid_medicine_id = fields.Many2one(
        'res.partner', 'Prepaid Medicine',
        domain="[('is_prepaid_medicine', '=', True)]")
    work_days_value = fields.Char()
    use_percentage_rent = fields.Boolean()
    work_hours_value = fields.Char()
    calculate_base = fields.Boolean()
    asigned_base = fields.Selection([
        ('model', 'Model'),
        ('value', 'Value'),
        ('categ', 'Categ')], default='model')
    value = fields.Char()
    categ = fields.Char()
    model = fields.Many2one('ir.model')
    field = fields.Many2one(
        'ir.model.fields', domain="[('model_id', '=', model)]")

    def copy(self, default=None):
        """Sequence and Name while copy."""
        self.ensure_one()
        sequence = 1
        salary_rule_seq = self.env['hr.salary.rule'].search_read(
            [('sequence', '!=', False)], ['sequence'],
            order='sequence desc', limit=1)
        if salary_rule_seq:
            sequence = salary_rule_seq[0].get('sequence', '') + 1
        default = dict(default or {}, name=_(
            '%s (copy)') % self.name, sequence=sequence)
        return super(HrSalaryRule, self).copy(default)

    @api.constrains('autocomplete_flex')
    def _check_autocomplete_flex(self):
        if self.search_count([('autocomplete_flex', '=', True)]) > 1:
            raise ValidationError(_(
                "Autocomplete Flex already exist in the another record."))

    '''
    @api.constrains('sequence', 'name')
    def check_data(self):
        """No Duplication."""
        if self.sequence and self.name and \
                len(self.search([('name', '=', self.name)])) > 1:
            raise ValidationError("Salary Rule already exist!.")
    '''


class HrPayrollStructure(models.Model):
    _inherit = "hr.payroll.structure"

    categ_id = fields.Many2one('hr.payroll.structure.categ', string='Category')

    '''
    @api.model
    def create(self, vals):
        res = super(HrPayrollStructure, self).create(vals)
        if res.parent_id and res.rule_ids:
            res.check_duplicate_hr_rule()
        return res
    
    
    def write(self, vals):
        res = super(HrPayrollStructure, self).write(vals)
        if self.parent_id and self.rule_ids:
            self.check_duplicate_hr_rule()
        return res
    
    
    def check_duplicate_hr_rule(self):
        if self.parent_id and self.rule_ids:
            duplicate_ids = list(set(self.parent_id.rule_ids) & set(self.rule_ids))
            duplicate_rule_name_list = [hr_rule_id.name for hr_rule_id in duplicate_ids]
            if duplicate_rule_name_list:
                raise Warning(_("Following salary rule is duplicate either"
                                " in Salary Rules or Parent Salary Rules!"
                                "\n %s") % duplicate_rule_name_list)
    '''


class HrPayrollStructureCateg(models.Model):
    _name = "hr.payroll.structure.categ"
    _description = 'HR Payroll Structure Categ'

    name = fields.Char(required=True)
    description = fields.Text()
