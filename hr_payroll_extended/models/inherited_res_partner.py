# Copyright 2019-TODAY Anand Kansagra <anandkansagra@qdata.io>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError
import odoo
import logging
from odoo import http

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    """Extend Partner."""

    _inherit = 'res.partner'

    is_found_layoffs = fields.Boolean(string='Found Layoffs')
    is_compensation_box = fields.Boolean(string='Compensation Box')
    is_eps = fields.Boolean(string='EPS')
    required_physical_evidence = fields.Boolean(string='Required Physical Evidence')
    is_unemployee_fund = fields.Boolean(string='Unemployee Fund')
    is_arl = fields.Boolean(string='ARL')
    is_prepaid_medicine = fields.Boolean(string='Prepaid Medicine')
    is_afc = fields.Boolean(string='AFC')
    is_voluntary_contribution = fields.Boolean(string='Voluntary Contribution')
    is_afp = fields.Boolean(string='AFP')
