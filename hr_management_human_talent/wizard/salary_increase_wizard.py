from odoo import api, fields, models
from datetime import date


class SalaryIncreaseWizard(models.TransientModel):
    _name = 'salary.increase.wizard'

    type_novelty = fields.Many2one('type.novelty', 'Novelty Type')
    start_date = fields.Date('Date Start')
    end_date = fields.Date('Date End')

    def create_news(self):
        salary_increase_id = self.env[self._context.get('active_model', '')].browse(
            self._context.get('active_id', ''))
        salary_increase_id.increase_salary()

        if salary_increase_id.tipo_de_salario_contrato == 'sueldo_basico':
            type_salary = 'basic_salary'

        if salary_increase_id.tipo_de_salario_contrato == 'salario_integral':
            type_salary = 'integral_salary'

        if salary_increase_id.tipo_de_salario_contrato == 'apoyo_sostenimiento':
            type_salary = 'support_sustainability'

        for line in salary_increase_id.increase_lines_ids:

            if line.tipo_de_salario_contrato == 'sueldo_basico':
                type_salary = 'basic_salary'

            if line.tipo_de_salario_contrato == 'salario_integral':
                type_salary = 'integral_salary'

            if line.tipo_de_salario_contrato == 'apoyo_sostenimiento':
                type_salary = 'support_sustainability'

            vals = {
                'model': 'contract',
                'employee_id': line.employee_id.id,
                'related_contract': line.contract_id.name,
                'document_number': line.contract_id.identification_id,
                'start_date': self.start_date,
                'final_date': self.end_date,
                'salary_percent': salary_increase_id.percentage,
                'current_salary': line.current_wage,
                'type_novelty': self.type_novelty.id,
                'new_salary': line.new_wage,
                'salary_type': type_salary,
                'creation_date': date.today(),
            }
            news = self.env['hr.request.for.news'].create(vals)
            news.validate_document()
            news.change_state()
