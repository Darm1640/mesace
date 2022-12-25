from odoo import fields, models
import odoo.addons.decimal_precision as dp


class MrpRoutingWorkcenter(models.Model):

    _inherit = "mrp.routing.workcenter"

    operation_cost = fields.Float(
        string="Operation cost",
        digits=dp.get_precision("Product Price"),
        compute="_compute_operation_cost",
        group_operator="sum",
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        default=lambda self: self.env.user.company_id.currency_id.id,
    )

    def _compute_operation_cost(self):
        for record in self:
            service_product = record.workcenter_id.service_product_id

            operation_cost = 0
            if service_product:
                service_cost = service_product.standard_price
                operation_duration = record.time_cycle_manual

                operation_cost = service_cost * operation_duration / 60

            record.operation_cost = operation_cost
