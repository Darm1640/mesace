# -*- coding: utf-8 -*-
from odoo import tools
from odoo import api, fields, models, _
import time
import datetime
from datetime import datetime, timedelta, date
from time import mktime
from dateutil.relativedelta import relativedelta

class AsstockpickingUFV(models.Model):
    _inherit = "stock.picking"
    _description = "Packages"
    

    def button_ufvs(self):
        for line in self.move_ids_without_package:
            line.as_ufv_sm=line.get_saldo_entrada(line.product_id.id,line.location_dest_id.id,line.date)


class AsstockmoveUFV(models.Model):
    _inherit = "stock.move"
    _description = "UFVS"
    
    as_ufv_sm = fields.Float('Acumulador UFV')

    def get_saldo_entrada(self,product,almacen,fecha):
      
        year = (datetime.strptime(str(fecha), '%Y-%m-%d %H:%M:%S')).strftime('%Y')
        ultimo_dia_year = year+'-'+'12'+'-'+'31'
        #tomamos 
        query_movements = ("""
            SELECT
                pp.default_code as "Codigo Producto"
                ,CONCAT(COALESCE(sp.name, sm.name), ' - ', COALESCE(sp.origin, 'S/Origen')) as "Comprobante"
                ,COALESCE(sp.date_done::date, sm.date::date) as "Fecha"
                ,COALESCE(rp.name,'SIN NOMBRE') as "Cliente/Proveedor"
                ,CASE 
                    WHEN (sm.location_dest_id IN ("""+str(almacen)+""") AND sm.location_id NOT IN ("""+str(almacen)+""")) THEN sm.product_qty
                    WHEN (sm.location_id IN ("""+str(almacen)+""") AND sm.location_dest_id NOT IN ("""+str(almacen)+""")) THEN -sm.product_qty
                    ELSE 0 END as "Cantidad"
                ,COALESCE(sm.price_unit, 0) as "Costo"
            FROM
                stock_move sm
                LEFT JOIN stock_picking sp ON sm.picking_id = sp.id
                LEFT JOIN product_product pp ON pp.id = sm.product_id
                LEFT JOIN res_partner rp ON rp.id = sp.partner_id
            WHERE
                
                sm.state = 'done'
                AND (sm.location_id IN ("""+str(almacen)+""") or sm.location_dest_id IN ("""+str(almacen)+"""))
                AND pp.id = """+str(product)+"""
                AND (sm.date::TIMESTAMP+ '-4 hr')::date <= '"""+str(fecha)+"""'
            ORDER BY COALESCE(sp.date_done::date, sm.date::date)  asc
        """)
        self.env.cr.execute(query_movements)
        
        ultimo_monto = [k for k in self.env.cr.fetchall()]
        total= 0.0
        stock= 0.0
        bandera = False
        fecha_ininial = ''
        fecha_ultimo = ''
        for stock_move in ultimo_monto:
            fecha_ultimo = stock_move[2]
            total_ingreso = 0.0
            total_egreso= 0.0
            stock_ingreso = 0.0
            stock_egreso= 0.0
            if stock_move[4]>0:
                fecha_ininial = stock_move[2]
                total_ingreso = stock_move[5]*abs(stock_move[4])
                stock_ingreso = abs(stock_move[4])
            if stock_move[4]<0:
                total_egreso = stock_move[5]*abs(stock_move[4])
                stock_egreso = abs(stock_move[4])
            if bandera:
                total= total_ingreso - total_egreso + total
                stock= stock_ingreso - stock_egreso + stock
            else:
                total = total_ingreso - total_egreso
                stock= stock_ingreso - stock_egreso 
                bandera = True
        if fecha_ininial=='':
            fecha_ininial = ultimo_dia_year
        ufv_inicial = float(self.get_rate_ufv_start(fecha_ininial))
        ufv_final = float(self.get_rate_ufv_end(ultimo_dia_year))
        monto_actualizacon = total*(ufv_final/ufv_inicial)
        if stock > 0:
            precio_costo = monto_actualizacon / stock
        else:
            precio_costo = 0
        diferencia =monto_actualizacon-total
        vals = {
            'fecha': (datetime.strptime(str(ultimo_dia_year), '%Y-%m-%d')).strftime('%d/%m/%Y'),
            'PU': precio_costo,
            'stock': stock,
            'total': monto_actualizacon,
            'diff': diferencia,
        }
        return diferencia
    
    def get_rate_ufv_end(self,fecha):
        ufv = self.env['res.currency'].search([('name', '=', 'UFV')],limit=1)
        as_ufv_actual = self.env['res.currency.rate'].search([('name', '<=', fecha),('currency_id', '=', ufv.id)], order="name desc", limit=1).rate or 1
        return as_ufv_actual

    def get_rate_ufv_start(self,fecha):
        ufv = self.env['res.currency'].search([('name', '=', 'UFV')],limit=1)
        as_ufv_ant = self.env['res.currency.rate'].search([('name', '=', fecha),('currency_id', '=', ufv.id)], order="name desc",limit=1).rate or 1
        return as_ufv_ant


   