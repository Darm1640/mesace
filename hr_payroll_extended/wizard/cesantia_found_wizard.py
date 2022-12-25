from odoo import api, fields, models, _
from odoo.tools import date_utils
from odoo.tools.misc import xlsxwriter
from datetime import timedelta, date
from io import BytesIO
import base64
import json


class CesantiaFoundWizard(models.TransientModel):
    _name = 'hr.payroll.cesantia.found.wizard'
    _description = 'Generate report xls Cesantia Found'

    salary_rule_id = fields.Many2one('hr.salary.rule', 'Salary Rule one', required=True)
    salary_rule_two_id = fields.Many2one('hr.salary.rule', 'Salary Rule two', required=True)

    def print_xlsx(self):

        partners = []
        for payslip in self._context.get('active_ids'):
            obj_payslip = self.env['hr.payslip'].search([('id', '=', payslip)])
            for obj in obj_payslip:

                days_worked = obj.employee_id.get_days_annual(obj.date_to)

                salary_rule_id = 0
                salary_rule_two_id = 0
                for line in obj.line_ids:
                    if line.salary_rule_id == self.salary_rule_id:
                        salary_rule_id = line.amount
                    if line.salary_rule_id == self.salary_rule_two_id:
                        salary_rule_two_id = line.amount

                data = {
                    'type_document': obj.employee_id.ident_type.code,
                    'identification_id': obj.employee_id.identification_id,
                    'third_name': obj.employee_id.third_name,
                    'fourth_name': obj.employee_id.fourth_name,
                    'first_name': obj.employee_id.first_name,
                    'second_name': obj.employee_id.second_name,
                    'name_found': obj.employee_id.found_layoffs_id.name,
                    'days_worked': days_worked,
                    'salary_rule_id': salary_rule_id,
                    'salary_rule_two_id': salary_rule_two_id,
                }

                partners.append(data)

        data = {
            'salary_rule_id': self.salary_rule_id.name,
            'salary_rule_two_id': self.salary_rule_two_id.name,
            'partners': partners,
        }

        return {
            'type': 'ir_actions_xlsx_download',
            'data': {'model': 'hr.payroll.cesantia.found.wizard',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Fondo de Cesantias ' + str(date.today().strftime("%d-%m-%y")),
                     }
        }

    def get_xlsx_report(self, data, response):

        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()

        cell_format = workbook.add_format({'bold': True})
        sheet.set_column(0, 9, 30)  # Width of columns B:D set to 30.

        sheet.write('A1', 'Tipo de Documento', cell_format)
        sheet.write('B1', 'Numero Documento', cell_format)
        sheet.write_string('C1', 'Primer Apellido', cell_format)
        sheet.write_string('D1', 'Segundo Apellido', cell_format)
        sheet.write_string('E1', 'Primer Nombre', cell_format)
        sheet.write_string('F1', 'Segundo Nombre', cell_format)
        sheet.write('G1', 'Nombre Fondo', cell_format)
        sheet.write('H1', 'Dias trabajados', cell_format)
        sheet.write('I1', data['salary_rule_id'], cell_format)
        sheet.write('J1', data['salary_rule_two_id'], cell_format)

        # Start from the first cell. Rows and columns are zero indexed.
        row = 1
        col = 0

        # Iterate over the data and write it out row by row.
        for item in data['partners']:
            sheet.write(row, col, item['type_document'])
            sheet.write(row, col + 1, item['identification_id'])

            if item['third_name']:
                sheet.write_string(row, col + 2, item['third_name'])
            else:
                sheet.write_string(row, col + 2, "")

            if item['fourth_name']:
                sheet.write_string(row, col + 3, item['fourth_name'])
            else:
                sheet.write_string(row, col + 3, "")

            if item['first_name']:
                sheet.write_string(row, col + 4, item['first_name'])
            else:
                sheet.write_string(row, col + 4, "")

            if item['second_name']:
                sheet.write_string(row, col + 5, item['second_name'])
            else:
                sheet.write_string(row, col + 5, "")

            sheet.write(row, col + 6, item['name_found'])
            sheet.write(row, col + 7, item['days_worked'])
            sheet.write_number(row, col + 8, item['salary_rule_id'])
            sheet.write_number(row, col + 9, item['salary_rule_two_id'])
            row += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
