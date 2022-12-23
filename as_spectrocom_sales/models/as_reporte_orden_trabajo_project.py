from odoo import tools
from odoo import api, fields, models, _
import time
import datetime
from datetime import datetime, timedelta, date
from time import mktime
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup

class Asstockpicking(models.Model):
    _inherit = "project.task"
    _description = "Packages"
    
    
    def _lineas_ordenadas(self):
        type_order = self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_type_order_report')
        if not type_order or type_order == 'Ninguno':
            order_lines =self.order_line
        else:
            order_lines= self.env['sale.order.line'].sudo().search([('order_id','=',self.id)],order=(str(type_order)+" asc"))
        return order_lines
        
    def info_sucursal(self, requerido):
        info = ''
        diccionario_dosificacion = {
            'nombre_empresa' : self.env.user.company_id.name or '',
            'nit' : self.env.user.company_id.vat or '',
            'direccion1' : self.env.user.company_id.street or '',
            'telefono' : self.env.user.company_id.phone or '',
            'ciudad' : self.env.user.company_id.city or '',
            'pais' : self.env.user.company_id.country_id.name or '',
        }
        info = diccionario_dosificacion[str(requerido)]
        return info

    ####Funcion para quitar elementos de texto enriquecido en reportes
    def get_pobs(self,text):
        textstr = ''
        if text:
            # textstr = BeautifulSoup(text,"html.parser").text
            textstr= self.as_description_ot.replace('\n', '<br/>')
        return textstr
    
    # def amount_bruto(self,picking_id):
    #     move_lines = self.env['stock.move'].sudo().search([('picking_id', '=', picking_id)])
    #     monto=0.00
    #     for line in move_lines:
    #         monto += (line.price_unit * line.product_uom_qty)
    #     return monto
    # def amount_cantidad(self,picking_id):
    #     move_lines = self.env['stock.move'].sudo().search([('picking_id', '=', picking_id)])
    #     monto=0.00
    #     for line in move_lines:
    #         monto += line.product_uom_qty
    #     return monto

