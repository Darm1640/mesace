from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class SaleOrderCampos(models.Model):
    _inherit = 'project.project'

    @api.constrains('sale_line_id', 'pricing_type')
    def _check_sale_line_type(self):
        for project in self:
            if project.pricing_type == 'fixed_rate':
                # if project.sale_line_id and not project.sale_line_id.is_service:
                #     raise ValidationError(_("A billable project should be linked to a Sales Order Item having a Service product."))
                if project.sale_line_id and project.sale_line_id.is_expense:
                    raise ValidationError(_("A billable project should be linked to a Sales Order Item that does not come from an expense or a vendor bill."))