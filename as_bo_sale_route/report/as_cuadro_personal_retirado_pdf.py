# # -*- coding: utf-8 -*-
import time
from openpyxl.styles import Alignment
import datetime
from datetime import datetime
import pytz
from odoo import models,fields
from datetime import datetime, timedelta
from time import mktime
import logging
from io import BytesIO
from odoo.tools.image import image_data_uri
import math
import locale
from urllib.request import urlopen
from odoo.tools.translate import _
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)

class as_persona_reporte_pdf(models.AbstractModel):
    _name = 'report.as_bo_sale_route.as_persona_retirado_pdf'
    _inherit = 'report.report_xlsx.abstract'
    
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        return {
                'nit':self.env.user.company_id.vat,
                'direccion':self.env.user.company_id.street,
                'telefono':self.env.user.company_id.phone,
                'fecha_actual' : self._fecha_actual(),
                'nombre_contrato' : self.nombre_cliente(data['form']),
                'lista_salidas_inventarios' : self.generate_xlsx_report(data),
                'logo':self.env.user.company_id.logo,
                'usuario':self.env.user.partner_id.name
                }
        
    def _fecha_actual(self):
        fecha_actual = time.strftime('%d-%m-%Y %H:%M:%S')
        struct_time_convert = time.strptime(fecha_actual, '%d-%m-%Y %H:%M:%S')
        date_time_convert = datetime.fromtimestamp(mktime(struct_time_convert))
        date_time_convert = date_time_convert - timedelta(hours = 4)
        fecha_actual = date_time_convert.strftime('%d-%m-%Y %H:%M:%S')
        return fecha_actual
     
    def generate_xlsx_report(self,data):       
        dict_empleado=[] #aqui se guardan los ids del wizard
        filtro_empleados_po =''
        if data['form']['as_nombre_empleado']:
            for line in data['form']['as_nombre_empleado']:
                dict_empleado.append(line)
        if dict_empleado: 
            whe = 'AND hrc.employee_id IN'
            filtro_empleados_po += whe
            filtro_empleados_po +=str(dict_empleado).replace('[','(').replace(']',')')
        else:
            filtro_empleados_po += ''

        consulta_empleados= ("""
               select 
                hre.identification_id,
                hre.name, 
                hrj.name,
                hrc.date_start,
                hrc.date_end,
                hrc.as_monto
                from hr_contract as hrc
                left join hr_employee as hre on hre.id = hrc.employee_id
                left join hr_job as hrj on hrj.id = hrc.job_id

                where hrc.state = 'close'  """+str(filtro_empleados_po)+ """
                """)
        self.env.cr.execute(consulta_empleados)
        empleadoslinea = [j for j in self.env.cr.fetchall()]
        lista = []
        if empleadoslinea != []:
            for linea in empleadoslinea:
                vals={
                    'val0':linea[0],
                    'val1':linea[1],
                    'val2':linea[2],
                    'val3':linea[3],
                    'val4':linea[4],
                    'val5':linea[5],
                }
                lista.append(vals)        
        return lista
    
    def nombre_cliente(self,data):
        dict_aux = []
        almacen=data['as_nombre_empleado']
        if almacen:
            for line in almacen:
                dict_aux.append(line)
        filtro_almacenes_name = 'Varios'
        for y in dict_aux:
            almacen_obj = self.env['hr.employee'].search([('id', '=', y)], limit=1)
            if almacen_obj:
                filtro_almacenes_name += ', ' + almacen_obj.name 
        if len(dict_aux) == 1:
            filtro_almacenes_name = self.env['hr.employee'].search([('id', '=', dict_aux[0])], limit=1).name
        return filtro_almacenes_name