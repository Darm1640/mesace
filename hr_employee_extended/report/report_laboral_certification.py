from odoo import models, fields, exceptions, api
import datetime
import locale


class LaboralCertification(models.AbstractModel):
    _name = 'report.hr_employee_extended.laboral_certification'

    @api.model
    def _get_report_values(self, docids, data=None):
        """ Sobreescritura del metodo para validación de contrato activo
        de los empleados a certificar."""

        employees = self.env['hr.employee'].search([('id', 'in', docids)])
        for employee in employees:
            if not employee.current_contract:
                raise exceptions.UserError("No hay un contrato asignado.")

        return {
            'doc_ids': docids,
            'doc_model': 'hr.employee',
            'employees': employees,
        }
