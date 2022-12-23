# # -*- coding: utf-8 -*-
import time
from openpyxl.styles import Alignment
import datetime
from datetime import datetime
import pytz
from odoo import models, fields
from datetime import datetime, timedelta
from time import mktime
import logging
from io import BytesIO
from odoo.tools.image import image_data_uri
import math
import locale
from urllib.request import urlopen
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class as_resumen_estado_cuentas(models.AbstractModel):
    _name = 'report.as_bo_accounting.as_resumen_estado_cuentas_xlsx.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        sheet = workbook.add_worksheet('Resumen de estado de cuentas detallado')
        titulo1 = workbook.add_format(
            {'font_size': 22, 'align': 'center', 'color': '#4682B4', 'top': True, 'bold': True})
        titulo2 = workbook.add_format(
            {'font_size': 12, 'align': 'center', 'bottom': True, 'top': True, 'right': True, 'left': True, 'bold': True,
             'color': '#ffffff', 'bg_color': '#4682B4', 'text_wrap': True, 'border_color': '#ffffff'})
        titulo3 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True, 'top': False, 'bold': True})
        titulo1_debajo = workbook.add_format(
            {'font_size': 15, 'align': 'center', 'text_wrap': True, 'top': False, 'bold': True, 'bottom': True})

        titulo3derecha = workbook.add_format(
            {'font_size': 10, 'align': 'right', 'text_wrap': True, 'top': False, 'bold': True})

        titulo4 = workbook.add_format(
            {'font_size': 12, 'align': 'left', 'text_wrap': True, 'bottom': False, 'top': False, 'bold': True,
             'color': '#4682B4'})

        number_left = workbook.add_format(
            {'font_size': 10, 'align': 'left', 'num_format': '#,##0.00', 'text_wrap': True, })
        number_center_sn = workbook.add_format({'font_size': 10, 'align': 'center', 'text_wrap': True, })
        number_left_totales = workbook.add_format(
            {'font_size': 12, 'align': 'left', 'num_format': '#,##0.00', 'bg_color': '#A9A9A9'})
        number_right_totales = workbook.add_format(
            {'font_size': 12, 'align': 'right', 'num_format': '#,##0.00', 'bg_color': '#A9A9A9'})

        number_right = workbook.add_format(
            {'font_size': 10, 'align': 'right', 'num_format': '#,##0.00', 'text_wrap': True, })
        number_right_col = workbook.add_format(
            {'font_size': 12, 'align': 'right', 'num_format': '#,##0.00', 'bg_color': 'silver'})
        number_center = workbook.add_format({'font_size': 10, 'align': 'center', 'num_format': '#,##0.00'})
        number_right_col.set_locked(False)

        letter1 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True})
        letter3 = workbook.add_format({'font_size': 12, 'align': 'right', 'text_wrap': True})
        letter_locked = letter3
        letter_locked.set_locked(True)
        # sheet.set_row(10,25)
        titulo2.set_align('vcenter')
        number_center_sn.set_align('vcenter')
        number_center.set_align('vcenter')
        number_right.set_align('vcenter')
        number_left.set_align('vcenter')
        sheet.set_column('A:N', 10, titulo2)
        # Aqui definimos en los anchos de columna
        sheet.set_column('A:A', 12, letter1)
        sheet.set_column('B:B', 18, letter1)
        sheet.set_column('C:C', 12, letter1)
        sheet.set_column('D:D', 30, letter1)
        sheet.set_column('E:E', 18, letter1)
        sheet.set_column('F:F', 18, letter1)
        sheet.set_column('G:G', 18, letter1)

        sheet.write(11, 0, 'FECHA', titulo2)
        sheet.write(11, 1, 'COMPROBANTE', titulo2)
        sheet.write(11, 2, 'Nro Factura', titulo2)
        sheet.write(11, 3, 'DETALLE', titulo2)
        sheet.write(11, 4, 'DEBE', titulo2)
        sheet.write(11, 5, 'HABER', titulo2)
        sheet.write(11, 6, 'SALDO', titulo2)

        # Titulos, subtitulos, filtros y campos del reporte
        sheet.merge_range('A5:G5', 'ESTADO DE CUENTA', titulo1)
        sheet.merge_range('A6:G6', '(Expresado en bolivianos)', titulo1_debajo)
        fecha = (datetime.now() - timedelta(hours=4)).strftime('%d/%m/%Y %H:%M:%S')
        # fecha_inicial = datetime.strptime(str(data['form']['fecha_inicial']), '%Y').strftime('%Y')
        url = image_data_uri(self.env.user.company_id.logo)
        image_data = BytesIO(urlopen(url).read())
        sheet.insert_image('A1:B5', url, {'image_data': image_data, 'x_scale': 0.22, 'y_scale': 0.17})

        sheet.write(8, 0, 'Usuario: ', titulo4)
        sheet.write(8, 1, str(self.env.user.partner_id.name), titulo3)
        sheet.write(9, 0, 'Cuenta: ', titulo4)
        sheet.write(9, 1, self.nombre_cuentas(data['form']), titulo3)

        sheet.write(8, 4, 'Fecha de impresion: ', titulo4)
        sheet.write(8, 5, fecha, titulo3)
        sheet.write(9, 4, 'Cliente: ', titulo4)
        sheet.merge_range('F10:G10', self.nombre_cliente(data['form']), titulo3)

        sheet.write(0, 4, 'NIT: ', titulo3)
        sheet.write(1, 4, 'DIRECCION: ', titulo3)
        sheet.write(2, 4, 'CELULAR, TELEFONO:', titulo3)
        sheet.merge_range('F1:G1', str(self.env.user.company_id.vat), titulo3derecha)
        sheet.merge_range('F2:G2', str(self.env.user.company_id.street), titulo3derecha)
        sheet.merge_range('F3:G3', str(self.env.user.company_id.phone), titulo3derecha)
        filas = 12
        # Preparando variables para cada casod e consulta
        # consultas
        if data['form']['as_nombre_cliente']:
            filtro_cliente = """AND rp.id = '""" + str(data['form']['as_nombre_cliente']) + """'"""
        else:
            filtro_cliente = ''
        consulta_productos = ("""
                select 
                    to_char(((am.date AT TIME ZONE'UTC' AT TIME ZONE'BOT' ) :: TIMESTAMP :: DATE ), 'DD/MM/YYYY' ) as  "fecha",
                    am.name as "comprobante",
                    aml.name as "detalle",
                    aml.debit,
                    aml.credit,
                    am.as_contable,
                    am.as_numero_factura_compra,
                    am.as_invoice_number,
                    am.move_type,
                    coalesce(rp.name,'') as socio
                    from account_move_line as aml
                    left join account_account as aa on aa.id = aml.account_id
                    left join account_move as am on am.id = aml.move_id
                    left join res_partner as rp on rp.id = aml.partner_id
                    where
                    am.state = 'posted'
                    AND (am.as_contable is NULL OR am.as_contable = False)
                    AND aml.account_id = '""" + str(data['form']['as_cuentas_proveedor']) + """'
                    """ + str(filtro_cliente) + """
                    AND (am.date AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date >= '""" + str(
            data['form']['start_date']) + """'
                    AND (am.date AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date <= '""" + str(data['form']['end_date']) + """'
                    order by am.date asc
                """)
        # """+str(filtro_products_po)+ """
        cont = 0
        self.env.cr.execute(consulta_productos)
        productoslinea = [j for j in self.env.cr.fetchall()]
        cont_1 = 0.0
        cont_2 = 0.0
        contador = 0
        saldo = 0.0
        if productoslinea != []:
            for linea in productoslinea:

                sheet.write(filas, 0, linea[0], number_center)
                sheet.write(filas, 1, linea[1], number_center)

                # columna numero de factura
                if linea[8] == 'out_invoice':  # comparando move_type muestro : as_invoice_number
                    sheet.write(filas, 2, linea[7], number_center_sn)

                if linea[8] == 'in_invoice':  # comparando move_type muestro : as_numero_factura_compra
                    sheet.write(filas, 2, linea[6], number_center_sn)

                if linea[8] != 'out_invoice' and linea[8] != 'in_invoice':  # comparando move_type muestro : 0
                    sheet.write(filas, 2, 0, number_center_sn)

                if linea[8] == 'out_invoice':
                    texto = ''
                    if linea[7] != 0:
                        texto = str(linea[7]) + texto
                    if linea[9] != '':
                        texto = texto + '|' + str(linea[9]) + '|' + linea[2]
                    # if texto != '':
                    #    texto = linea[2]
                    sheet.write(filas, 3, texto, number_right)

                if linea[8] == 'in_invoice':
                    texto = ''
                    if linea[6] != '0':
                        texto = linea[6] + texto
                    if linea[9] != '':
                        texto = texto + '|' + str(linea[9]) + '|' + linea[2]
                    # if texto != '':
                    #    texto = linea[2]
                    sheet.write(filas, 3, texto, number_right)
                if linea[8] != 'out_invoice' and linea[8] != 'in_invoice':
                    sheet.write(filas, 3, linea[2], number_right)

                cont_1 += linea[3]
                sheet.write(filas, 4, linea[3], number_right)
                sheet.write(filas, 5, linea[4], number_right)
                cont_2 += linea[4]
                saldo = saldo + linea[3] - linea[4]

                sheet.write(filas, 6, saldo, number_right)
                filas += 1
                contador += 1

        sheet.merge_range('A' + str(filas + 2) + ':D' + str(filas + 2), 'TOTAL ', number_left_totales)
        sheet.write(filas + 1, 4, cont_1, number_right_totales)
        sheet.write(filas + 1, 5, cont_2, number_right_totales)
        sheet.write(filas + 1, 6, saldo, number_right_totales)

    def nombre_cuentas(self, data):
        almacen = data['as_cuentas_proveedor']
        if almacen:
            filtro_nombre = self.env['account.account'].search([('id', '=', almacen)]).name
            filtro_code = self.env['account.account'].search([('id', '=', almacen)]).code
            nombre = str(filtro_code) + ' ' + str(filtro_nombre)
        return nombre

    def nombre_cliente(self, data):
        almacen = data['as_nombre_cliente']
        filtro_nombre = ''
        if almacen:
            filtro_nombre = self.env['res.partner'].search([('id', '=', almacen)]).name
        return filtro_nombre