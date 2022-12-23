from datetime import datetime
from odoo import api, fields, models
from time import mktime
import logging
from datetime import datetime, timedelta
from datetime import datetime

class as_resumen_ventas_gestion(models.TransientModel):
    _name="as.report.cuadro.beneficios.sociales"
    
    as_nombre_empleado = fields.Many2many('hr.employee', string='Empleados')
    fecha = fields.Date(string="Hasta la fecha", default=lambda *a: (datetime.now() - timedelta(hours = 4)).strftime('%Y-%m-%d'), required=True)
    
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'as.report.cuadro.beneficios.sociales'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return self.env.ref('as_bo_sale_route.as_cuadro_beneficios_sociales_xlsx').report_action(self, data=datas)
            

    