from datetime import datetime
from odoo import api, fields, models

class as_resumen_ventas_gestion(models.TransientModel):
    _name="as.report.cuadro.personal.retirado"
    
    as_nombre_empleado = fields.Many2many('hr.employee', string='Empleados')
    
    
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'as.report.cuadro.personal.retirado'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return self.env.ref('as_bo_sale_route.as_cuadro_personal_retirado_xlsx').report_action(self, data=datas)
        
    def imprimir_reporte_pdf(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'as.report.cuadro.personal.retirado'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        return self.env.ref('as_bo_sale_route.as_reporte_persona_retirado_pdf').report_action(self, data=datas)
    

    