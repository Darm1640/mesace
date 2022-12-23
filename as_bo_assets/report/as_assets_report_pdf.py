# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError
import calendar
import datetime
from datetime import datetime
import pytz
from odoo import models,fields
import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools import float_compare, float_is_zero
import logging
_logger = logging.getLogger(__name__)
class ReportTax(models.AbstractModel):
    _name = 'report.as_bo_assets.assets_pdf'

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        return {
            'data': data['form'],
            'info': self.info_sucursal(),
            'fechai': str(data['form']['start_date']),
            'fechaf': str(data['form']['end_date']),
            'UFV': self.get_rate_ufv_end(data['form']['end_date']),
            'lines': self._get_line_report(data['form']['start_date'],data['form']['end_date'])
          
        }

    # @api.multi
    def info_sucursal(self):
        info = ''
        diccionario_dosificacion= {}
        diccionario_dosificacion = {
            'nombre_empresa' : self.env.user.company_id.name or '',
            'nit' : self.env.user.company_id.vat or '',
            'direccion1' : self.env.user.company_id.street or '',
            'telefono' : self.env.user.company_id.phone or '',
            'ciudad' : self.env.user.company_id.city or '',
            'sucursal' : self.env.user.company_id.city or '',
            'pais' : self.env.user.company_id.country_id.name or '',
            'actividad' :  self.env.user.company_id.name or '',
            'fechal' : self.env.user.company_id.phone or '',
            'email' : self.env.user.company_id.email or '',

        }
        return diccionario_dosificacion

    # @api.multi
    def get_rate_ufv_end(self,fecha):
        mes= (datetime.strptime(str(fecha), '%Y-%m-%d') + relativedelta(months=1)).strftime('%m')
        anio= (datetime.strptime(str(fecha), '%Y-%m-%d')).strftime('%Y')
        periodo = calendar.monthrange(int(anio),int(mes))
        primer_dia= fecha
        primer_ultimo= str(int(anio))+'-'+mes+'-'+str(periodo[1])
        ufv = self.env['res.currency'].search([('name', '=', 'UFV')],limit=1)
        as_ufv_actual = self.env['res.currency.rate'].search([('name', '<=', fecha),('currency_id', '=', ufv.id)], order="name desc", limit=1).rate or 1
        return as_ufv_actual

    # @api.multi
    def get_rate_ufv_start(self,fecha):
        mes= (datetime.strptime(str(fecha), '%Y-%m-%d') + relativedelta(months=1)).strftime('%m')
        anio= (datetime.strptime(str(fecha), '%Y-%m-%d')).strftime('%Y')
        periodo = calendar.monthrange(int(anio),int(mes))
        primer_dia= fecha
        primer_ultimo= str(int(anio))+'-'+mes+'-'+str(periodo[1])
        ufv = self.env['res.currency'].search([('name', '=', 'UFV')],limit=1)
        as_ufv_ant = self.env['res.currency.rate'].search([('name', '=', fecha),('currency_id', '=', ufv.id)], order="name desc",limit=1).rate or 1
        return as_ufv_ant

    # @api.multi
    def _get_line_report(self,fechas,fechae):
        detalle_consulta_format = []
        lines = []
        category_ids = self.env['account.asset.category'].search([], order="name desc")
        for cate in category_ids:
            detalle_consulta = []
            detalle_categ = []
            total_cantidad = 0.0
            total_saldo_anterior = 0.0
            total_saldo_actual = 0.0
            total_valor = 0.0
            actualizacion = 0.0
            actualizacion2 = 0.0
            dep_acum = 0.0
            valor_actualizacion = 0.0
            total_actualizacion = 0.0
            total_actualizacion2 = 0.0
            total_valor_actualizacion = 0.0
            total_dep_acum = 0.0
            total_dep_actualizado = 0.0
            dep_actualizado=0.0
            dep_periodo=0.0
            total_dep_periodo=0.0            
            dep_periodo_end=0.0
            total_dep_periodo_end=0.0            
            dep_periodo_final=0.0
            total_dep_periodo_final=0.0
            dep_valor_neto=0.0
            total_dep_valor_neto=0.0
            vals2 ={
                'categ':cate.id,
                'default_code':'',
                'name':cate.name,
            }
            product_ids = self.env['product.product'].search([('asset_category_id','=',cate.id)], order="name desc")
            vals={}
            for product in product_ids:
                cantidad = 0.0
                saldo_anterior = 0.0
                saldo_actual = 0.0
                saldo_valor = 0.0
                text_query = ("""
                       SELECT
                        pp.id
                        ,sum(assl.as_value)
                        ,sum(assl.as_value_updates)
                        ,sum(assl.as_updates)
                        ,sum(assl.as_value_updates)
                        ,sum(assl.as_depreciation_store)
                        ,sum(assl.as_update_depreciation)
                        ,sum(assl.as_depreciation_periodo)
                        ,sum(assl.as_depreciation_end)
                        ,sum(assl.as_valor_neto)
                        from account_asset_depreciation_line assl
                        join account_asset_asset ass on ass.id = assl.asset_id
                        join product_product pp on pp.id = ass.product_id
                        left join account_move_line ai on ai.move_id = ass.invoice_id and ai.product_id = pp.id
                        where
                        assl.move_check='True'
                            and pp.id = '"""+str(product.id)+"""'
                            AND assl.depreciation_date::date BETWEEN '"""+str(fechas)+"""' AND '"""+str(fechae)+"""'
                        GROUP BY 1
                """)
                self.env.cr.execute(text_query)
                result= self.env.cr.fetchall()
                res= self._get_saldos_fechas(product.id,fechas,fechae,cate.account_depreciation_expense_id.id)
                cantidad = res['cantidad']
                saldo_anterior = res['saldo_anterior']
                saldo_actual = res['saldo_actual']
                if result:
                    saldo_valor = float(result[0][1])
                    actualizacion = float(result[0][2])
                    valor_actualizacion = float(result[0][3])
                    dep_acum = float(result[0][4])
                    actualizacion2 = float(result[0][6])
                    dep_actualizado = float(result[0][6])
                    dep_periodo_end = float(result[0][7])
                    dep_periodo_final = float(result[0][8])
                    dep_valor_neto = float(result[0][9])

                #totales
                total_cantidad += cantidad           
                total_saldo_anterior += saldo_anterior
                total_saldo_actual += saldo_actual
                total_valor += saldo_valor
                total_actualizacion += actualizacion
                total_valor_actualizacion += valor_actualizacion
                total_dep_acum += dep_acum
                total_actualizacion2 +=actualizacion2
                total_dep_actualizado += dep_actualizado
                total_dep_periodo_end += dep_periodo_end
                total_dep_periodo_final += dep_periodo_final
                total_dep_valor_neto += dep_valor_neto

                vals ={
                    'categ':'',
                    'default_code':product.default_code,
                    'name':product.name,
                    'cantidad': cantidad,
                    'saldo_anterior': saldo_anterior,
                    'saldo_actual': saldo_actual,
                    'saldo_valor': saldo_valor,
                    'actualizacion': actualizacion,
                    'valor_actualizacion': valor_actualizacion,
                    'dep_acum': dep_acum,
                    'actualizacion2': actualizacion2,
                    'dep_actualizado': dep_actualizado,
                    'dep_periodo_end': dep_periodo_end,
                    'dep_periodo_final': dep_periodo_final,
                    'dep_valor_neto': dep_valor_neto,

                }
                detalle_consulta.append(vals)
            vals2['cantidad']=total_cantidad
            vals2['saldo_anterior']=total_saldo_anterior
            vals2['saldo_actual']=total_saldo_actual
            vals2['saldo_valor']=total_valor
            vals2['actualizacion']=total_actualizacion
            vals2['valor_actualizacion']=total_valor_actualizacion
            vals2['dep_acum']=total_dep_acum
            vals2['actualizacion2']=total_actualizacion2
            vals2['dep_actualizado']=total_dep_actualizado
            vals2['dep_periodo_end']=total_dep_periodo_end
            vals2['dep_periodo_final']=total_dep_periodo_final
            vals2['dep_valor_neto']=total_dep_valor_neto
            detalle_categ.append(vals2)
            detalle_consulta_format+=detalle_categ
            detalle_consulta_format+=detalle_consulta
        
        return detalle_consulta_format



    # @api.multi
    def _get_saldos_fechas(self,product_id,fecha_start,fecha_end,account_id):
        mes= (datetime.strptime(str(fecha_end), '%Y-%m-%d')).strftime('%m')
        anio= (datetime.strptime(str(fecha_end), '%Y-%m-%d')).strftime('%Y')
        year_a= (datetime.strptime(str(fecha_end), '%Y-%m-%d') - relativedelta(years=+1)).strftime('%Y')
        primer_dia_anterior= year_a+'-'+'01'+'-'+'01'
        ultimo_dia_anterior= year_a+'-'+'12'+'-'+'31'
        tuple_query = []
        saldo_anterior = 0.0
        cantidad = 0.0
        saldo_actual = 0.0
        depre_anterior = 0.0
        #saldo_anterior
        text_query = ("""
            SELECT
            pp.id b
            ,sum(ass.value)
            from account_asset_asset ass 
            join product_product pp on pp.id = ass.product_id
            left join account_move_line ai on ai.move_id = ass.invoice_id and ai.product_id = pp.id
            left join account_move aii on aii.id = ai.move_id
            where 
            ass.state='open'
            and pp.id = '"""+str(product_id)+"""'
            AND aii.date_invoice::date < '"""+str(fecha_start)+"""' 
            GROUP BY 1
        """)
        _logger.debug(text_query)

        self.env.cr.execute(text_query)
        res= self.env.cr.fetchall()
        if res:
            saldo_anterior = res[0][1]
            depre_anterior = res[0][1]
        #saldo actual 
        year=  (datetime.strptime(str(fecha_end), '%Y-%m-%d')).strftime('%Y')
        primer_dia_actual= year+'-'+'01'+'-'+'01'
        ultimo_dia_actual= fecha_end
        text_query = ("""
        SELECT
            pp.id
            ,sum(ai.quantity)
            ,sum(ass.value)
            from account_asset_asset ass 
            join product_product pp on pp.id = ass.product_id
            left join account_move_line ai on ai.move_id = ass.invoice_id and ai.product_id = pp.id
            left join account_move aii on aii.id = ai.move_id
            where 
            ass.state='open'
            and pp.id = '"""+str(product_id)+"""'
            AND aii.date_invoice::date BETWEEN '"""+str(fecha_start)+"""' AND '"""+str(fecha_end)+"""'
            GROUP BY 1
        """)
        self.env.cr.execute(text_query)
        res1= self.env.cr.fetchall()
        if res1:
            if res1[0][1] != None:
                cantidad = float(res1[0][1])
            saldo_actual += float(res1[0][2])
            
        vals = {
            'cantidad': cantidad,
            'saldo_anterior': saldo_anterior,
            'saldo_actual': saldo_actual,
            'depre_anterior': depre_anterior,

        }
        return vals