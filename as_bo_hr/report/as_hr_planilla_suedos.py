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
    _name = 'report.as_bo_hr.planilla_sueldos.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):     
        #fILTROS
        filtro =''
        if data['form']['as_name_afp']:
            filtro+= ' and hea.id in '+ str(data['form']['as_name_afp']).replace('[','(').replace(']',')')
        #estilos
        sheet = workbook.add_worksheet('Resumen de ventas')
        titulo1 = workbook.add_format({'font_size': 13, 'align': 'center', 'text_wrap': True, 'bold':True })
        titulo1p = workbook.add_format({'font_size': 8, 'align': 'center', 'text_wrap': True })
        titulo2 = workbook.add_format({'font_size': 8, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True })
        titulo3 = workbook.add_format({'font_size': 7, 'align': 'left', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True })
        titulo3_number = workbook.add_format({'font_size': 8, 'align': 'right', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True, 'num_format': '#,##0.00' })
        titulo4 = workbook.add_format({'font_size': 8, 'align': 'center', 'bold':True , 'text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True})
        titulo10 = workbook.add_format({'font_size': 8, 'align': 'right', 'text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True, 'bold':True })
        titulo5 = workbook.add_format({'font_size': 8, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True, 'bold':False })
        titulo55 = workbook.add_format({'font_size': 8, 'align': 'left', 'text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True, 'bold':False })
        titulo9 = workbook.add_format({'font_size': 8, 'align': 'right', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False })
        titulo6 = workbook.add_format({'font_size': 8, 'align': 'center', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False, 'color': 'red'})
        titulo12 = workbook.add_format({'font_size': 8, 'align': 'right', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False, 'color': 'red'})
        titulo7 = workbook.add_format({'font_size': 8, 'align': 'left', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':False})
        titulo8 = workbook.add_format({'font_size': 8, 'align': 'center', 'text_wrap': True, 'bottom': False, 'top': False, 'left': False, 'right': False, 'bold':True})

        number_left = workbook.add_format({'font_size': 7, 'align': 'left', 'num_format': '#,##0.00'})
        number_right = workbook.add_format({'font_size': 7, 'align': 'right', 'num_format': '#,##0.00','text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True})
        number_rightT = workbook.add_format({'font_size': 7, 'align': 'right', 'num_format': '#,##0.00','bg_color': 'silver','text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True})
        number_right_bold = workbook.add_format({'font_size': 7, 'align': 'right', 'num_format': '#,##0.00', 'bold':True,'text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True})
        number_right_boldT = workbook.add_format({'font_size': 7, 'align': 'right', 'num_format': '#,##0.00', 'bold':True,'bg_color': 'silver','text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True})
        number_right_col = workbook.add_format({'font_size': 7, 'align': 'right', 'num_format': '#,##0.00','bg_color': 'silver'})
        number_center = workbook.add_format({'font_size': 7, 'align': 'center', 'num_format': '#,##0.00'})
        number_right_col.set_locked(False)

        letter1 = workbook.add_format({'font_size': 7, 'align': 'left', 'text_wrap': True})
        letter2 = workbook.add_format({'font_size': 7, 'align': 'left', 'bold':True})
        letter3 = workbook.add_format({'font_size': 7, 'align': 'right', 'text_wrap': True})
        letter3 = workbook.add_format({'font_size': 7, 'align': 'right', 'text_wrap': True})
        letter4 = workbook.add_format({'font_size': 8, 'align': 'left', 'text_wrap': True, 'bold': True,})
        letter4L = workbook.add_format({'font_size': 8, 'align': 'left', 'text_wrap': True, 'bold': True,'top': True,})
        titulo4T = workbook.add_format({'font_size': 7, 'align': 'left', 'text_wrap': True, 'bold': True,'bg_color': 'silver', 'bottom': True, 'top': True, 'left': True, 'right': True})
        letter444 = workbook.add_format({'font_size': 11, 'align': 'left', 'text_wrap': True, 'bold': True})
        letter44 = workbook.add_format({'font_size': 11, 'align': 'left', 'text_wrap': True, 'bold': True})
        letter_locked = letter3
        letter_locked.set_locked(False)

        filtro_afp = data['form']['as_name_afp']
        filtro_state = data['form']['as_state']
        # Aqui definimos en los anchos de columna
        sheet.set_column('A:A',7, letter1)
        sheet.set_column('B:B',10, letter1)
        sheet.set_column('C:C',25, letter1)
        sheet.set_column('D:D',10, letter1)
        sheet.set_column('E:E',10, letter1)
        sheet.set_column('F:F',8, letter1)
        sheet.set_column('G:G',15, letter1)
        sheet.set_column('H:H',10, letter1)
        sheet.set_column('I:I',7, letter1)
        sheet.set_column('J:J',7, letter1)
        sheet.set_column('K:K',10, letter1)

        sheet.merge_range('A1:D1', 'NOMBRE O RAZÓN SOCIAL: '+str(self.env.user.company_id.name), letter44)
        sheet.merge_range('A2:D2', 'PADRÓN MUNICIPAL: '+str(self.env.user.company_id.as_patronal_municipal), letter444)
        sheet.merge_range('L1:R1', 'NIT: '+str(self.env.user.company_id.vat), letter444)
        sheet.merge_range('L2:R2', 'NUMERO PATRONAL: '+str(self.env.user.company_id.as_numero_patronal), letter444)




        # Titulos, subtitulos, filtros y campos del reporte
        sheet.merge_range('A4:X4', 'PLANILLA DE SUELDOS Y SALARIOS', titulo1)
        payslip =  self.env[self._context['active_model']].sudo().search([('id', '=', data['form']['payslip_run_id'])])
        fecha_inicial = datetime.strptime(str(payslip.date_start), '%Y-%m-%d').strftime('%d/%m/%Y')
        fecha_final = datetime.strptime(str(payslip.date_end), '%Y-%m-%d').strftime('%d/%m/%Y')
        # sheet.merge_range('A5:X5', fecha_inicial +' - '+ fecha_final,titulo4)
        sheet.merge_range('A5:X5', '(En Bolivianos)',titulo4)
        sheet.write(5, 22, 'Mes', titulo5)
        sheet.write(6, 22, 'Año', titulo5)
        sheet.write(5, 23, self.get_mes(datetime.strptime(str(payslip.date_start), '%Y-%m-%d').strftime('%m')), titulo5)
        sheet.write(6, 23, datetime.strptime(str(payslip.date_start), '%Y-%m-%d').strftime('%Y'), titulo5)

        sheet.freeze_panes(9, 0)
        sheet.set_row(8, 50)

        filas = 7
        sheet.merge_range('A'+str(filas+1)+':A'+str(filas+2),'Nro.', titulo4)
        sheet.merge_range('B'+str(filas+1)+':B'+str(filas+2), 'Documento de identidad', titulo4)
        sheet.merge_range('C'+str(filas+1)+':C'+str(filas+2), 'Apellidos y nombres', titulo4)
        sheet.merge_range('D'+str(filas+1)+':D'+str(filas+2), 'País de nacionalidad', titulo4)
        sheet.merge_range('E'+str(filas+1)+':E'+str(filas+2), 'Fecha de nacimiento', titulo4)
        sheet.merge_range('F'+str(filas+1)+':F'+str(filas+2), 'Sexo(V/M)', titulo4)
        sheet.merge_range('G'+str(filas+1)+':G'+str(filas+2), 'Ocupación que desempeña', titulo4)
        sheet.merge_range('H'+str(filas+1)+':H'+str(filas+2), 'Fecha de ingreso', titulo4)
        sheet.merge_range('I'+str(filas+1)+':I'+str(filas+2), 'Días pagados (Mes)', titulo4)
        sheet.merge_range('J'+str(filas+1)+':J'+str(filas+2), 'Horas pagadas (Día)', titulo4)
        
        sheet.merge_range('K'+str(filas+1)+':K'+str(filas+2), '(1) Haber básico', titulo4)
        sheet.merge_range('L'+str(filas+1)+':L'+str(filas+2), '(2) Bono de Antigüedad', titulo4)
        sheet.merge_range('M'+str(filas+1)+':M'+str(filas+2), '(3) Bono de producción', titulo4)
        sheet.merge_range('N'+str(filas+1)+':N'+str(filas+2), '(4) Subsidio de frontera', titulo4)
        sheet.merge_range('O'+str(filas+1)+':O'+str(filas+2), '(5) Trabajo extraordi-nario y nocturno', titulo4)
        sheet.merge_range('P'+str(filas+1)+':P'+str(filas+2), '(6) Pago dominical y domingo trabajado', titulo4)
        sheet.merge_range('Q'+str(filas+1)+':Q'+str(filas+2), '(7) Otros bonos', titulo4)
        sheet.merge_range('R'+str(filas+1)+':R'+str(filas+2), '(8) TOTAL GANADO Suma (1 a 7)"', titulo4T)
        sheet.merge_range('S'+str(filas+1)+':S'+str(filas+2), '(9) Aporte a las AFPs', titulo4)
        sheet.merge_range('T'+str(filas+1)+':T'+str(filas+2), '(10) RC-IVA', titulo4)
        sheet.merge_range('U'+str(filas+1)+':U'+str(filas+2), '(11) Otros descuentos', titulo4)
        sheet.merge_range('V'+str(filas+1)+':V'+str(filas+2), '(12) TOTAL DESCUENTOS Suma (9 a 11)"', titulo4T)
        sheet.merge_range('W'+str(filas+1)+':W'+str(filas+2), '(13) LÍQUIDO PAGABLE (12-8)"', titulo4T)
        sheet.merge_range('X'+str(filas+1)+':X'+str(filas+2), '(14) Firma', titulo4)

        filas +=2
        cont = 0
        monto_sueldo_basico = 0.0
        monto_sueldo_ganado = 0.0
        monto_otros_ingresos = 0.0
        monto_mba = 0.0
        monto_subt = 0.0
        monto_afp = 0.0
        monto_asol = 0.0
        monto_subtbed = 0.0
        monto_total = 0.0
        query_movements = ("""
            select hp.id from hr_payslip hp
            join hr_employee he on he.id=hp.employee_id
            left join as_hr_employee_afp hea on he.as_name_afp = hea.id
            where 
            hp.state = '"""+str(filtro_state)+"""'
            and hp.payslip_run_id="""+str(payslip.id)+"""
            """+filtro+"""
            """)
        #_logger.debug(query_movements)
        self.env.cr.execute(query_movements)
        slip = [k for k in self.env.cr.fetchall()] 
        payslips = self.env['hr.payslip'].sudo().search([('id', 'in', slip)])
        inicio = filas
        for payslip in payslips:
            cont += 1
            birthday = '' 
            if payslip.employee_id.birthday:
                birthday = payslip.employee_id.birthday.strftime('%d/%m/%Y')
            sheet.write(filas, 0, cont, titulo5)
            sheet.write(filas, 1, payslip.employee_id.identification_id, titulo5)
            sheet.write(filas, 2, payslip.employee_id.name, titulo55)
            sheet.write(filas, 3, payslip.employee_id.country_id.name, titulo5)
            sheet.write(filas, 4, birthday, titulo5)
            genero=''
            if payslip.employee_id.gender =='male':
                genero='M'
            elif payslip.employee_id.gender =='female':
                genero='F'
            else:
                genero='O'
            sheet.write(filas, 5, genero, titulo5)
            sheet.write(filas, 6, payslip.employee_id.job_id.name, titulo5)
            if payslip.employee_id.as_fecha_ingreso:
                fechain= payslip.employee_id.as_fecha_ingreso.strftime('%d/%m/%Y')
            else:
                fechain = 0
            sheet.write(filas, 7, fechain, titulo5)
            total_dias= 0
            total_horas= 0
            for line in payslip.worked_days_line_ids:
                total_dias += line.number_of_days
                total_horas += line.number_of_hours
            #columns de la planilla
         
            sheet.write(filas, 8, total_dias, titulo5)
            sheet.write(filas, 9, payslip.employee_id.resource_calendar_id.hours_per_day, titulo5)

            sheet.write(filas, 10, self.get_total_rules(payslip.id,'BASIC',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            sheet.write(filas, 11, self.get_total_rules(payslip.id,'MBA',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            sheet.write(filas, 12, self.get_total_rules(payslip.id,'BOPRO',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            sheet.write(filas, 13, self.get_total_rules(payslip.id,'BOFRON',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            sheet.write(filas, 14, self.get_total_rules(payslip.id,'HOURS100',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            sheet.write(filas, 15, self.get_total_rules(payslip.id,'DOMIN100',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            sheet.write(filas, 16, self.get_total_rules(payslip.id,'OTING',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            sheet.write(filas, 17, self.get_total_rules(payslip.id,'SUBT',payslip.employee_id.id,payslip.contract_id.id),number_rightT) 
            sheet.write(filas, 18, self.get_total_rules(payslip.id,'AFP',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            sheet.write(filas, 19, self.get_total_rules(payslip.id,'IMRCR',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            sheet.write(filas, 20, self.get_total_rules(payslip.id,'OTDES',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            sheet.write(filas, 21, self.get_total_rules(payslip.id,'SUBTDED',payslip.employee_id.id,payslip.contract_id.id),number_rightT) 
            sheet.write(filas, 22, self.get_total_rules(payslip.id,'TOTAL',payslip.employee_id.id,payslip.contract_id.id),number_rightT) 
            sheet.write(filas, 23,'',number_right) 
        
            filas +=1
        #suma de columnas
        sheet.merge_range('A'+str(filas+1)+':J'+str(filas+1), 'TOTAL', number_right_bold)
        sheet.write(filas, 10, '=SUM(K'+str(inicio+1)+':K'+str(filas)+')',number_right_bold)
        sheet.write(filas, 11, '=SUM(L'+str(inicio+1)+':L'+str(filas)+')',number_right_bold)
        sheet.write(filas, 12, '=SUM(M'+str(inicio+1)+':M'+str(filas)+')',number_right_bold)
        sheet.write(filas, 13, '=SUM(N'+str(inicio+1)+':N'+str(filas)+')',number_right_bold)
        sheet.write(filas, 14, '=SUM(O'+str(inicio+1)+':O'+str(filas)+')',number_right_bold)
        sheet.write(filas, 15, '=SUM(P'+str(inicio+1)+':P'+str(filas)+')',number_right_bold)
        sheet.write(filas, 16, '=SUM(Q'+str(inicio+1)+':Q'+str(filas)+')',number_right_bold)
        sheet.write(filas, 17, '=SUM(R'+str(inicio+1)+':R'+str(filas)+')',number_right_boldT)
        sheet.write(filas, 18, '=SUM(S'+str(inicio+1)+':S'+str(filas)+')',number_right_bold)
        sheet.write(filas, 19, '=SUM(T'+str(inicio+1)+':T'+str(filas)+')',number_right_bold)
        sheet.write(filas, 20, '=SUM(U'+str(inicio+1)+':U'+str(filas)+')',number_right_bold)
        sheet.write(filas, 21, '=SUM(V'+str(inicio+1)+':V'+str(filas)+')',number_right_boldT)
        sheet.write(filas, 22, '=SUM(W'+str(inicio+1)+':W'+str(filas)+')',number_right_boldT)
        sheet.write(filas, 23, '',number_right_bold)
        filas +=2
        sheet.merge_range('A'+str(filas+1)+':P'+str(filas+1), 'Personas con discapacidad', titulo4)
        filas +=1
        sheet.write(filas, 0, 'Nro', titulo4)
        sheet.write(filas, 1, 'CI', titulo4)
        sheet.write(filas, 2, 'Fecha de nacimiento', titulo4)
        sheet.merge_range('D'+str(filas+1)+':G'+str(filas+1),'Nombre completo', titulo4)
        sheet.merge_range('H'+str(filas+1)+':I'+str(filas+1), 'Figura en planilla', titulo4)
        sheet.merge_range('J'+str(filas+1)+':L'+str(filas+1), 'N° del dependiente laboral relacionado', titulo4)
        sheet.merge_range('M'+str(filas+1)+':P'+str(filas+1), 'Relación del dependiente laboral con la persona con discapacidad', titulo4)
        filas+=1
        for i in range(0,3):
            sheet.write(filas, 0, '', titulo4)
            sheet.write(filas, 1, '', titulo4)
            sheet.write(filas, 2, '', titulo4)
            sheet.merge_range('D'+str(filas+1)+':G'+str(filas+1),'', titulo4)
            sheet.merge_range('H'+str(filas+1)+':I'+str(filas+1), '', titulo4)
            sheet.merge_range('J'+str(filas+1)+':L'+str(filas+1), '', titulo4)
            sheet.merge_range('M'+str(filas+1)+':P'+str(filas+1), '', titulo4)
            filas+=1
        sheet.merge_range('U'+str(filas+1)+':V'+str(filas+1), 'Fecha Impresión: ',titulo1p)
        fecha = (datetime.now() - timedelta(hours=4)).strftime('%d/%m/%Y %H:%M:%S')
        sheet.write(filas, 22, fecha,titulo1p)
        filas +=3
        sheet.merge_range('D'+str(filas+1)+':K'+str(filas+1),'NOMBRE DEL EMPLEADOR O REPRESENTANTE LEGAL', letter4L)
        sheet.merge_range('M'+str(filas+1)+':P'+str(filas+1), 'Figura en planilla', letter4L)
        sheet.merge_range('S'+str(filas+1)+':X'+str(filas+1), 'N° del dependiente laboral relacionado', letter4L)


    def get_total_rules(self,slip_id,code,employee_id,contract_id): 
        slip_line=self.env['hr.payslip.line'].sudo().search([('slip_id', '=', slip_id),('code', '=',code),('contract_id', '=',contract_id)],limit=1)
        if slip_line:
            return slip_line.total
        else:
            return 0.0    

    def get_mes(self,mes):
        mesesDic = {
            "01":'Enero',
            "02":'Febrero',
            "03":'Marzo',
            "04":'Abril',
            "05":'Mayo',
            "06":'Junio',
            "07":'Julio',
            "08":'Agosto',
            "09":'Septiembre',
            "10":'Octubre',
            "11":'Noviembre',
            "12":'Diciembre'
        }
        return mesesDic[str(mes)]