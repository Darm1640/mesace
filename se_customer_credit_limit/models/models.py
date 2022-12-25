# -*- coding: utf-8 -*-

from odoo import api, models, fields, _

class ResPartner(models.Model):
    _inherit= 'res.partner'
    
    check_creditlimit = fields.Boolean('Check Credit')
    cl_on_hold = fields.Boolean('Credit limit on Hold')


class sale_order(models.Model):
    _inherit = 'sale.order'

    total_exceeded_amount = fields.Float('Exceeded Amount')
    manager_ids = fields.Many2many('res.users', string='Credit Limit Approval Users', default=lambda self: self.env.ref('sales_team.group_sale_manager').sudo().users.ids)
    state = fields.Selection(selection_add=[('credit_limit', 'Credit limit')])

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super(sale_order, self).onchange_partner_id()
        partner_id = self.partner_id
        if self.partner_id.parent_id:
            partner_id = self.partner_id.parent_id
        if partner_id:
            if partner_id.cl_on_hold:
                return {'warning': {
                            'title': 'Credit Limit On Hold',
                            'message': partner_id.name + "' is on credit limit hold."
                            }
                        }

    def action_confirm_creditlimit(self):
        partner_id = self.partner_id
        if self.partner_id.parent_id:
            partner_id = self.partner_id.parent_id
        partner_ids = [partner_id.id]
        for partner in partner_id.child_ids:
            partner_ids.append(partner.id)

        if partner_id.check_creditlimit:
            sol_obj = self.env['sale.order.line'].sudo()
            aml_obj = self.env['account.move.line'].sudo()
            sale_orders = []
            to_inv_amount = 0.0
            for one_so_line in sol_obj.search([('order_id.partner_id', 'in', partner_ids), ('order_id.state', 'in', ['sale', 'credit_limit', 'done'])]):
                taxes = one_so_line.tax_id.compute_all(one_so_line.price_unit * (1 - (one_so_line.discount or 0.0) / 100.0), one_so_line.order_id.currency_id,\
                    one_so_line.product_uom_qty - one_so_line.qty_invoiced, product=one_so_line.product_id, partner=one_so_line.order_id.partner_id)
                if one_so_line.order_id.id not in sale_orders:
                    if one_so_line.order_id.invoice_ids:
                        for one_invoice in one_so_line.order_id.invoice_ids:
                            if one_invoice.state == 'draft':
                                sale_orders.append(one_so_line.order_id.id)
                                break
                    else:
                        sale_orders.append(one_so_line.order_id.id)
                to_inv_amount += taxes['total_included']

            invoices = []
            draft_inv_amount = 0.0
            for line in aml_obj.search([('sale_line_ids', '!=', False), ('move_id.partner_id', 'in', partner_ids), ('move_id.state', '=', 'draft')]):
                taxes = line.tax_ids.compute_all(line.price_unit * (1 - (line.discount or 0.0) / 100.0), line.move_id.currency_id,
                    line.quantity, product=line.product_id, partner=line.move_id.partner_id)
                to_inv_amount += taxes['total_included']
                draft_inv_amount += taxes['total_included']
                if line.move_id.id not in invoices:
                    invoices.append(line.move_id.id)

            if self.amount_total > (partner_id.credit_limit - partner_id.credit - to_inv_amount - draft_inv_amount):
                wizard_action = self.env.ref('se_customer_credit_limit.action_sale_credit_limit_wizard').sudo()
                return {
                    'name': _('Credit Limit Exceeded!'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'sale.credit.limit.wizard',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'target': 'new',
                    'res_id': self.env['sale.credit.limit.wizard'].create({
                                    'partner_id': partner_id.id,
                                    'current_order_total': self.amount_total or 0.0,
                                    'total_exceeded_amount': (to_inv_amount + draft_inv_amount + partner_id.credit + self.amount_total) - partner_id.credit_limit,
                                    'credit': partner_id.credit,
                                }).id,
                }
            else:
                self.action_confirm()
        else:
            self.action_confirm()