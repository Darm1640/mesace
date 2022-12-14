# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class MeasurementUnits(models.Model):
    _name = 'l10n_co_factura.unit_measurement'

    code = fields.Char(
        string='Código DIAN',
        required=True
    )
    name = fields.Char(
        string='Descripción',
        compute='compute_name',
        store = True

    )
    description = fields.Char(
        string='Descripción DIAN',
        required=True
    )

    @api.depends('description')
    def compute_name(self):
        for record in self:
            record.name = record.description


