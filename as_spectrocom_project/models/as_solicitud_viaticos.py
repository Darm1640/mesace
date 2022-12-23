import time
from openpyxl.styles import Alignment
import datetime
from datetime import datetime
import pytz
from datetime import datetime, timedelta
from time import mktime
import logging
from io import BytesIO
from odoo.tools.image import image_data_uri
import math
import locale
from urllib.request import urlopen
from odoo import api, fields, models, _
from odoo.tools.translate import _
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)

class Clientes(models.Model):
    _inherit = "project.task"

    as_nro_tarea = fields.Char(string='Numero Correlativo')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals_product in vals_list:
            secuence =  self.env['ir.sequence'].next_by_code('as.viaticos.code')
            vals_product['as_nro_tarea'] = secuence
        templates = super(Clientes, self).create(vals_list)
        return templates

    def generar_reporte(self):
        report_obj = self.env.ref("as_spectrocom_project.as_solicitud_viaticos_xlsx")
        return report_obj.report_action()

class ReporteClientes(models.AbstractModel):
    _name = "report.as_spectrocom_project.as_solicitud_viaticos_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Reporte de cliente"


    def generate_xlsx_report(self, workbook, data, lines):     
        sheet = workbook.add_worksheet('Resumen de estado de cuentas detallado')
        titulo1 = workbook.add_format({'font_size': 22 ,'align': 'center','color': '#4682B4','top': True, 'bold':True})
        tituloAzul = workbook.add_format({'font_size': 22, 'align': 'center',  'bottom': True, 'top': True, 'bold':True })
        titulo2 = workbook.add_format({'font_size': 22, 'align': 'center', 'bottom': True, 'top': True, 'right': True, 'left': True, 'bold':True,'color':'#ffffff','bg_color':'#4682B4','text_wrap': True,'border_color': '#ffffff'})
        titulo3 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True,'top': False, 'bold':True })
        titulo1_debajo = workbook.add_format({'font_size': 15, 'align': 'center', 'text_wrap': True,'top': False, 'bold':True, 'bottom': True })

        titulo3derecha = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True,'top': False, 'bold':True })

        titulo3_number = workbook.add_format({'font_size': 14, 'align': 'right', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True, 'num_format': '#,##0.00' })
        titulo4 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True, 'bottom': False, 'top': False, 'bold':True})

        number_left = workbook.add_format({'font_size': 12, 'align': 'left', 'num_format': '#,##0.00', })
        number_left_totales = workbook.add_format({'font_size': 12, 'align': 'left', 'num_format': '#,##0.00','bg_color':'#A9A9A9','bold':True })
        number_right_totales = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00','bg_color':'#A9A9A9','bold':True })

        number_subtitulos=workbook.add_format({'font_size': 12, 'align': 'left', 'num_format': '#,##0.00', 'bold':True })
        totales = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00', 'top':True,  'bold':True })
        totales_valores = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00', 'top':True,  })
        number_right = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00', 'text_wrap': True,})
        number_right_bold = workbook.add_format({'font_size': 12, 'align': 'left', 'num_format': '#,##0.00', 'bold':True})
        number_right_col = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00','bg_color': 'silver'})
        number_center = workbook.add_format({'font_size': 12, 'align': 'center', 'num_format': '#,##0.00'})
        number_right_col.set_locked(False)
        color_cabecera_plomo=workbook.add_format({'font_size': 12, 'align': 'left', 'bold':True,'bg_color':'#A9A9A9'})
        color_subts=workbook.add_format({'font_size': 12, 'align': 'left', 'bold':True,'bg_color':'#F0F8FF'})

        letter1 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True})
        letter2 = workbook.add_format({'font_size': 12, 'align': 'left', 'bold':True})
        letter3 = workbook.add_format({'font_size': 12, 'align': 'right', 'text_wrap': True})
        letter4 = workbook.add_format({'font_size': 12, 'align': 'center', 'text_wrap': True})
        letter_locked = letter3
        letter_locked.set_locked(True)
        totales_Azul = workbook.add_format({'font_size': 12, 'align': 'right', 'bold':True,'bg_color':'#F0F8FF'})
        # sheet.set_row(10,25)
        titulo2.set_align('vcenter')
        #sheet.set_column('A:N',10, titulo2)
        #Aqui definimos en los anchos de columna
        sheet.set_column('A:A',20, letter1)
        sheet.set_column('B:B',25, letter1)
        sheet.set_column('C:C',20, letter1) 
        sheet.set_column('D:D',20, letter1)
        sheet.set_column('E:E',20, letter1)
        sheet.set_column('F:F',20, letter1)
        sheet.set_column('G:G',30, letter1)
        sheet.set_column('H:H',8, letter1)
        sheet.set_column('I:I',8, letter1)
        sheet.set_column('J:J',8, letter1)
        sheet.set_column('K:K',20, letter1)
        sheet.set_row(28,40, letter1)
        #logo de la empresa
        url = image_data_uri(self.env.user.company_id.logo)
        image_data = BytesIO(urlopen(url).read())
        sheet.insert_image('A1:B5', url, {'image_data': image_data,'x_scale': 0.28, 'y_scale': 0.17})

        sheet.write(0, 5, 'N°: ', titulo4)
        sheet.write(0, 6, lines.as_nro_tarea, letter3)
        sheet.write(1, 5, 'Estado: ', titulo4)

        #titulo
        sheet.merge_range('A5:G5', 'SOLICITUD DE VIATICOS', titulo2)
        #columna izquierda
        sheet.write(11, 0, 'Proyecto: ', titulo4)
        sheet.write(12, 0, 'Solicitado por: ', titulo4)
        sheet.write(12, 1, str(self.env.user.partner_id.name), letter3)
        sheet.write(13, 0, 'Cuenta Analitica: ', titulo4)

        sheet.write(15, 0, 'Feha de Salida: ', titulo4)
        #fecha = (datetime.now() - timedelta(hours=4)).strftime('%d/%m/%Y')
        #sheet.merge_range('H8:J8', 'Fecha de impresion: ', titulo4)
        #sheet.write(15, 1, fecha, letter3)

        sheet.write(17, 0, 'Descripcion del Viatico: ', titulo4)

        #columna derecha
        sheet.write(11, 5, 'Cliente: ', titulo4)
        sheet.write(12, 5, 'Nro. OT: ', titulo4)
        
        sheet.write(15, 5, 'Fecha de Regreso: ', titulo4)
        sheet.write(17, 5, 'Viajeros: ', titulo4)

        sheet.merge_range('A22'':B22', 'PRESUPUESTO TENTATIVO DE VIATICOS: ', number_left_totales) 
        
        sheet.merge_range('D22'':G22', '', number_left_totales) 


        firma = self.env['hr.employee'].search([('user_id','=',self.env.user.id)])
        if firma.as_firma_archivo:
            url2 = image_data_uri(firma.as_firma_archivo)
            image_data2 = BytesIO(urlopen(url2).read())
            sheet.insert_image('C29:D29', url2, {'image_data': image_data2,'x_scale': 0.50, 'y_scale': 0.25})
        if lines.as_worker_signature:
            url3 = image_data_uri(lines.as_worker_signature)
            image_data3 = BytesIO(urlopen(url3).read())
            sheet.insert_image('F29'':G29', url3, {'image_data': image_data3,'x_scale': 0.28, 'y_scale': 0.25})


        sheet.write(28, 1, 'solicitado por: ', titulo4)
        sheet.write(29, 2, str(self.env.user.partner_id.name), letter3)
        sheet.write(28, 4, 'autorizado por: ', titulo4)
        #sheet.write(28, 5, lines.as_worker_signature, titulo4)
        if lines.as_responsable:
            sheet.merge_range('E30'':F30', lines.as_responsable, letter3)
        else:
            sheet.merge_range('E30'':F30', "", letter3)

       
        sheet.write(11, 1, str(lines.project_id.name), letter3)
        sheet.write(13, 1, str(lines.as_analytic_account_id.name), letter3)
        sheet.write(11, 6, str(lines.partner_id.name), letter3)
        sheet.write(12, 6, lines.as_ot, letter3)

        if lines.as_fecha_salida:
            sheet.write(15, 1, lines.as_fecha_salida, letter3)
        else:
            sheet.write(15, 1, "", letter3)
        if lines.as_fecha_llegada:
            sheet.write(15, 6, lines.as_fecha_llegada, letter3)
        else:
            sheet.write(15, 6, "", letter3)

        sheet.write(21, 2, lines.as_presupuesto,number_right_totales )
        sheet.merge_range('A19:B19', lines.name, letter3)
        if lines.as_state_viatico == "draft":
            sheet.write(1, 6,  "Borrador", letter3)
        if lines.as_state_viatico == "to_approval":
            sheet.write(1, 6,  "Para Aprobar", letter3)
        if lines.as_state_viatico == "approval":
            sheet.write(1, 6,  "Aprobado", letter3)
        
        
        attachment = self.env['project.task'].search([('id','=',lines.id)])
        if attachment:
            attachment2 = self.env['as.viaticos'].search([('as_project_id','=',attachment.id)])
            if attachment2:
                cont = ''
                for j in attachment2:
                        
                    empleado = self.env['hr.employee'].search([('id','=',j.as_empleado.id)])
                        
                    cont += str(empleado.name)+','
                sheet.write(18, 6, cont, letter3)
                    


        