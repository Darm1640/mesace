from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrPvConciliation(models.Model):
    """Hr Pv Conciliation."""

    _name = "hr.pv.conciliation"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Hr Pv Conciliation"

    @api.depends('line_ids', 'line_ids.amount')
    def _calculate_summatory_amount(self):
        for rec in self:
            amount = 0.0
            if amount == 0 and not rec.pv_id:
                amount = rec.summatory_amount or 0.0
            for line in rec.line_ids:
                amount += line.amount
            rec.summatory_amount = amount

    @api.depends('pv_ids', 'pv_ids.amount')
    def _balance_to_conciliate(self):
        for rec in self:
            amount = 0.0
            for line in rec.pv_ids:
                amount += (
                            line.amount * -1) if line.event_id.exploitation or line.event_id.employee_balance else line.amount
            if amount == 0 and not rec.pv_id:
                amount = rec.balance_to_conciliate or 0.0
            rec.balance_to_conciliate = rec.amount_paid - amount

    @api.depends('amount_paid', 'summatory_amount')
    def _calculate_different_amount(self):
        for rec in self:
            rec.different_amount = rec.amount_paid - rec.summatory_amount

    name = fields.Char(copy=False, default=lambda self: _('New'),
                       tracking=True)
    employee_id = fields.Many2one('hr.employee', tracking=True)
    employee_active = fields.Boolean(related='employee_id.active')
    pv_id = fields.Many2one(
        'hr.pv',
        domain="[('is_leave_calculate','=', True), \
                ('employee_id','=', employee_id), \
                ('conciliate_id','=', None), \
                ('state', 'in', ['approved', 'processed'])]",
        tracking=True)
    partner_con_id = fields.Many2one('res.partner',
                                     related='pv_id.partner_con_id', store=True, tracking=True)
    amount_paid = fields.Float(
        related='pv_id.value_leave', store=True, tracking=True)
    summatory_amount = fields.Float(
        compute='_calculate_summatory_amount', store=True, tracking=True)
    balance_to_conciliate = fields.Float(
        compute='_balance_to_conciliate', store=True, tracking=True)
    different_amount = fields.Float(
        compute='_calculate_different_amount', store=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('conciliate', 'Conciliate'),
        ('reject', 'Reject'),
        ('tramited', 'Tramited')], string='Status', copy=False,
        default='draft', tracking=True)
    line_ids = fields.One2many(
        'hr.pv.conciliation.lines', 'hr_pv_conciliation_id')
    pv_ids = fields.One2many('hr.pv', 'conciliate_pv_id')
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company)
    center_cost_id = fields.Many2one('account.analytic.account', string='Center Cost')

    @api.onchange('pv_id')
    def check_conciliates_pvs(self):
        conciliate_id = self.search([('pv_id', '=', self.pv_id.id)])
        if conciliate_id and self.pv_id:
            raise ValidationError(_('Already exist another conciliate for this PV'))

    @api.model
    def create(self, vals):
        """Sequence Add."""
        res = super(HrPvConciliation, self).create(vals)
        if vals.get('name', _('New')) == _('New'):
            res.name = self.env['ir.sequence'].next_by_code(
                'hr.pv.conciliation') or _('New')
        if vals['pv_id']:
            pv_id = self.env['hr.pv'].search([('id', '=', vals['pv_id'])])
            pv_id.write({'conciliate_id': res.id})
        return res

    def unlink(self):
        """Delete Validation."""
        for item in self:
            if item.pv_ids:
                raise ValidationError(
                    _(
                        "You cannot delete the record because there are PVs"
                    ))
        return super(HrPvConciliation, self).unlink()

    def action_reject(self):
        """Move state to Reject."""
        for rec in self:
            rec.state = 'reject'

    def action_in_progress(self):
        """Move state to Reject."""
        for rec in self:
            rec.state = 'in_progress'

    def action_conciliate(self):
        """Move state to Conciliate."""
        for rec in self:
            if self.env['hr.pv.conciliation.lines'].search_count([
                ('hr_pv_conciliation_id', '=', rec.id),
                ('state', '!=', 'conciliate')]) > 0:
                raise ValidationError(_(
                    "All lines must be Conciliate"))
            rec.state = 'conciliate'


class HrPvConciliationLine(models.Model):
    """Hr Pv Conciliation Line."""

    _name = "hr.pv.conciliation.lines"

    date_process = fields.Date(required=False)
    amount = fields.Float(required=True)
    hr_pv_conciliation_id = fields.Many2one('hr.pv.conciliation')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('conciliate', 'Conciliate')], string='Status', copy=False,
        default='draft')
    pv_id = fields.Many2one('hr.pv', 'Pv')

    def action_cancel(self):
        """Cancel the line and remove the reference of PV."""
        for rec in self:
            rec.state = 'draft'
            if rec.pv_id:
                rec.pv_id = False

    def action_conciliate_line(self):
        hr_pv_conciliation_line_id = self
        hr_pv_conciliation_id = hr_pv_conciliation_line_id.hr_pv_conciliation_id
        if hr_pv_conciliation_id:
            different_amount = hr_pv_conciliation_id.different_amount
            if hr_pv_conciliation_id.state != 'conciliate':
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
                return {
                    "name": "Hr Pv",
                    "view_mode": "form",
                    "view_type": "form",
                    "res_model": "hr.pv",
                    "type": "ir.actions.act_window",
                    "res_id": hr_pv_rec.id,
                }
