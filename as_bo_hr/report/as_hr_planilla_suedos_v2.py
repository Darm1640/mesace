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
    _name = 'report.as_bo_hr.planilla_sueldos_v_dos.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):     
        #fILTROS
        filtro =''
        if data['form']['as_name_afp']:
            filtro+= ' and hea.id in '+ str(data['form']['as_name_afp']).replace('[','(').replace(']',')')
        filtro_trabajo=''
        if data['form']['as_lugar_trabajo']:
            filtro_trabajo="""and ahlt.id = '"""+ str(data['form']['as_lugar_trabajo'])+"""'"""
        #estilos
        sheet = workbook.add_worksheet('Desarrollo Reporte Planilla de Sueldos y Salarios V2')
        titulo1 = workbook.add_format({'font_size': 13, 'align': 'center', 'text_wrap': True, 'bold':True })
        titulo_1 = workbook.add_format({'font_size': 10, 'align': 'center', 'text_wrap': True,})

        titulo5_contador = workbook.add_format({'font_size': 9, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True, 'bold':False,'border': 3 })
        titulo2 = workbook.add_format({'font_size': 9, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True })
        titulo4 = workbook.add_format({'font_size': 9, 'align': 'center', 'bold':True , 'text_wrap': True,})
        titulo_4 = workbook.add_format({'font_size': 9, 'align': 'center', 'bold':True , 'text_wrap': True,'top': True,})
        titulo4_4 = workbook.add_format({'font_size': 9, 'align': 'center', 'bold':True , 'text_wrap': True,'top': 5, 'bottom': 5,'right':3})
        titulo4_4_4 = workbook.add_format({'font_size': 9, 'align': 'center', 'bold':True , 'text_wrap': True,'top': 5, 'left': 5, 'bottom': 5, 'right':3})
        titulo4_4_44 = workbook.add_format({'font_size': 9, 'align': 'center', 'bold':True , 'text_wrap': True,'top': 5, 'right': 5, 'bottom': 5})
        titulo5 = workbook.add_format({'font_size': 9, 'align': 'right', 'text_wrap': True, 'bottom': 5, 'top': 5, 'left': 3, 'right': 3, 'num_format': '#,##0.00' })
        titulo_5 = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True, 'bottom': 5, 'top': 5, 'left': 5, 'right': 3, 'bold':True, 'num_format': '#,##0.00' })
        titulo_5_5 = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True, 'bottom': 5, 'top': 5, 'left': 3, 'right': 5, 'bold':True, 'num_format': '#,##0.00' })
        titulo_centrito = workbook.add_format({'font_size': 9, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True, 'bold':False, 'num_format': '#,##0.00','border': 3 })
        titulo_left = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True, 'bold':False, 'border': 3})
        number_right = workbook.add_format({'font_size': 9, 'align': 'right', 'num_format': '#,##0.00','text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True, 'border': 3})
        number_right_col = workbook.add_format({'font_size': 7, 'align': 'right', 'num_format': '#,##0.00','bg_color': 'silver'})
        number_right_col.set_locked(False)

        letter1 = workbook.add_format({'font_size': 7, 'align': 'left', 'text_wrap': True})
        letter3 = workbook.add_format({'font_size': 7, 'align': 'right', 'text_wrap': True})
        letter3 = workbook.add_format({'font_size': 7, 'align': 'right', 'text_wrap': True})
        
        letter444 = workbook.add_format({'font_size': 11, 'align': 'left', 'text_wrap': True, 'bold': True, 'bottom': True, 'top': True, 'left': True, 'right': True})
        letter_444 = workbook.add_format({'font_size': 11, 'align': 'right', 'text_wrap': True, 'bold': True, 'bottom': True, 'top': True, 'left': True, 'right': True})

        letter44 = workbook.add_format({'font_size': 11, 'align': 'left', 'text_wrap': True, 'bold': True})
        letter_locked = letter3
        letter_locked.set_locked(False)
        titulo2.set_align('vcenter')
        titulo4_4.set_align('vcenter')
        titulo5_contador.set_align('vcenter')
        titulo4_4_44.set_align('vcenter')
        filtro_afp = data['form']['as_name_afp']
        # Aqui definimos en los anchos de columna
        sheet.set_column('A:A',3, letter1)
        sheet.set_column('B:B',3, letter1)
        sheet.set_column('C:C',10, letter1)
        sheet.set_column('D:D',8, letter1)
        sheet.set_column('E:E',8, letter1)
        sheet.set_column('F:F',8, letter1)
        sheet.set_column('G:G',8, letter1)
        sheet.set_column('H:H',9, letter1)
        sheet.set_column('I:I',8, letter1)
        sheet.set_column('J:J',6, letter1)
        sheet.set_column('K:K',14, letter1)
        sheet.set_column('L:L',8, letter1)
        sheet.set_column('M:M',8, letter1)
        sheet.set_column('N:N',8, letter1)
        sheet.set_column('O:O',8, letter1)
        sheet.set_column('P:P',8, letter1)
        sheet.set_column('Q:Q',8, letter1)
        sheet.set_column('R:R',8, letter1)
        sheet.set_column('S:S',8, letter1)
        sheet.set_column('T:T',8, letter1)
        sheet.set_column('U:U',8, letter1)
        sheet.set_column('V:V',8, letter1)
        sheet.set_column('W:W',8, letter1)
        sheet.set_column('X:X',8, letter1)
        sheet.set_column('Y:Y',12, letter1)

        sheet.merge_range('B2:G2', 'ESPECTRO COMUNICACIONES S.R.L. (ESPECTROCOM S.R.L.)', letter44)
        sheet.merge_range('B3:E3', 'Dom.: '+str(self.env.user.company_id.street), letter44)
        sheet.merge_range('B4:E4', 'Teléfono: '+str(self.env.user.company_id.phone), letter44)
        id_lugar_teabajo=str(data['form']['as_lugar_trabajo'])
        nombre_ciudad_trabajo= self.env['as.hr.lugar.trabajo'].search([('id', '=', id_lugar_teabajo)])
        if nombre_ciudad_trabajo:
            sheet.merge_range('B5:E5', str(nombre_ciudad_trabajo.as_ciudad) +' - '+ 'Bolivia', letter44)
            sheet.merge_range('B8:E8', str(nombre_ciudad_trabajo.name), letter44)
            sheet.merge_range('X2:Y2',str(nombre_ciudad_trabajo.as_nro_patronal), letter_444)
        sheet.merge_range('U2:W2', 'N° Patronal: ', letter444)
        sheet.merge_range('U3:W3', 'Nº de Identificacion Uributaria:', letter444)
        sheet.merge_range('U4:W4', 'Nº Empleador Min. Trabajo : ', letter444)
        
        
        sheet.merge_range('X3:Y3', str(self.env.user.company_id.vat), letter_444)
        sheet.merge_range('X4:Y4', str(self.env.user.company_id.as_nro_empleador_min_trabajo), letter_444)
        # Titulos, subtitulos, filtros y campos del reporte
        sheet.merge_range('K5:N5', 'PLANILLA DE SUELDOS Y SALARIOS', titulo1)
        sheet.merge_range('K6:N6', 'Expresado en Bolivianos', titulo_1)
        payslip =  self.env[self._context['active_model']].sudo().search([('id', '=', data['form']['payslip_run_id'])])
        fecha_inicial = datetime.strptime(str(payslip.date_start), '%Y-%m-%d').strftime('%d/%m/%Y')
        fecha_final = datetime.strptime(str(payslip.date_end), '%Y-%m-%d').strftime('%d/%m/%Y')
        
        # sheet.write(5, 22, 'Mes', titulo5)
        # sheet.write(6, 22, 'Año', titulo5)
        
        mesesito=self.get_mes(datetime.strptime(str(payslip.date_start), '%Y-%m-%d').strftime('%m'))
        anito=datetime.strptime(str(payslip.date_start), '%Y-%m-%d').strftime('%Y')
        sheet.merge_range('S8:X8', 'CORRESPONDE A'+' '+str(mesesito)+' '+ str(anito), titulo1)
        titulo4.set_align('vcenter')
        titulo_left.set_align('vcenter')
        titulo5.set_align('vcenter')
        titulo_centrito.set_align('vcenter')
        number_right.set_align('vcenter')
        # sheet.freeze_panes(9, 0)
        # sheet.set_row(8, 50)

        filas = 9
        sheet.merge_range('B'+str(filas+1)+':B'+str(filas+2),'N°', titulo4_4_4)
        sheet.merge_range('C'+str(filas+1)+':C'+str(filas+2), 'Número de documento de identidad', titulo4_4)
        sheet.merge_range('D'+str(filas+1)+':D'+str(filas+2), 'Apellido Paterno', titulo4_4)
        sheet.merge_range('E'+str(filas+1)+':E'+str(filas+2), 'Apellido Materno', titulo4_4)
        sheet.merge_range('F'+str(filas+1)+':F'+str(filas+2), 'Primer nombre', titulo4_4)
        sheet.merge_range('G'+str(filas+1)+':G'+str(filas+2), 'Otros nombres', titulo4_4)
        sheet.merge_range('H'+str(filas+1)+':H'+str(filas+2), 'País de nacionalidad', titulo4_4)
        sheet.merge_range('I'+str(filas+1)+':I'+str(filas+2), 'Fecha de nacimiento', titulo4_4)
        sheet.merge_range('J'+str(filas+1)+':J'+str(filas+2), 'Sexo', titulo4_4)
        sheet.merge_range('K'+str(filas+1)+':K'+str(filas+2), 'Cargo', titulo4_4)
        sheet.merge_range('L'+str(filas+1)+':L'+str(filas+2), 'Fecha de ingreso', titulo4_4)
        sheet.merge_range('M'+str(filas+1)+':M'+str(filas+2), 'Días pagados (mes)', titulo4_4)
        sheet.merge_range('N'+str(filas+1)+':N'+str(filas+2), 'Haber Básico ', titulo4_4)
        sheet.merge_range('O'+str(filas+1)+':O'+str(filas+2), 'Horas extra', titulo4_4)
        sheet.merge_range('P'+str(filas+1)+':P'+str(filas+2), 'Bono de antigüedad', titulo4_4)
        sheet.merge_range('Q'+str(filas+1)+':Q'+str(filas+2), 'Otros bonos', titulo4_4)
        sheet.merge_range('R'+str(filas+1)+':R'+str(filas+2), 'Total ganado', titulo4_4)
        
        sheet.merge_range('S'+str(filas+1)+':V'+str(filas+1), 'DESCUENTOS', titulo4_4)
        
        sheet.merge_range('W'+str(filas+1)+':W'+str(filas+2), 'Total descuentos', titulo4_4)
        sheet.merge_range('X'+str(filas+1)+':X'+str(filas+2), 'Líquido pagable', titulo4_4)
        sheet.merge_range('Y'+str(filas+1)+':Y'+str(filas+2), 'FIRMA', titulo4_4_44)
        sheet.write(filas+1, 18, 'Aporte AFPs 12.71%', titulo4_4)
        sheet.write(filas+1, 19, 'Aporte Nacional Solidario', titulo4_4)
        sheet.write(filas+1, 20, 'RC-IVA', titulo4_4)
        sheet.write(filas+1, 21, 'Otros descuentos', titulo4_4)
        filas +=2
        cont = 0
        monto_sueldo_basico = 0.0
        tot_horas_extra = 0.0
        tot_bono_ant=0.0
        tot_otros_bonos=0.0
        totales_ganado=0.0
        tot_aport_afp=0.0
        tot_aporte_nac_solidario=0.0
        tot_rc_iva=0.0
        tot_descuentos=0.0
        tot_liquido_pagable=0.0
        sum_descuentos=0.0
        query_movements = ("""
            select hp.id from hr_payslip hp
            join hr_employee he on he.id=hp.employee_id
            left join as_hr_employee_afp hea on he.as_name_afp = hea.id
            left join as_hr_lugar_trabajo ahlt on he.as_lugar_de_trabajo = ahlt.id
            where 
            hp.payslip_run_id="""+str(payslip.id)+"""
            """+filtro+"""
            """+filtro_trabajo+"""
            """)
        #_logger.debug(query_movements)
        self.env.cr.execute(query_movements)
        slip = [k for k in self.env.cr.fetchall()] 
        payslips = self.env['hr.payslip'].sudo().search([('id', 'in', slip)]).sorted(lambda q: q.employee_id.apellido_1 or q.employee_id.apellido_2)
        inicio = filas
        for payslip in payslips:
            cont += 1 
            sheet.write(filas, 1, cont, titulo5_contador)
            if payslip.employee_id.identification_id != False:
                sheet.write(filas, 2, payslip.employee_id.identification_id, titulo_left)
            if payslip.employee_id.apellido_1 != False:
                sheet.write(filas, 3, payslip.employee_id.apellido_1,titulo_left)
            if payslip.employee_id.apellido_2 != False:
                sheet.write(filas, 4, payslip.employee_id.apellido_2, titulo_left)
            else:
                sheet.write(filas, 4, 'S/N', titulo_left)
            if payslip.employee_id.nombre != False:
                sheet.write(filas, 5, payslip.employee_id.nombre, titulo_left)
            if payslip.employee_id.nombre_2 != False:
                sheet.write(filas, 6, payslip.employee_id.nombre_2, titulo_left)
            else:
                sheet.write(filas, 6, 'S/N', titulo_left)
            if payslip.employee_id.country_id.name != False:
                sheet.write(filas, 7, payslip.employee_id.country_id.name, titulo_left)
            else:
                sheet.write(filas, 7, 'S/N', titulo_left)
            if payslip.employee_id.birthday != False:
                sheet.write(filas, 8, payslip.employee_id.birthday.strftime('%d/%m/%Y'), number_right)
            if payslip.employee_id.gender=='male':
                sheet.write(filas, 9, 'M', titulo_centrito)
            if payslip.employee_id.gender=='female':
                sheet.write(filas, 9, 'F', titulo_centrito)
            if payslip.employee_id.gender=='other':
                sheet.write(filas, 9, 'O', titulo_centrito)
            if payslip.employee_id.job_title != False:
                sheet.write(filas, 10, payslip.employee_id.job_title, titulo_left)
            id_contrato =self.env['hr.contract'].sudo().search([('employee_id', '=', payslip.employee_id.id)])
            if id_contrato:
                for i in id_contrato:
                    sheet.write(filas, 11, str(i.date_start.day)+'/'+str(i.date_start.month)+'/'+str(i.date_start.year), number_right)
               
            total_dias= 0
            total_horas= 0
            for line in payslip.worked_days_line_ids:
                if line.work_entry_type_id.code == 'WORK100':
                    total_dias += line.number_of_days
                    total_horas += line.number_of_hours
            #columns de la planilla
         
            sheet.write(filas, 12,total_dias, titulo_centrito) #dias
            sheet.write(filas, 13, self.get_total_rules(payslip.id,'BASIC',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            monto_sueldo_basico+=self.get_total_rules(payslip.id,'BASIC',payslip.employee_id.id,payslip.contract_id.id)
            
            sheet.write(filas, 14, 0,number_right) #PENDIENTE HORAS EXTRA
            tot_horas_extra+=0
            
            sheet.write(filas, 15, self.get_total_rules(payslip.id,'MBA',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            tot_bono_ant+=self.get_total_rules(payslip.id,'MBA',payslip.employee_id.id,payslip.contract_id.id)
            
            sheet.write(filas, 16, self.get_total_rules(payslip.id,'OTING',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            tot_otros_bonos+=self.get_total_rules(payslip.id,'OTING',payslip.employee_id.id,payslip.contract_id.id)
            
            sheet.write(filas, 17, self.get_total_rules(payslip.id,'SUBT',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            tot_ganado=self.get_total_rules(payslip.id,'SUBT',payslip.employee_id.id,payslip.contract_id.id)
            subti=self.get_total_rules(payslip.id,'SUBT',payslip.employee_id.id,payslip.contract_id.id)
            totales_ganado+=self.get_total_rules(payslip.id,'SUBT',payslip.employee_id.id,payslip.contract_id.id)
            
            sheet.write(filas, 18, self.get_total_rules(payslip.id,'AFP',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            tot_aport_afp+=self.get_total_rules(payslip.id,'AFP',payslip.employee_id.id,payslip.contract_id.id)
            
            sheet.write(filas, 19, self.get_total_rules(payslip.id,'ANS',payslip.employee_id.id,payslip.contract_id.id),number_right)
            tot_aporte_nac_solidario+=self.get_total_rules(payslip.id,'ANS',payslip.employee_id.id,payslip.contract_id.id)
            
            sheet.write(filas, 20, self.get_total_rules(payslip.id,'IMRCR',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            tot_rc_iva+=self.get_total_rules(payslip.id,'IMRCR',payslip.employee_id.id,payslip.contract_id.id)
            
            
            sheet.write(filas, 21, self.get_total_rules(payslip.id,'OTDES',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            otros_desc=self.get_total_rules(payslip.id,'OTDES',payslip.employee_id.id,payslip.contract_id.id)
            tot_descuentos+=self.get_total_rules(payslip.id,'OTDES',payslip.employee_id.id,payslip.contract_id.id)
            
            sheet.write(filas, 22, self.get_total_rules(payslip.id,'SUBTDED',payslip.employee_id.id,payslip.contract_id.id),number_right)
            sum_descuentos+=self.get_total_rules(payslip.id,'SUBTDED',payslip.employee_id.id,payslip.contract_id.id)
            
            sheet.write(filas, 23, self.get_total_rules(payslip.id,'TOTAL',payslip.employee_id.id,payslip.contract_id.id),number_right)
            tot_liquido_pagable+=self.get_total_rules(payslip.id,'TOTAL',payslip.employee_id.id,payslip.contract_id.id)
            sheet.write(filas, 24, '',number_right)
            filas+=1
        sheet.merge_range('B'+str(filas+1)+':M'+str(filas+1), 'TOTALES', titulo_5)
        sheet.write(filas, 13,monto_sueldo_basico, titulo5)
        sheet.write(filas, 14,tot_horas_extra, titulo5)
        sheet.write(filas, 15,tot_bono_ant, titulo5)
        sheet.write(filas, 16,tot_otros_bonos, titulo5)
        sheet.write(filas, 17,totales_ganado, titulo5)
        sheet.write(filas, 18,tot_aport_afp, titulo5)
        sheet.write(filas, 19,tot_aporte_nac_solidario, titulo5)
        sheet.write(filas, 20,tot_rc_iva, titulo5)
        sheet.write(filas, 21,tot_descuentos, titulo5)
        sheet.write(filas, 22,sum_descuentos, titulo5)
        sheet.write(filas, 23,tot_liquido_pagable, titulo5)
        sheet.write(filas, 24,'', titulo_5_5)
        
        
        sheet.merge_range('G'+str(filas+7)+':J'+str(filas+7), self.env.user.company_id.as_representante, titulo4)
        sheet.merge_range('G'+str(filas+8)+':J'+str(filas+8), 'NOMBRE DEL EMPLEADOR O REPRESENTANTE LEGAL', titulo_4)
        
        sheet.merge_range('L'+str(filas+7)+':N'+str(filas+7), self.env.user.company_id.as_ci_company, titulo4)
        sheet.merge_range('L'+str(filas+8)+':N'+str(filas+8), 'CEDULA DE IDENTIDAD ', titulo_4)
        
        sheet.merge_range('P'+str(filas+8)+':R'+str(filas+8), 'FIRMA', titulo_4)
        
        sheet.merge_range('L'+str(filas+12)+':N'+str(filas+12), 'TOTAL POR PAGAR A LA CNS VMT', titulo4)
        sheet.merge_range('L'+str(filas+13)+':N'+str(filas+13), totales_ganado * 0.10 , titulo_4)
        

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
    
    