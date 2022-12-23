# # -*- coding: utf-8 -*-

import datetime
from datetime import datetime
import pytz
from odoo import models,fields
from datetime import datetime, timedelta
from time import mktime
import logging
_logger = logging.getLogger(__name__)

class as_sales_emit_excel(models.AbstractModel):
    _name = 'report.as_bo_hr.planilla_patronal.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):     
        #fILTROS
        filtro =''
        if data['form']['as_name_afp']:
            filtro+= ' and hea.id in '+ str(data['form']['as_name_afp']).replace('[','(').replace(']',')')
        #estilos
        sheet = workbook.add_worksheet('Resumen de ventas')
        titulo1 = workbook.add_format({'font_size': 13, 'align': 'center', 'text_wrap': True, 'bold':True })
        titulo2 = workbook.add_format({'font_size': 8, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True })
        titulo3 = workbook.add_format({'font_size': 7, 'align': 'left', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True })
        titulo3_number = workbook.add_format({'font_size': 8, 'align': 'right', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True, 'num_format': '#,##0.00' })
        titulo4 = workbook.add_format({'font_size': 8, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True, 'bold':True })
        titulo10 = workbook.add_format({'font_size': 8, 'align': 'right', 'text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True, 'bold':True })
        titulo5 = workbook.add_format({'font_size': 8, 'align': 'center', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False })
        titulo55 = workbook.add_format({'font_size': 8, 'align': 'left', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False })
        titulo9 = workbook.add_format({'font_size': 8, 'align': 'right', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False })
        titulo6 = workbook.add_format({'font_size': 8, 'align': 'center', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False, 'color': 'red'})
        titulo12 = workbook.add_format({'font_size': 8, 'align': 'right', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False, 'color': 'red'})
        titulo7 = workbook.add_format({'font_size': 8, 'align': 'left', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False})
        titulo8 = workbook.add_format({'font_size': 8, 'align': 'center', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':True})

        number_left = workbook.add_format({'font_size': 7, 'align': 'left', 'num_format': '#,##0.00'})
        number_right = workbook.add_format({'font_size': 7, 'align': 'right', 'num_format': '#,##0.00'})
        number_right_bold = workbook.add_format({'font_size': 7, 'align': 'right', 'num_format': '#,##0.00', 'bold':True})
        number_right_col = workbook.add_format({'font_size': 7, 'align': 'right', 'num_format': '#,##0.00','bg_color': 'silver'})
        number_center = workbook.add_format({'font_size': 7, 'align': 'center', 'num_format': '#,##0.00'})
        number_right_col.set_locked(False)

        letter1 = workbook.add_format({'font_size': 7, 'align': 'left', 'text_wrap': True})
        letter2 = workbook.add_format({'font_size': 7, 'align': 'left', 'bold':True})
        letter3 = workbook.add_format({'font_size': 7, 'align': 'right', 'text_wrap': True})
        letter4 = workbook.add_format({'font_size': 7, 'align': 'left', 'text_wrap': True, 'bold': True})
        letter444 = workbook.add_format({'font_size': 7, 'align': 'left', 'text_wrap': True, 'bold': True})
        letter44 = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True, 'bold': True})
        letter_locked = letter3
        letter_locked.set_locked(False)

        filtro_afp = data['form']['as_name_afp']
        # Aqui definimos en los anchos de columna
        sheet.set_column('A:A',7, letter1)
        sheet.set_column('B:B',14, letter1)
        sheet.set_column('C:C',25, letter1)
        sheet.set_column('D:D',10, letter1)
        sheet.set_column('E:E',10, letter1)
        sheet.set_column('F:F',8, letter1)
        sheet.set_column('G:G',15, letter1)
        sheet.set_column('H:H',15, letter1)
        sheet.set_column('I:I',18, letter1)
        sheet.set_column('J:J',18, letter1)
        sheet.set_column('K:K',15, letter1)

        # Titulos, subtitulos, filtros y campos del reporte
        sheet.merge_range('A1:H1', 'PLANILLA DE APORTES PATRONALES Y BENEFICIOS SOCIALES', titulo1)
        payslip =  self.env[self._context['active_model']].sudo().search([('id', '=', data['form']['payslip_run_id'])])
        fecha_inicial = datetime.strptime(str(payslip.date_start), '%Y-%m-%d').strftime('%d/%m/%Y')
        fecha_final = datetime.strptime(str(payslip.date_end), '%Y-%m-%d').strftime('%d/%m/%Y')
        sheet.merge_range('A2:H2', fecha_inicial +' - '+ fecha_final, titulo4)
        fecha = (datetime.now() - timedelta(hours=4)).strftime('%d/%m/%Y %H:%M:%S')
        sheet.merge_range('A3:D3', self.env.user.company_id.name, letter44)
        sheet.merge_range('A4:D4', 'NIT: '+str(self.env.user.company_id.vat)+' Numero Patronal: '+str(self.env.user.company_id.as_numero_patronal), letter444)
        sheet.merge_range('A5:D5', 'Email: '+self.env.user.company_id.email+' Teléfono: '+self.env.user.company_id.phone, letter444)
        sheet.merge_range('A6:D6', self.env.user.company_id.city+' '+self.env.user.company_id.country_id.name, letter444)
        sheet.merge_range('A7:D7', 'Padrón Municipal: '+str(self.env.user.company_id.as_patronal_municipal), letter444)
        sheet.write(2, 6, 'Fecha de impresion: ', letter4)
        sheet.merge_range('H3:J3', fecha)
        sheet.freeze_panes(9, 0)

        filas = 7
        sheet.merge_range('A'+str(filas+1)+':A'+str(filas+2),'NO', titulo4)
        sheet.merge_range('B'+str(filas+1)+':B'+str(filas+2), 'CARNET DE IDENTIDAD', titulo4)
        sheet.merge_range('C'+str(filas+1)+':C'+str(filas+2), 'NOMBRE DEL EMPLEADO', titulo4)
        sheet.merge_range('D'+str(filas+1)+':D'+str(filas+2), 'TOTAL GANADO', titulo4)
        sheet.write(filas, 4, 'C.N.S', titulo4)
        sheet.write(filas+1, 4, '10%', titulo4)        
        sheet.write(filas, 5, 'R. Prof', titulo4)
        sheet.write(filas+1, 5, '1.71%', titulo4)        
        sheet.write(filas, 6, 'Pro VIv', titulo4)
        sheet.write(filas+1, 6, '2%', titulo4)        
        sheet.write(filas, 7, 'Fdo Sol.', titulo4)
        sheet.write(filas+1, 7, '3%', titulo4)        
        sheet.write(filas, 8, 'Infocal', titulo4)
        sheet.write(filas+1, 8, '1%', titulo4)        
        sheet.merge_range('J'+str(filas+1)+':J'+str(filas+2), 'TOTALES', titulo4)
        sheet.write(filas, 10, 'Agui.', titulo4)
        sheet.write(filas+1, 10, '8.3333%', titulo4)          
        sheet.write(filas, 11, 'Indemn.', titulo4)
        sheet.write(filas+1, 11, '8.3333%', titulo4)   
        sheet.merge_range('M'+str(filas+1)+':M'+str(filas+2), 'TOTALES', titulo4)
        sheet.merge_range('N'+str(filas+1)+':N'+str(filas+2), 'SUMA TOTALES', titulo4)
 
        filas +=2
        cont = 0
        query_movements = ("""
            select hp.id from hr_payslip hp
            join hr_employee he on he.id=hp.employee_id
            left join hr_employee_afp hea on he.as_name_afp = hea.id
            where 
            hp.state in ('draft','done')
            and hp.payslip_run_id="""+str(payslip.id)+"""
            """+filtro+"""
            """)
        #_logger.debug(query_movements)
        self.env.cr.execute(query_movements)
        slip = [k for k in self.env.cr.fetchall()] 
        payslips = self.env['hr.payslip'].sudo().search([('id', 'in', slip)])
        monto_total_aporte=0.0
        monto_total_benedicios=0.0
        monto_sueldos = 0.0
        monto_cns = 0.0
        monto_prof = 0.0
        monto_prov = 0.0
        monto_fdo = 0.0
        monto_infocal = 0.0
        monto_agui = 0.0
        monto_inde = 0.0
        monto_total_suma = 0.0
        for payslip in payslips:
            cont += 1 
            total_aporte = 0.0
            total_beneficios = 0.0
            sheet.write(filas, 0, cont, titulo5)
            sheet.write(filas, 1, payslip.employee_id.identification_id, titulo5)
            sheet.write(filas, 2, payslip.employee_id.name, titulo55)
            sheet.write(filas, 3, payslip._get_salary_line_total('SALGAN') or 0.0, number_right)
            monto_sueldos +=  payslip._get_salary_line_total('SALGAN') or 0.0
            sheet.write(filas, 4, payslip._get_salary_line_total('CNS') or 0.0, number_right)
            monto_cns += payslip._get_salary_line_total('CNS') or 0.0
            sheet.write(filas, 5, payslip._get_salary_line_total('PPROF') or payslip._get_salary_line_total('FPROF'), number_right)
            monto_prof += payslip._get_salary_line_total('PPROF') or payslip._get_salary_line_total('FPROF')
            sheet.write(filas, 6, payslip._get_salary_line_total('PPROVIV') or payslip._get_salary_line_total('FPROVIV'), number_right)
            monto_prov += payslip._get_salary_line_total('PPROVIV') or payslip._get_salary_line_total('FPROVIV')
            sheet.write(filas, 7, payslip._get_salary_line_total('FSPA') or payslip._get_salary_line_total('PSPA'), number_right)
            monto_fdo += payslip._get_salary_line_total('FSPA') or payslip._get_salary_line_total('PSPA')
            sheet.write(filas, 8, payslip._get_salary_line_total('INFOCAL'), number_right)
            monto_infocal += payslip._get_salary_line_total('INFOCAL')
            total_aporte= float(payslip._get_salary_line_total('CNS')) + float(payslip._get_salary_line_total('PPROF') or payslip._get_salary_line_total('FPROF'))+ float(payslip._get_salary_line_total('PPROVIV') or payslip._get_salary_line_total('FPROVIV')) + float(payslip._get_salary_line_total('FSPA') or payslip._get_salary_line_total('PSPA')) + float(payslip._get_salary_line_total('INFOCAL'))
            monto_total_aporte += total_aporte
            sheet.write(filas, 9, total_aporte, number_right)
            sheet.write(filas, 10, payslip._get_salary_line_total('AAGUI'), number_right)
            monto_agui += payslip._get_salary_line_total('AAGUI')
            sheet.write(filas, 11, payslip._get_salary_line_total('INDEMN'), number_right)
            monto_inde += payslip._get_salary_line_total('INDEMN')
            total_beneficios= payslip._get_salary_line_total('AAGUI') + payslip._get_salary_line_total('INDEMN')
            monto_total_benedicios += total_beneficios
            sheet.write(filas, 12, total_beneficios, number_right)
            monto_total_suma += total_beneficios+total_aporte
            sheet.write(filas, 13, total_beneficios+total_aporte, number_right)
            filas +=1
        sheet.merge_range('A'+str(filas+1)+':C'+str(filas+1), 'TOTALES', titulo8)  
        sheet.write(filas, 3, monto_sueldos, number_right_bold) 
        sheet.write(filas, 4, monto_cns, number_right_bold) 
        sheet.write(filas, 5, monto_prof, number_right_bold) 
        sheet.write(filas, 6, monto_prov, number_right_bold) 
        sheet.write(filas, 7, monto_fdo, number_right_bold) 
        sheet.write(filas, 8, monto_infocal, number_right_bold) 
        sheet.write(filas, 9, monto_total_aporte, number_right_bold) 
        sheet.write(filas, 10, monto_agui, number_right_bold) 
        sheet.write(filas, 11, monto_inde, number_right_bold) 
        sheet.write(filas, 12, monto_total_benedicios, number_right_bold) 
        sheet.write(filas, 13, monto_total_suma, number_right_bold) 
     
