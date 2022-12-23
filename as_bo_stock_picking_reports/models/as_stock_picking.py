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