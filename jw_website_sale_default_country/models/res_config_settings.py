# -*- coding: utf-8 -*-

from odoo import api, models, fields, modules


class ResConfigSettingsDefaultCountry(models.TransientModel):
    # _name = 'res.config.settings'
    _inherit = 'res.config.settings'

    website_default_country_id = fields.Many2one('res.country', string='Default Country')

    def get_values(self):
        res = super(ResConfigSettingsDefaultCountry, self).get_values()
        res.update(
            website_default_country_id = int(self.env['ir.config_parameter'].sudo().get_param('jw_website_sale_default_country.website_default_country_id')),
        )
        return res

    def set_values(self):
        super(ResConfigSettingsDefaultCountry, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        website_default_country_id = int(self.website_default_country_id and self.website_default_country_id.id) or False

        param.set_param('jw_website_sale_default_country.website_default_country_id', website_default_country_id)
