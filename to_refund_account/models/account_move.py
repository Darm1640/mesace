from odoo import models

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _reverse_move_vals(self, default_values, cancel=False):
        res = super(AccountMove, self)._reverse_move_vals(default_values, cancel)
        move_type = self.move_type
        for line in res.get('line_ids', []):
            product_id = line[2].get('product_id', False)
            if not product_id:
                continue
            else:
                product = self.env['product.product'].browse(product_id)
                accounts = product.product_tmpl_id._get_product_accounts()
                income_refund_acc = accounts['income_refund']
                expense_refund_acc = accounts['expense_refund']

            if  move_type == 'out_invoice' and income_refund_acc:
                line[2]['account_id'] = income_refund_acc.id
            elif move_type == 'in_invoice' and expense_refund_acc:
                line[2]['account_id'] = expense_refund_acc.id
        return res
