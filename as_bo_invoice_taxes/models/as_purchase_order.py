from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.addons.stock_account.tests.test_anglo_saxon_valuation_reconciliation_common import ValuationReconciliationTestCommon
from odoo.tests import Form, tagged
import logging
_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('as_tipo_retencion')
    def as_get_retencion(self):
        for purchase in self:
            if purchase.as_tipo_retencion.as_extract_purchase:
                for line in purchase.order_line:
                    line.taxes_id = purchase.as_tipo_retencion.as_taxes_ids

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('product_id')
    def as_get_product_id(self):
        for purchase_line in self:
            if purchase_line.order_id.as_tipo_retencion.as_extract_purchase:
                purchase_line.taxes_id = purchase_line.order_id.as_tipo_retencion.as_taxes_ids

    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        res = super(PurchaseOrderLine, self)._onchange_quantity()
        self.as_get_product_id()
        return res