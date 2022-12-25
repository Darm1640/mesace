from odoo import api, fields, models


class L10nLatamIdentificationType(models.Model):
    _inherit = 'l10n_latam.identification.type'

    code = fields.Char('Code')
