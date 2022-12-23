from odoo import tools
from odoo import api, fields, models, _
import time
import datetime
from datetime import datetime, timedelta, date
from time import mktime
from dateutil.relativedelta import relativedelta

class Asstockpicking(models.Model):
    _inherit = "stock.picking"
    _description = "Packages"
    
    as_codigo_venta=fields.Char(string="Codigo:", compute="obtener_numero_cotizacion")
    
    def obtener_numero_cotizacion(self):
        move_lines = self.env['sale.order'].sudo().search([('name', '=', self.origin)],limit=1)
        numero_codigo=''
        if move_lines:
            numero_codigo=move_lines.as_template_id.name
        self.as_codigo_venta=numero_codigo
        
        
    def _lineas_ordenadas(self):
        type_order = self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_type_order_report')
        if not type_order or type_order == 'Ninguno':
                order_lines =self.move_lines
        else:
            order_lines= self.env['stock.move'].search([('picking_id','=',self.id)],order=(str(type_order)+" asc"))
        return order_lines
        
    def info_sucursal(self, requerido):
        info = ''
        diccionario_dosificacion = {
            'nombre_empresa' : self.company_id.name or '',
            'nit' : self.company_id.vat or '',
            'direccion1' : self.company_id.street or '',
            'telefono' : self.company_id.phone or '',
            'ciudad' : self.company_id.city or '',
            'pais' : self.company_id.country_id.name or '',
        }
        info = diccionario_dosificacion[str(requerido)]
        return info
    def _traduccion_estado(self,estate):
        estado = ''
        if estate == 'draft':
            estado = 'Presupuesto borrador'
        if estate == 'Ready':
            estado = 'Listo'
        if estate == 'cancel':
            estado = 'Cancelado'
        if estate == 'waiting':
            estado = 'Esperando'
        if estate == 'confirmed':
            estado = 'Esperando Disponibilidad'
        if estate == 'partially_available':
            estado = 'Parcialmente disponible'
        if estate == 'assigned':
            estado = 'Listo para transferir'
        if estate == 'done':
            estado = 'Realizado'
        return estado
    def amount_bruto(self,picking_id):
        move_lines = self.env['stock.move'].sudo().search([('picking_id', '=', picking_id)])
        monto=0.00
        for line in move_lines:
            monto += (line.price_unit * line.product_uom_qty)
        return monto
    def amount_cantidad(self,picking_id):
        move_lines = self.env['stock.move'].sudo().search([('picking_id', '=', picking_id)])
        monto=0.00
        for line in move_lines:
            monto += line.product_uom_qty
        return monto
class Asstockpicking_lines(models.Model):
    _inherit = "stock.move"
    as_product_stock=fields.Float(string="Stock", compute='_detalle_producto', help=u'Stock disponible actual del producto.')

    @api.onchange('product_id')
    def _detalle_producto(self):
        for record in self:
            if record:
                cantidad = 0.0
                if record.location_id and record.product_id:
                    almacen = record.location_id.id
                    producto = record.product_id.id
                    now= datetime.now().strftime('%Y-%m-%d')
                    query_movements = ("""
                        SELECT
                            pp.default_code as "Codigo Producto"
                            ,CONCAT(COALESCE(sp.name, sm.name), ' - ', COALESCE(sp.origin, 'S/Origen')) as "Comprobante"
                            ,COALESCE((sp.date_done AT TIME ZONE 'UTC' AT TIME ZONE 'BOT')::date, sm.date::date) as "Fecha"
                            ,COALESCE(rp.name,'SIN NOMBRE') as "Cliente/Proveedor"
                            ,CASE 
                                WHEN (sm.location_dest_id = """+str(almacen)+""" AND sm.location_id != """+str(almacen)+""") THEN sm.product_qty
                                WHEN (sm.location_id = """+str(almacen)+""" AND sm.location_dest_id != """+str(almacen)+""") THEN -sm.product_qty
                                ELSE 0 END as "Cantidad"
                            ,COALESCE(sm.price_unit, 0) as "Costo"
                        FROM
                            stock_move sm
                            LEFT JOIN stock_picking sp ON sm.picking_id = sp.id
                            LEFT JOIN product_product pp ON pp.id = sm.product_id
                            LEFT JOIN res_partner rp ON rp.id = sp.partner_id
                        WHERE
                            sm.state = 'done'
                            AND (sm.location_id = """+str(almacen)+""" or sm.location_dest_id = """+str(almacen)+""")
                            AND pp.id = """+str(producto)+"""
                            AND (sm.date::TIMESTAMP+ '-4 hr')::date <= '"""+str(now)+"""'
                        ORDER BY COALESCE(sp.date_done, sm.date)  asc
                    """)
                    self.env.cr.execute(query_movements)
                    all_movimientos_almacen = [k for k in self.env.cr.fetchall()]
                    for line in all_movimientos_almacen:
                        cantidad += line[4]






                # cantidad= record.product_id.with_context(location_id=record.location_id).qty_available
                #previsto =  producto.product_id.with_context(location=[ruta]).virtual_available
                record.as_product_stock = cantidad
            else:
                record.as_product_stock = 0.0
    