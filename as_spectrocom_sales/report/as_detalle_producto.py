
# # -*- coding: utf-8 -*-
import xlwt
import datetime
import xlsxwriter
from datetime import datetime
import pytz
from odoo import models,fields
from datetime import datetime, timedelta
from time import mktime
from dateutil import relativedelta
import time
import locale
import operator
import itertools
from datetime import datetime, timedelta
from dateutil import relativedelta
import xlwt
from xlsxwriter.workbook import Workbook
from odoo.tools.translate import _
import base64
from io import BytesIO
from odoo.tools.image import image_data_uri
import locale
from odoo import netsvc
from odoo import tools
from urllib.request import urlopen
from time import mktime
import logging
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)

class as_sales_emit_exce(models.AbstractModel):
    _inherit = 'report.as_bo_sales_reports.product_detail_report_xls.xlsx'

    def generate_xlsx_report(self, workbook, data, lines):     
    
        sheet = workbook.add_worksheet('Resumen de ventas')
        titulo1 = workbook.add_format({'font_size': 22 ,'align': 'center','color': '#4682B4','top': True, 'bold':True})
        tituloAzul = workbook.add_format({'font_size': 12, 'align': 'center',  'bottom': True, 'top': True, 'bold':True })
        titulo2 = workbook.add_format({'font_size': 12, 'align': 'center', 'text_wrap': True, 'bottom': True, 'top': True, 'right': True, 'left': True, 'bold':True,'color':'#ffffff','bg_color':'#4682B4'})
        titulo3 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True,'top': False, 'bold':True })
        titulo3_number = workbook.add_format({'font_size': 10, 'align': 'right', 'text_wrap': True, 'bottom': True, 'top': True, 'bold':True, 'num_format': '#,##0.00' })
        titulo4 = workbook.add_format({'font_size': 12, 'align': 'left', 'text_wrap': True, 'bottom': False, 'top': False, 'bold':True,'color':'#4682B4'})
        number_left = workbook.add_format({'font_size': 10, 'align': 'left', 'num_format': '#,##0.00'})
        number_right = workbook.add_format({'font_size': 10, 'align': 'right', 'num_format': '#,##0.00'})
        number_right_bold = workbook.add_format({'font_size': 10, 'align': 'right', 'num_format': '#,##0.00', 'bold':True})
        number_right_col = workbook.add_format({'font_size': 10, 'align': 'right', 'num_format': '#,##0.00','bg_color': 'silver'})
        number_center = workbook.add_format({'font_size': 10, 'align': 'center', 'num_format': '#,##0.00'})
        number_right_col.set_locked(False)

        letter1 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True})
        letter2 = workbook.add_format({'font_size': 10, 'align': 'left', 'bold':True})
        letter3 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True})
        letter4 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True, 'bold': True})
        letter_locked = letter3
        letter_locked.set_locked(False)

        # Aqui definimos en los anchos de columna
        sheet.set_column('A:A',25, letter1)
        sheet.set_column('B:B',25, letter1)
        sheet.set_column('C:C',20, letter1)
        sheet.set_column('D:D',15, letter1)
        sheet.set_column('E:E',20, letter1)
        sheet.set_column('F:F',20, letter1)
        sheet.set_column('G:G',25, letter1)
        sheet.set_column('H:H',26, letter1)
        sheet.set_column('I:I',18, letter1)
        sheet.set_column('J:J',18, letter1)
        sheet.set_column('K:K',20, letter1)
        sheet.set_column('L:L',20, letter1)
        sheet.set_column('M:M',20, letter1)
        sheet.set_column('N:N',28, letter1)
        sheet.set_column('O:O',28, letter1)
        sheet.set_column('P:P',25, letter1)
        sheet.set_column('Q:Q',20, letter1)
        sheet.set_column('R:R',20, letter1)
        
        # Titulos, subtitulos, filtros y campos del reporte
        sheet.merge_range('A6:Q6', 'DETALLE VISTA POR PRODUCTO', titulo1)

        fecha = (datetime.now() - timedelta(hours=4)).strftime('%d/%m/%Y %H:%M:%S')
        fecha_inicial = datetime.strptime(str(data['form']['star_date']), '%Y-%m-%d').strftime('%d/%m/%Y')
        fecha_final = datetime.strptime(str(data['form']['end_date']), '%Y-%m-%d').strftime('%d/%m/%Y')
        sheet.merge_range('A7:O7', fecha_inicial +' - '+ fecha_final, tituloAzul)
        url = image_data_uri(self.env.user.company_id.logo)
        image_data = BytesIO(urlopen(url).read())
        sheet.insert_image('A1:A6', url, {'image_data': image_data,'x_scale': 0.38, 'y_scale': 0.20})
        sheet.write(8, 0, 'Cliente', titulo4)
        sheet.write(8, 1, str(self.env.user.partner_id.name), titulo3)
        sheet.write(9, 0, 'Fecha de impresion: ', titulo4)
        sheet.write(9, 1, fecha, titulo3)
        
        sheet.write(0, 13, 'NIT: ', titulo3) 
        sheet.write(1, 13, 'DIRECCION: ', titulo3) 
        sheet.write(2, 13, 'CELULAR, TELEFONO:', titulo3)   
        fila=12
        filtro_consulta = " "
        as_bussiness_id = data['form']['as_bussiness_id'] or ''
        producto_categ = data['form']['producto_categ'] or ''
        cliente = data['form']['cliente'] or ''
        asesor = data['form']['asesor'] or ''
        producto = data['form']['producto']  or ''
        agrupar = data['form']['agrupar'] or ''
        star_date = str(data['form']['star_date']) or ''
        end_date = str(data['form']['end_date']) or ''
            
            
        if agrupar != 'Vendedor' and agrupar != 'producto':
            sheet.write(fila,0,'FECHA VENTA',titulo2)
            sheet.write(fila,1,'FECHA FACTURAS',titulo2)
            sheet.write(fila,2,'No VENTA',titulo2)      
            sheet.write(fila,3,'CLIENTE',titulo2)
            sheet.write(fila,4,'CÓDIGO DE CLIENTE',titulo2)
            sheet.write(fila,5,'CÓDIGO DE PRODUCTO',titulo2)
            sheet.write(fila,6,'UNIDAD NEGOCIO',titulo2)
            sheet.write(fila,7,'DETALLE',titulo2)
            sheet.write(fila,8,'TIPO DE PRODUCTO',titulo2)
            sheet.write(fila,9,'CANTIDAD',titulo2)
            sheet.write(fila,10,'PRECIO UNITARIO',titulo2)
            sheet.write(fila,11,'DESCUENTO',titulo2)
            sheet.write(fila,12,'TOTAL BS',titulo2)
            sheet.write(fila,13,'ESTADO',titulo2)
            sheet.write(fila,14,'ALMACEN',titulo2)
        else:
            sheet.write(fila,0,'FECHA VENTA',titulo2)
            sheet.write(fila,1,'FECHA FACTURAS',titulo2)
            sheet.write(fila,2,'No VENTA',titulo2)      
            sheet.write(fila,3,'CLIENTE',titulo2)
            sheet.write(fila,4,'CÓDIGO DE CLIENTE',titulo2)
            sheet.write(fila,5,'CÓDIGO DE PRODUCTO',titulo2)
            sheet.write(fila,6,'UNIDAD NEGOCIO',titulo2)
            sheet.write(fila,7,'DETALLE',titulo2)
            sheet.write(fila,8,'TIPO DE PRODUCTO',titulo2)
            sheet.write(fila,9,'CANTIDAD',titulo2)
            sheet.write(fila,10,'PRECIO UNITARIO',titulo2)
            sheet.write(fila,11,'DESCUENTO',titulo2)
            sheet.write(fila,12,'TOTAL BS',titulo2)
            sheet.write(fila,13,'ESTADO',titulo2)
            sheet.write(fila,14,'ALMACEN',titulo2)

        def titulos(fila):
            sheet.write(fila,0,'FECHA VENTA',titulo2)
            sheet.write(fila,1,'FECHA FACTURAS',titulo2)
            sheet.write(fila,2,'No VENTA',titulo2)      
            sheet.write(fila,3,'CLIENTE',titulo2)
            sheet.write(fila,4,'CÓDIGO DE CLIENTE',titulo2)
            sheet.write(fila,5,'CÓDIGO DE PRODUCTO',titulo2)
            sheet.write(fila,6,'UNIDAD NEGOCIO',titulo2)
            sheet.write(fila,7,'DETALLE',titulo2)
            sheet.write(fila,8,'TIPO DE PRODUCTO',titulo2)
            sheet.write(fila,9,'CANTIDAD',titulo2)
            sheet.write(fila,10,'PRECIO UNITARIO',titulo2)
            sheet.write(fila,11,'DESCUENTO',titulo2)
            sheet.write(fila,12,'TOTAL BS',titulo2)
            sheet.write(fila,13,'ESTADO',titulo2)
            sheet.write(fila,14,'ALMACEN',titulo2)
            sheet.freeze_panes(5, 0)
        filtro_agrupar=''
        if producto_categ:
            filtro_consulta += " AND pt.categ_id = " + str(producto_categ)
        if cliente:
            filtro_consulta += " AND cliente.id = " + str(cliente)
        if asesor:
            filtro_consulta += " AND so.user_id = " + str(asesor)
        if producto:
            filtro_consulta += " AND pp.id = " + str(producto)
        if as_bussiness_id:
            filtro_consulta += "AND bus.id = " + str(as_bussiness_id)
        filtro_consulta += " AND (so.date_order AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::DATE BETWEEN '" + str(star_date) + "' AND '" + str(end_date) + "'"
        
            
        if agrupar == 'Vendedor':
            filtro_agrupar += " ORDER BY 14,2,3"
        elif agrupar == 'producto':
            filtro_agrupar += " ORDER BY 8,2,3"
        else:
            filtro_agrupar += " ORDER BY 2,3"
        consulta = self.get_consultas_fuente(filtro_consulta,filtro_agrupar)
        self.env.cr.execute(consulta)
        product_categories = [j for j in self.env.cr.fetchall()]
        _logger.debug("\n\n\n\nCONSULTA: %s\n\n\n\n",consulta+filtro_consulta)

        id_asesor = subtotal_dolares_asesor = subtotal_bolivianos_asesor = gran_total_dolares = gran_total_bolivianos = 0
        descuento= 0.00
        total_cantidad=0.00
        total_descuento=0.00
        # if agrupar == 'Vendedor':
        #     product_categories = self.agrupa_row(product_categories)
        for reporte in product_categories:
            fila += 1
            list_price = self.env['product.pricelist'].browse(reporte[13])
            tasa = self.obtener_tasa(reporte[1])
            # factor de Descuento global por linea de productos
            prec = self.env['decimal.precision'].precision_get('Discount')
            descuento= self.amount_discount(reporte[16])
            porcentaje_descuento = round(descuento or 0,prec)
            if reporte[16] == 'Monetario':
                porcentaje_descuento = (descuento or 0) * 100.0 / ((descuento or 0) + reporte[18])

            if list_price.currency_id.name == 'USD':
                monto_bob = (reporte[12] * (1.0 - (porcentaje_descuento or 0.0)/100.0)) / tasa
                monto_usd = reporte[12] * (1.0 - (porcentaje_descuento or 0.0)/100.0)
                descuento_bob = (reporte[11] * (1.0 - (porcentaje_descuento or 0.0)/100.0)) / tasa
                descuento_usd = reporte[11] * (1.0 - (porcentaje_descuento or 0.0)/100.0)
            else:
                monto_bob = reporte[12]
                monto_usd = (reporte[12])
                descuento_bob = descuento
                descuento_usd = descuento
            
                    


            sheet.write(fila,0,reporte[0],number_right) # FECHA VENTA
            #me quede aki, origin no esta fucnionando
            invoices = self.env['account.move'].search([('name','=',reporte[2]),('state','=','canceled')])
            if invoices:
                facturas=''
                coma=''
                fechas_facturas=''
                cont=1
                tam=len(invoices)
                for fac in invoices:
                    if cont != tam:
                        coma=str(',')
                    facturas+= str(fac.invoice_number)+str(coma)
                    fechas_facturas+= str(fac.fecha_boliviana)+str(coma)
                    cont+=1
                sheet.write(fila,1,fechas_facturas,number_right) # FECHA FACTURA
                sheet.write(fila,2,facturas,number_right) # FECHA FACTURA
            else:
                sheet.write(fila,1,'S/F',number_right) # FECHA FACTURA
                sheet.write(fila,2,'S/F',number_right) # FECHA FACTURA

            sheet.write(fila,2,reporte[2],number_right) # No VENTA
            sheet.write(fila,3,reporte[3],number_left) # CLIENTE
            sheet.write(fila,4,reporte[4],number_right) # Codigo de cliente
            sheet.write(fila,5,reporte[5],number_right) # CÓDIGO DE PRODUCTO           
            sheet.write(fila,6,(reporte[6]),number_left) # UNIDAD de negocio         
            sheet.write(fila,7,(reporte[7]),number_right) # DETALLE
            sheet.write(fila,8,reporte[8],number_left) # tipo producto
            sheet.write(fila,9,reporte[9],number_right) # cantidad
            sheet.write(fila,10,reporte[10],number_right) # PU        
            sheet.write(fila,11,descuento_bob,number_right) # descuento %
            sheet.write(fila,12,monto_bob,number_right) # TOTAL BS
            sheet.write(fila,13,reporte[20],number_left) # estado
            sheet.write(fila,14,reporte[21],number_left) # ALMACEN
            total_cantidad+=reporte[9]
            total_descuento+=descuento_bob
            subtotal_bolivianos_asesor += monto_bob
            gran_total_bolivianos += monto_bob
        fila += 1
        

        sheet.merge_range(fila,0,fila,8,'TOTAL', number_right)
        sheet.write(fila,9,total_cantidad, number_right)
        sheet.write(fila,11,total_descuento, number_right)
        sheet.write(fila,12,gran_total_bolivianos, number_right)
