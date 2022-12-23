# # -*- coding: utf-8 -*-

import datetime
from datetime import datetime
import pytz
from odoo import models,fields
from datetime import datetime, timedelta
from time import mktime
import logging
_logger = logging.getLogger(__name__)

class as_report_ministerio(models.AbstractModel):
    _name = 'report.as_bo_hr.planilla_ministerio.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):     
        #fILTROS
        
        filtro_trabajo=''
        if data['form']['as_lugar_trabajo']:
            filtro_trabajo="""and ahlt.id = '"""+ str(data['form']['as_lugar_trabajo'])+"""'"""
        #estilos
        sheet = workbook.add_worksheet('Desarrollo Reporte Planilla Ministerio')
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
        titulo5 = workbook.add_format({'font_size': 9, 'align': 'right', 'text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True })
        titulo_5 = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True, 'bold':True })
        titulo_5_5 = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True, 'bold':True })
        titulo_centrito = workbook.add_format({'font_size': 9, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True, 'bold':False })
        titulo_left = workbook.add_format({'font_size': 9, 'align': 'left', 'text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True, 'bold':False,})
        number_right = workbook.add_format({'font_size': 9, 'align': 'right','text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True,})
        number_meses = workbook.add_format({'font_size': 9, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True,})
        number_right_col = workbook.add_format({'font_size': 7, 'align': 'right','bg_color': 'silver'})
        number_right_col.set_locked(False)

        letter1 = workbook.add_format({'font_size': 7, 'align': 'left', 'text_wrap': True})
        letter3 = workbook.add_format({'font_size': 7, 'align': 'right', 'text_wrap': True})
        letter3 = workbook.add_format({'font_size': 7, 'align': 'right', 'text_wrap': True})
        
        letter444 = workbook.add_format({'font_size': 11, 'align': 'left', 'text_wrap': True, 'bold': True, 'bottom': True, 'top': True, 'left': True, 'right': True})
        letter_444 = workbook.add_format({'font_size': 11, 'align': 'right', 'text_wrap': True, 'bold': True, 'bottom': True, 'top': True, 'left': True, 'right': True})

        letter44 = workbook.add_format({'font_size': 11, 'align': 'left', 'text_wrap': True, 'bold': True})
    
        # Aqui definimos en los anchos de columna
        sheet.set_column('A:A',3, letter1)
        sheet.set_column('B:B',14, letter1)
        sheet.set_column('C:C',18, letter1)
        sheet.set_column('D:D',14, letter1)
        sheet.set_column('E:E',14, letter1)
        sheet.set_column('F:F',14, letter1)
        sheet.set_column('G:G',14, letter1)
        sheet.set_column('H:H',14, letter1)
        sheet.set_column('I:I',14, letter1)
        sheet.set_column('J:J',5, letter1)
        sheet.set_column('K:K',14, letter1)
        sheet.set_column('L:L',14, letter1)
        sheet.set_column('M:M',14, letter1)
        sheet.set_column('N:N',14, letter1)
        sheet.set_column('O:O',14, letter1)
        sheet.set_column('P:P',14, letter1)
        sheet.set_column('Q:Q',14, letter1)
        sheet.set_column('R:R',14, letter1)
        sheet.set_column('S:S',14, letter1)
        sheet.set_column('T:T',14, letter1)
        sheet.set_column('U:U',14, letter1)
        sheet.set_column('V:V',14, letter1)
        sheet.set_column('W:W',14, letter1)
        sheet.set_column('X:X',14, letter1)
        sheet.set_column('Y:Y',14, letter1)
        sheet.set_column('Z:Z',14, letter1)
        sheet.set_column('AF:AF',14, letter1)
        sheet.set_column('AG:AG',14, letter1)
        sheet.set_column('AI:AI',14, letter1)
        sheet.set_column('AK:AK',14, letter1)
        sheet.set_column('AL:AL',14, letter1)
        id_lugar_teabajo=str(data['form']['as_lugar_trabajo'])
        nombre_ciudad_trabajo= self.env['as.hr.lugar.trabajo'].search([('id', '=', id_lugar_teabajo)])
        # sheet.merge_range('F1:J1',str(self.env.user.company_id.name), letter_444)
        # sheet.merge_range('F2:J2', str(self.env.user.company_id.as_nro_empleador_min_trabajo), letter_444)
        # sheet.merge_range('F3:J3', str(self.env.user.company_id.vat), letter_444)
        # sheet.merge_range('F4:J4', 'VACIO', letter_444)

        # sheet.merge_range('A6:U6', 'PLANILLA DE PAGO DE AGUINALDO DE NAVIDAD', titulo1)
        # sheet.merge_range('A7:U7', '(En Bolivianos)', titulo_1)
        # payslip =  self.env[self._context['active_model']].sudo().search([('id', '=', data['form']['payslip_run_id'])])
        # fecha_inicial = datetime.strptime(str(payslip.date_start), '%Y-%m-%d').strftime('%d/%m/%Y')
        # fecha_final = datetime.strptime(str(payslip.date_end), '%Y-%m-%d').strftime('%d/%m/%Y')
        
        # sheet.write(5, 22, 'Mes', titulo5)
        # sheet.write(6, 22, 'Año', titulo5)
        
        # mesesito=self.get_mes(datetime.strptime(str(payslip.date_start), '%Y-%m-%d').strftime('%m'))
        # anito=datetime.strptime(str(payslip.date_start), '%Y-%m-%d').strftime('%Y')
        # sheet.merge_range('S8:U8', 'GESTION'+' ' +str(anito), titulo1)
        titulo4.set_align('vcenter')
        titulo_left.set_align('vcenter')
        titulo5.set_align('vcenter')
        titulo_centrito.set_align('vcenter')
        number_right.set_align('vcenter')
        letter_locked = letter3
        letter_locked.set_locked(False)
        titulo2.set_align('vcenter')
        titulo4_4.set_align('vcenter')
        titulo5_contador.set_align('vcenter')
        titulo4_4_44.set_align('vcenter')
        number_meses.set_align('vcenter')
        # sheet.freeze_panes(9, 0)
        # sheet.set_row(8, 50)
        filas = 0
        payslip =  self.env[self._context['active_model']].sudo().search([('id', '=', data['form']['payslip_run_id'])])

        sheet.merge_range('A'+str(filas+1)+':A'+str(filas+2),'Nro', titulo4_4_4)
        sheet.merge_range('B'+str(filas+1)+':B'+str(filas+2),'Tipo de documento de identidad', titulo4_4_4)
        sheet.merge_range('C'+str(filas+1)+':C'+str(filas+2), 'Número de documento de identidad', titulo4_4)
        sheet.merge_range('D'+str(filas+1)+':D'+str(filas+2), 'Lugar de expedición', titulo4_4)
        sheet.merge_range('E'+str(filas+1)+':E'+str(filas+2), 'Fecha de nacimiento', titulo4_4)
        sheet.merge_range('F'+str(filas+1)+':F'+str(filas+2), 'Apellido Paterno', titulo4_4)
        sheet.merge_range('G'+str(filas+1)+':G'+str(filas+2), 'Apellido Materno', titulo4_4)
        sheet.merge_range('H'+str(filas+1)+':H'+str(filas+2), 'Nombres', titulo4_4)
        sheet.merge_range('I'+str(filas+1)+':I'+str(filas+2), 'País de nacionalidad', titulo4_4)
        sheet.merge_range('J'+str(filas+1)+':J'+str(filas+2), 'Sexo', titulo4_4)
        sheet.merge_range('K'+str(filas+1)+':K'+str(filas+2), 'Jubilado', titulo4_4)
        sheet.merge_range('L'+str(filas+1)+':L'+str(filas+2), '¿Aporta a la AFP?', titulo4_4)
        sheet.merge_range('M'+str(filas+1)+':M'+str(filas+2), '¿Persona con discapacidad?', titulo4_4)
        sheet.merge_range('N'+str(filas+1)+':N'+str(filas+2), 'Tutor de persona con discapacidad', titulo4_4)
        sheet.merge_range('O'+str(filas+1)+':O'+str(filas+2), 'Fecha de ingreso', titulo4_4)
        sheet.merge_range('P'+str(filas+1)+':P'+str(filas+2), 'Fecha de retiro', titulo4_4)
        sheet.merge_range('Q'+str(filas+1)+':Q'+str(filas+2), 'Motivo retiro', titulo4_4)
        sheet.merge_range('R'+str(filas+1)+':R'+str(filas+2), 'Caja de salud', titulo4_4)
        sheet.merge_range('S'+str(filas+1)+':S'+str(filas+2), 'AFP a la que aporta', titulo4_4)
        sheet.merge_range('T'+str(filas+1)+':T'+str(filas+2), 'NUA/CUA', titulo4_4)
        sheet.merge_range('U'+str(filas+1)+':U'+str(filas+2), 'Sucursal o ubicación adicional', titulo4_4)
        sheet.merge_range('V'+str(filas+1)+':V'+str(filas+2), 'Clasificación laboral', titulo4_4)
        sheet.merge_range('W'+str(filas+1)+':W'+str(filas+2), 'Cargo', titulo4_4)
        sheet.merge_range('X'+str(filas+1)+':X'+str(filas+2), 'Modalidad de contrato', titulo4_4)
        sheet.merge_range('Y'+str(filas+1)+':Y'+str(filas+2), 'Tipo contrato', titulo4_4)
        sheet.merge_range('Z'+str(filas+1)+':Z'+str(filas+2), 'Días pagados', titulo4_4)
        sheet.merge_range('AA'+str(filas+1)+':AA'+str(filas+2), 'Horas pagadas', titulo4_4)
        sheet.merge_range('AB'+str(filas+1)+':AB'+str(filas+2), 'Haber Básico', titulo4_4)
        sheet.merge_range('AC'+str(filas+1)+':AC'+str(filas+2), 'Bono de antigüedad', titulo4_4)
        sheet.merge_range('AD'+str(filas+1)+':AD'+str(filas+2), 'Horas extra', titulo4_4)
        sheet.merge_range('AE'+str(filas+1)+':AE'+str(filas+2), 'Monto horas extra', titulo4_4)
        sheet.merge_range('AF'+str(filas+1)+':AF'+str(filas+2), 'Horas recargo nocturno', titulo4_4)
        sheet.merge_range('AG'+str(filas+1)+':AG'+str(filas+2), 'Monto horas extra nocturnas', titulo4_4)
        sheet.merge_range('AH'+str(filas+1)+':AH'+str(filas+2), 'Horas extra dominicales', titulo4_4)
        sheet.merge_range('AI'+str(filas+1)+':AI'+str(filas+2), 'Monto horas extra dominicales', titulo4_4)
        sheet.merge_range('AJ'+str(filas+1)+':AJ'+str(filas+2), 'Domingos trabajados', titulo4_4)
        sheet.merge_range('AK'+str(filas+1)+':AK'+str(filas+2), 'Monto domingo trabajado', titulo4_4)
        sheet.merge_range('AL'+str(filas+1)+':AL'+str(filas+2), 'Nro. Dominicales', titulo4_4)
        sheet.merge_range('AM'+str(filas+1)+':AM'+str(filas+2), 'Salario dominical', titulo4_4)
        sheet.merge_range('AN'+str(filas+1)+':AN'+str(filas+2), 'Bono producción', titulo4_4)
        sheet.merge_range('AO'+str(filas+1)+':AO'+str(filas+2), 'Subsidio frontera', titulo4_4)
        sheet.merge_range('AP'+str(filas+1)+':AP'+str(filas+2), 'Otros bonos y pagos', titulo4_4)
        sheet.merge_range('AQ'+str(filas+1)+':AQ'+str(filas+2), 'RC-IVA', titulo4_4)
        sheet.merge_range('AR'+str(filas+1)+':AR'+str(filas+2), 'Aporte Caja Salud', titulo4_4)
        sheet.merge_range('AS'+str(filas+1)+':AS'+str(filas+2), 'Aporte AFP', titulo4_4)
        sheet.merge_range('AT'+str(filas+1)+':AT'+str(filas+2), 'Otros descuentos', titulo4_4)
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
            left join as_hr_lugar_trabajo ahlt on he.as_lugar_de_trabajo = ahlt.id
            where 
            hp.state in ('draft','done')
            and hp.payslip_run_id="""+str(payslip.id)+"""
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
            if payslip.employee_id.as_documento != False:
                sheet.write(filas, 1, payslip.employee_id.as_documento, titulo_centrito)
            else:
                sheet.write(filas, 1, '', number_right)
            if payslip.employee_id.identification_id != False:
                sheet.write(filas, 2, payslip.employee_id.identification_id,number_right)
            else:
                sheet.write(filas, 2, '', number_right)
            if payslip.employee_id.as_expedito != False:
                sheet.write(filas, 3, payslip.employee_id.as_expedito, titulo_left)
            else:
                sheet.write(filas, 3, '', number_right)
            if payslip.employee_id.birthday != False:
                sheet.write(filas, 4, payslip.employee_id.birthday.strftime('%d/%m/%Y'), number_right)
            else:
                sheet.write(filas, 4, '', number_right)
            if payslip.employee_id.apellido_1 != False:
                sheet.write(filas, 5, payslip.employee_id.apellido_1, titulo_left)
            else:
                sheet.write(filas, 5, '', number_right)
            if payslip.employee_id.apellido_2 != False:
                sheet.write(filas, 6, payslip.employee_id.apellido_2, titulo_left)
            else:
                sheet.write(filas, 6, '', number_right)
            if payslip.employee_id.nombre != False:
                if payslip.employee_id.nombre_2 != False:
                    sheet.write(filas, 7, payslip.employee_id.nombre +' '+payslip.employee_id.nombre_2, titulo_left)
                else:
                    sheet.write(filas, 7, payslip.employee_id.nombre, titulo_left)
                    
            if payslip.employee_id.country_id.name != False:
                sheet.write(filas, 8, payslip.employee_id.country_id.name, titulo_left)
            else:
                sheet.write(filas, 8, '', titulo_left)
            
            if payslip.employee_id.gender=='male':
                sheet.write(filas, 9, 'H', titulo_centrito)
            if payslip.employee_id.gender=='female':
                sheet.write(filas, 9, 'M', titulo_centrito)
            if payslip.employee_id.gender=='other':
                sheet.write(filas, 9, 'Otro', titulo_centrito)
            if payslip.employee_id.as_jubilado != False:
                sheet.write(filas, 10, payslip.employee_id.as_jubilado, number_right)
            else:
                sheet.write(filas, 10, '', titulo_left)
            if payslip.employee_id.as_aportador_afp != False:
                sheet.write(filas, 11, payslip.employee_id.as_aportador_afp, number_right)
            else:
                sheet.write(filas, 11, '', titulo_left)
            if payslip.employee_id.as_persona_discapacidad != False:
                sheet.write(filas, 12, payslip.employee_id.as_persona_discapacidad, number_right)
            else:
                sheet.write(filas, 12, '', titulo_left)
            contrato = self.env['hr.contract'].sudo().search([('employee_id', '=', payslip.employee_id.id)])
            if payslip.employee_id.as_tutor_persona_discapacidad != False:
                sheet.write(filas, 13, payslip.employee_id.as_tutor_persona_discapacidad, number_right)
            else:
                sheet.write(filas, 13, '', number_right)
            if contrato:
                if contrato.date_start != False:
                    sheet.write(filas, 14, contrato.date_start.strftime('%d/%m/%Y'), number_right)
                else:
                    sheet.write(filas, 14, '', number_right)
            else:
                sheet.write(filas, 14, '', number_right)
            if contrato:
                if contrato.date_end != False:
                    sheet.write(filas, 15, contrato.date_end.strftime('%d/%m/%Y'), number_right)
                else:
                    sheet.write(filas, 15, '', number_right)
            else:
                sheet.write(filas, 15, '', number_right)
            if contrato:
                if contrato.as_motivo_retiro != False:
                    sheet.write(filas, 16, contrato.as_motivo_retiro, number_right)
                else:
                    sheet.write(filas, 16, '', number_right)
            else:
                sheet.write(filas, 16, '', number_right)
            if payslip.employee_id.as_caja_salud != False:
                sheet.write(filas, 17, payslip.employee_id.as_caja_salud, number_right)
            else:
                sheet.write(filas, 17, '', number_right)
            
            if payslip.employee_id.as_name_afp != False:
                sheet.write(filas, 18, payslip.employee_id.as_name_afp, number_right)
            else:
                sheet.write(filas, 18, '', number_right)    
            
            if payslip.employee_id.as_nua != False:
                sheet.write(filas, 19, payslip.employee_id.as_nua, number_right)
            else:
                sheet.write(filas, 19, '', number_right)
            if payslip.employee_id.as_lugar_de_trabajo != None:
                lugar_trabajo = self.env['as.hr.lugar.trabajo'].sudo().search([('id', '=', payslip.employee_id.as_lugar_de_trabajo.id)])
                if lugar_trabajo:
                    sheet.write(filas, 20, lugar_trabajo.as_codigo_sucursal, number_right) 
                else:
                    sheet.write(filas, 20, '', number_right) 
            else:  
                sheet.write(filas, 20, '', number_right) 
            if payslip.employee_id.as_clasificacion_laboral != False:
                sheet.write(filas, 21, payslip.employee_id.as_clasificacion_laboral, number_right)
            else:
                sheet.write(filas, 21, '', number_right) 
            
            if payslip.employee_id.job_title != False:
                sheet.write(filas, 22, payslip.employee_id.job_title, titulo_left)
            else:
                sheet.write(filas, 22, '', number_right)
            
            if contrato:
                if contrato.as_modalidad_contrato != False:
                    sheet.write(filas, 23, contrato.as_modalidad_contrato, number_right)
                else:
                    sheet.write(filas, 23, '', number_right)
            else:
                sheet.write(filas, 23, '', number_right)
            
            if contrato:
                if contrato.as_tipo_contrato != False:
                    sheet.write(filas, 24, contrato.as_tipo_contrato, number_right)
                else:
                    sheet.write(filas, 24, '', number_right)
            else:
                sheet.write(filas, 24, '', number_right)
            
            total_dias= 0
            total_horas= 0
            for line in payslip.worked_days_line_ids:
                total_dias += line.number_of_days
                total_horas += line.number_of_hours
            #columns de la planilla
            
            sheet.write(filas, 25,total_dias, titulo_centrito) #dias
            sheet.write(filas, 26,payslip.struct_id.type_id.default_resource_calendar_id.hours_per_day, titulo_centrito) #horas pagadas
            sheet.write(filas, 27, self.get_total_rules(payslip.id,'BASIC',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            monto_sueldo_basico = self.get_total_rules(payslip.id,'BASIC',payslip.employee_id.id,payslip.contract_id.id)
            sheet.write(filas, 28, self.get_total_rules(payslip.id,'MBA',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            tot_bono_ant = self.get_total_rules(payslip.id,'MBA',payslip.employee_id.id,payslip.contract_id.id)
            hor_extra = 0.0
            for line in payslip.input_line_ids:
                if line.input_type_id.name == 'Pago horas con reposicion de 1 Dias':
                    hor_extra += line.amount
            sheet.write(filas, 29, hor_extra,number_right) 
            sheet.write(filas, 30, self.get_total_rules(payslip.id,'HOURS100',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            sheet.write(filas, 31, 0,number_right) #FALTA SIMULACION
            sheet.write(filas, 32, 0,number_right) #FALTA SIMULACION
            sheet.write(filas, 33, 0,number_right) #FALTA SIMULACION
            sheet.write(filas, 34, 0,number_right) #FALTA SIMULACION
            
            dom_extra = 0.0
            for line in payslip.input_line_ids:
                if line.input_type_id.name == 'Pago Dominical Con reposicion de 1 Dias':
                    dom_extra += line.amount
            sheet.write(filas, 35, dom_extra,number_right)
            sheet.write(filas, 36, self.get_total_rules(payslip.id,'DOMIN100',payslip.employee_id.id,payslip.contract_id.id),number_right)
            sheet.write(filas, 37, 0,number_right) #FALTA SIMULACION
            sheet.write(filas, 38, 0,number_right) #FALTA SIMULACION
            sheet.write(filas, 39, 0,number_right) #estatico
            sheet.write(filas, 40, 0,number_right) #estatico
            sheet.write(filas, 41, self.get_total_rules(payslip.id,'OTHING',payslip.employee_id.id,payslip.contract_id.id),number_right)
            sheet.write(filas, 42, self.get_total_rules(payslip.id,'IMPRV',payslip.employee_id.id,payslip.contract_id.id),number_right)
            sheet.write(filas, 43, round((monto_sueldo_basico + tot_bono_ant)* 0.1,2),number_right)
            sheet.write(filas, 44, 0,number_right)
            sheet.write(filas, 45, 0,number_right)
            # monto_sueldo_basico+=self.get_total_rules(payslip.id,'BASIC',payslip.employee_id.id,payslip.contract_id.id)

            # sheet.write(filas, 11, self.get_total_rules(payslip.id,'MBA',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            # tot_bono_ant+=self.get_total_rules(payslip.id,'MBA',payslip.employee_id.id,payslip.contract_id.id)
            # sheet.write(filas, 12, self.get_total_rules(payslip.id,'BOPRO',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            # tot_bono_prod+=self.get_total_rules(payslip.id,'BOPRO',payslip.employee_id.id,payslip.contract_id.id)
            # sheet.write(filas, 13, '0',number_right) 
            # #frontera
            # frontera+=0
            
            
            # sheet.write(filas, 14, self.get_total_rules(payslip.id,'HOURS100',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            # tot_trabajo_nocturno+=self.get_total_rules(payslip.id,'HOURS100',payslip.employee_id.id,payslip.contract_id.id)
            
            # sheet.write(filas, 15, self.get_total_rules(payslip.id,'DOMIN100',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            # tot_dominical+=self.get_total_rules(payslip.id,'DOMIN100',payslip.employee_id.id,payslip.contract_id.id)
            
            # sheet.write(filas, 16, self.get_total_rules(payslip.id,'OTING',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            # tot_otros_bonos+=self.get_total_rules(payslip.id,'OTING',payslip.employee_id.id,payslip.contract_id.id)
            
            # sheet.write(filas, 17, self.get_total_rules(payslip.id,'SUBT',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            # totales_ganado+=self.get_total_rules(payslip.id,'SUBT',payslip.employee_id.id,payslip.contract_id.id)
            # sheet.write(filas, 18, meses,number_meses)
            # sheet.write(filas, 19, self.get_total_rules(payslip.id,'TOTAL',payslip.employee_id.id,payslip.contract_id.id),number_right) 
            # tot_liquido_pagable+=self.get_total_rules(payslip.id,'TOTAL',payslip.employee_id.id,payslip.contract_id.id)
            # sheet.write(filas, 20, '',number_right)
            filas+=1
        

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
    
    