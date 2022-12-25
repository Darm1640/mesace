# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

# Extend the WebsiteSale class
class CustomWebsiteSale(WebsiteSale):

    # Override the route to add in the areas
    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        res = super(CustomWebsiteSale, self).address(**kw)

        default_country_id = int(request.env['ir.config_parameter'].sudo().get_param('jw_website_sale_default_country.website_default_country_id'))
        default_country = request.env['res.country'].sudo().browse(default_country_id)

        res.qcontext['country'] = (
            res.qcontext.get('country') or
            default_country
            # request.website.company_id.country_id
        )
        return res
