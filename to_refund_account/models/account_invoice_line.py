from odoo import models

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def get_invoice_line_account(self, move_type, product_id, fiscal_position_id, company_id):
        accounts = product_id.product_tmpl_id.get_product_accountsmove_id(fiscal_position_id)
        if move_type == 'out_refund' and accounts['income_refund']:
            return accounts['income_refund']
        elif move_type == 'in_refund' and accounts['expense_refund']:
            return accounts['expense_refund']

        return super(AccountMoveLine, self).get_invoice_line_account(move_type, product_id, fiscal_position_id, company_id)
