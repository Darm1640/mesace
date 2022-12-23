import datetime
from datetime import datetime
import pytz
from odoo import models,fields
from datetime import datetime, timedelta
from time import mktime
import logging
_logger = logging.getLogger(__name__)

class as_reporte_ministerio(models.AbstractModel):
    _name = 'report.as_bo_sales_reports.planilla_ministerio.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):     
        #fILTROS
        
        filtro_trabajo=''
        if data['form']['ass_lugar_trabajo']:
            filtro_trabajo="""and ahlt.id = '"""+ str(data['form']['ass_lugar_trabajo'])+"""'"""
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
        sheet.set_column('E:E',12, letter1)
        sheet.set_column('F:F',12, letter1)
        sheet.set_column('G:G',12, letter1)
        sheet.set_column('H:H',14, letter1)
        sheet.set_column('I:I',12, letter1)
        sheet.set_column('J:J',5, letter1)
        sheet.set_column('K:K',12, letter1)
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
        sheet.set_column('V:V',12, letter1)
        sheet.set_column('W:W',15, letter1)
        sheet.set_column('X:X',12, letter1)
        sheet.set_column('Y:Y',12, letter1)
        sheet.set_column('Z:Z',12, letter1)
        sheet.set_column('AF:AF',14, letter1)
        sheet.set_column('AG:AG',14, letter1)
        sheet.set_column('AI:AI',14, letter1)
        sheet.set_column('AK:AK',14, letter1)
        sheet.set_column('AL:AL',14, letter1)
        id_lugar_teabajo=str(data['form']['ass_lugar_trabajo'])
        nombre_ciudad_trabajo= self.env['as.hr.lugar.trabajo'].search([('id', '=', id_lugar_teabajo)])
        
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
        payslip =  self.env[self._context['active_model']].sudo().search([('id', '=', data['form']['ass_payslip_run_id'])])

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
            select
                hp.id,
                he.as_documento,
                he.identification_id,
                he.as_expedito,
                he.birthday,
                he.apellido_1,
                he.apellido_2,
                he.nombre,
                he.nombre_2,
                rc.name as "nacionalidad",
                he.gender as "10 sexo",
                he.as_jubilado,
                he.as_aportador_afp,
                he.as_persona_discapacidad,
                he.id as "hr contract",
                he.as_tutor_persona_discapacidad,
                he.as_caja_salud,
                he.as_name_afp,
                ahea.name as "18 afp",
                he.as_nua as "19 nua",
                he.as_lugar_de_trabajo,
                ahlt.name,
                he.as_clasificacion_laboral as "22 clas laboral",
                he.job_title as  "23 titule",
                he.id
                
                from hr_payslip hp
                join hr_employee he on he.id=hp.employee_id
                left join as_hr_lugar_trabajo ahlt on he.as_lugar_de_trabajo = ahlt.id
                left join res_country as rc on rc.id = he.country_id
                left join as_hr_employee_afp as ahea on ahea.id = he.as_name_afp
                where 
                hp.state in ('draft','done')
            and hp.payslip_run_id="""+str(payslip.id)+"""
            """+filtro_trabajo+"""
           ORDER by he.apellido_1  ASC
            """)
        #_logger.debug(query_movements)
        self.env.cr.execute(query_movements)
        slip = [k for k in self.env.cr.fetchall()] 
        # payslips = self.env['hr.payslip'].sudo().search([('id', 'in', slip)], order='as_apellido_empleado desc')
        inicio = filas
        for payslip in slip:
            cont += 1 
            sheet.write(filas, 0, cont, titulo5_contador)
            if payslip[1] != False:
                sheet.write(filas, 1, payslip[1], titulo_centrito)
            else:
                sheet.write(filas, 1, '', number_right)
            if payslip[2] != False:
                sheet.write(filas, 2, payslip[2],number_right)
            else:
                sheet.write(filas, 2, '', number_right)
            if payslip[3] != False:
                if payslip[3] == 'SZ':
                    sheet.write(filas, 3, 'SC', titulo_left)
                if payslip[3] == 'CB':
                    sheet.write(filas, 3, 'CB', titulo_left)
                if payslip[3] == 'LP':
                    sheet.write(filas, 3, 'LP', titulo_left)
                if payslip[3] == 'OR':
                    sheet.write(filas, 3, 'OR', titulo_left)
                if payslip[3] == 'PT':
                    sheet.write(filas, 3, 'PT', titulo_left)
                if payslip[3] == 'TAR':
                    sheet.write(filas, 3, 'TJ', titulo_left)
                if payslip[3] == 'BN':
                    sheet.write(filas, 3, 'BN', titulo_left)
                if payslip[3] == 'CH':
                    sheet.write(filas, 3, 'CH', titulo_left)
                if payslip[3] == 'PD':
                    sheet.write(filas, 3, 'PD', titulo_left)
            else:
                sheet.write(filas, 3, '', number_right)
            if payslip[4] != False:
                sheet.write(filas, 4, payslip[4].strftime('%d/%m/%Y'), number_right)
            else:
                sheet.write(filas, 4, '', number_right)
            if payslip[5] != False:
                sheet.write(filas, 5, payslip[5], titulo_left)
            else:
                sheet.write(filas, 5, '', number_right)
            if payslip[6] != False:
                sheet.write(filas, 6, payslip[6], titulo_left)
            else:
                sheet.write(filas, 6, '', number_right)
            if payslip[7] != None:
                if payslip[8] != None:
                    sheet.write(filas, 7,  str(payslip[7]) +' '+ str(payslip[8]), titulo_left)
                else:
                    sheet.write(filas, 7, payslip[7], titulo_left)
                    
            if payslip[9] != False:
                sheet.write(filas, 8, payslip[9], titulo_left)
            else:
                sheet.write(filas, 8, '', titulo_left)
            
            if payslip[10]=='male':
                sheet.write(filas, 9, 'M', titulo_centrito)
            if payslip[10]=='female':
                sheet.write(filas, 9, 'F', titulo_centrito)
            if payslip[10]=='other':
                sheet.write(filas, 9, 'Otro', titulo_centrito)
            if payslip[11] != False:
                sheet.write(filas, 10, payslip[11], number_right)
            else:
                sheet.write(filas, 10, '', titulo_left)
            if payslip[12] != False:
                sheet.write(filas, 11, payslip[12], number_right)
            else:
                sheet.write(filas, 11, '', titulo_left)
            if payslip[13] != False:
                sheet.write(filas, 12, payslip[13], number_right)
            else:
                sheet.write(filas, 12, '', titulo_left)
            contrato = self.env['hr.contract'].sudo().search([('employee_id', '=', payslip[14])])
            if payslip[15] != False:
                sheet.write(filas, 13, payslip[15], number_right)
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
            if payslip[16] != False:
                sheet.write(filas, 17, payslip[16], number_right)
            else:
                sheet.write(filas, 17, '', number_right)
            
            if payslip[17]:
                if payslip[18] == 'Prevision':
                    sheet.write(filas, 18, 1, number_right)
                if payslip[18] == 'Futuro':
                    sheet.write(filas, 18, 2, number_right)
            else:
                sheet.write(filas, 18, '', number_right)    
            
            if payslip[19] != None:
                sheet.write(filas, 19, payslip[19], number_right)
            else:
                sheet.write(filas, 19, 0, number_right)
                
            if payslip[20] != None:
                if payslip[21] == 'OFICINA VILLAMONTES':
                    sheet.write(filas, 20, 2, number_right)
                if payslip[21] == 'OFICINA SANTA CRUZ':
                    sheet.write(filas, 20, 1, number_right)
            else:  
                sheet.write(filas, 20, '', number_right)
                
            
            if payslip[22] != False:
                sheet.write(filas, 21, payslip[22], number_right)
            else:
                sheet.write(filas, 21, '', number_right) 
            
            if payslip[23] != False:
                sheet.write(filas, 22, payslip[23], titulo_left)
            else:
                sheet.write(filas, 22, '', number_right)
            
            if contrato:
                if contrato.as_modalidad_contrato:
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
            payslips_lines = self.env['hr.payslip'].sudo().search([('id', '=', payslip[0])])
            for line in payslips_lines.worked_days_line_ids:
                if line.name == 'Attendance':
                    total_dias += line.number_of_days
                    total_horas += line.number_of_hours
            #columns de la planilla
            
            sheet.write(filas, 25,total_dias, titulo_centrito) #dias
            sheet.write(filas, 26,8, titulo_centrito) #horas pagadas
            sheet.write(filas, 27, self.get_total_rules(payslip[0],'BASIC',payslip[24],payslips_lines.contract_id.id),number_right) 
            monto_sueldo_basico = self.get_total_rules(payslip[0],'BASIC',payslip[24],payslips_lines.contract_id.id)
            sheet.write(filas, 28, self.get_total_rules(payslip[0],'MBA',payslip[24],payslips_lines.contract_id.id),number_right) 
            tot_bono_ant = self.get_total_rules(payslip[0],'MBA',payslip[24],payslips_lines.contract_id.id)
            hor_extra = 0.0
            for line in payslips_lines.input_line_ids:
                if line.input_type_id.name == 'Pago horas con reposicion de 1 Dias':
                    hor_extra += line.amount
            sheet.write(filas, 29, hor_extra,number_right) 
            sheet.write(filas, 30, self.get_total_rules(payslip[0],'HOURS100',payslip[24],payslips_lines.contract_id.id),number_right) 
            sheet.write(filas, 31, 0,number_right) #FALTA SIMULACION
            sheet.write(filas, 32, 0,number_right) #FALTA SIMULACION
            sheet.write(filas, 33, 0,number_right) #FALTA SIMULACION
            sheet.write(filas, 34, 0,number_right) #FALTA SIMULACION
            
            dom_extra = 0.0
            for line in payslips_lines.input_line_ids:
                if line.input_type_id.name == 'Pago Dominical Con reposicion de 1 Dias':
                    dom_extra += line.amount
            sheet.write(filas, 35, dom_extra,number_right)
            sheet.write(filas, 36, self.get_total_rules(payslip[0],'DOMIN100',payslip[24],payslips_lines.contract_id.id),number_right)
            sheet.write(filas, 37, 0,number_right) #FALTA SIMULACION
            sheet.write(filas, 38, 0,number_right) #FALTA SIMULACION
            sheet.write(filas, 39, 0,number_right) #estatico
            sheet.write(filas, 40, 0,number_right) #estatico
            sheet.write(filas, 41, self.get_total_rules(payslip[0],'OTHING',payslip[24],payslips_lines.contract_id.id),number_right)
            sheet.write(filas, 42, self.get_total_rules(payslip[0],'IMRCR',payslip[24],payslips_lines.contract_id.id),number_right)
            sheet.write(filas, 43, self.get_total_rules(payslip[0],'CNS',payslip[24],payslips_lines.contract_id.id),number_right)
            sheet.write(filas, 44, self.get_total_rules(payslip[0],'AFP',payslip[24],payslips_lines.contract_id.id),number_right)
            sheet.write(filas, 45, self.get_total_rules(payslip[0],'OTDES',payslip[24],payslips_lines.contract_id.id),number_right)
            
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