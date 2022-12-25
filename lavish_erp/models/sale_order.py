from odoo import api, models, fields

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    rt_enable = fields.Boolean("Auto Rete", default=True)
   

    def calculate_rtefte(self):
        """
        Unlinks ReteFuente taxes from account invoice line if the sum of lines with same retefuente tax is not greater than min base
        """
        self.ensure_one()
        rtefte_taxes = self.order_line.mapped('taxes_id').filtered('retefuente')
        for tax in rtefte_taxes:
            lines = self.order_line.filtered(lambda l: tax.id in l.taxes_id.ids)
            subtotal = sum(lines.mapped('price_subtotal'))
            if subtotal < tax.min_base:
                [line.write({'taxes_id': [(3, tax.id, 0)]}) for line in lines]
            else: pass

        return True  
class PurchaseOrder(models.Model):
    _inherit = "purchase.order"


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    # @api.model
    # def _prepare_purchase_order_line(self, product_id, partner_id, product_qty, product_uom, company_id, supplier, po):
    #     partner = supplier.name
    #     uom_po_qty = product_uom._compute_quantity(product_qty, product_id.uom_po_id)
    #     # _select_seller is used if the supplier have different price depending
    #     # the quantities ordered.
    #     seller = product_id.with_company(company_id)._select_seller(
    #         partner_id=partner,
    #         quantity=uom_po_qty,
    #         date=po.date_order and po.date_order.date(),
    #         uom_id=product_id.uom_po_id)
    #     if self.product_id.supplier_taxes_id:
    #         product_taxes = product_id.supplier_taxes_id.filtered(lambda x: x.company_id.id == company_id.id) + product_id.categ_id.supplier_taxes_ids.filtered(lambda x: x.company_id.id == company_id.id) +  partner_id.supplier_taxes_ids.filtered(lambda tax: tax.company_id == self.order_id.company_id)
    #     elif self.partner_id.is_ica:
    #         product_taxes = partner_id.supplier_taxes_ids.filtered(lambda tax: tax.company_id == self.order_id.company_id)
    #     elif self.product_id.categ_id.supplier_taxes_ids:
    #         product_taxes = product_id.categ_id.supplier_taxes_ids.filtered(lambda x: x.company_id.id == company_id.id)
    #     taxes = po.fiscal_position_id.map_tax(product_taxes)

    #     price_unit = self.env['account.tax']._fix_tax_included_price_company(
    #         seller.price, product_taxes, taxes, company_id) if seller else 0.0
    #     if price_unit and seller and po.currency_id and seller.currency_id != po.currency_id:
    #         price_unit = seller.currency_id._convert(
    #             price_unit, po.currency_id, po.company_id, po.date_order or fields.Date.today())

    #     product_lang = product_id.with_prefetch().with_context(
    #         lang=partner.lang,
    #         partner_id=partner.id,
    #     )
    #     name = product_lang.with_context(seller_id=seller.id).display_name
    #     if product_lang.description_purchase:
    #         name += '\n' + product_lang.description_purchase

    #     date_planned = self.order_id.date_planned or self._get_date_planned(seller, po=po)

    #     return {
    #         'name': name,
    #         'product_qty': uom_po_qty,
    #         'product_id': product_id.id,
    #         'product_uom': product_id.uom_po_id.id,
    #         'price_unit': price_unit,
    #         'date_planned': date_planned,
    #         'taxes_id': [(6, 0, taxes.ids)],
    #         'order_id': po.id,
    #     }
        
    # def _compute_tax_id(self):
    #     taxes = " "
    #     for line in self:
    #         line = line.with_company(line.company_id)
    #         fpos = line.order_id.fiscal_position_id or line.order_id.fiscal_position_id.get_fiscal_position(line.order_id.partner_id.id)
    #         # filter taxes by company
    #         if self.product_id.supplier_taxes_id:
    #             taxes = line.product_id.supplier_taxes_id.filtered(lambda r: r.company_id == line.env.company) + line.partner_id.supplier_taxes_ids.filtered(lambda r: r.company_id  == line.env.company) + line.product_id.categ_id.supplier_taxes_ids.filtered(lambda r: r.company_id  == line.env.company)
    #         elif self.product_id.categ_id.supplier_taxes_ids:
    #             taxes = line.product_id.categ_id.supplier_taxes_ids.filtered(lambda r: r.company_id == self.order_id.company_id)
    #         elif self.partner_id.is_ica:
    #             taxes = line.partner_id.supplier_taxes_ids.filtered(lambda r: r.company_id  == self.order_id.company_id)
    #         line.taxes_id = fpos.map_tax(taxes)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    rt_enable = fields.Boolean("Auto Rete", default=True)

    def calculate_rtefte(self):
        """
        Unlinks ReteFuente taxes from account invoice line if the sum of lines with same retefuente tax is not greater than min base
        """
        self.ensure_one()
        rtefte_taxes = self.order_line.mapped('tax_id').filtered('retefuente')
        for tax in rtefte_taxes:
            lines = self.order_line.filtered(lambda l: tax.id in l.tax_id.ids)
            subtotal = sum(lines.mapped('price_subtotal'))
            if subtotal < tax.min_base:
                [line.write({'tax_id': [(3, tax.id, 0)]}) for line in lines]
            else: pass
        return True  
    
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
        
    # def _compute_tax_id(self):
    #     taxes = " "
    #     for line in self:
    #         line = line.with_company(line.company_id)
    #         fpos = line.order_id.fiscal_position_id or line.order_id.fiscal_position_id.get_fiscal_position(line.order_partner_id.id)
    #         # If company_id is set, always filter taxes by the company
    #         if self.product_id.categ_id.taxes_ids:
    #             taxes = line.product_id.categ_id.taxes_ids.filtered(lambda t: t.company_id == line.env.company) and line.product_id.taxes_id.filtered(lambda t: t.company_id == line.env.company)
    #         elif self.product_id.taxes_id:
    #             taxes = line.product_id.taxes_id.filtered(lambda t: t.company_id == line.env.company)
    #         line.tax_id = fpos.map_tax(taxes)