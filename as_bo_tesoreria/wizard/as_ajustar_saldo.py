# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class AssetaccountFiscalWizard(models.TransientModel):
    _name = "as.sale.ajust.saldo"
    _description = "as.sale.ajust.saldo"


    def as_ajustar_saldos(self):
        self.ensure_one()
        context = self._context
        created_move_ids = self.env['sale.order'].search([('id','in',tuple(self._context['active_ids']))])
        for sale in created_move_ids:
            if sale.state == 'sale':
                sale.ajustar_saldos(False)
        return True


