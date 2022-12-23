# # -*- coding: utf-8 -*-

import datetime
from datetime import datetime
import pytz
from odoo import models,fields
from datetime import datetime, timedelta
from time import mktime
import logging
_logger = logging.getLogger(__name__)

class ProductosExportados(models.AbstractModel):
    _name = 'report.as_bo_stock.archivo_producto.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):

        sheet = workbook.add_worksheet('PRODUCTOS EXPORTADOS')
        letter1 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True})
        letter2 = workbook.add_format({'font_size': 12, 'align': 'center', 'text_wrap': True})
        letter3 = workbook.add_format({'font_size': 12, 'align': 'right', 'text_wrap': True})
        titulo2 = workbook.add_format({'font_size': 14, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True })
        sheet.set_column('A:A',20, letter1)
        sheet.set_column('B:B',20, letter3)
        sheet.set_column('C:C',20, letter3)
        sheet.set_column('D:D',20, letter3)
        sheet.set_column('E:E',20, letter3)
        sheet.set_column('F:F',20, letter3)
        sheet.set_column('G:G',20, letter3)
        sheet.set_column('H:H',20, letter3)
        sheet.set_column('I:I',20, letter3)
        sheet.set_column('J:J',20, letter3)
        sheet.set_column('K:K',20, letter3)
        sheet.set_column('L:L',20, letter3)
        sheet.set_column('M:M',20, letter3)
        sheet.set_column('N:N',20, letter3)
        sheet.set_column('O:O',20, letter3)
        sheet.set_column('P:P',20, letter3)
        sheet.set_column('Q:Q',20, letter3)
        sheet.set_column('R:R',20, letter3)
        sheet.set_column('S:S',20, letter3)
        sheet.set_column('T:T',20, letter3)
        sheet.set_column('U:U',20, letter3)

        datos = data.get('form')
        campos = self.env['ir.model.fields'].browse(datos.get('as_fields_ids'))
        if datos.get('product_template_ids') != []:
            productos = self.env['product.template'].browse(datos.get('product_template_ids'))
        else:
            productos = self.env['product.template'].search([('id', '!=', 0)])
            _logger.debug("\n\nIDS\n\n")
            # productos = self.env['product.template'].browse(ids_productos)
        col = 1
        obtener_datos = {}
        sheet.write(0, 0, 'id', titulo2)
        for f in campos:
            sheet.write(0, col, f.name, titulo2)
            obtener_datos[f.name] = col
            col += 1
        fila = 1
        cantidad = len(productos)
        for x in productos:
            datos = x.read()[0]
            sheet.write(fila,0, x.id)
            for f in campos:
                if not datos.get(f.name):
                    continue
                if f.ttype == 'many2one':
                    dato = datos.get(f.name)[0]
                elif f.ttype == 'many2many':
                    dato = ','.join(map(str,datos.get(f.name)))
                else:
                    dato = datos.get(f.name)
                sheet.write(fila,obtener_datos[f.name], dato)
            _logger.info('\n\nproducto  %r                  numero %r de %r \n\n', x.name,fila,cantidad)
            fila += 1
            