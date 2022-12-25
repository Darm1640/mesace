# -*- coding: utf-8 -*-

from odoo import api, fields, models


class sale_credit_limit_wizard(models.TransientModel):
    _name = "sale.credit.limit.wizard"
    _description = 'Credit Limit Wizard'

    partner_id = fields.Many2one('res.partner', string="Customer")
    credit_limit = fields.Float(related='partner_id.credit_limit', string="Credit Limit")
    credit = fields.Float('Total Receivable')
    current_order_total = fields.Float('Current Order Total')
    total_exceeded_amount = fields.Float('Exceeded Amount')

    def confirm_creditlimit(self):
        order = self.env['sale.order'].sudo().browse(self._context.get('active_id'))
        if order:
            order.write({
                'total_exceeded_amount': self.total_exceeded_amount,
                'state': 'credit_limit',
            })
            #Send mail to sales managers
            self.env.ref('se_customer_credit_limit.credit_limit_approval_mail_manager').send_mail(order.id, force_send=True)
            partner_id = self.partner_id
            if partner_id.parent_id:
                partner_id= partner_id.parent_id
            partner_id.cl_on_hold = True
        return True