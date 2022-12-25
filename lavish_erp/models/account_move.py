from email.policy import default
from odoo import models, fields,api


class AccountMove(models.Model):
    _inherit = "account.move"
    
    rt_enable = fields.Boolean("Auto Rete", default=True)
    
    def action_post(self):
        res = super().action_post()
        if not self.rt_enable:
            return res
        self.calculate_rtefte()

    def calculate_rtefte(self):
        """
        Unlinks ReteFuente taxes from account invoice line if the sum of lines with same retefuente tax is not greater than min base
        """
        self.ensure_one()
        rtefte_taxes = self.invoice_line_ids.mapped('tax_ids').filtered('retefuente')
        for tax in rtefte_taxes:
            lines = self.invoice_line_ids.filtered(lambda l: tax.id in l.tax_ids.ids)
            subtotal = sum(lines.mapped('price_subtotal'))
            if subtotal < tax.min_base:
                [line.write({'tax_ids': [(3, tax.id, 0)]}) for line in lines]
            else: pass

        return True  
    

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # def _get_computed_taxes(self):
    #     #self.ensure_one()
    #     tax_ids = False
    #     if self.move_id.is_sale_document(include_receipts=True):
    #             # Out invoice.
    #         if self.product_id.categ_id.taxes_ids :
    #             tax_ids = self.product_id.categ_id.taxes_ids.filtered(lambda tax: tax.company_id == self.move_id.company_id) + self.product_id.taxes_id.filtered(lambda tax: tax.company_id == self.move_id.company_id)
    #         elif self.product_id.supplier_taxes_id:
    #             tax_ids = self.product_id.taxes_id.filtered(lambda tax: tax.company_id == self.move_id.company_id)
    #         elif self.account_id.tax_ids:
    #             tax_ids = self.account_id.tax_ids
    #         else:
    #             tax_ids = self.env['account.tax']
    #         if not tax_ids and not self.exclude_from_invoice_tab:
    #             tax_ids = self.move_id.company_id.account_sale_tax_id
    #     elif self.move_id.is_purchase_document(include_receipts=True):
    #             # In invoice.
    #         if self.product_id.categ_id.supplier_taxes_ids:
    #             tax_ids = self.product_id.categ_id.supplier_taxes_ids.filtered(lambda tax: tax.company_id == self.move_id.company_id) + self.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == self.move_id.company_id) +  self.partner_id.supplier_taxes_ids.filtered(lambda tax: tax.company_id == self.move_id.company_id)
    #             # tax_ids = self.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == self.move_id.company_id)
    #         elif self.product_id.supplier_taxes_id:
    #             tax_ids = self.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == self.move_id.company_id)
    #         elif self.partner_id:
    #             tax_ids = self.partner_id.supplier_taxes_ids.filtered(lambda tax: tax.company_id == self.move_id.company_id)
    #         elif self.account_id.tax_ids:
    #             tax_ids = self.account_id.tax_ids
    #         else:
    #             tax_ids = self.env['account.tax']
    #         if not tax_ids and not self.exclude_from_invoice_tab:
    #             tax_ids = self.move_id.company_id.account_purchase_tax_id
    #     else:
    #         # Miscellaneous operation.
    #         tax_ids = self.account_id.tax_ids

    #     if self.company_id and tax_ids:
    #         tax_ids = tax_ids.filtered(lambda tax: tax.company_id == self.company_id)

            
    #     return tax_ids