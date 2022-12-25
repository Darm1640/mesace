from odoo import models, fields, exceptions, api
import datetime
import locale


class HistoryExtend(models.AbstractModel):
    _name = 'report.hr_management_human_talent.history_extend'

    @api.model
    def _get_report_values(self, docids, data=None):
        """ Sobreescritura del metodo para validación de contrato activo
        de los empleados a certificar."""

        contract = self.env['hr.contract'].search([('id', 'in', docids)])

        return {
            'doc_ids': docids,
            'doc_model': 'hr.contract',
            'contracts': contract,
        }
