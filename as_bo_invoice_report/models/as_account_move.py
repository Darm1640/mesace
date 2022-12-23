from odoo import api, fields, models, _
from odoo.exceptions import UserError
import json
import base64
from dateutil.relativedelta import relativedelta
from werkzeug.urls import url_encode
import random
from datetime import timedelta, datetime

class as_account_move(models.Model):
    _inherit = 'account.move'
    
    as_oc =fields.Char(string='OC')
    as_po =fields.Char(string='PO')
    as_gr =fields.Char(string='GR')
    as_ses =fields.Char(string='SES')
    as_contrato =fields.Char(string='Contrato')
    as_certificacion =fields.Char(string='Certificacion')
    as_referencia_prefactura =fields.Char(string='Referencia Prefactura')
    as_escritura_prefactura =fields.Char(string='Escritura Prefactura')

    def as_get_date_literal(self,fecha):
        dia = datetime.strptime(str(fecha), '%Y-%m-%d').strftime('%d')
        mes = self.get_mes(datetime.strptime(str(fecha), '%Y-%m-%d').strftime('%m'))
        ano = datetime.strptime(str(fecha), '%Y-%m-%d').strftime('%Y')
        return str(dia)+' de '+ str(mes)+' de '+str(ano)

    def acumulador_de_totales_reporte(self, requerido):
        acumulador_total_neto=0.00
        lineas_factura = self.env['account.move.line'].search([('move_id','=',self.id),('exclude_from_invoice_tab','=',False)])
        if lineas_factura:
            for line in lineas_factura:
                acumulador_total_neto += line.price_total  
            lineas={
                'acumulador_total_neto':acumulador_total_neto,
                    }
        else:
            lineas={
            'acumulador_total_neto':0,
            }
        nit = lineas[str(requerido)]
        return nit

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
    
    def get_campos_cotizacion(self, requerido):
        value=''
        sale = self.env['sale.order'].search([('name','=',self.invoice_origin)])
        if sale:
            value=sale.as_template_id.name
        else:
            value=''
        json={
            'codigo':value
        }
        valor = json[str(requerido)]
        return valor
    
    def as_action_invoice_preliminar(self):
        return self.env.ref('as_bo_invoice_report.as_bo_invoice_report_preliminar').report_action(self)