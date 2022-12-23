from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError, MissingError

import logging
_logger = logging.getLogger(__name__)

class AccountInvoicenits(models.Model):
    _name = 'as.nits'

    name = fields.Char(string="NIT")
    as_nit = fields.Char(string='Razon Social')
    partner_id = fields.Many2one('res.partner', string='Cliente')