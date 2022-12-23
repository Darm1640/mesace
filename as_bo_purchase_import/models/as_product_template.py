import logging
from odoo.exceptions import UserError, RedirectWarning, ValidationError, MissingError
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
_logger = logging.getLogger(__name__)  


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    property_account_import_id = fields.Many2one('account.account', company_dependent=True,string="Cuenta de gasto de importación",domain=[('deprecated', '=', False)])
