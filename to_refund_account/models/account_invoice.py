from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def _refund_cleanup_lines(self, lines):
        """ consider different accounts for refund invoices

            :param recordset lines: records to convert
            :return: list of command tuple for one2many line creation [(0, 0, dict of valueis), ...]
        """

        inv_type = self._context.get('move_type', self.move_type)
        result = super(AccountMove, self)._refund_cleanup_lines(lines)
        Product = self.env['product.product']

        if lines._name == 'account.move.line':
            for line in result:
                if 'product_id' not in line[2]:
                    continue

                if line[2]['product_id']:
                    product_id = Product.browse(line[2]['product_id'])
                    accounts = product_id.product_tmpl_id.get_product_accounts()
                    income_refund_acc = accounts['income_refund']
                    expense_refund_acc = accounts['expense_refund']

                else:
                    move_id = False
                    if line[2]['move_id']:
                        move_id = self.browse(line[2]['move_id'])
                    else:
                        move_id = self

                    income_refund_acc = move_id.journal_id.default_account_id
                    expense_refund_acc = move_id.journal_id.default_account_id

                if inv_type == 'out_invoice' and income_refund_acc:
                    line[2]['account_id'] = income_refund_acc.id
                elif inv_type == 'in_invoice' and expense_refund_acc:
                    line[2]['account_id'] = expense_refund_acc.id

        return result
