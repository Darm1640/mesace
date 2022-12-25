# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round, float_compare

from itertools import groupby

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.constrains('product_id', 'product_tmpl_id', 'bom_line_ids')
    def _check_bom_lines(self):
        print ('--New Constrain')
        for bom in self:
            for bom_line in bom.bom_line_ids:
                # if bom.product_id:
                #     same_product = bom.product_id == bom_line.product_id
                # else:
                #     same_product = bom.product_tmpl_id == bom_line.product_id.product_tmpl_id
                # if same_product:
                #     raise ValidationError(_("BoM line product %s should not be the same as BoM product.") % bom.display_name)
                if bom.product_id and bom_line.bom_product_template_attribute_value_ids:
                    raise ValidationError(
                        _("BoM cannot concern product %s and have a line with attributes (%s) at the same time.")
                        % (bom.product_id.display_name, ", ".join(
                            [ptav.display_name for ptav in bom_line.bom_product_template_attribute_value_ids])))
                for ptav in bom_line.bom_product_template_attribute_value_ids:
                    if ptav.product_tmpl_id != bom.product_tmpl_id:
                        raise ValidationError(
                            _("The attribute value %s set on product %s does not match the BoM product %s.") %
                            (ptav.display_name, ptav.product_tmpl_id.display_name,
                             bom_line.parent_product_tmpl_id.display_name)
                        )

class StockMove(models.Model):
    _inherit = "stock.move"
    
    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, description):
        # This method returns a dictionary to provide an easy extension hook to modify the valuation lines (see purchase for an example)
        self.ensure_one()
        debit_account = False
        if self.picking_type_id.code == 'outgoing':
            debit_account = self.product_id.categ_id.x_alternativa.id or debit_account_id
        else:
            debit_account = debit_account_id
        debit_line_vals = {
            'name': description,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': description,
            'partner_id': partner_id,
            'debit': debit_value if debit_value > 0 else 0,
            'credit': -debit_value if debit_value < 0 else 0,
            'account_id': debit_account,
        }
        
        credit_line_vals = {
            'name': description,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': description,
            'partner_id': partner_id,
            'credit': credit_value if credit_value > 0 else 0,
            'debit': -credit_value if credit_value < 0 else 0,
            'account_id': credit_account_id,
        }

        rslt = {'credit_line_vals': credit_line_vals, 'debit_line_vals': debit_line_vals}
        if credit_value != debit_value:
            # for supplier returns of product in average costing method, in anglo saxon mode
            diff_amount = debit_value - credit_value
            price_diff_account = self.product_id.property_account_creditor_price_difference

            if not price_diff_account:
                price_diff_account = self.product_id.categ_id.property_account_creditor_price_difference_categ
            if not price_diff_account:
                raise UserError(_('Configuration error. Please configure the price difference account on the product or its category to process this operation.'))

            rslt['price_diff_line_vals'] = {
                'name': self.name,
                'product_id': self.product_id.id,
                'quantity': qty,
                'product_uom_id': self.product_id.uom_id.id,
                'ref': description,
                'partner_id': partner_id,
                'credit': diff_amount > 0 and diff_amount or 0,
                'debit': diff_amount < 0 and -diff_amount or 0,
                'account_id': price_diff_account.id,
            }
        return rslt