from datetime import datetime
from odoo import api, fields, models

class as_report_vacaciones(models.TransientModel):
    _name="as.report.vacaciones"
    
    as_nombre_empleado = fields.Many2many('hr.employee', string='Empleados')
    as_detallado = fields.Boolean(string='Detallado')
    as_departamento = fields.Many2one('hr.department', string='Departamento')

    
    
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'as.report.vacaciones'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return self.env.ref('as_bo_hr_ausencias.as_reporte_vacaciones_xlsx').report_action(self, data=datas)
        
    def imprimir_reporte_pdf(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'as.report.vacaciones'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        return self.env.ref('as_bo_hr_ausencias.as_reporte_vacaciones_pdf').report_action(self, data=datas)
    

    