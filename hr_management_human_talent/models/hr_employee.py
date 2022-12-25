from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    beneficiary_line_id = fields.One2many('beneficiary', 'employee_id', tracking=True)
    history_promotion_ids = fields.One2many('hr.history.promotion', 'employee_id')
    history_extend_ids = fields.One2many('hr.history.extend', 'employee_id')

    """Smart Buttons"""
    labor_relation_count = fields.Integer(compute='compute_count')
    request_new_count = fields.Integer(compute='compute_request_new')

    def get_labor_relations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Disciplinary Proceedings',
            'view_mode': 'tree,form',
            'res_model': 'hr.labor.relation',
            'domain': [('employee_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def compute_count(self):
        for record in self:
            record.labor_relation_count = self.env['hr.labor.relation'].search_count([('employee_id', '=', self.id)])

    def get_request_news(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Request for news',
            'view_mode': 'tree,form',
            'res_model': 'hr.request.for.news',
            'domain': [('employee_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def compute_request_new(self):
        for record in self:
            record.request_new_count = self.env['hr.request.for.news'].search_count([('employee_id', '=', self.id)])


class HistoryPromotion(models.Model):
    _name = 'hr.history.promotion'
    _description = 'History promotion from request news'
    _rec_name = 'employee_id'

    _order = 'start_date desc'

    company_id = fields.Many2one('res.company', string='Company', change_default=True,
                                 default=lambda self: self.env.company)
    employee_id = fields.Many2one('hr.employee')
    position_id = fields.Many2one('hr.job', string='Position')
    start_date = fields.Date('Start date')
    end_date = fields.Date('End date')
    salary = fields.Float('Salary')


class HistoryExtend(models.Model):
    _name = 'hr.history.extend'

    company_id = fields.Many2one('res.company', string='Company', change_default=True,
                                 default=lambda self: self.env.company)

    employee_id = fields.Many2one('hr.employee', string='Employee')
    contract_id = fields.Many2one('hr.contract', string='Contract')
    start_date = fields.Date('Start date')
    end_date = fields.Date('End date')
    number_extend = fields.Integer('Extend number')
    duration_year = fields.Integer('Duration in years')
    duration_month = fields.Integer('Duration in months')
    duration_day = fields.Integer('Durations in days')


class TipoCotizante(models.Model):
    _name = 'tipo.cotizante'
    _description = 'Type Cotizante'

    name = fields.Char(index=True)
    code = fields.Char(strin="Code")

    has_eps = fields.Boolean()
    eps_rate = fields.Float()
    has_afp = fields.Boolean()
    pension_rate = fields.Float()
    eps_rate = fields.Float()
    has_ccf = fields.Boolean()
    ccf_rate = fields.Float()


class SubTipoCotizante(models.Model):
    _name = 'subtipo.cotizante'
    _description = 'SubType Cotizante'

    name = fields.Char()
    code = fields.Char(string="Code")
