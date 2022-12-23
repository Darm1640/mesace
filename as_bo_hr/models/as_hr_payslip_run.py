# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime, timedelta
from time import mktime
import time
from datetime import datetime, timedelta


class HrEmployee(models.Model):
    _inherit = 'hr.payslip.run'

    @api.onchange('slip_ids')
    def as_change_sequence(self):
        cont = 1
        for res in self.slip_ids:
            res.as_sequence = cont
            cont += 1

    as_indicadores_id = fields.Many2one('hr.indicadores', string='Indicadores',required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'Verify'),
        ('close', 'Done'),
        ('cancel', 'Cancelada'),
    ], string='Estado', index=True, readonly=True, copy=False, default='draft')
    as_asiento_count = fields.Integer(compute="_invoice_count")
    as_ff_count = fields.Integer(compute="_invoice_ff_count")

    def _invoice_count(self):
        for rec in self:
            rec.ensure_one()
            cajas = []
            for mov in self.slip_ids:
                if mov.move_id:
                    if mov.move_id.id not in cajas:
                        cajas.append(mov.move_id.id)
            rec.as_asiento_count = len(cajas)

    def action_view_asiento(self):
        self.ensure_one()
        action_pickings = self.env.ref('account.action_move_journal_line')
        action = action_pickings.read()[0]
        action['context'] = {}
        cajas = []
        for mov in self.slip_ids:
            if mov.move_id.id not in cajas:
                if mov.move_id:
                    cajas.append(mov.move_id.id)
        action['domain'] = [('id', 'in', cajas)]
        return action

    def _invoice_ff_count(self):
        for rec in self:
            rec.ensure_one()
            cajas = []
            facturas = self.env['account.move'].sudo().search([('as_payslip_run','=',self.id)])
            for mov in facturas:
                cajas.append(mov.id)
            rec.as_ff_count = len(cajas)

    def action_view_ff(self):
        self.ensure_one()
        action_pickings = self.env.ref('account.action_move_in_invoice_type')
        action = action_pickings.read()[0]
        action['context'] = {}
        cajas = []
        facturas = self.env['account.move'].sudo().search([('as_payslip_run','=',self.id)])
        for mov in facturas:
            cajas.append(mov.id)
        action['domain'] = [('id', 'in', cajas)]
        return action


    def action_cancel(self):
        # la nomina se pone en estado cancelado en la linea 60
        for mov in self.slip_ids:
            if mov.move_id:
                mov.move_id.state = 'cancel'
        self.write({'state' : 'cancel'})
        self.mapped('slip_ids').filtered(lambda slip: slip.state != 'cancel').action_payslip_cancel()
        facturas = self.env['account.move'].sudo().search([('as_payslip_run','=',self.id)])
        for mov in facturas:
            mov.state = 'cancel'
        self.state = 'cancel'

    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'hr.payslip.run'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return self.env.ref('as_hr.as_hr_planilla_sueldos_report').report_action(self, data=datas)

    def close_payslip_run(self):
        for slip in self.mapped('slip_ids').filtered(lambda slip: slip.state != 'cancel'):
            slip.action_payslip_done()
        self.action_close()

    def action_close(self):
        if self._are_payslips_ready():
            self.write({'state' : 'close'})

    def _are_payslips_ready(self):
        return all(slip.state in ['done', 'cancel'] for slip in self.mapped('slip_ids'))