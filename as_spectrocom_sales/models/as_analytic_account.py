from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class Account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'

    @api.model
    def create(self, vals):
        res = super(Account_analytic_account, self).create(vals)
        # res['name'] = res['name'] + ' - ' +res['partner_id']['name']
        x = res['name'].rsplit(": ")
        if len(x) > 0:
            
            order = self.env['sale.order'].sudo().search([('name', '=', x)],limit=1)
            if order.as_template_id.name != False:
                res['name'] = res['name'] + ' ' + order.as_template_id.name
        return res
