from odoo import fields, models


class MrpWorkcenter(models.Model):

    _inherit = "mrp.workcenter"

    service_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Service product",
        domain=[("type", "=", "service")],
        help="Add a priced service product here to calculate operation costs",
    )
