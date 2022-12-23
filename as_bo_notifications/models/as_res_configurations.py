from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class ResConfigSettings_model(models.TransientModel):
    _inherit = 'res.config.settings'
    