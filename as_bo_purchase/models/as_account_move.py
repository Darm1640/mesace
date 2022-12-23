from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    as_purchase_id = fields.Many2one('purchase.order', string='Compra')

    @api.model_create_multi
    def create(self, vals_list):
        rslt = super(AccountMove, self).create(vals_list)
        for inv in rslt:
            if inv.move_type == 'in_invoice':
                if inv.as_purchase_id:
                    inv.as_related_purchase_inv(inv.as_purchase_id,inv)
        return rslt

    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        for inv in self:
            ids = []
            if inv.move_type == 'in_invoice':
                if inv.as_purchase_id:
                    inv.as_related_purchase_inv(inv.as_purchase_id,inv)
        return res

    def as_related_purchase_inv(self,purchase,invoice):
        cont = 0
        for line_invoice in invoice.invoice_line_ids:
            cont += 1
            if cont < len(purchase.order_line):
                purchase.order_line[cont].invoice_lines = line_invoice
            else:
                cont-=1
                purchase.order_line[cont].invoice_lines = line_invoice
        return True

            
    # @api.onchange('as_purchase_id')
    # def _onchange_purchase_auto_complete(self):
    #     for invoice_purchase in self:
    #         if invoice_purchase.as_purchase_id:
    #             invoice_purchase._onchange_invoice_vendor_bill()
        
    #         # Copy data from PO
    #         if invoice_purchase.as_purchase_id:
    #         invoice_vals = invoice_purchase.as_purchase_id.with_company(invoice_purchase.as_purchase_id.company_id)._prepare_invoice()
    #         del invoice_vals['ref']
    #         invoice_purchase.update(invoice_vals)

    #         # Compute invoice_origin.
    #         origins = set(invoice_purchase.line_ids.mapped('purchase_line_id.order_id.name'))
    #         invoice_purchase.invoice_origin = ','.join(list(origins))

    #         # Compute ref.
    #         refs = invoice_purchase._get_invoice_reference()
    #         invoice_purchase.ref = ', '.join(refs)

    #         # Compute payment_reference.
    #         if len(refs) == 1:
    #             invoice_purchase.payment_reference = refs[0]

    #         # invoice_purchase.as_purchase_id = False
    #         invoice_purchase._onchange_currency()
    #         invoice_purchase.partner_bank_id = invoice_purchase.bank_partner_id.bank_ids and invoice_purchase.bank_partner_id.bank_ids[0]

