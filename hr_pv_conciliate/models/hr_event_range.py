from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrEventRange(models.Model):
    """Hr Event Range."""

    _name = "hr.event.range"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Hr Event Range"

    name = fields.Char(copy=False, tracking=True)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done'), (
        'close', 'Close')], string='Status', copy=False,
                             default='draft', tracking=True)
    line_ids = fields.One2many('hr.event.range.lines', 'range_id')

    def action_done(self):
        """Move State."""
        for rec in self:
            rec.state = 'done'

    def action_draft(self):
        """Move State."""
        for rec in self:
            rec.state = 'draft'

    def action_close(self):
        """Move State."""
        for rec in self:
            rec.state = 'close'


class HrEventRangeLines(models.Model):
    """Hr Event Range Lines."""

    _name = "hr.event.range.lines"
    _description = "Hr Event Range Lines"

    min_days = fields.Integer()
    max_days = fields.Integer()
    percentage = fields.Float()
    range_id = fields.Many2one('hr.event.range')

    @api.constrains('range_id', 'min_days', 'max_days')
    def _check_range_id_min_days_max_days(self):
        for rec in self:
            if rec.range_id and rec.min_days and rec.max_days:
                if rec.search_count(
                        [('range_id', '=', rec.range_id.id),
                         ('min_days', '<=', rec.max_days),
                         ('max_days', '>=', rec.min_days)]) > 1:
                    raise ValidationError(_(
                        "Min days and Max days overwrite."))

    @api.constrains('min_days', 'max_days')
    def _check_min_days_max_days(self):
        for rec in self:
            if rec.min_days and rec.max_days:
                if rec.min_days > rec.max_days:
                    raise ValidationError(_(
                        "The Min Days not better Max Days."))
