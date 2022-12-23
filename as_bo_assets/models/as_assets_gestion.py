# -*- coding: utf-8 -*-
from odoo import models, api, fields,  _
import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools import float_compare, float_is_zero

class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.depreciation.line'
    _description = 'Asset/Revenue Recognition inherit'

    qty = fields.Float(string = "Cantidad", compute='_get_line_report')
    category_id = fields.Many2one('account.asset.category', string='Category', related='asset_id.category_id', store=True)
    # saldo_anterior = fields.Float(string = "Saldo Anterior",compute='_get_line_report')
    # saldo_actual = fields.Float(string = "Incorporaciones",compute='_get_line_report')
    # saldo_valor = fields.Float(string = "Valor",compute='_get_line_report')
    # actualizacion = fields.Float(string = "Actualizacion",compute='_get_line_report')
    # valor_actualizacion = fields.Float(string = "Valor Actualizado",compute='_get_line_report')
    # dep_acum = fields.Float(string = "Dep. Acumulada",compute='_get_line_report')
    # actualizacion2 = fields.Float(string = "Actualizacion",compute='_get_line_report')
    # dep_actualizado = fields.Float(string = "Dep. Acumulada Actualizada",compute='_get_line_report')
    # dep_periodo_end = fields.Float(string = "Depreciacion Periodo",compute='_get_line_report')
    # dep_periodo_final = fields.Float(string = "Dep. Acumulada Final",compute='_get_line_report')
    # dep_valor_neto = fields.Float(string = "Valor Neto",compute='_get_line_report')

    # @api.multi
    def _get_line_report(self):
        detalle_consulta_format = []
        lines = []
        for product_tmpl in self:
            product_tmpl.qty = 0.0
            for invoice in product_tmpl.asset_id.invoice_id.invoice_line_ids:
                if invoice.product_id == product_tmpl.asset_id.product_id:
                    product_tmpl.qty += invoice.quantity
            # product_ids = self.env['product.product'].search([('product_tmpl_id','=',product_tmpl.id)])
            # vals={}
            # fechae = (datetime.strptime(str(fields.Datetime.now()), '%Y-%m-%d %H:%M:%S')).strftime('%Y-%m-%d')
            # aniof = (datetime.strptime(str(fields.Datetime.now() - relativedelta(years=1)), '%Y-%m-%d %H:%M:%S')).strftime('%Y')
            # periodo2 = calendar.monthrange(int(aniof),int(12))
            # fechas= str(aniof)+'-'+'12'+'-'+str(periodo2[1])
            # mes= (datetime.strptime(str(fechae), '%Y-%m-%d') - relativedelta(months=1)).strftime('%m')
            # anio= (datetime.strptime(str(fechae), '%Y-%m-%d')).strftime('%Y')
            # for product in product_ids:
            #     if product.property_account_expense_id:
            #         res= product_tmpl._get_saldos_fechas(product.id,fechas,fechae,product.property_account_expense_id.id)
            #         product_tmpl.cantidad = res['cantidad'] or 0
            #         product_tmpl.saldo_anterior = res['saldo_anterior'] or 0
            #         product_tmpl.saldo_actual = res['saldo_actual'] or 0
            #         product_tmpl.qty = res['cantidad'] or 0
            #     else:
            #         product_tmpl.cantidad =  0
            #         product_tmpl.saldo_anterior = 0
            #         product_tmpl.saldo_actual =  0
            #     product_tmpl.saldo_valor = product_tmpl.saldo_anterior+product_tmpl.saldo_actual
            #     as_ufv_ant = float(product_tmpl.get_rate_ufv_start(fechae))
            #     as_ufv_actual = float(product_tmpl.get_rate_ufv_end(fechae))
            #     ufvs = as_ufv_actual / as_ufv_ant   
            #     product_tmpl.actualizacion = product_tmpl.saldo_valor*((ufvs-1))
            #     product_tmpl.valor_actualizacion = product_tmpl.actualizacion+product_tmpl.saldo_valor
            #     if product_tmpl.asset_category_id.account_depreciation_expense_id:
            #         res2= product_tmpl._get_saldos_fechas(product.id,fechas,fechae,product_tmpl.asset_category_id.account_depreciation_expense_id.id)
            #         product_tmpl.dep_acum = res['saldo_actual'] or 0
            #     else:
            #         product_tmpl.dep_acum = 0.0
            #     product_tmpl.actualizacion2 = product_tmpl.dep_acum*((ufvs-1))
            #     product_tmpl.dep_actualizado = product_tmpl.dep_acum+product_tmpl.actualizacion2
            #     fecha_factura = datetime.strptime(str(fechas), '%Y-%m-%d')
            #     fecha_ultimo = datetime.strptime(str(fechae), '%Y-%m-%d')
            #     dias = fecha_ultimo - fecha_factura
            #     dias = int(dias.days)
            #     if product_tmpl.asset_category_id.as_dias_util > 0:
            #         factor = (dias*100)/product_tmpl.asset_category_id.as_dias_util
            #     else:
            #         factor = 1
            #     dep_periodo_end = product_tmpl.dep_actualizado *(factor/100)
            #     product_tmpl.dep_periodo_end = product_tmpl.dep_actualizado * (product_tmpl.asset_category_id.as_coeficiente/100)
            #     product_tmpl.dep_periodo_final = product_tmpl.dep_actualizado+ product_tmpl.dep_periodo_end
            #     product_tmpl.dep_valor_neto = product_tmpl.valor_actualizacion- product_tmpl.dep_periodo_final
    


    # @api.multi
    def get_rate_ufv_end(self,fecha):
        mes= (datetime.strptime(str(fecha), '%Y-%m-%d') + relativedelta(months=1)).strftime('%m')
        anio= (datetime.strptime(str(fecha), '%Y-%m-%d')).strftime('%Y')
        periodo = calendar.monthrange(int(anio),int(mes))
        primer_dia= fecha
        primer_ultimo= str(int(anio))+'-'+mes+'-'+str(periodo[1])
        ufv = self.env['res.currency'].search([('name', '=', 'UFV')],limit=1)
        as_ufv_actual = self.env['res.currency.rate'].search([('name', '<=', primer_ultimo),('currency_id', '=', ufv.id)], order="name desc", limit=1).rate or 1
        return as_ufv_actual

    # @api.multi
    def get_rate_ufv_start(self,fecha):
        mes= (datetime.strptime(str(fecha), '%Y-%m-%d') + relativedelta(months=1)).strftime('%m')
        anio= (datetime.strptime(str(fecha), '%Y-%m-%d')).strftime('%Y')
        periodo = calendar.monthrange(int(anio),int(mes))
        primer_dia= fecha
        primer_ultimo= str(int(anio))+'-'+mes+'-'+str(periodo[1])
        ufv = self.env['res.currency'].search([('name', '=', 'UFV')],limit=1)
        as_ufv_ant = self.env['res.currency.rate'].search([('name', '=', primer_dia),('currency_id', '=', ufv.id)], order="name desc",limit=1).rate or 1
        return as_ufv_ant

    
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
            pp.id
            ,sum(assl.as_value_updates)
            ,sum(assl.as_depreciation_end)
            from account_asset_depreciation_line assl
            join account_asset_asset ass on ass.id = assl.asset_id
            join product_product pp on pp.id = ass.product_id
            where 
            assl.move_id is not null
                and pp.id = '"""+str(product_id)+"""'
                AND assl.depreciation_date::date < '"""+str(fecha_start)+"""' 
            GROUP BY 1
        """)
        self.env.cr.execute(text_query)
        res= self.env.cr.fetchall()
        if res:
            saldo_anterior = res[0][1]
            depre_anterior = res[0][2]
        #saldo actual 
        year=  (datetime.strptime(str(fecha_end), '%Y-%m-%d')).strftime('%Y')
        primer_dia_actual= year+'-'+'01'+'-'+'01'
        ultimo_dia_actual= fecha_end
        text_query = ("""
        SELECT
            pp.id
            ,sum(ai.quantity)
            ,sum(assl.as_value_updates)
            ,sum(assl.as_value)
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
            left join account_invoice_line ai on ai.invoice_id = ass.invoice_id and ai.product_id = pp.id
            where
            assl.move_id is not null
                and pp.id = '"""+str(product_id)+"""'
                AND assl.depreciation_date::date BETWEEN '"""+str(fecha_start)+"""' AND '"""+str(fecha_end)+"""'
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