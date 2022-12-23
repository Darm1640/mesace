# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models,_
from time import mktime
from datetime import date, datetime
from odoo.exceptions import UserError
import logging
import calendar
from datetime import date, datetime
from odoo.tools import float_compare, float_is_zero
from dateutil.rrule import rrule, MONTHLY, YEARLY
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import formatLang
_logger = logging.getLogger(__name__)

class as_ajustar_assets(models.TransientModel):
    _name="as.ajustar.assets"
    _description = "Modelo para gestionar ajuste o Revaluo"

    as_assets = fields.Many2one('account.asset.asset',string='Activo Fijo')
    as_assets_line = fields.Many2one('account.asset.depreciation.line',string='Activo Fijo linea')
    as_modality = fields.Selection([
        ('Ajuste', 'Ajuste'),
        ('Revaluo', 'Revaluo'),
        ('Ventas', 'Ventas'),
        ('mantenimiento', 'Mantenimiento'),
    ], string="Tipo",default="Ajuste")
    as_date = fields.Date(string='Fecha', default=lambda *a: (datetime.now() - timedelta(hours = 4)).strftime('%Y-%m-%d'), required=True)
    as_vida_util = fields.Integer(string='Vida util asignado (Años)')
    as_value = fields.Float(string='Valor asignado')
    as_coeficiente = fields.Float(string='Coeficiente')
    as_partner_id = fields.Many2one('res.partner',string='Cliente/Proveedor')
    as_ruta = fields.Many2one('stock.location.route',string='Ruta de Venta')
    as_porcentaje = fields.Float(string='Porcentaje',default=20.0)
    as_amount_purchase = fields.Float(string='Monto Compra',default=1000.0)

    @api.onchange('as_vida_util','as_value')
    def as_get_coeficiente(self):
        if self.as_vida_util > 0.0:
            self.as_coeficiente = 100/self.as_vida_util

    @api.model
    def default_get(self, fields):
        res = super(as_ajustar_assets, self).default_get(fields)
        res_ids = self._context.get('active_ids')
        as_modelo = self._context.get('active_model')
        so_line_obj = self.env[as_modelo].browse(res_ids)
        res['as_assets'] = so_line_obj
        return res

    @api.onchange('as_date','as_porcentaje')
    def as_date_depreciasion(self):
        linea_depre = False
        if self.as_modality == 'mantenimiento':
            for line in self.as_assets.depreciation_line_ids:
                if self.as_date <= line.depreciation_date:
                    linea_depre = line
                    break
            self.as_amount_purchase = (linea_depre.as_value_updates*self.as_porcentaje)/100
            self.as_assets_line = linea_depre
            if not linea_depre:
                raise UserError(_('No se ha podido seleccionar una linea de depresiacion'))
        
     

    def as_process_assets(self):
        if self.as_modality == 'Ajuste':
            self.as_process_ajuste()
        elif self.as_modality == 'mantenimiento':
            self.as_process_mantenimiento()
        elif self.as_modality == 'Revaluo':
            self.as_process_revaluo()
        else:
            self.as_process_sale()

    
    def as_process_mantenimiento(self):
        if self.as_value < self.as_amount_purchase:
            raise UserError(_('ESTA SEGURO QUE EL VALOR SU COMPRA CORRESPONDE >20%: el monto es menor realice el registro desde el modulo de compras '))
        depreciacion = 0.0
        bandera = False
        for line in self.as_assets.depreciation_line_ids:
            if self.as_date <= line.depreciation_date:
                if depreciacion > 0.0:
                    line.as_depreciation_store = depreciacion
                if not bandera:
                    line.as_value_updates = line.as_value_updates+self.as_value
                    bandera = True
                line.as_depreciation_periodo = line.as_value_updates * line.as_factor
                line.as_depreciation_update = line.as_depreciation_store * line.as_factor_ufvs
                line.as_update_depreciation = line.as_depreciation_store + line.as_depreciation_update
                line.as_depreciation_end = line.as_depreciation_periodo + line.as_update_depreciation
                line.as_valor_neto = line.as_depreciation_end + line.as_value_updates
                depreciacion = line.as_depreciation_store 
        purchase_order = self.env['purchase.order'].create({
            'partner_id': self.as_partner_id.id,
            'as_assets': self.as_assets.id,
            'order_line': [(0, 0, {
                'name': self.as_assets.product_id.name,
                'product_id': self.as_assets.product_id.id,
                'product_qty': 1,
                'product_uom': self.as_assets.product_id.uom_id.id,
                'taxes_id': self.as_assets.product_id.taxes_id.ids,
                'price_unit': self.as_value,
                'date_planned': fields.Date.today(),
            })]
        })
        purchase_order.button_confirm()

    def as_process_sale(self):
        cant = self.as_assets.category_id.method_number
        cont = 0
        calculo = 0.0
        afv_final = 0.0
        line_last = False
        date_depresiacion = ''
        if len(self.as_assets.depreciation_line_ids) < 1:
            raise UserError(_('No se puede vender activo, sin lineas de depreciación'))
        for line_asset in self.as_assets.depreciation_line_ids:
            if self.as_date <= line_asset.depreciation_date and not line_asset.move_check:
                cont+=1
                date_depresiacion = line_asset.depreciation_date
                line_last = line_asset
                break
        if not line_last:
            raise UserError(_('No se ha encontrado lineas de depresiacion con esa fecha'))
        date_start = str(date_depresiacion)
        date_to = str(self.as_date)
        ufv = self.env['res.currency'].search([('name', '=', 'UFV')],limit=1)
        as_ufv_ant = self.env['res.currency.rate'].search([('name', '=', date_start),('currency_id', '=', ufv.id)], order="name desc",limit=1).rate or 1
        if not as_ufv_ant:
            raise UserError(_('Debe darle valor a la UFV para la fecha de la factura'))
        as_ufv_actual = self.env['res.currency.rate'].search([('name', '=', date_to),('currency_id', '=', ufv.id)], order="name desc", limit=1).rate or 1
        if as_ufv_actual <=1 or as_ufv_ant <=1:
            ufvs = afv_final
        else:
            ufvs = as_ufv_actual / as_ufv_ant   
        self.as_assets.as_amount = line_last.as_depreciation_end
        self.as_assets.as_amount_sale_value = (line_last.as_value*abs(ufvs-1))
        self.as_assets.as_amount_sale_update = line_last.as_value_updates #valor actualizado
        self.as_assets.as_amount_sale = self.as_value
        self.as_generate_sale()
        assent = [] 
        for asiento in self.as_assets.as_account_sale_ids:
            assent.append(asiento.id)                                                                                            
        #Asiento contable numero 1
        account1 = self.as_create_account_move(
            self.as_assets.category_id.journal_id,
            self.as_assets.as_amount_sale_value,
            self.as_assets.as_amount_sale_value,
            self.as_assets.category_id.as_estructura_assets_id.as_account_1_debit_id,
            self.as_assets.category_id.as_estructura_assets_id.as_account_1_credit_id,
        )
        assent.append(account1.id)
        #Asiento contable numero 2
        account2 = self.as_create_account_move(
            self.as_assets.category_id.journal_id,
            self.as_assets.as_amount_sale_update,
            self.as_assets.as_amount_sale_update,
            self.as_assets.category_id.as_estructura_assets_id.as_account_2_debit_id,
            self.as_assets.category_id.as_estructura_assets_id.as_account_2_credit_id,
        )
        assent.append(account2.id)
        if self.as_value > line_last.as_depreciation_end:
            account3 = self.as_create_account_move(
            self.as_assets.category_id.journal_id,
            line_last.as_depreciation_end,
            line_last.as_value_updates,
            self.as_assets.category_id.as_estructura_assets_id.as_account_3_dep_id,
            self.as_assets.category_id.as_estructura_assets_id.as_account_3_her_id,
            True,True
            )
            assent.append(account3.id)
        else:
            account3 = self.as_create_account_move(
            self.as_assets.category_id.journal_id,
            line_last.as_depreciation_end,
            line_last.as_value_updates,
            self.as_assets.category_id.as_estructura_assets_id.as_account_3_dep_id,
            self.as_assets.category_id.as_estructura_assets_id.as_account_3_her_id,
            True,False
            )
            assent.append(account3.id)
        self.as_assets.as_account_sale_ids = assent
        self.as_assets.state = 'sale'
        for line_asset_a in self.as_assets.depreciation_line_ids:
            if line_asset_a.id > line_last.id and not line_asset.move_check:
                line_asset_a.unlink()
    
    def as_create_account_move(self,journal_id,amount_debit,amount_credit,debit,credit,type_assets=False,mayor=False):
        amount_debit = round(amount_debit,2)
        amount_credit = round(amount_credit,2)
        accoun_obj = self.env['account.move']
        account_line_obj = self.env['account.move.line']
        partner_search = self.env.user.partner_id
        pur_date = datetime.today()
        vals = {
            'journal_id' : journal_id.id,
            'currency_id' : self.env.user.company_id.currency_id.id,
            'date':pur_date,
            'move_type':'entry',
            'ref' : 'Asiento de venta de '+str(self.as_assets.name),
        }
        pur_id = accoun_obj.create(vals)
        res = {
            'move_id': pur_id.id,
            'name': 'Asiento de venta de '+str(self.as_assets.name),
            'partner_id': partner_search.id,
            'analytic_account_id': self.as_assets.account_analytic_id.id,
            'account_id': debit.id,
            'date_maturity':pur_date,
            'debit': amount_debit,
            'credit': 0.0,
            'currency_id': self.env.user.company_id.currency_id.id,
            }
        account_line_obj.with_context(check_move_validity=False).create(res)

        res = {
            'move_id': pur_id.id,
            'name': 'Asiento de venta de '+str(self.as_assets.name),
            'partner_id': partner_search.id,
            'analytic_account_id': self.as_assets.account_analytic_id.id,
            'account_id': credit.id,
            'date_maturity':pur_date,
            'debit': 0.0,
            'credit': amount_credit,
            'currency_id': self.env.user.company_id.currency_id.id,
            }
        account_line_obj.with_context(check_move_validity=False).create(res)
        if type_assets:
            #IT por cobrar
            res = {
                'move_id': pur_id.id,
                'name': 'Impuesto a las transacciones '+str(self.as_assets.name),
                'partner_id': partner_search.id,
                'analytic_account_id': self.as_assets.account_analytic_id.id,
                'account_id': self.as_assets.category_id.as_estructura_assets_id.as_account_3_itc_id.id,
                'date_maturity':pur_date,
                'debit': self.as_assets.as_amount_sale*0.03,
                'credit': 0.0,
                'currency_id': self.env.user.company_id.currency_id.id,
                }
            account_line_obj.with_context(check_move_validity=False).create(res)
            #Cuenta caja
            res = {
                'move_id': pur_id.id,
                'name': 'Caja banco '+str(self.as_assets.name),
                'partner_id': partner_search.id,
                'analytic_account_id': self.as_assets.account_analytic_id.id,
                'account_id': self.as_assets.category_id.as_estructura_assets_id.as_account_3_caj_id.id,
                'date_maturity':pur_date,
                'debit': self.as_assets.as_amount_sale,
                'credit': 0.0,
                'currency_id': self.env.user.company_id.currency_id.id,
                }
            account_line_obj.with_context(check_move_validity=False).create(res)
            #IT por pagar
            res = {
                'move_id': pur_id.id,
                'name': 'IT por pagar '+str(self.as_assets.name),
                'partner_id': partner_search.id,
                'analytic_account_id': self.as_assets.account_analytic_id.id,
                'account_id': self.as_assets.category_id.as_estructura_assets_id.as_account_3_itp_id.id,
                'date_maturity':pur_date,
                'debit': 0.0,
                'credit': self.as_assets.as_amount_sale*0.03,
                'currency_id': self.env.user.company_id.currency_id.id,
                }
            account_line_obj.with_context(check_move_validity=False).create(res)
            res = {
                'move_id': pur_id.id,
                'name': 'IVA DEF '+str(self.as_assets.name),
                'partner_id': partner_search.id,
                'analytic_account_id': self.as_assets.account_analytic_id.id,
                'account_id': self.as_assets.category_id.as_estructura_assets_id.as_account_3_iva_id.id,
                'date_maturity':pur_date,
                'debit': 0.0,
                'credit': self.as_assets.as_amount_sale*0.13,
                'currency_id': self.env.user.company_id.currency_id.id,
                }
            account_line_obj.with_context(check_move_validity=False).create(res)
            monto1 = (self.as_assets.as_amount_sale+(self.as_assets.as_amount_sale*0.03)+amount_debit)-(amount_credit+self.as_assets.as_amount_sale*0.13+self.as_assets.as_amount_sale*0.03)
            monto2 =  (amount_credit+self.as_assets.as_amount_sale*0.13+self.as_assets.as_amount_sale*0.03)-(self.as_assets.as_amount_sale+self.as_assets.as_amount_sale*0.03+self.as_assets.as_amount)
            if mayor:
                res = {
                    'move_id': pur_id.id,
                    'name': 'Otros ingresos '+str(self.as_assets.name),
                    'partner_id': partner_search.id,
                    'analytic_account_id': self.as_assets.account_analytic_id.id,
                    'account_id': self.as_assets.category_id.as_estructura_assets_id.as_account_3_oin_id.id,
                    'date_maturity':pur_date,
                    'debit': 0.0,
                    'credit': monto1,
                    'currency_id': self.env.user.company_id.currency_id.id,
                    }
                account_line_obj.with_context(check_move_validity=False).create(res)
            else:
                res = {
                    'move_id': pur_id.id,
                    'name': 'Otros ingresos '+str(self.as_assets.name),
                    'partner_id': partner_search.id,
                    'analytic_account_id': self.as_assets.account_analytic_id.id,
                    'account_id': self.as_assets.category_id.as_estructura_assets_id.as_account_3_oin_id.id,
                    'date_maturity':pur_date,
                    'debit': monto2,
                    'credit': 0.0,
                    'currency_id': self.env.user.company_id.currency_id.id,
                    }
                account_line_obj.with_context(check_move_validity=False).create(res)
        pur_id.action_post()
        return pur_id


    def as_generate_sale(self):
        so_vals = {
            'partner_id': self.as_partner_id.id,
            'as_assets': self.as_assets.id,
            'as_alias_lugar': 'AC',
            'order_line': [
                (0, 0, {
                    'name': self.as_assets.product_id.name,
                    'product_id': self.as_assets.product_id.id,
                    'product_uom_qty': 1,
                    'product_uom': self.as_assets.product_id.uom_id.id,
                    'tax_id': self.as_assets.product_id.taxes_id.ids,
                    'price_unit': self.as_value,
                    'route_id': self.as_ruta.id,
                    'discount': 0,
                })
            ],
            'company_id': self.as_assets.company_id.id,
        }
        sale_order = self.env['sale.order'].create(so_vals)
        sale_order.action_confirm()


    def as_process_revaluo(self):
        cant = self.as_assets.category_id.method_number
        cont = 0
        calculo = 0.0
        date_depresiacion = ''
        date_depresiacion_2 = ''
        for line_asset in self.as_assets.depreciation_line_ids:
            cont+=1
            date_depresiacion = line_asset.depreciation_date
            line_last = line_asset
        for line_asset in self.as_assets.depreciation_line_ids:
            date_depresiacion_2 = line_asset.depreciation_date
        bandera = False
        bandera_mon = False
        if self.as_date < date_depresiacion:
            raise UserError(_('La fecha de Reevaluo debe ser mayor a la ultima fecha de depreciación'))
        assets_lines_ajuste = self.as_assets.depreciation_line_ids.filtered(lambda line: line.as_revaluo)
        for x in range(0, self.as_vida_util):
            if self.as_assets.category_id.as_modality == 'anual':
                date_comprobacion = date_depresiacion + relativedelta(years=self.as_vida_util)
                if str(date_comprobacion) != str(self.as_date):
                    raise UserError(_('la fecha del revaluo deberia ser %s')%str(date_comprobacion))
                if not bandera:
                    date_start = str(self.as_date)
                    date_to =  str(self.as_date.strftime('%Y'))+'-'+'12'+'-'+'31'
                    bandera = True
                    if self.as_date < date_depresiacion_2:
                        raise UserError(_('La fecha de Reevaluo debe ser mayor a la ultima fecha de depreciación'))
                else:
                    date_assest = fields.Date.from_string(date_to)+ relativedelta(years=1)
                    date_anterior = str(fields.Date.from_string(date_to)+ relativedelta(years=1))
                    date_start = str(date_to)
                    date_to =  str(date_anterior)
                    if date_assest < date_depresiacion_2:
                        raise UserError(_('La fecha de Reevaluo debe ser mayor a la ultima fecha de depreciación'))
                line_last = self.as_get_assets_line(date_start,date_to,line_last,bandera_mon)
                bandera_mon = True
            else:
                date_comprobacion = date_depresiacion + relativedelta(month=self.as_vida_util)
                if str(date_comprobacion) != str(self.as_date):
                    raise UserError(_('la fecha del revaluo deberia ser %s')%str(date_comprobacion))
                if not bandera:
                    mes2= self.as_date.strftime('%M')
                    anio2= self.as_date.strftime('%Y')
                    periodo2 = calendar.monthrange(int(anio2),int(mes2))
                    date_start = str(self.as_date)
                    date_to =  str(self.as_date.strftime('%Y'))+'-'+str(self.as_date.strftime('%M'))+'-'+str(periodo2[1])
                    bandera = True
                    if self.as_date < date_depresiacion_2:
                        raise UserError(_('La fecha de Reevaluo debe ser mayor a la ultima fecha de depreciación'))
                else:
                    date_assest = fields.Date.from_string(date_to)+ relativedelta(month=1)
                    date_anterior = str(fields.Date.from_string(date_to)+ relativedelta(month=1))
                    date_start = str(date_to)
                    date_to =  str(date_anterior)
                    if date_assest < date_depresiacion_2:
                        raise UserError(_('La fecha de Reevaluo debe ser mayor a la ultima fecha de depreciación'))
                line_last = self.as_get_assets_line(date_start,date_to,line_last,bandera_mon)
                bandera_mon = True

    
    def as_process_ajuste(self):
        cant = self.as_assets.category_id.method_number
        cont = 0
        calculo = 0.0
        date_depresiacion = ''
        for line_asset in self.as_assets.depreciation_line_ids.filtered(lambda line: not line.as_ajustado):
            cont+=1
            date_depresiacion = line_asset.depreciation_date
            line_last = line_asset
            if cont == cant:
                if str(self.as_date) != str(line_asset.depreciation_date):
                    raise UserError(_('La fecha debe corresponder a ultima linea para ajustar %s')%str(line_asset.depreciation_date))
                if line_asset.as_valor_neto < 0:
                    if self.as_assets.category_id.as_assets_type == 'Tangible':
                        calculo = -1+(line_asset.as_depreciation_periodo -(-line_asset.as_valor_neto))
                    else:
                        calculo = (line_asset.as_depreciation_periodo -(-line_asset.as_valor_neto))
                    line_asset.as_depreciation_periodo = calculo
                    line_asset.as_depreciation_end = line_asset.as_update_depreciation+ line_asset.as_depreciation_periodo
                    line_asset.as_valor_neto = line_asset.as_value_updates-line_asset.as_depreciation_end
                    if self.as_assets.category_id.as_modality == 'anual':
                        date_start = str(line_asset.depreciation_date)
                        date_to =  str(line_asset.depreciation_date + relativedelta(years=1))
                    else:
                        date_start = str(line_asset.depreciation_date)
                        date_to = str(line_asset.depreciation_date + relativedelta(month=1))
        assets_lines_ajuste = self.as_assets.depreciation_line_ids.filtered(lambda line: line.as_ajustado)
        if assets_lines_ajuste:
            assets_lines_ajuste.unlink()
        date_depresiacion= datetime.strptime(str(date_depresiacion + relativedelta(days=1)), '%Y-%m-%d')
        date_wiz = datetime.strptime(str(self.as_date), '%Y-%m-%d')
        year = 0
        periodos = []
        if date_depresiacion <= date_wiz:
            for period in rrule(freq=YEARLY, bymonth=(12), dtstart=fields.Date.from_string(date_depresiacion), until=fields.Date.from_string(date_wiz)):
                periodos.append(str(period.date().strftime('%Y-%m')+'-31'))
            if periodos != []:
                bandera_mon = False
                for perid in periodos:
                    if self.as_assets.category_id.as_modality == 'anual':
                        date_start = str(fields.Date.from_string(perid)- relativedelta(years=1))
                        date_to =  str(perid)
                    else:
                        date_start = str(fields.Date.from_string(perid)- relativedelta(month=1))
                        date_to =  str(perid)
                    line_last = self.as_get_assets_line(date_start,date_to,line_last,bandera_mon)
                    bandera_mon = True



    def as_get_assets_line(self,date_start,date_to,line,bandera_mon):
        afv_final = 0.0
        sequence = len(self.as_assets.depreciation_line_ids)+1
        residual_amount = line.as_value
        if self.as_modality == 'Ajuste':
            as_value_updates2 = line.as_value_updates
        else:
            if not bandera_mon:
                as_value_updates2 = line.as_value_updates+self.as_value
            else:
                as_value_updates2 = line.as_value_updates

        ufv = self.env['res.currency'].search([('name', '=', 'UFV')],limit=1)
        as_ufv_ant = self.env['res.currency.rate'].search([('name', '=', date_start),('currency_id', '=', ufv.id)], order="name desc",limit=1).rate or 1
        if not as_ufv_ant:
            raise UserError(_('Debe darle valor a la UFV para la fecha de la factura'))
        as_ufv_actual = self.env['res.currency.rate'].search([('name', '=', date_to),('currency_id', '=', ufv.id)], order="name desc", limit=1).rate or 1
        if as_ufv_actual <=1 or as_ufv_ant <=1:
            ufvs = afv_final
        else:
            ufvs = as_ufv_actual / as_ufv_ant   
        as_updates = (as_value_updates2)*(ufvs-1)
        as_value_updates = as_value_updates2 + as_updates
        if self.as_modality == 'Ajuste':
            as_depreciation_periodo = 0.0
        else:
            meses = 0
            for period in rrule(freq=MONTHLY, bymonth=(), dtstart=fields.Date.from_string(date_start), until=fields.Date.from_string(date_to)):
                meses+=1
            factor = (self.as_coeficiente/100)/12*meses
            as_depreciation_periodo = as_value_updates * factor
        #Deprecion Acumulada
        as_depreciation_store = line.as_depreciation_end
        as_depreciation_update= (as_depreciation_store)*(ufvs-1)
        as_update_depreciation= as_depreciation_store + as_depreciation_update
        #Dep. Acumulada Final.
        as_depreciation_end= as_update_depreciation + as_depreciation_periodo
        # as_valor_neto = as_value_updates-as_depreciation_end
        if self.as_assets.category_id.as_assets_type == 'Tangible':
            as_valor_neto = 1
        else:
            as_valor_neto = 0
        vals = {
            'amount': line.as_depreciation_end,
            'asset_id': self.as_assets.id,
            'sequence': sequence,
            'name': ('Lineas de Ajuste') + '/' + str(sequence),
            'remaining_value': residual_amount,
            'depreciated_value': 0.0,
            'depreciation_date': date_to,
            'as_value': as_value_updates2,
            'as_ufv_inicial': str(as_ufv_ant),
            'as_ufv_final': str(as_ufv_actual),
            'as_updates': as_updates,
            'as_value_updates': as_value_updates,
            'as_depreciation_store': as_depreciation_store,
            'as_depreciation_periodo': as_depreciation_periodo,
            'as_update_depreciation': as_update_depreciation,
            'as_depreciation_update': as_depreciation_update,
            'as_depreciation_end': as_depreciation_end,
            'as_valor_neto': as_valor_neto,
        }
        if self.as_modality == 'Ajuste':
            vals['as_ajustado'] = True
        else:
            vals['as_revaluo'] = True
        
        return self.env['account.asset.depreciation.line'].create(vals)