#me quede en : como jalar numeracion interna,

    def get_consultas_fuente(self,filtro_sale,filtro_agrupar):
        consulta_sale=(
            '''
            SELECT
            to_char((( so.date_order AT TIME ZONE'UTC' AT TIME ZONE'BOT' ) :: TIMESTAMP :: DATE ), 'DD/MM/YYYY' ) AS fecha_venta,
            ( so.date_order AT TIME ZONE'UTC' AT TIME ZONE'BOT' ) :: TIMESTAMP AS fecha_orden_consulta,
            so.NAME AS nota_venta,
            cliente.NAME AS nombre_cliente,
            COALESCE ( REPLACE ( cliente.as_code, '-', '' ), 'S/C' ) AS codigo_cliente,
            COALESCE ( pp.default_code, '' ) AS codigo_producto,
            bus.name AS nombre_negocio,
            pt.name AS nombre_producto,
            CASE 
                WHEN pt.type = 'product' THEN 'Almacenable'
                WHEN pt.type = 'service' THEN 'Servicio'
                WHEN pt.type = 'consu' THEN 'Consumible'
                ELSE 'S/T'
            END AS tipo_producto,
            sol.product_uom_qty AS cantidad,
            sol.price_unit AS precio_unitario,
            ( sol.product_uom_qty * sol.price_unit ) * ( sol.discount / 100 ) AS descuento,
            ( sol.product_uom_qty * sol.price_unit ) * (( 100-sol.discount ) / 100 ) AS subtotal_neto,
            so.pricelist_id,
            asesor.NAME AS nombre_asesor,
            asesor.ID,
            sol.id,
            so.name,
            so.amount_total,
            (CASE WHEN puom.uom_type='bigger' THEN round(sol.product_uom_qty/puom.factor) ELSE round(sol.product_uom_qty*puom.factor) END) as "Cantidad Almacen"
            
            ,CASE 
                WHEN so.state = 'sale' THEN 'Pedido de Venta'
                WHEN so.state = 'done' THEN 'Realizado'
                ELSE 'Devolucion'
            END as estado
            ,sl.name
            ,0
        FROM
            sale_order AS so
            JOIN sale_order_line AS sol ON sol.order_id = so.id
            JOIN res_partner AS cliente ON cliente.ID = so.partner_id
            JOIN product_product AS pp ON pp.ID = sol.product_id
            LEFT JOIN res_users AS ru ON ru.ID = so.user_id
            LEFT JOIN res_partner AS asesor ON asesor.ID = ru.partner_id
            LEFT JOIN uom_uom puom ON puom.id = sol.product_uom
            LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id           
            LEFT JOIN stock_move sm on sm.sale_line_id = sol.id
            LEFT JOIN stock_location sl ON sl.id = sm.location_id
            JOIN as_business_unit AS bus ON bus.id = pt.as_bussiness_id
        WHERE
            so.STATE IN ('sale','done')
        '''
        )
        return '('+consulta_sale+filtro_sale+')'+filtro_agrupar
  
    def obtener_tasa(self,date):
        moneda = self.env['res.currency'].search([('name','=','USD')])
        divisa = moneda.rate
        return divisa

    def amount_discount(self,id):
        order_line = self.env['sale.order.line'].sudo().search([('id', '=', id)])
        monto=0.00
        monto_discount=0.00
        for line in order_line:
            if line.discount > 0.00:
                monto = (line.price_unit * line.product_uom_qty)
                monto_discount += (monto*line.discount)/100
        return monto_discount