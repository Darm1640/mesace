# # -*- coding: utf-8 -*-

import datetime
from datetime import datetime
import pytz
from odoo import models,fields
from datetime import datetime, timedelta
from time import mktime
import logging
_logger = logging.getLogger(__name__)

class as_report_aguinaldo(models.AbstractModel):
    _name = 'report.as_bo_hr.planilla_aguinaldo.xlsx'
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
        sheet = workbook.add_worksheet('Desarrollo Reporte Planilla de Aguinaldo')
        titulo1 = workbook.add_format({'font_size': 13, 'align': 'center', 'text_wrap': True, 'bold':True })
        titulo_1 = workbook.add_format({'font_size': 10, 'align': 'center', 'text_wrap': True,})

        titulo5_contador = workbook.add_format({'font_size': 9, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True, 'bold':False })
        titulo2 = workbook.add_format({'font_size': 9, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True })
        titulo4 = workbook.add_format({'font_size': 9, 'align': 'center', 'bold':True , 'text_wrap': True,})
        titulo_4 = workbook.add_format({'font_size': 9, 'align': 'center', 'bold':True , 'text_wrap': True,'top': True,})
        titulo4_4 = workbook.add_format({'font_size': 9, 'align': 'center', 'bold':True , 'text_wrap': True,'top': True, 'bottom': True,'right':True})
        titulo_promedio = workbook.add_format({'font_size': 9, 'align': 'center', 'text_wrap': True})
        titulo4_4_4 = workbook.add_format({'font_size': 9, 'align': 'center', 'bold':True , 'text_wrap': True,'top': True, 'left': True, 'bottom': True, 'right':True})
        titulo4_4_44 = workbook.add_format({'font_size': 9, 'align': 'center', 'bold':True , 'text_wrap': True,'top': True, 'right': True, 'bottom': True})
        titulo5 = workbook.add_format({'font_size': 9, 'align': 'right', 'text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True, 'num_format': '#,##0.00' })
        titulo_5 = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True, 'bold':True, 'num_format': '#,##0.00' })
        titulo_5_5 = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True, 'bold':True, 'num_format': '#,##0.00' })
        titulo_centrito = workbook.add_format({'font_size': 9, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True, 'bold':False, 'num_format': '#,##0.00' })
        titulo_left = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True, 'bold':False,})
        number_right = workbook.add_format({'font_size': 9, 'align': 'right', 'num_format': '#,##0.00','text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True,})
        number_meses = workbook.add_format({'font_size': 9, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True,})
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
        number_meses.set_align('vcenter')
        filtro_afp = data['form']['as_name_afp']
        # Aqui definimos en los anchos de columna
        sheet.set_column('A:A',2, letter1)
        sheet.set_column('B:B',10, letter1)
        sheet.set_column('C:C',10, letter1)
        sheet.set_column('D:D',10, letter1)
        sheet.set_column('E:E',10, letter1)
        sheet.set_column('F:F',12, letter1)
        sheet.set_column('G:G',10, letter1)
        sheet.set_column('H:H',4, letter1)
        sheet.set_column('I:I',15, letter1)
        sheet.set_column('J:J',10, letter1)
        sheet.set_column('K:K',14, letter1)
        sheet.set_column('L:L',14, letter1)
        sheet.set_column('M:M',14, letter1)
        sheet.set_column('N:N',18, letter1)
        sheet.set_column('O:O',19, letter1)
        sheet.set_column('P:P',18, letter1)
        sheet.set_column('Q:Q',14, letter1)
        sheet.set_column('R:R',18, letter1)
        sheet.set_column('S:S',14, letter1)
        sheet.set_column('T:T',18, letter1)
        sheet.set_column('U:U',14, letter1)

        sheet.merge_range('A1:E1', 'NOMBRE O RAZON SOCIAL', letter44)
        sheet.merge_range('A2:E2', 'Nº EMPLEADOR MINISTERIO DE TRABAJO', letter44)
        sheet.merge_range('A3:E3','Nº DE NIT', letter44)
        sheet.merge_range('A4:E4','Nº DE EMPLEADOR (Caja de Salud)', letter44)
        id_lugar_teabajo=str(data['form']['as_lugar_trabajo'])
        nombre_ciudad_trabajo= self.env['as.hr.lugar.trabajo'].search([('id', '=', id_lugar_teabajo)])
        sheet.merge_range('F1:J1',str(self.env.user.company_id.name), letter_444)
        sheet.merge_range('F2:J2', str(self.env.user.company_id.as_nro_empleador_min_trabajo), letter_444)
        sheet.merge_range('F3:J3', str(self.env.user.company_id.vat), letter_444)
        sheet.merge_range('F4:J4', 'VACIO', letter_444)

        sheet.merge_range('A6:U6', 'PLANILLA DE PAGO DE AGUINALDO DE NAVIDAD', titulo1)
        sheet.merge_range('A7:U7', '(En Bolivianos)', titulo_1)
        payslip =  self.env[self._context['active_model']].sudo().search([('id', '=', data['form']['payslip_run_id'])])
        fecha_inicial = datetime.strptime(str(payslip.date_start), '%Y-%m-%d').strftime('%d/%m/%Y')
        fecha_final = datetime.strptime(str(payslip.date_end), '%Y-%m-%d').strftime('%d/%m/%Y')
        
        # sheet.write(5, 22, 'Mes', titulo5)
        # sheet.write(6, 22, 'Año', titulo5)
        
        mesesito=self.get_mes(datetime.strptime(str(payslip.date_start), '%Y-%m-%d').strftime('%m'))
        anito=datetime.strptime(str(payslip.date_start), '%Y-%m-%d').strftime('%Y')
        sheet.merge_range('S8:U8', 'GESTION'+' ' +str(anito), titulo1)
        titulo4.set_align('vcenter')
        titulo_left.set_align('vcenter')
        titulo5.set_align('vcenter')
        titulo_centrito.set_align('vcenter')
        number_right.set_align('vcenter')
        # sheet.freeze_panes(9, 0)
        # sheet.set_row(8, 50)
        filitas = 8
        sheet.write(filitas, 10, 'Promedio lo meses de SEP -OCT u NOV', titulo_promedio)
        sheet.write(filitas, 11, 'Promedio lo meses de SEP -OCT u NOV', titulo_promedio)
        sheet.write(filitas, 12, 'Promedio lo meses de SEP -OCT u NOV', titulo_promedio)
        sheet.write(filitas, 13, 'Promedio lo meses de SEP -OCT u NOV', titulo_promedio)
        sheet.write(filitas, 14, 'Promedio lo meses de SEP -OCT u NOV', titulo_promedio)
        sheet.write(filitas, 15, 'Promedio lo meses de SEP -OCT u NOV', titulo_promedio)
        sheet.write(filitas, 16, 'Promedio lo meses de SEP -OCT u NOV', titulo_promedio)
        filas = 9
        sheet.merge_range('A'+str(filas+1)+':A'+str(filas+2),'N°', titulo4_4_4)
        sheet.merge_range('B'+str(filas+1)+':B'+str(filas+2),'CARNET DE IDENTIDAD', titulo4_4_4)
        sheet.merge_range('C'+str(filas+1)+':C'+str(filas+2), 'APELLIDO PATERNO', titulo4_4)
        sheet.merge_range('D'+str(filas+1)+':D'+str(filas+2), 'APELLIDO MATERNO', titulo4_4)
        sheet.merge_range('E'+str(filas+1)+':E'+str(filas+2), 'NOMBRES', titulo4_4)
        sheet.merge_range('F'+str(filas+1)+':F'+str(filas+2), 'NACIONALIDAD', titulo4_4)
        sheet.merge_range('G'+str(filas+1)+':G'+str(filas+2), 'FECHA DE NACIMIENTO', titulo4_4)
        sheet.merge_range('H'+str(filas+1)+':H'+str(filas+2), 'SEXO', titulo4_4)
        sheet.merge_range('I'+str(filas+1)+':I'+str(filas+2), 'OCUPACIÓN QUE DESEMPEÑA', titulo4_4)
        sheet.merge_range('J'+str(filas+1)+':J'+str(filas+2), 'FECHA DE INGRESO', titulo4_4)
        sheet.merge_range('K'+str(filas+1)+':K'+str(filas+2), 'Promedio del haber básico', titulo4_4)
        sheet.merge_range('L'+str(filas+1)+':L'+str(filas+2), 'Promedio del bono de antigüedad', titulo4_4)
        sheet.merge_range('M'+str(filas+1)+':M'+str(filas+2), 'Promedio del bono de producción', titulo4_4)
        sheet.merge_range('N'+str(filas+1)+':N'+str(filas+2), 'Promedio del subsidio de frontera', titulo4_4)
        sheet.merge_range('O'+str(filas+1)+':O'+str(filas+2), 'Promedio trabajo extraordinario y nocturno', titulo4_4)
        sheet.merge_range('P'+str(filas+1)+':P'+str(filas+2), 'Promedio pago dominical y domingo trabajado', titulo4_4)
        sheet.merge_range('Q'+str(filas+1)+':Q'+str(filas+2), 'Promedio otros bonos', titulo4_4)
        sheet.merge_range('R'+str(filas+1)+':R'+str(filas+2), 'Promedio total ganado (H=A+B+C+D+E+F+G)', titulo4_4)
        sheet.merge_range('S'+str(filas+1)+':S'+str(filas+2), 'Meses trabajados', titulo4_4)
        sheet.merge_range('T'+str(filas+1)+':T'+str(filas+2), 'Total ganado después de duodécimas (J=H*I/12)', titulo4_4)
        sheet.merge_range('U'+str(filas+1)+':U'+str(filas+2), 'FIRMA DEL EMPLEADO', titulo4_4)
        
        filas +=2
        cont = 0
        monto_sueldo_basico = 0.0
        tot_bono_ant=0.0
        tot_otros_bonos=0.0
        tot_trabajo_nocturno=0.0
        tot_dominical=0.0
        tot_bono_prod=0.0
        totales_ganado=0.0
        tot_liquido_pagable=0.0
        frontera =0.0
        query_movements = ("""
            select hp.id from hr_payslip hp
            join hr_employee he on he.id=hp.employee_id
            left join as_hr_employee_afp hea on he.as_name_afp = hea.id
            left join as_hr_lugar_trabajo ahlt on he.as_lugar_de_trabajo = ahlt.id
            where 
            hp.state in ('draft','done')
            and hp.payslip_run_id="""+str(payslip.id)+"""
            """+filtro+"""
            """+filtro_trabajo+"""
            """)
        #_logger.debug(query_movements)
        self.env.cr.execute(query_movements)
        slip = [k for k in self.env.cr.fetchall()] 
        payslips = self.env['hr.payslip'].sudo().search([('id', 'in', slip)])
        inicio = filas
        for payslip in payslips:
            cont += 1 
            sheet.write(filas, 0, cont, titulo5_contador)
            if payslip.employee_id.identification_id != False:
                sheet.write(filas, 1, payslip.employee_id.identification_id, titulo_left)
            if payslip.employee_id.apellido_1 != False:
                sheet.write(filas, 2, payslip.employee_id.apellido_1,titulo_left)
            if payslip.employee_id.apellido_2 != False:
                sheet.write(filas, 3, payslip.employee_id.apellido_2, titulo_left)
            else:
                sheet.write(filas, 3, 'S/N', titulo_left)
            if payslip.employee_id.nombre != False:
                if payslip.employee_id.nombre_2 != False:
                    sheet.write(filas, 4, payslip.employee_id.nombre +' '+payslip.employee_id.nombre_2, titulo_left)
                else:
                    sheet.write(filas, 4, payslip.employee_id.nombre, titulo_left)
            if payslip.employee_id.country_id.name != False:
                sheet.write(filas, 5, payslip.employee_id.country_id.name, titulo_left)
            else:
                sheet.write(filas, 5, 'S/N', titulo_left)
            if payslip.employee_id.birthday != False:
                sheet.write(filas, 6, payslip.employee_id.birthday.strftime('%d/%m/%Y'), number_right)
            if payslip.employee_id.gender=='male':
                sheet.write(filas, 7, 'H', titulo_centrito)
            if payslip.employee_id.gender=='female':
                sheet.write(filas, 7, 'M', titulo_centrito)
            if payslip.employee_id.gender=='other':
                sheet.write(filas, 7, 'Otro', titulo_centrito)
            if payslip.employee_id.job_title != False:
                sheet.write(filas, 8, payslip.employee_id.job_title, titulo_left)
            id_contrato =self.env['hr.contract'].sudo().search([('employee_id', '=', payslip.employee_id.id)])
            if id_contrato:
                sheet.write(filas, 9, str(id_contrato.date_start.year) + '/'+str(id_contrato.date_start.month)+'/'+str(id_contrato.date_start.day), number_right)
                
            fecha_hoydia='2021-12-31 00:00:00'
            fecha_fact=id_contrato.date_start
            meses = abs((fecha_fact.year - 2021) * 12 + fecha_fact.month - 12)
            sheet.write(filas, 10, self.get_total_rules(payslip.id,'BASIC',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            monto_sueldo_basico+=self.get_total_rules(payslip.id,'BASIC',payslip.employee_id.id,payslip.contract_id.id)

            sheet.write(filas, 11, self.get_total_rules(payslip.id,'MBA',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            tot_bono_ant+=self.get_total_rules(payslip.id,'MBA',payslip.employee_id.id,payslip.contract_id.id)
            sheet.write(filas, 12, self.get_total_rules(payslip.id,'BOPRO',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            tot_bono_prod+=self.get_total_rules(payslip.id,'BOPRO',payslip.employee_id.id,payslip.contract_id.id)
            sheet.write(filas, 13, '0',number_right) 
            #frontera
            frontera+=0
            
            
            sheet.write(filas, 14, self.get_total_rules(payslip.id,'HOURS100',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            tot_trabajo_nocturno+=self.get_total_rules(payslip.id,'HOURS100',payslip.employee_id.id,payslip.contract_id.id)
            
            sheet.write(filas, 15, self.get_total_rules(payslip.id,'DOMIN100',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            tot_dominical+=self.get_total_rules(payslip.id,'DOMIN100',payslip.employee_id.id,payslip.contract_id.id)
            
            sheet.write(filas, 16, self.get_total_rules(payslip.id,'OTING',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            tot_otros_bonos+=self.get_total_rules(payslip.id,'OTING',payslip.employee_id.id,payslip.contract_id.id)
            
            sheet.write(filas, 17, self.get_total_rules(payslip.id,'SUBT',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            totales_ganado+=self.get_total_rules(payslip.id,'SUBT',payslip.employee_id.id,payslip.contract_id.id)
            sheet.write(filas, 18, meses,number_meses)
            sheet.write(filas, 19, self.get_total_rules(payslip.id,'TOTAL',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            tot_liquido_pagable+=self.get_total_rules(payslip.id,'TOTAL',payslip.employee_id.id,payslip.contract_id.id)
            sheet.write(filas, 20, '',number_right)
            filas+=1
        sheet.merge_range('A'+str(filas+1)+':J'+str(filas+1), 'TOTALES', titulo_5)
        sheet.write(filas, 10,monto_sueldo_basico, titulo5)
        sheet.write(filas, 11,tot_bono_ant, titulo5)
        sheet.write(filas, 12,tot_bono_prod, titulo5)
        sheet.write(filas, 13,frontera, titulo5)
        sheet.write(filas, 14,tot_trabajo_nocturno, titulo5)
        sheet.write(filas, 15,tot_dominical, titulo5)
        sheet.write(filas, 16,tot_otros_bonos, titulo5)
        sheet.write(filas, 17,totales_ganado, titulo5)
        sheet.write(filas, 18,'', titulo5)
        sheet.write(filas, 19,tot_liquido_pagable, titulo5)
        sheet.write(filas, 20,'', titulo_5_5)
        
        
        sheet.merge_range('C'+str(filas+7)+':G'+str(filas+7), self.env.user.company_id.as_representante, titulo4)
        sheet.merge_range('C'+str(filas+8)+':G'+str(filas+8), 'NOMBRE DEL EMPLEADOR O REPRESENTANTE LEGAL', titulo_4)
        
        sheet.merge_range('J'+str(filas+7)+':L'+str(filas+7), self.env.user.company_id.as_ci_company, titulo4)
        sheet.merge_range('J'+str(filas+8)+':L'+str(filas+8), 'Nº DE DOCUMENTO DE IDENTIDAD', titulo_4)
        
        sheet.merge_range('O'+str(filas+8)+':Q'+str(filas+8), 'FIRMA', titulo_4)
        
        sheet.merge_range('S'+str(filas+8)+':U'+str(filas+8), 'FECHA', titulo_4)
        
        # sheet.merge_range('L'+str(filas+12)+':N'+str(filas+12), 'TOTAL POR PAGAR A LA CNS VMT', titulo4)
        # sheet.merge_range('L'+str(filas+13)+':N'+str(filas+13), totales_ganado * 0.10 , titulo_4)
        

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
    
    