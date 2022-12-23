# # -*- coding: utf-8 -*-

import datetime
from datetime import datetime
import pytz
from odoo import models,fields
from datetime import datetime, timedelta
from time import mktime
import logging
import calendar
from dateutil.relativedelta import relativedelta
_logger = logging.getLogger(__name__)

class as_sales_emit_excel(models.AbstractModel):
    _name = 'report.as_bo_hr.planilla_tributaria.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):     
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
        number_right_boldTC = workbook.add_format({'font_size': 7, 'align': 'right', 'num_format': '#,##0.00', 'bold':True,'bg_color': 'silver','text_wrap': True, 'bottom': True, 'top': True, 'left': True, 'right': True})
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
        titulo4TC = workbook.add_format({'font_size': 7, 'align': 'left', 'text_wrap': True, 'bold': True,'bg_color': 'silver', 'bottom': True, 'top': True, 'left': True, 'right': True})
        letter444 = workbook.add_format({'font_size': 11, 'align': 'left', 'text_wrap': True, 'bold': True})
        letter44 = workbook.add_format({'font_size': 11, 'align': 'left', 'text_wrap': True, 'bold': True})
        letter_locked = letter3
        letter_locked.set_locked(False)

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
        sheet.set_column('J:J',10, letter1)
        sheet.set_column('K:K',10, letter1)
        sheet.set_column('X:X',10, letter1)

        sheet.merge_range('A1:D1', 'NOMBRE O RAZÓN SOCIAL: '+str(self.env.user.company_id.name), letter44)
        sheet.merge_range('A2:D2', 'PADRÓN MUNICIPAL: '+str(self.env.user.company_id.as_patronal_municipal), letter444)
        sheet.merge_range('L1:R1', 'NIT: '+str(self.env.user.company_id.vat), letter444)
        sheet.merge_range('L2:R2', 'NUMERO PATRONAL: '+str(self.env.user.company_id.as_numero_patronal), letter444)




        # Titulos, subtitulos, filtros y campos del reporte
        sheet.merge_range('A4:X4', 'PLANILLA TRIBUTARIA V3', titulo1)
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
        sheet.merge_range('A'+str(filas+1)+':A'+str(filas+2), 'Año', titulo4)
        sheet.merge_range('B'+str(filas+1)+':B'+str(filas+2), 'Periodo', titulo4)
        sheet.merge_range('C'+str(filas+1)+':C'+str(filas+2), 'Código Dependiente RC-IVA', titulo4)
        sheet.merge_range('D'+str(filas+1)+':D'+str(filas+2), 'Nombre', titulo4)
        sheet.merge_range('E'+str(filas+1)+':E'+str(filas+2), 'Primer Apellido', titulo4)
        sheet.merge_range('F'+str(filas+1)+':F'+str(filas+2), 'Segundo Apellido', titulo4)
        sheet.merge_range('G'+str(filas+1)+':G'+str(filas+2), 'Número de Documento de Identidad', titulo4)
        sheet.merge_range('H'+str(filas+1)+':H'+str(filas+2), 'Tipo de Documento', titulo4)
        sheet.merge_range('I'+str(filas+1)+':I'+str(filas+2), 'Novedades (I-V-D)', titulo4)
        sheet.merge_range('J'+str(filas+1)+':J'+str(filas+2), 'Monto de Ingreso Neto', titulo4T)
        sheet.merge_range('K'+str(filas+1)+':K'+str(filas+2), 'Dos (2) Salarios Mínimos Nacionales No Imponibles', titulo4)
        sheet.merge_range('L'+str(filas+1)+':L'+str(filas+2), 'Importe Sujeto a Impuesto (Base Imponible)', titulo4)
        sheet.merge_range('M'+str(filas+1)+':M'+str(filas+2), 'Impuesto RC-IVA', titulo4)
        sheet.merge_range('N'+str(filas+1)+':N'+str(filas+2), '13% de Dos (2) Salarios Mínimos Nacionales', titulo4)
        sheet.merge_range('O'+str(filas+1)+':O'+str(filas+2), 'Impuesto Neto RC-IVA', titulo4)
        sheet.merge_range('P'+str(filas+1)+':P'+str(filas+2), 'Formulario 110 CASILLA 693', titulo4)
        sheet.merge_range('Q'+str(filas+1)+':Q'+str(filas+2), 'Saldo a Favor del Fisco', titulo4)
        sheet.merge_range('R'+str(filas+1)+':R'+str(filas+2), 'Saldo a Favor del Dependiente', titulo4)
        sheet.merge_range('S'+str(filas+1)+':U'+str(filas+1), 'Saldo a favor del dependiente', titulo4)
        sheet.merge_range('V'+str(filas+1)+':V'+str(filas+2), 'Saldo Utilizado', titulo4)
        sheet.merge_range('W'+str(filas+1)+':W'+str(filas+2), 'Saldo  RC-IVA sugeto a retención', titulo4T)
        sheet.merge_range('X'+str(filas+1)+':X'+str(filas+2), 'Saldo deCrédito Fiscal a Favor del Dependiente para el mes Siguiente', titulo4T)
        sheet.write(filas+1, 18, 'del periodo anterior', titulo4)
        sheet.write(filas+1, 19, 'Mantenimiento de valor', titulo4)
        sheet.write(filas+1, 20, 'Saldo Actualizado', titulo4)
        filas+=2
        fila_total = filas
        filas+=1
        inicio = filas
        for nomina in payslip.slip_ids:
            sheet.write(filas, 0, datetime.strptime(str(payslip.date_start), '%Y-%m-%d').strftime('%Y'), titulo5)
            sheet.write(filas, 1, datetime.strptime(str(payslip.date_start), '%Y-%m-%d').strftime('%m'), titulo5)
            sheet.write(filas, 2, nomina.employee_id.as_code_iva, titulo5)
            sheet.write(filas, 3, nomina.employee_id.nombre, titulo5)
            sheet.write(filas, 4, nomina.employee_id.apellido_1, titulo5)
            sheet.write(filas, 5, nomina.employee_id.apellido_2, titulo5)
            sheet.write(filas, 6, nomina.employee_id.identification_id, titulo5)
            sheet.write(filas, 7, nomina.employee_id.as_documento, titulo5)
            sheet.write(filas, 8, nomina.employee_id.as_novedades, titulo5)
            total_bruto = float(self.get_total_rules(nomina.id,'SUBT',nomina.employee_id.id,nomina.contract_id.id))
            total_afp = float(self.get_total_rules(nomina.id,'AFP',nomina.employee_id.id,nomina.contract_id.id))
            total_m = total_bruto-total_afp
            sheet.write(filas, 9, total_m, number_rightT)
            sheet.write(filas, 10, float(nomina.as_smn_id.amount)*2, number_right)
            sheet.write(filas, 12, self.get_total_rules(nomina.id,'IMPRV',nomina.employee_id.id,nomina.contract_id.id), number_right)
            sheet.write(filas, 11, self.get_total_rules(nomina.id,'IMPSU',nomina.employee_id.id,nomina.contract_id.id), number_right)
            sheet.write(filas, 13, self.get_total_rules(nomina.id,'IMSMN',nomina.employee_id.id,nomina.contract_id.id), number_right)
            sheet.write(filas, 14, self.get_total_rules(nomina.id,'IMSMNN',nomina.employee_id.id,nomina.contract_id.id), number_right)
            sheet.write(filas, 15, self.get_total_rules(nomina.id,'FACT',nomina.employee_id.id,nomina.contract_id.id), number_right)
            sheet.write(filas, 16, self.get_total_rules(nomina.id,'SALFF',nomina.employee_id.id,nomina.contract_id.id), number_right)
            sheet.write(filas, 17, self.get_total_rules(nomina.id,'SALFD',nomina.employee_id.id,nomina.contract_id.id), number_right)
            sheet.write(filas, 18, self.get_total_rules(nomina.id,'SALFDA',nomina.employee_id.id,nomina.contract_id.id), number_right)
            sheet.write(filas, 19, self.get_total_rules(nomina.id,'SALMV',nomina.employee_id.id,nomina.contract_id.id), number_right)
            sheet.write(filas, 20, self.get_total_rules(nomina.id,'SALUFV',nomina.employee_id.id,nomina.contract_id.id), number_right)
            sheet.write(filas, 21, self.get_total_rules(nomina.id,'SALUT',nomina.employee_id.id,nomina.contract_id.id), number_right)
            sheet.write(filas, 22, self.get_total_rules(nomina.id,'IMRCR',nomina.employee_id.id,nomina.contract_id.id), number_rightT)
            sheet.write(filas, 23, self.get_total_rules(nomina.id,'SALDOSN',nomina.employee_id.id,nomina.contract_id.id), number_rightT)
            filas+=1
        sheet.merge_range('A'+str(fila_total+1)+':I'+str(fila_total+1), 'Importes globales para la Planilla', titulo4TC)
        sheet.write(fila_total, 9, '=SUM(J'+str(inicio+1)+':J'+str(filas)+')',number_right_boldTC)
        sheet.write(fila_total, 10, '=SUM(K'+str(inicio+1)+':K'+str(filas)+')',number_right_boldTC)
        sheet.write(fila_total, 12, '=SUM(L'+str(inicio+1)+':L'+str(filas)+')',number_right_boldTC)
        sheet.write(fila_total, 11, '=SUM(M'+str(inicio+1)+':M'+str(filas)+')',number_right_boldTC)
        sheet.write(fila_total, 13, '=SUM(N'+str(inicio+1)+':N'+str(filas)+')',number_right_boldTC)
        sheet.write(fila_total, 14, '=SUM(O'+str(inicio+1)+':O'+str(filas)+')',number_right_boldTC)
        sheet.write(fila_total, 15, '=SUM(P'+str(inicio+1)+':P'+str(filas)+')',number_right_boldTC)
        sheet.write(fila_total, 16, '=SUM(Q'+str(inicio+1)+':Q'+str(filas)+')',number_right_boldTC)
        sheet.write(fila_total, 17, '=SUM(R'+str(inicio+1)+':R'+str(filas)+')',number_right_boldTC)
        sheet.write(fila_total, 18, '=SUM(S'+str(inicio+1)+':S'+str(filas)+')',number_right_boldTC)
        sheet.write(fila_total, 19, '=SUM(T'+str(inicio+1)+':T'+str(filas)+')',number_right_boldTC)
        sheet.write(fila_total, 20, '=SUM(U'+str(inicio+1)+':U'+str(filas)+')',number_right_boldTC)
        sheet.write(fila_total, 21, '=SUM(V'+str(inicio+1)+':V'+str(filas)+')',number_right_boldTC)
        sheet.write(fila_total, 22, '=SUM(W'+str(inicio+1)+':W'+str(filas)+')',number_right_boldTC)
        sheet.write(fila_total, 23, '=SUM(X'+str(inicio+1)+':X'+str(filas)+')',number_right_boldTC)




        # sheet.merge_range('A'+str(filas+1)+':A'+str(filas+2),'Nro.', titulo4)
        # sheet.merge_range('B'+str(filas+1)+':B'+str(filas+2), 'Documento de identidad', titulo4)
        # sheet.merge_range('C'+str(filas+1)+':C'+str(filas+2), 'Apellidos y nombres', titulo4)
        # sheet.merge_range('D'+str(filas+1)+':D'+str(filas+2), 'País de nacionalidad', titulo4)
        # sheet.merge_range('E'+str(filas+1)+':E'+str(filas+2), 'Fecha de nacimiento', titulo4)
        # sheet.merge_range('F'+str(filas+1)+':F'+str(filas+2), 'Sexo(V/M)', titulo4)
        # sheet.merge_range('G'+str(filas+1)+':G'+str(filas+2), 'Ocupación que desempeña', titulo4)
        # sheet.merge_range('H'+str(filas+1)+':H'+str(filas+2), 'Fecha de ingreso', titulo4)
        # sheet.merge_range('I'+str(filas+1)+':I'+str(filas+2), 'Días pagados (Mes)', titulo4)
        # sheet.merge_range('J'+str(filas+1)+':J'+str(filas+2), 'Horas pagadas (Día)', titulo4)
        
        # sheet.merge_range('K'+str(filas+1)+':K'+str(filas+2), '(1) Haber básico', titulo4)
        # sheet.merge_range('L'+str(filas+1)+':L'+str(filas+2), '(2) Bono de Antigüedad', titulo4)
        # sheet.merge_range('M'+str(filas+1)+':M'+str(filas+2), '(3) Bono de producción', titulo4)
        # sheet.merge_range('N'+str(filas+1)+':N'+str(filas+2), '(4) Subsidio de frontera', titulo4)
        # sheet.merge_range('O'+str(filas+1)+':O'+str(filas+2), '(5) Trabajo extraordi-nario y nocturno', titulo4)
        # sheet.merge_range('P'+str(filas+1)+':P'+str(filas+2), '(6) Pago dominical y domingo trabajado', titulo4)
        # sheet.merge_range('Q'+str(filas+1)+':Q'+str(filas+2), '(7) Otros bonos', titulo4)
        # sheet.merge_range('R'+str(filas+1)+':R'+str(filas+2), '(8) TOTAL GANADO Suma (1 a 7)"', titulo4T)
        # sheet.merge_range('S'+str(filas+1)+':S'+str(filas+2), '(9) Aporte a las AFPs', titulo4)
        # sheet.merge_range('T'+str(filas+1)+':T'+str(filas+2), '(10) RC-IVA', titulo4)
        # sheet.merge_range('U'+str(filas+1)+':U'+str(filas+2), '(11) Otros descuentos', titulo4)
        # sheet.merge_range('V'+str(filas+1)+':V'+str(filas+2), '(12) TOTAL DESCUENTOS Suma (9 a 11)"', titulo4T)
        # sheet.merge_range('W'+str(filas+1)+':W'+str(filas+2), '(13) LÍQUIDO PAGABLE (12-8)"', titulo4T)
        # sheet.merge_range('X'+str(filas+1)+':X'+str(filas+2), '(14) Firma', titulo4)



        # consulta_rate = ("""
        #     select rcr.rate from res_currency_rate rcr
        #     inner join res_currency rc on rc.id = rcr.currency_id
        #     where 
        #     rc.name='UFV' and 
        #     rcr.name in ('""" + str(fechai) + """', '""" + str(fechaf) + """') order by rcr.name limit 2
        #     """)
        # self.env.cr.execute(consulta_rate)
        # rates = [k for k in self.env.cr.fetchall()]
        # tasa_inicial = 0.0
        # tasa_final = 0.0
        # if len(rates)>0:
        #     tasa_inicial = rates[0][0]
        # if len(rates)>1:
        #     tasa_final = rates[1][0]
        # sheet.write(4, 6, 'UFV INICIAL: ', letter4)
        # sheet.write(4, 7, tasa_inicial, number_right4)
        # sheet.write(4, 8, 'UFV FINAL: ', letter4)
        # sheet.write(4, 9, tasa_final, number_right4)
        # smns =self.env['as.hr.smn'].sudo().search([('state', '=', 'V')])
        # sheet.write(5, 6, 'SMN: ', letter4)
        # sheet.write(5, 7, smns.amount, number_right4)
        # sheet.freeze_panes(10, 0)

        # filas = 8
        # sheet.merge_range('A'+str(filas+1)+':A'+str(filas+2),'NO', titulo4)
        # sheet.write(filas, 1, 'AÑO', titulo4)
        # sheet.write(filas, 2, 'PERIODO', titulo4)
        # sheet.write(filas, 3, 'CODIGO DEPENDIENTE RC-IVA', titulo4)
        # sheet.write(filas, 4, 'NOMBRES', titulo4)
        # sheet.write(filas, 5, 'PRIMER APELLIDO', titulo4)
        # sheet.write(filas, 6, 'SEGUNDO APELLIDO', titulo4)
        # sheet.write(filas, 7, 'NRO DOCUMENTO IDENTIDAD', titulo4)
        # sheet.write(filas, 8, 'TIPO DE DOCUMENTO', titulo4)
        # sheet.write(filas, 9, 'NOVEDADES', titulo4)
        # sheet.merge_range('K'+str(filas+1)+':K'+str(filas+2),'TOTAL GANADO INGRESOS COTIZABLES', titulo4)
        # sheet.merge_range('L'+str(filas+1)+':L'+str(filas+2),'AFPs 12.71%', titulo4)
        # sheet.merge_range('M'+str(filas+1)+':M'+str(filas+2),'ANS 10%-5%-1%', titulo4)
        # sheet.merge_range('N'+str(filas+1)+':N'+str(filas+2),'OTROS INGRESOS NO COTIZABLES', titulo4)
        # sheet.write(filas, 14, 'MONTO INGRESO NETO', titulo4)
        # sheet.write(filas, 15, '2 MINIMOS NACIONALES NO IMPONIBLES', titulo4)
        # sheet.write(filas, 16, 'IMP SUJETO A IMPUESTO (BASE IMPONIBLE)', titulo4)
        # sheet.write(filas, 17, 'IMPUESTO RC-IVA', titulo4)
        # sheet.write(filas, 18, '13% de 2 SALARIOS MINIMOS NACIONALES', titulo4)
        # sheet.write(filas, 19, 'IMPUESTO NETO RC-IVA', titulo4)
        # sheet.write(filas, 20, 'F-110 13% DE FACTURAS PRESENTADAS', titulo4)
        # sheet.write(filas, 21, 'SALDO A FAVOR DEL FISCO', titulo4)
        # sheet.write(filas, 22, 'SALDO A FAVOR DEL DEPENDIENTE', titulo4)
        # sheet.write(filas, 23, 'SALDO A FAVOR DEL DEPENDIENTE PERIODO ANTERIOR', titulo4)
        # sheet.write(filas, 24, 'MNTTO DE VALOR SALDO PERIODO ANTERIOR', titulo4)
        # sheet.write(filas, 25, 'SALDO DEL PERIODO ANTERIOR ACTUALIZADO', titulo4)
        # sheet.write(filas, 26, 'SALDO UTILIZADO', titulo4)
        # sheet.write(filas, 27, 'IMPUESTO  RC-IVA RETENIDO ', titulo4)
        # sheet.write(filas, 28, 'SALDO PARA EL SIGUIETE MES', titulo4)
        # sheet.set_row(8,20,titulo4)
        # sheet.set_row(9,20,titulo4)

        # sheet.write(filas+1, 1,  'a', titulo4)
        # sheet.write(filas+1, 2,  'b', titulo4)
        # sheet.write(filas+1, 3,  'c', titulo4)
        # sheet.write(filas+1, 4,  'd', titulo4)
        # sheet.write(filas+1, 5,  'e', titulo4)
        # sheet.write(filas+1, 6,  'f', titulo4)
        # sheet.write(filas+1, 7,  'g', titulo4)
        # sheet.write(filas+1, 8,  'h', titulo4)
        # sheet.write(filas+1, 9, 'i', titulo4)
        # sheet.write(filas+1, 10, '', titulo4)
        # sheet.write(filas+1, 11, '', titulo4)
        # sheet.write(filas+1, 12, '', titulo4)
        # sheet.write(filas+1, 13, '', titulo4)
        # sheet.write(filas+1, 14, 'j', titulo4)
        # sheet.write(filas+1, 15, 'k', titulo4)
        # sheet.write(filas+1, 16, 'l=j-k (si j>k)', titulo4)
        # sheet.write(filas+1, 17, 'm=l*13%', titulo4)
        # sheet.write(filas+1, 18, 'n', titulo4)
        # sheet.write(filas+1, 19, 'o=m-n (si m>n)', titulo4)
        # sheet.write(filas+1, 20, 'p', titulo4)
        # sheet.write(filas+1, 21, 'q=o-p (si o>p)', titulo4)
        # sheet.write(filas+1, 22, 'r=p-o (si p>o)', titulo4)
        # sheet.write(filas+1, 23, 's', titulo4)
        # sheet.write(filas+1, 24, 't', titulo4)
        # sheet.write(filas+1, 25, 'u=s+t', titulo4)
        # sheet.write(filas+1, 26, 'v=u (si u<=q) v=q (si q<u)', titulo4)
        # sheet.write(filas+1, 27, 'w=q-v (SI q>v)', titulo4)
        # sheet.write(filas+1, 28, 'x=r+u-v', titulo4)

        # filas +=2
        # cont = 0
        # monto_sueldos = 0.0
        # monto_afp = 0.0
        # monto_ans = 0.0
        # monto_otros = 0.0
        # monto_neto = 0.0
        # monto_dos_salarios = 0.0
        # monto_base_imponible = 0.0
        # monto_impuestorc = 0.0
        # monto_smn = 0.0
        # monto_neto_ec= 0.0
        # monto_facturas= 0.0
        # monto_fisco= 0.0
        # monto_dependiente= 0.0
        # monto_saldo_anterior= 0.0
        # monto_saldo_anterior= 0.0
        # monto_anterior_actualizado= 0.0
        # monto_saldo_utilizado= 0.0
        # monto_saldo_perido= 0.0
        # monto_saldo_impuestorc= 0.0
        # monto_mes_siguiente= 0.0
        # for payslip in payslip.slip_ids:
        #     cont += 1 
        #     sheet.write(filas, 0, cont, titulo5)
        #     sheet.write(filas, 1, datetime.strptime(str( payslip.payslip_run_id.date_start), '%Y-%m-%d').strftime('%Y'), titulo5)
        #     sheet.write(filas, 2, datetime.strptime(str( payslip.payslip_run_id.date_start), '%Y-%m-%d').strftime('%m'), titulo5)
        #     sheet.write(filas, 3, payslip.employee_id.as_code_iva, titulo5)
        #     sheet.write(filas, 4, payslip.employee_id.nombre, titulo5)
        #     sheet.write(filas, 5, payslip.employee_id.apellido_1, titulo5)
        #     sheet.write(filas, 6, payslip.employee_id.apellido_2, titulo5)
        #     sheet.write(filas, 7, payslip.employee_id.identification_id, titulo5)
        #     sheet.write(filas, 8, payslip.employee_id.as_documento, titulo5)
        #     sheet.write(filas, 9, payslip.employee_id.as_novedades, titulo5)
        #     total_asignacion = 0.0
        #     total_deduccion = 0.0
        #     total_fact = 0.0
        #     total_saldo = 0.0
        #     for line in payslip.line_ids:
        #         if line.code == 'SUBT':
        #             sheet.write(filas, 10, line.total, number_right2)   
        #             total_asignacion += line.total
        #             monto_sueldos += line.total    
        #             sheet.write(filas, 12, line.total, number_right2) 
        #         elif line.code == 'OTING':
        #             sheet.write(filas, 13, line.total, number_right2) 
        #             total_asignacion += line.total  
        #             monto_afp +=  line.total  
        #         elif line.code == 'AFP':
        #             sheet.write(filas, 11, line.total, number_right2)  
        #             total_deduccion += line.total 
        #             monto_ans +=  line.total  
        #             sheet.write(filas, 12, line.total, number_right2)  
        #         elif line.code == 'ASOL':
        #             sheet.write(filas, 13, line.total, number_right2)  
        #             total_deduccion += line.total 
        #             monto_otros +=  line.total  
        #         elif line.code == 'FACT':
        #             total_fact += line.total 
        #         elif line.code == 'SALFAV':
        #             total_saldo += line.total 
        #     total_ingreso = total_asignacion - total_deduccion   
        #     monto_neto += total_ingreso
        #     total_sueldo = float(payslip.as_smn_id.amount)*2 
        #     monto_dos_salarios += total_sueldo
        #     sheet.write(filas, 14, round(total_ingreso,3), number_right0)
        #     sheet.write(filas, 15, round(float(payslip.as_smn_id.amount)*2,3), number_right4)
        #     if total_ingreso > total_sueldo:
        #         base_impuesto = total_ingreso - total_sueldo
        #     else:
        #         base_impuesto = 0
        #     monto_base_imponible +=base_impuesto
        #     sheet.write(filas, 16, round(base_impuesto,0), number_right0)
        #     base_impuesto_iva = base_impuesto*0.13
        #     monto_impuestorc += base_impuesto_iva
        #     base_sin = 0.0
        #     if base_impuesto_iva > 0.0:
        #         base_sin = base_impuesto_iva * 0.13
        #     monto_smn += base_sin
        #     sheet.write(filas, 17, round(base_impuesto*0.13,3), number_right0)
        #     sheet.write(filas, 18, round(base_sin,3), number_right0)
        #     monto_n = 0.0
        #     if base_impuesto_iva > base_sin:
        #         monto_n =base_impuesto_iva - base_sin
        #     sheet.write(filas, 19, round(monto_n,3), number_right0)
        #     monto_neto_ec +=  monto_n
        #     sheet.write(filas, 20, round(total_fact,3), number_right0)
        #     monto_facturas += total_fact
        #     fisco = 0.0
        #     if monto_n > total_fact:
        #         fisco = monto_n - total_fact
        #     sheet.write(filas, 21, round(fisco,3), number_right0)
        #     monto_fisco += fisco
        #     dependiente = 0.0
        #     if total_fact > monto_n:
        #         dependiente = total_fact - monto_n
        #     monto_dependiente += dependiente
        #     sheet.write(filas, 22, round(dependiente,3), number_right0)
        #     sheet.write(filas, 23, round(total_saldo,3), number_right0)
        #     monto_saldo_anterior += total_saldo
        #     monto_anterior =0
        #     if tasa_final > 0:
        #         monto_anterior = (tasa_inicial/tasa_final)*total_saldo
        #     monto_anterior_actualizado += monto_anterior
        #     sheet.write(filas, 24, round(monto_anterior,0), number_right0)
        #     anterior_actual = monto_anterior+total_saldo
        #     monto_saldo_utilizado += anterior_actual
        #     sheet.write(filas, 25, round(anterior_actual,0), number_right0)
        #     saldo_utilizado = 0.0
        #     if anterior_actual <= fisco:
        #         saldo_utilizado =  anterior_actual
        #     else:
        #         saldo_utilizado =  fisco
        #     monto_saldo_perido += saldo_utilizado
        #     sheet.write(filas, 26, round(saldo_utilizado,0), number_right0)
        #     impuestorc= 0
        #     if fisco > saldo_utilizado:
        #         impuestorc = fisco - saldo_utilizado
        #     monto_saldo_impuestorc +=impuestorc
        #     sheet.write(filas, 27, round(impuestorc,0), number_right0)
        #     saldo_mes_siguiente = (dependiente + saldo_utilizado)- saldo_utilizado
        #     monto_mes_siguiente += saldo_mes_siguiente
        #     sheet.write(filas, 28, round(saldo_mes_siguiente,0), number_right0)

        #     filas +=1
        # filas +=1
        # sheet.merge_range('A'+str(filas+1)+':J'+str(filas+1),'TOTALES', titulo4)
        # sheet.write(filas, 10, monto_sueldos, number_right_bold)
        # sheet.write(filas, 11, monto_afp, number_right_bold)
        # sheet.write(filas, 12, monto_ans, number_right_bold)
        # sheet.write(filas, 13, monto_otros, number_right_bold)
        # sheet.write(filas, 14, monto_neto, number_right_bold)
        # sheet.write(filas, 15, monto_dos_salarios, number_right_bold)
        # sheet.write(filas, 16, monto_base_imponible, number_right_bolds0bb)
        # sheet.write(filas, 17, monto_impuestorc, number_right_bolds0bb)
        # sheet.write(filas, 18, monto_smn, number_right_bolds0bb)
        # sheet.write(filas, 19, monto_neto_ec, number_right_bolds0bb)
        # sheet.write(filas, 20, monto_facturas, number_right_bolds0bb)
        # sheet.write(filas, 21, monto_fisco, number_right_bolds0bb)
        # sheet.write(filas, 22, monto_dependiente, number_right_bolds0bb)
        # sheet.write(filas, 23, monto_saldo_anterior, number_right_bolds0bb)
        # sheet.write(filas, 24, monto_anterior_actualizado, number_right_bolds0bb)
        # sheet.write(filas, 25, monto_saldo_utilizado, number_right_bolds0bb)
        # sheet.write(filas, 26, monto_saldo_perido, number_right_bolds0bb)
        # sheet.write(filas, 27, monto_saldo_impuestorc, number_right_bolds0bb)
        # sheet.write(filas, 28, monto_mes_siguiente, number_right_bolds0bb)
        # filas +=1
        # sheet.merge_range('A'+str(filas+1)+':M'+str(filas+2),'FORMULARIO 608', titulo10)
        # sheet.write(filas, 14, 'Cod. 13', titulo5)
        # sheet.write(filas+1, 14, monto_neto, number_right_boldsb)
        # sheet.write(filas, 15, 'Cod. 26', titulo5)
        # sheet.write(filas+1, 15, monto_dos_salarios, number_right_boldsb)
        # sheet.write(filas, 16, 'Cod. 27', titulo5)
        # sheet.write(filas+1, 16, monto_base_imponible, number_right0b)
        # sheet.write(filas, 17, 'Cod. 2000', titulo5)
        # sheet.write(filas+1, 17, monto_impuestorc, number_right0b)
        # sheet.write(filas, 18, 'Cod. 215', titulo5)
        # sheet.write(filas+1, 18, monto_smn, number_right0b)
        # sheet.write(filas, 19, 'Cod. 1215', titulo5)
        # sheet.write(filas+1, 19, monto_neto_ec, number_right0b)
        # sheet.write(filas, 20, 'Cod. 202', titulo5)
        # sheet.write(filas+1, 20, monto_facturas, number_right_bolds0b)
        # sheet.write(filas, 21, 'Cod. 2001', titulo5)
        # sheet.write(filas+1, 21, monto_fisco, number_right_bolds0b)
        # sheet.write(filas, 22, 'Cod. 634', titulo5)
        # sheet.write(filas+1, 22, monto_dependiente, number_right_bolds0b)
        # sheet.write(filas, 23, 'Cod. 635', titulo5)
        # sheet.write(filas+1, 23, monto_saldo_anterior, number_right_bolds0b)
        # sheet.write(filas, 24, 'Cod. 648', titulo5)
        # sheet.write(filas+1, 24, monto_anterior_actualizado, number_right_bolds0b)
        # sheet.write(filas, 25, 'Cod. 649', titulo5)
        # sheet.write(filas+1, 25, monto_saldo_utilizado, number_right_bolds0b)
        # sheet.write(filas, 26, 'Cod. 650', titulo5)
        # sheet.write(filas+1, 26, monto_saldo_perido, number_right_bolds0b)
        # sheet.write(filas, 27, 'Cod. 909', titulo5)
        # sheet.write(filas+1, 27, monto_saldo_impuestorc, number_right_bolds0b)
        # sheet.write(filas, 28, 'Cod. 592', titulo5)
        # sheet.write(filas+1, 28, monto_mes_siguiente, number_right_bolds0b)

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

    def get_total_rules(self,slip_id,code,employee_id,contract_id): 
        slip_line=self.env['hr.payslip.line'].sudo().search([('slip_id', '=', slip_id),('code', '=',code),('contract_id', '=',contract_id)],limit=1)
        if slip_line:
            return slip_line.total
        else:
            return 0.0    