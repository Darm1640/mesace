# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class CustomerComment(http.Controller):
    @http.route(['/custom_customer/comment'], type='json', auth="user", website=True)
    def custom_customer_comment(self, **kw):
        custom_sale_id=request.env['sale.order'].sudo().browse(int(kw.get('order_id')))
        vals = {
              'custom_customer_comment':kw.get('comment'),
            }
        custom_sale_id.sudo().write(vals)

        return True
           