# -*- coding: utf-8 -*-
from odoo import models, api, fields,  _
import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools import float_compare, float_is_zero
from dateutil.rrule import rrule, MONTHLY

class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'
    _description = 'Asset/Revenue Recognition inherit'

    product_id = fields.Many2one('product.product', 'Product', required=True)
    first_depreciation_manual_date = fields.Date(
        string='First Depreciation Date',
        readonly=False,
        help='Note that this date does not alter the computation of the first journal entry in case of prorata temporis assets. It simply changes its accounting date'
    )
    as_date_depreciacion = fields.Date(string='Fecha para Depreciacion anterior (para extraer monto)')
    as_dias_activo = fields.Date(string='Fecha para el computo continuo de la depreciacion del periodo')
    as_depre_anterior = fields.Float(string='Dep. Acum. Final Anterior')
    as_account_move = fields.Many2one('account.move', string='Asiento de baja')
    state = fields.Selection(selection_add=[('sale', 'Vendido'),('discharged', 'De Baja')],ondelete={'sale': 'cascade','discharged': 'cascade'})
    as_amount = fields.Float(string='Valor para asentar')
    as_block = fields.Boolean(string='Bloquar Activo',default=False)
    #campos de ventas
    as_amount_sale_value = fields.Float(string='Valor',copy=False)
    as_amount_sale_update = fields.Float(string='Valor Actualizado',copy=False)
    as_amount_sale = fields.Float(string='Valor Venta',copy=False)
    as_account_sale_ids = fields.Many2many('account.move', string='Asiento de venta',copy=False)
    as_sale_count = fields.Integer(compute='_compute_sale_count',copy=False)
    as_purchase_count = fields.Integer(compute='_compute_purchase_count',copy=False)
    as_asiento_count = fields.Integer(compute="_invoice_count",copy=False)
    as_asentado = fields.Boolean(string="Asentada linea",copy=False)


    def as_process_sale(self):
        cant = self.category_id.method_number
        cont = 0
        calculo = 0.0
        afv_final = 0.0
        line_last = False
        date_depresiacion = ''
        if len(self.depreciation_line_ids) < 1:
            raise UserError(_('No se puede vender activo, sin lineas de depreciación'))
        if not self.category_id.as_estructura_assets_id:
            raise UserError(_('Debe seleccionar en la categoria de activos, la estructura de cuentas contables para venta'))
        for line_asset in self.depreciation_line_ids:
            if fields.Date.context_today(self) <= line_asset.depreciation_date and not line_asset.move_check:
                cont+=1
                date_depresiacion = line_asset.depreciation_date
                line_last = line_asset
                break
        if not line_last:
            raise UserError(_('No se ha encontrado lineas de depresiacion con esa fecha'))
        date_start = str(date_depresiacion)
        date_to = str(fields.Date.context_today(self))
        ufv = self.env['res.currency'].search([('name', '=', 'UFV')],limit=1)
        as_ufv_ant = self.env['res.currency.rate'].search([('name', '=', date_start),('currency_id', '=', ufv.id)], order="name desc",limit=1).rate or 1
        if not as_ufv_ant:
            raise UserError(_('Debe darle valor a la UFV para la fecha de la factura'))
        as_ufv_actual = self.env['res.currency.rate'].search([('name', '=', date_to),('currency_id', '=', ufv.id)], order="name desc", limit=1).rate or 1
        if as_ufv_actual <=1 or as_ufv_ant <=1:
            ufvs = afv_final
        else:
            ufvs = as_ufv_actual / as_ufv_ant   
        self.as_amount = line_last.as_depreciation_end
        self.as_amount_sale_value = (line_last.as_value*abs(ufvs-1))
        self.as_amount_sale_update = line_last.as_value_updates #valor actualizado
        self.as_amount_sale = self.as_value
        self.as_sale.as_assets = self
        assent = [] 
        for asiento in self.as_account_sale_ids:
            assent.append(asiento.id)                                                                                            
        #Asiento contable numero 1
        account1 = self.as_create_account_move(
            self.category_id.journal_id,
            self.as_amount_sale_value,
            self.as_amount_sale_value,
            self.category_id.as_estructura_assets_id.as_account_1_debit_id,
            self.category_id.as_estructura_assets_id.as_account_1_credit_id,
        )
        assent.append(account1.id)
        #Asiento contable numero 2
        account2 = self.as_create_account_move(
            self.category_id.journal_id,
            self.as_amount_sale_update,
            self.as_amount_sale_update,
            self.category_id.as_estructura_assets_id.as_account_2_debit_id,
            self.category_id.as_estructura_assets_id.as_account_2_credit_id,
        )
        assent.append(account2.id)
        if self.as_value > line_last.as_depreciation_end:
            account3 = self.as_create_account_move(
            self.category_id.journal_id,
            line_last.as_depreciation_end,
            line_last.as_value_updates,
            self.category_id.as_estructura_assets_id.as_account_3_dep_id,
            self.category_id.as_estructura_assets_id.as_account_3_her_id,
            True,True
            )
            assent.append(account3.id)
        else:
            account3 = self.as_create_account_move(
            self.category_id.journal_id,
            line_last.as_depreciation_end,
            line_last.as_value_updates,
            self.category_id.as_estructura_assets_id.as_account_3_dep_id,
            self.category_id.as_estructura_assets_id.as_account_3_her_id,
            True,False
            )
            assent.append(account3.id)
        self.as_account_sale_ids = assent
        self.state = 'sale'
        for line_asset_a in self.depreciation_line_ids:
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

    def _invoice_count(self):
        for rec in self:
            rec.ensure_one()
            rec.as_asiento_count = len(rec.as_account_sale_ids.ids)

    def action_view_asiento(self):
        self.ensure_one()
        action_pickings = self.env.ref('account.action_move_journal_line')
        action = action_pickings.read()[0]
        action['context'] = {}
        action['domain'] = [('id', 'in', self.as_account_sale_ids.ids)]
        return action

    def action_request_sale(self):
        self.ensure_one()
        action_hr_expense = self.env.ref('sale.action_orders')
        action = action_hr_expense.read()[0]
        action['context'] = {}
        result = self.env['sale.order'].search([('as_assets','=',self.id)])
        action['domain'] = [('id', 'in', result.ids)]
        return action

    def _compute_sale_count(self):
        result = self.env['sale.order'].search([('as_assets','=',self.id)])
        for order in self:
            order.as_sale_count = len(result)

    def action_request_purchase(self):
        self.ensure_one()
        action_hr_expense = self.env.ref('purchase.purchase_form_action')
        action = action_hr_expense.read()[0]
        action['context'] = {}
        result = self.env['purchase.order'].search([('as_assets','=',self.id)])
        action['domain'] = [('id', 'in', result.ids)]
        return action

    def _compute_purchase_count(self):
        result = self.env['purchase.order'].search([('as_assets','=',self.id)])
        for order in self:
            order.as_purchase_count = len(result)

    def validate(self):
        res = super(AccountAssetAsset, self).validate()
        self.as_block = True
        return res

    def as_state_close(self):
        for asset in self:
            cant = asset.category_id.method_number
            cont = 0
            asset.as_amount = 0.0
            for line_asset in self.depreciation_line_ids:
                cont+=1
                if cont == cant:
                    asset.as_amount = line_asset.as_depreciation_end 
            self.as_account_move =  asset.category_id.as_estructura_id.as_get_account(self)
            assent = []        
            for asiento in self.as_account_sale_ids:
                assent.append(asiento.id)                                                                                  
            #Asiento contable numero 1
            account1 = self.as_create_account_move(
                self.category_id.journal_id,
                self.as_amount,
                self.as_amount,
                self.category_id.as_estructura_assets_id.as_discharged_debit_id,
                self.category_id.as_estructura_assets_id.as_discharged_credit_id,
            )
            assent.append(account1.id)
            self.as_account_sale_ids = assent
            self.state = 'discharged'

    def as_create_account_move(self,journal_id,amount_debit,amount_credit,debit,credit,type_assets=False,mayor=False):
        accoun_obj = self.env['account.move']
        account_line_obj = self.env['account.move.line']
        partner_search = self.env.user.partner_id
        pur_date = datetime.today()
        vals = {
            'journal_id' : journal_id.id,
            'currency_id' : self.env.user.company_id.currency_id.id,
            'date':pur_date,
            'move_type':'entry',
            'ref' : 'Asiento dar de baja de '+str(self.name),
        }
        pur_id = accoun_obj.create(vals)
        res = {
            'move_id': pur_id.id,
            'name': 'Asiento dar de baja de '+str(self.name),
            'partner_id': partner_search.id,
            'analytic_account_id': self.account_analytic_id.id,
            'account_id': debit.id,
            'date_maturity':pur_date,
            'debit': amount_debit,
            'credit': 0.0,
            'currency_id': self.env.user.company_id.currency_id.id,
            }
        account_line_obj.with_context(check_move_validity=False).create(res)

        res = {
            'move_id': pur_id.id,
            'name': 'Asiento dar de baja de '+str(self.name),
            'partner_id': partner_search.id,
            'analytic_account_id': self.account_analytic_id.id,
            'account_id': credit.id,
            'date_maturity':pur_date,
            'debit': 0.0,
            'credit': amount_credit,
            'currency_id': self.env.user.company_id.currency_id.id,
            }
        account_line_obj.with_context(check_move_validity=False).create(res)
        pur_id.action_post()
        return pur_id
    # @api.multi
    def action_draft(self):
        for registro in self:
            registro.state='draft'
            registro.as_block = False

    # @api.multi
    def action_open(self):
        for registro in self:
            registro.state='open'
            registro.as_account_move.button_draft()
            registro.as_account_move.button_cancel()
            for account in registro.as_account_sale_ids:
                account.button_draft()
                account.button_cancel()
            registro.as_account_sale_ids = False
            registro.as_account_move = False

    # @api.multi
    def compute_generated_entries_category(self, date, asset_type=None,active_ids=None):
        created_move_ids = []
        type_domain = []
        if asset_type:
            type_domain = [('type', '=', asset_type)]
        ungrouped_assets = self.env['account.asset.asset'].search(type_domain + [('state', '=', 'open'), ('category_id.group_entries', '=', False),('id', 'in', active_ids)])
        created_move_ids += ungrouped_assets._compute_entries(date, group_entries=False)

        for grouped_category in self.env['account.asset.category'].search(type_domain + [('group_entries', '=', True)]):
            assets = self.env['account.asset.asset'].search([('state', '=', 'open'), ('category_id', '=', grouped_category.id),('id', 'in', active_ids)])
            created_move_ids += assets._compute_entries(date, group_entries=True)
        return created_move_ids

    # @api.multi
    @api.depends('depreciation_line_ids.move_id')
    def _entry_count(self):
        for asset in self:
            res = self.env['account.asset.depreciation.line'].search_count([('asset_id', '=', asset.id), ('move_id', '!=', False)])
            res2 = self.env['account.asset.depreciation.line'].search_count([('asset_id', '=', asset.id), ('move_id2', '!=', False)])
            asset.entry_count = res+res2 or 0

    # @api.multi
    def open_entries(self):
        move_ids = []
        for asset in self:
            for depreciation_line in asset.depreciation_line_ids:
                if depreciation_line.move_id:
                    move_ids.append(depreciation_line.move_id.id)
                if depreciation_line.move_id2:
                    move_ids.append(depreciation_line.move_id2.id)
        return {
            'name': _('Journal Entries'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', move_ids)],
        }

    # @api.multi
    def compute_depreciation_board(self):
        as_depre_anterior = 0.0
        self.ensure_one()
        if not self.as_block:
            posted_depreciation_line_ids = self.depreciation_line_ids.filtered(lambda x: x.move_check).sorted(key=lambda l: l.depreciation_date)
            unposted_depreciation_line_ids = self.depreciation_line_ids.filtered(lambda x: not x.move_check)

            # Remove old unposted depreciation lines. We cannot use unlink() with One2many field
            commands = [(2, line_id.id, False) for line_id in unposted_depreciation_line_ids]
            if self.value_residual != 0.0:
                amount_to_depr = residual_amount = self.value_residual
                amount_to_depr2 = residual_amount2 = self.value - self.salvage_value
                # if we already have some previous validated entries, starting date is last entry + method period
                if posted_depreciation_line_ids and posted_depreciation_line_ids[-1].depreciation_date:
                    last_depreciation_date = fields.Date.from_string(posted_depreciation_line_ids[-1].depreciation_date)
                    depreciation_date = last_depreciation_date + relativedelta(months=+self.method_period)
                else:
                    # depreciation_date computed from the purchase date
                    depreciation_date = self.date
                    if self.date_first_depreciation == 'last_day_period':
                        # depreciation_date = the last day of the month
                        depreciation_date = depreciation_date + relativedelta(day=31)
                        # ... or fiscalyear depending the number of period
                        if self.method_period == 12:
                            depreciation_date = depreciation_date + relativedelta(month=int(self.company_id.fiscalyear_last_month))
                            depreciation_date = depreciation_date + relativedelta(day=self.company_id.fiscalyear_last_day)
                            if depreciation_date < self.date:
                                depreciation_date = depreciation_date + relativedelta(years=1)
                    elif self.first_depreciation_manual_date and self.first_depreciation_manual_date != self.date:
                        # depreciation_date set manually from the 'first_depreciation_manual_date' field
                        depreciation_date = self.first_depreciation_manual_date

                as_value_updates = residual_amount
                as_value_updates1 = residual_amount
                as_value_updates2 = -1
                total_days = (depreciation_date.year % 4) and 365 or 366
                month_day = depreciation_date.day
                as_update_depreciation = 0.0
                as_depreciation_store = 0.0
                as_depreciation_end = 0.0
                as_depreciation_update = 0.0
                as_valor_neto = 0.0
                undone_dotation_number = self._compute_board_undone_dotation_nb(depreciation_date, total_days)
                afv_inicial = 0.0
                afv_final = 0.0
                as_depre_anterior = 0.0
                depreciacion_anterior = 0.0
                if self.as_date_depreciacion:
                    assets = self.env['account.asset.depreciation.line'].search([('depreciation_date', '=', str(self.as_date_depreciacion)),('asset_id.product_id', '=', self.product_id.id)],limit=1)
                    if assets:
                        as_depre_anterior = float(assets.as_depreciation_end)
                fecha=''
                as_primer_dia = False
                for x in range(len(posted_depreciation_line_ids), undone_dotation_number):
                    sequence = x + 1
                    amount = self._compute_board_amount(sequence, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, depreciation_date)
                    amount = self.currency_id.round(amount)
                    if float_is_zero(amount, precision_rounding=self.currency_id.rounding):
                        continue
                    residual_amount -= amount
                    primer_dia = ''
                    primer_ultimo = ''
                    mes= (datetime.strptime(str(self.date), '%Y-%m-%d')).strftime('%m')
                    anio= (datetime.strptime(str(self.date), '%Y-%m-%d')).strftime('%Y')
                    year= (datetime.strptime(str(self.date), '%Y-%m-%d') - relativedelta(years=+1)).strftime('%Y')
                    periodo = calendar.monthrange(int(anio),int(mes))
                    if self.method_period == 12:
                        if sequence <= 1:
                            primer_dia= str(self.date)
                            primer_anterior= str(year)+'-'+'12'+'-'+'31'
                            primer_ultimo= str(anio)+'-'+'12'+'-'+'31'
                        else:
                            anio= (datetime.strptime(str(depreciation_date), '%Y-%m-%d')).strftime('%Y')
                            year= (datetime.strptime(str(depreciation_date), '%Y-%m-%d') - relativedelta(years=+1)).strftime('%Y')
                            primer_dia= str(year)+'-'+'12'+'-'+'31'
                            primer_anterior= str(year)+'-'+'12'+'-'+'31'
                            primer_ultimo= str(anio)+'-'+'12'+'-'+'31'
                    else:
                        if sequence <= 1:
                            if not self.first_depreciation_manual_date:
                                primer_dia= str(self.invoice_id.date.strftime('%Y-%m-%d'))
                            else:
                                primer_dia= str(self.first_depreciation_manual_date)
                            mes= (datetime.strptime(str(primer_dia), '%Y-%m-%d')).strftime('%m')
                            anio= (datetime.strptime(str(primer_dia), '%Y-%m-%d')).strftime('%Y')
                            periodo = calendar.monthrange(int(anio),int(mes))
                            primer_ultimo= str(int(anio))+'-'+mes+'-'+str(periodo[1])
                            as_depreciation_store= as_depre_anterior
                        else:
                            #primer dia
                            mes2= (datetime.strptime(str(depreciation_date), '%Y-%m-%d') - relativedelta(months=1)).strftime('%m')
                            anio2= (datetime.strptime(str(depreciation_date), '%Y-%m-%d') - relativedelta(months=1)).strftime('%Y')
                            periodo2 = calendar.monthrange(int(anio2),int(mes2))
                            primer_dia= str(int(anio2))+'-'+mes2+'-'+str(periodo2[1])
                            #ultimo dia
                            mes= (datetime.strptime(str(depreciation_date), '%Y-%m-%d')).strftime('%m')
                            anio= (datetime.strptime(str(depreciation_date), '%Y-%m-%d')).strftime('%Y')
                            periodo = calendar.monthrange(int(anio),int(mes))
                            primer_ultimo= str(int(anio))+'-'+mes+'-'+str(periodo[1])
                    ufv = self.env['res.currency'].search([('name', '=', 'UFV')],limit=1)
                    as_ufv_ant = self.env['res.currency.rate'].search([('name', '=', primer_dia),('currency_id', '=', ufv.id)], order="name desc",limit=1).rate or 1
                    if not as_ufv_ant:
                        raise UserError(_('Debe darle valor a la UFV para la fecha de la factura'))
                    as_ufv_actual = self.env['res.currency.rate'].search([('name', '=', primer_ultimo),('currency_id', '=', ufv.id)], order="name desc", limit=1).rate or 1
                    if as_ufv_actual <=1 or as_ufv_ant <=1:
                        ufvs = afv_final
                    else:
                        ufvs = as_ufv_actual / as_ufv_ant   
                    if as_value_updates2 == -1:
                        as_value_updates2 =  self.value_residual
                    #Actualizacion
                    as_updates = (as_value_updates2)*(ufvs-1)
                    #Valor Actualizado
                    as_value_updates = as_value_updates2 + as_updates
                    #depresiacion periodo
                    if self.as_dias_activo:
                        fecha_factura = datetime.strptime(str(self.as_dias_activo), '%Y-%m-%d')
                    else:
                        if self.first_depreciation_manual_date:
                            fecha_factura = datetime.strptime(str(self.first_depreciation_manual_date), '%Y-%m-%d')
                        elif self.invoice_id.date:
                            fecha_factura = datetime.strptime(str(self.invoice_id.date.strftime('%Y-%m-%d')), '%Y-%m-%d')
                    fecha_ultimo = datetime.strptime(str(primer_ultimo), '%Y-%m-%d')
                    dias = fecha_ultimo - fecha_factura
                    
                    if self.category_id.as_modality == 'anual':
                        fecha_inicio = str(self.date)
                        fecha_fin = primer_ultimo
                        meses = 0
                        for period in rrule(freq=MONTHLY, bymonth=(), dtstart=fields.Date.from_string(fecha_inicio), until=fields.Date.from_string(fecha_fin)):
                            meses+=1
                        coeficiente = (self.category_id.as_coeficiente)/100
                        if meses < self.method_period:
                            factor = meses*(coeficiente)/self.method_period
                        else:
                            factor = coeficiente
                    else:
                        dias = int(dias.days)
                        if self.category_id.as_dias_util > 0:
                            factor = (dias*100)/self.category_id.as_dias_util
                            factor = (factor/100)
                        else:
                            factor = 1
                    as_depreciation_periodo = as_value_updates * factor
                    #Deprecion Acumulada
                    if sequence > 1:
                        as_depreciation_store= as_depreciation_end
                    #Dep. Acumulada Actualizada
                    #Actualizacion Dep Acum
                    as_depreciation_update= (as_depreciation_store)*(ufvs-1)
                    as_update_depreciation= as_depreciation_store + as_depreciation_update
                    #Dep. Acumulada Final.
                    as_depreciation_end= as_update_depreciation + as_depreciation_periodo
                    #Valor neto
                    if self.category_id.as_date_inicio:
                        if not as_primer_dia:
                            as_primer_dia = True
                        else:
                            depreciation_date = datetime.strptime(primer_ultimo, '%Y-%m-%d').date()
                    as_valor_neto = as_value_updates-as_depreciation_end
                    vals = {
                        'amount': amount,
                        'asset_id': self.id,
                        'sequence': sequence,
                        'name': (self.code or '') + '/' + str(sequence),
                        'remaining_value': residual_amount,
                        'depreciated_value': self.value - (self.salvage_value + residual_amount),
                        'depreciation_date': depreciation_date,
                        'as_value': as_value_updates2,
                        'as_ufv_inicial': str(as_ufv_ant),
                        'as_ufv_final': str(as_ufv_actual),
                        'as_updates': as_updates,
                        'as_factor': factor,
                        'as_factor_ufvs': ufvs-1,
                        'as_value_updates': as_value_updates,
                        'as_depreciation_store': as_depreciation_store,
                        'as_depreciation_periodo': as_depreciation_periodo,
                        'as_update_depreciation': as_update_depreciation,
                        'as_depreciation_update': as_depreciation_update,
                        'as_depreciation_end': as_depreciation_end,
                        'as_valor_neto': as_valor_neto,
                    }
                    commands.append((0, False, vals))
                    fecha = primer_ultimo
                    afv_final = ufvs
                    as_value_updates2=as_value_updates2 + as_updates

                    depreciation_date = depreciation_date + relativedelta(months=+self.method_period)

                    if month_day > 28 and self.date_first_depreciation == 'manual':
                        max_day_in_month = calendar.monthrange(depreciation_date.year, depreciation_date.month)[1]
                        depreciation_date = depreciation_date.replace(day=min(max_day_in_month, month_day))

                    # datetime doesn't take into account that the number of days is not the same for each month
                    if not self.prorata and self.method_period % 12 != 0 and self.date_first_depreciation == 'last_day_period':
                        max_day_in_month = calendar.monthrange(depreciation_date.year, depreciation_date.month)[1]
                        depreciation_date = depreciation_date.replace(day=max_day_in_month)

            self.write({'depreciation_line_ids': commands,'as_depre_anterior':as_depre_anterior})

        return True    

    def as_get_ufvs_update(self):
        as_depre_anterior = 0.0
        self.ensure_one()
        posted_depreciation_line_ids = self.depreciation_line_ids.filtered(lambda x: x.move_check).sorted(key=lambda l: l.depreciation_date)
        unposted_depreciation_line_ids = self.depreciation_line_ids.filtered(lambda x: not x.move_check)

        # Remove old unposted depreciation lines. We cannot use unlink() with One2many field
        commands = [(2, line_id.id, False) for line_id in unposted_depreciation_line_ids]
        if self.value_residual != 0.0:
            amount_to_depr = residual_amount = self.value_residual
            amount_to_depr2 = residual_amount2 = self.value - self.salvage_value
            # if we already have some previous validated entries, starting date is last entry + method period
            if posted_depreciation_line_ids and posted_depreciation_line_ids[-1].depreciation_date:
                last_depreciation_date = fields.Date.from_string(posted_depreciation_line_ids[-1].depreciation_date)
                depreciation_date = last_depreciation_date + relativedelta(months=+self.method_period)
            else:
                # depreciation_date computed from the purchase date
                depreciation_date = self.date
                if self.date_first_depreciation == 'last_day_period':
                    # depreciation_date = the last day of the month
                    depreciation_date = depreciation_date + relativedelta(day=31)
                    # ... or fiscalyear depending the number of period
                    if self.method_period == 12:
                        depreciation_date = depreciation_date + relativedelta(month=int(self.company_id.fiscalyear_last_month))
                        depreciation_date = depreciation_date + relativedelta(day=self.company_id.fiscalyear_last_day)
                        if depreciation_date < self.date:
                            depreciation_date = depreciation_date + relativedelta(years=1)
                elif self.first_depreciation_manual_date and self.first_depreciation_manual_date != self.date:
                    # depreciation_date set manually from the 'first_depreciation_manual_date' field
                    depreciation_date = self.first_depreciation_manual_date

            as_value_updates = residual_amount
            as_value_updates1 = residual_amount
            as_value_updates2 = -1
            total_days = (depreciation_date.year % 4) and 365 or 366
            month_day = depreciation_date.day
            as_update_depreciation = 0.0
            as_depreciation_store = 0.0
            as_depreciation_end = 0.0
            as_depreciation_update = 0.0
            as_valor_neto = 0.0
            undone_dotation_number = self._compute_board_undone_dotation_nb(depreciation_date, total_days)
            afv_inicial = 0.0
            afv_final = 0.0
            as_depre_anterior = 0.0
            depreciacion_anterior = 0.0
            if self.as_date_depreciacion:
                assets = self.env['account.asset.depreciation.line'].search([('depreciation_date', '=', str(self.as_date_depreciacion)),('asset_id.product_id', '=', self.product_id.id)],limit=1)
                if assets:
                    as_depre_anterior = float(assets.as_depreciation_end)
            fecha=''
            as_primer_dia = False
            for x in range(len(posted_depreciation_line_ids), undone_dotation_number):
                sequence = x + 1
                amount = self._compute_board_amount(sequence, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, depreciation_date)
                amount = self.currency_id.round(amount)
                if float_is_zero(amount, precision_rounding=self.currency_id.rounding):
                    continue
                residual_amount -= amount
                primer_dia = ''
                primer_ultimo = ''
                mes= (datetime.strptime(str(self.date), '%Y-%m-%d')).strftime('%m')
                anio= (datetime.strptime(str(self.date), '%Y-%m-%d')).strftime('%Y')
                year= (datetime.strptime(str(self.date), '%Y-%m-%d') - relativedelta(years=+1)).strftime('%Y')
                periodo = calendar.monthrange(int(anio),int(mes))
                if self.method_period == 12:
                    if sequence <= 1:
                        primer_dia= str(self.date)
                        primer_anterior= str(year)+'-'+'12'+'-'+'31'
                        primer_ultimo= str(anio)+'-'+'12'+'-'+'31'
                    else:
                        anio= (datetime.strptime(str(depreciation_date), '%Y-%m-%d')).strftime('%Y')
                        year= (datetime.strptime(str(depreciation_date), '%Y-%m-%d') - relativedelta(years=+1)).strftime('%Y')
                        primer_dia= str(year)+'-'+'12'+'-'+'31'
                        primer_anterior= str(year)+'-'+'12'+'-'+'31'
                        primer_ultimo= str(anio)+'-'+'12'+'-'+'31'
                else:
                    if sequence <= 1:
                        if not self.first_depreciation_manual_date:
                            primer_dia= str(self.invoice_id.date.strftime('%Y-%m-%d'))
                        else:
                            primer_dia= str(self.first_depreciation_manual_date)
                        mes= (datetime.strptime(str(primer_dia), '%Y-%m-%d')).strftime('%m')
                        anio= (datetime.strptime(str(primer_dia), '%Y-%m-%d')).strftime('%Y')
                        periodo = calendar.monthrange(int(anio),int(mes))
                        primer_ultimo= str(int(anio))+'-'+mes+'-'+str(periodo[1])
                        as_depreciation_store= as_depre_anterior
                    else:
                        #primer dia
                        mes2= (datetime.strptime(str(depreciation_date), '%Y-%m-%d') - relativedelta(months=1)).strftime('%m')
                        anio2= (datetime.strptime(str(depreciation_date), '%Y-%m-%d') - relativedelta(months=1)).strftime('%Y')
                        periodo2 = calendar.monthrange(int(anio2),int(mes2))
                        primer_dia= str(int(anio2))+'-'+mes2+'-'+str(periodo2[1])
                        #ultimo dia
                        mes= (datetime.strptime(str(depreciation_date), '%Y-%m-%d')).strftime('%m')
                        anio= (datetime.strptime(str(depreciation_date), '%Y-%m-%d')).strftime('%Y')
                        periodo = calendar.monthrange(int(anio),int(mes))
                        primer_ultimo= str(int(anio))+'-'+mes+'-'+str(periodo[1])
                ufv = self.env['res.currency'].search([('name', '=', 'UFV')],limit=1)
                as_ufv_ant = self.env['res.currency.rate'].search([('name', '=', primer_dia),('currency_id', '=', ufv.id)], order="name desc",limit=1).rate or 1
                if not as_ufv_ant:
                    raise UserError(_('Debe darle valor a la UFV para la fecha de la factura'))
                as_ufv_actual = self.env['res.currency.rate'].search([('name', '=', primer_ultimo),('currency_id', '=', ufv.id)], order="name desc", limit=1).rate or 1
                if as_ufv_actual <=1 or as_ufv_ant <=1:
                    ufvs = afv_final
                else:
                    ufvs = as_ufv_actual / as_ufv_ant   
                if as_value_updates2 == -1:
                    as_value_updates2 =  self.value_residual
                #Actualizacion
                as_updates = (as_value_updates2)*(ufvs-1)
                #Valor Actualizado
                as_value_updates = as_value_updates2 + as_updates
                #depresiacion periodo
                if self.as_dias_activo:
                    fecha_factura = datetime.strptime(str(self.as_dias_activo), '%Y-%m-%d')
                else:
                    if self.first_depreciation_manual_date:
                        fecha_factura = datetime.strptime(str(self.first_depreciation_manual_date), '%Y-%m-%d')
                    elif self.invoice_id.date:
                        fecha_factura = datetime.strptime(str(self.invoice_id.date.strftime('%Y-%m-%d')), '%Y-%m-%d')
                fecha_ultimo = datetime.strptime(str(primer_ultimo), '%Y-%m-%d')
                dias = fecha_ultimo - fecha_factura
                
                if self.category_id.as_modality == 'anual':
                    fecha_inicio = str(self.date)
                    fecha_fin = primer_ultimo
                    meses = 0
                    for period in rrule(freq=MONTHLY, bymonth=(), dtstart=fields.Date.from_string(fecha_inicio), until=fields.Date.from_string(fecha_fin)):
                        meses+=1
                    coeficiente = (self.category_id.as_coeficiente)/100
                    if meses < self.method_period:
                        factor = meses*(coeficiente)/self.method_period
                    else:
                        factor = coeficiente
                else:
                    dias = int(dias.days)
                    if self.category_id.as_dias_util > 0:
                        factor = (dias*100)/self.category_id.as_dias_util
                        factor = (factor/100)
                    else:
                        factor = 1
                as_depreciation_periodo = as_value_updates * factor
                #Deprecion Acumulada
                if sequence > 1:
                    as_depreciation_store= as_depreciation_end
                #Dep. Acumulada Actualizada
                #Actualizacion Dep Acum
                as_depreciation_update= (as_depreciation_store)*(ufvs-1)
                as_update_depreciation= as_depreciation_store + as_depreciation_update
                #Dep. Acumulada Final.
                as_depreciation_end= as_update_depreciation + as_depreciation_periodo
                #Valor neto
                if self.category_id.as_date_inicio:
                    if not as_primer_dia:
                        as_primer_dia = True
                    else:
                        depreciation_date = datetime.strptime(primer_ultimo, '%Y-%m-%d').date()
                as_valor_neto = as_value_updates-as_depreciation_end
                vals = {
                    'amount': amount,
                    'asset_id': self.id,
                    'sequence': sequence,
                    'name': (self.code or '') + '/' + str(sequence),
                    'remaining_value': residual_amount,
                    'depreciated_value': self.value - (self.salvage_value + residual_amount),
                    'depreciation_date': depreciation_date,
                    'as_value': as_value_updates2,
                    'as_ufv_inicial': str(as_ufv_ant),
                    'as_ufv_final': str(as_ufv_actual),
                    'as_updates': as_updates,
                    'as_factor': factor,
                    'as_factor_ufvs': ufvs-1,
                    'as_value_updates': as_value_updates,
                    'as_depreciation_store': as_depreciation_store,
                    'as_depreciation_periodo': as_depreciation_periodo,
                    'as_update_depreciation': as_update_depreciation,
                    'as_depreciation_update': as_depreciation_update,
                    'as_depreciation_end': as_depreciation_end,
                    'as_valor_neto': as_valor_neto,
                }
                commands.append((0, False, vals))
                fecha = primer_ultimo
                afv_final = ufvs
                as_value_updates2=as_value_updates2 + as_updates

                depreciation_date = depreciation_date + relativedelta(months=+self.method_period)

                if month_day > 28 and self.date_first_depreciation == 'manual':
                    max_day_in_month = calendar.monthrange(depreciation_date.year, depreciation_date.month)[1]
                    depreciation_date = depreciation_date.replace(day=min(max_day_in_month, month_day))

                # datetime doesn't take into account that the number of days is not the same for each month
                if not self.prorata and self.method_period % 12 != 0 and self.date_first_depreciation == 'last_day_period':
                    max_day_in_month = calendar.monthrange(depreciation_date.year, depreciation_date.month)[1]
                    depreciation_date = depreciation_date.replace(day=max_day_in_month)

        self.write({'depreciation_line_ids': commands,'as_depre_anterior':as_depre_anterior})



class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'
    _description = 'Asset depreciation line inherit'

    as_value = fields.Float(string='Valor')
    as_updates = fields.Float(string='Actualización')
    as_value_updates = fields.Float(string='Valor Actualizado')
    as_depreciation_store = fields.Float(string='Depreciacion Acumulada')
    as_depreciation_update = fields.Float(string='Actualización Dep Acum')
    as_update_depreciation = fields.Float(string='Dep. Acumulada Actualizada')
    as_depreciation_periodo = fields.Float(string='Depreciacion Periodo')
    as_depreciation_end = fields.Float(string='Dep. Acumulada Final')
    as_valor_neto = fields.Float(string='Valor neto')
    as_factor = fields.Float(string='Factor',digits=(12, 6))
    as_factor_ufvs = fields.Float(string='Factor UFVs',digits=(12, 6))
    as_ufv_inicial = fields.Char(string='UFV inicial')
    as_ufv_final = fields.Char(string='UFV final')
    move_id2 = fields.Many2one('account.move', string='Depreciation Entry 2')
    move_id3 = fields.Many2one('account.move', string='Depreciation Entry 3')
    as_ajustado = fields.Boolean(string='Ajustado')
    as_revaluo = fields.Boolean(string='Revaluado')

    def post_lines_and_close_asset(self):
        for line in self:
            line.log_message_when_posted()
            asset = line.asset_id
            if asset.currency_id.is_zero(asset.value_residual):
                asset.message_post(body=_("Document closed."))
                # asset.write({'state': 'close'})

    # @api.multi
    def create_move(self, post_move=True):
        created_moves = self.env['account.move']
        for line in self:
            if line.move_id:
                raise UserError(_('This depreciation is already linked to a journal entry. Please post or delete it.'))
            move_vals = self._prepare_move(line,line.as_updates)
            if move_vals != {}:
                move = self.env['account.move'].create(move_vals)
                line.write({'move_id': move.id, 'move_check': True})
                created_moves |= move
            move_vals2 = self._prepare_move2(line,line.as_depreciation_update)
            if move_vals2 != {}:
                move2 = self.env['account.move'].create(move_vals2)
                line.write({'move_check': True,'move_id2': move2.id,})
                created_moves |= move2
            move_vals3 = self._prepare_move3(line,line.as_depreciation_periodo)
            if move_vals3 != {}:
                move_id3 = self.env['account.move'].create(move_vals3)
                line.write({'move_check': True,'move_id3': move_id3.id,})
                created_moves |= move_id3
            line.asset_id.as_asentado = True
            
        if post_move and created_moves:
            created_moves.filtered(lambda m: any(m.asset_depreciation_ids.mapped('asset_id.category_id.open_asset'))).post()
        return [x.id for x in created_moves]


    def _prepare_move(self, line,amount):
        category_id = line.asset_id.category_id
        account_analytic_id = line.asset_id.account_analytic_id
        analytic_tag_ids = line.asset_id.analytic_tag_ids
        depreciation_date = self.env.context.get('depreciation_date') or line.depreciation_date or fields.Date.context_today(self)
        depreciation_date_end = self.get_end_day(depreciation_date)
        company_currency = line.asset_id.company_id.currency_id
        current_currency = line.asset_id.currency_id
        prec = company_currency.decimal_places
        amount = current_currency._convert(
            amount, company_currency, line.asset_id.company_id, depreciation_date)
        asset_name = 'Depreciacion de Activos Fijos '+line.asset_id.name + ' (%s/%s)' % (line.sequence, len(line.asset_id.depreciation_line_ids))+' al '+depreciation_date_end
        move_line_1 = {
            'name': asset_name,
            'account_id': category_id.journal_id.payment_credit_account_id.id,
            'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
            'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'partner_id': line.asset_id.partner_id.id,
            'analytic_account_id': account_analytic_id.id if category_id.type == 'sale' else False,
            'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'sale' else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and - 1.0 * amount or 0.0,
            'product_id': line.asset_id.product_id.id,
            
        }
        move_line_2 = {
            'name': asset_name,
            'account_id':  category_id.account_asset_id.id,
            'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
            'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'partner_id': line.asset_id.partner_id.id,
            'analytic_account_id': account_analytic_id.id if category_id.type == 'purchase' else False,
            'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'purchase' else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and amount or 0.0,
            'product_id': line.asset_id.product_id.id,
        }
        if amount > 0.0:
            move_vals = {
                'ref': line.asset_id.code,
                'date': depreciation_date or False,
                'journal_id': category_id.journal_id.id,
                'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
            }
        else:
            move_vals = {}

        return move_vals

    def _prepare_move2(self, line,amount):
        category_id = line.asset_id.category_id
        account_analytic_id = line.asset_id.account_analytic_id
        analytic_tag_ids = line.asset_id.analytic_tag_ids
        depreciation_date = self.env.context.get('depreciation_date') or line.depreciation_date or fields.Date.context_today(self)
        depreciation_date_end = self.get_end_day(depreciation_date)
        company_currency = line.asset_id.company_id.currency_id
        current_currency = line.asset_id.currency_id
        prec = company_currency.decimal_places
        amount = current_currency._convert(
            amount, company_currency, line.asset_id.company_id, depreciation_date)
        asset_name = 'Depreciacion de Activos Fijos '+line.asset_id.name + ' (%s/%s)' % (line.sequence, len(line.asset_id.depreciation_line_ids))+' al '+depreciation_date_end
        move_line_1 = {
            'name': asset_name,
            'account_id':category_id.account_depreciation_id.id,
            'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
            'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'partner_id': line.asset_id.partner_id.id,
            'analytic_account_id': account_analytic_id.id if category_id.type == 'sale' else False,
            'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'sale' else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and - 1.0 * amount or 0.0,
            'product_id': line.asset_id.product_id.id,
            
        }
        move_line_2 = {
            'name': asset_name,
            'account_id': category_id.journal_id.payment_debit_account_id.id,
            'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
            'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'partner_id': line.asset_id.partner_id.id,
            'analytic_account_id': account_analytic_id.id if category_id.type == 'purchase' else False,
            'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'purchase' else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and amount or 0.0,
            'product_id': line.asset_id.product_id.id,
        }
        if amount > 0.0:
            move_vals = {
                'ref': line.asset_id.code,
                'date': depreciation_date or False,
                'journal_id': category_id.journal_id.id,
                'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
            }
        else:
            move_vals = {}
        return move_vals

    def _prepare_move3(self, line,amount):
        category_id = line.asset_id.category_id
        account_analytic_id = line.asset_id.account_analytic_id
        analytic_tag_ids = line.asset_id.analytic_tag_ids
        depreciation_date = self.env.context.get('depreciation_date') or line.depreciation_date or fields.Date.context_today(self)
        depreciation_date_end = self.get_end_day(depreciation_date)
        company_currency = line.asset_id.company_id.currency_id
        current_currency = line.asset_id.currency_id
        prec = company_currency.decimal_places
        amount = current_currency._convert(
            amount, company_currency, line.asset_id.company_id, depreciation_date)
        asset_name = 'Depreciacion de Activos Fijos '+line.asset_id.name + ' (%s/%s)' % (line.sequence, len(line.asset_id.depreciation_line_ids))+' al '+depreciation_date_end
        move_line_1 = {
            'name': asset_name,
            'account_id':category_id.account_depreciation_id.id,
            'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
            'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'partner_id': line.asset_id.partner_id.id,
            'analytic_account_id': account_analytic_id.id if category_id.type == 'sale' else False,
            'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'sale' else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and - 1.0 * amount or 0.0,
            'product_id': line.asset_id.product_id.id,
            
        }
        move_line_2 = {
            'name': asset_name,
            'account_id': category_id.account_depreciation_expense_id.id,
            'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
            'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'partner_id': line.asset_id.partner_id.id,
            'analytic_account_id': account_analytic_id.id if category_id.type == 'purchase' else False,
            'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'purchase' else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and amount or 0.0,
            'product_id': line.asset_id.product_id.id,
        }
        if amount > 0.0:
            move_vals = {
                'ref': line.asset_id.code,
                'date': depreciation_date or False,
                'journal_id': category_id.journal_id.id,
                'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
            }
        else:
            move_vals = {}
        return move_vals

    def _prepare_move_grouped(self):
        asset_id = self[0].asset_id
        category_id = asset_id.category_id  # we can suppose that all lines have the same category
        account_analytic_id = asset_id.account_analytic_id
        analytic_tag_ids = asset_id.analytic_tag_ids
        depreciation_date = self.env.context.get('depreciation_date') or fields.Date.context_today(self)
        depreciation_date_end = self.get_end_day(depreciation_date)
        amount = 0.0
        lines_account=[]
        product_ids=[]
        for line in self:
            if not line.asset_id.product_id.id in product_ids:
                product_ids.append(line.asset_id.product_id.id)
            # Sum amount of all depreciation lines
        for product_id in product_ids:
            amount = 0.0
            for line in self:
                if line.asset_id.product_id.id == product_id:
                    company_currency = line.asset_id.company_id.currency_id
                    current_currency = line.asset_id.currency_id
                    company = line.asset_id.company_id
                    amount += current_currency._convert(line.as_updates, company_currency, company, fields.Date.today())
            product = self.env['product.product'].search([('id', '=', product_id)])
            name = 'Depreciacion de Activos Fijos '+category_id.name +' ['+ product.name+'] al '+depreciation_date_end+ _(' (grouped)')
            move_line_1 = {
                'name': name,
                'account_id': category_id.journal_id.payment_credit_account_id.id,
                'debit': 0.0,
                'credit': amount,
                'product_id': product_id,
                'journal_id': category_id.journal_id.id,
                'analytic_account_id': account_analytic_id.id if category_id.type == 'sale' else False,
                'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'sale' else False,
            }
            move_line_2 = {
                'name': name,
                'account_id': category_id.account_asset_id.id,
                'credit': 0.0,
                'debit': amount,
                'product_id': product_id,
                'journal_id': category_id.journal_id.id,
                'analytic_account_id': account_analytic_id.id if category_id.type == 'purchase' else False,
                'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'purchase' else False,
            }
            lines_account.append((0, 0, move_line_2))
            lines_account.append((0, 0, move_line_1))
        if amount > 0.0:
            move_vals = {
                'ref': 'Depreciacion de Activos Fijos '+category_id.name+' al '+str(depreciation_date_end),
                'date': depreciation_date or False,
                'journal_id': category_id.journal_id.id,
                'line_ids': lines_account,
            }
        else:
            move_vals = {}
        return move_vals

    def _prepare_move_grouped2(self):
        asset_id = self[0].asset_id
        category_id = asset_id.category_id  # we can suppose that all lines have the same category
        account_analytic_id = asset_id.account_analytic_id
        analytic_tag_ids = asset_id.analytic_tag_ids
        depreciation_date = self.env.context.get('depreciation_date') or fields.Date.context_today(self)
        depreciation_date_end = self.get_end_day(depreciation_date)
        amount = 0.0
        lines_account=[]
        product_ids=[]
        for line in self:
            if not line.asset_id.product_id.id in product_ids:
                product_ids.append(line.asset_id.product_id.id)
            # Sum amount of all depreciation lines
        for product_id in product_ids:
            amount = 0.0
            for line in self:
                if line.asset_id.product_id.id == product_id:
                    company_currency = line.asset_id.company_id.currency_id
                    current_currency = line.asset_id.currency_id
                    company = line.asset_id.company_id
                    amount += current_currency._convert(line.as_depreciation_update, company_currency, company, fields.Date.today())
            product = self.env['product.product'].search([('id', '=', product_id)])
            name = 'Depreciacion de Activos Fijos '+category_id.name +' ['+ product.name+'] al '+depreciation_date_end+ _(' (grouped)')
            move_line_1 = {
                'name': name,
                'account_id': category_id.account_depreciation_id.id,
                'debit': 0.0,
                'credit': amount,
                'product_id': product_id,
                'journal_id': category_id.journal_id.id,
                'analytic_account_id': account_analytic_id.id if category_id.type == 'sale' else False,
                'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'sale' else False,
            }
            move_line_2 = {
                'name': name,
                'account_id': category_id.journal_id.payment_debit_account_id.id,
                'credit': 0.0,
                'debit': amount,
                'product_id': product_id,
                'journal_id': category_id.journal_id.id,
                'analytic_account_id': account_analytic_id.id if category_id.type == 'purchase' else False,
                'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'purchase' else False,
            }
            lines_account.append((0, 0, move_line_2))
            lines_account.append((0, 0, move_line_1))
        if amount > 0.0:
            move_vals = {
                'ref': 'Depreciacion de Activos Fijos '+category_id.name+' al '+str(depreciation_date_end),
                'date': depreciation_date or False,
                'journal_id': category_id.journal_id.id,
                'line_ids': lines_account,
            }
        else:
            move_vals = {}

        return move_vals

    def _prepare_move_grouped3(self):
        asset_id = self[0].asset_id
        category_id = asset_id.category_id  # we can suppose that all lines have the same category
        account_analytic_id = asset_id.account_analytic_id
        analytic_tag_ids = asset_id.analytic_tag_ids
        depreciation_date = self.env.context.get('depreciation_date') or fields.Date.context_today(self)
        depreciation_date_end = self.get_end_day(depreciation_date)
        amount = 0.0
        lines_account=[]
        product_ids=[]
        for line in self:
            if not line.asset_id.product_id.id in product_ids:
                product_ids.append(line.asset_id.product_id.id)
            # Sum amount of all depreciation lines
        for product_id in product_ids:
            amount = 0.0
            for line in self:
                if line.asset_id.product_id.id == product_id:
                    company_currency = line.asset_id.company_id.currency_id
                    current_currency = line.asset_id.currency_id
                    company = line.asset_id.company_id
                    amount += current_currency._convert(line.as_depreciation_periodo, company_currency, company, fields.Date.today())
            product = self.env['product.product'].search([('id', '=', product_id)])
            name = 'Depreciacion de Activos Fijos '+category_id.name +' ['+ product.name+'] al '+depreciation_date_end+ _(' (grouped)')
            move_line_1 = {
                'name': name,
                'account_id': category_id.account_depreciation_id.id,
                'debit': 0.0,
                'credit': amount,
                'product_id': product_id,
                'journal_id': category_id.journal_id.id,
                'analytic_account_id': account_analytic_id.id if category_id.type == 'sale' else False,
                'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'sale' else False,
            }
            move_line_2 = {
                'name': name,
                'account_id': category_id.account_depreciation_expense_id.id,
                'credit': 0.0,
                'debit': amount,
                'product_id': product_id,
                'journal_id': category_id.journal_id.id,
                'analytic_account_id': account_analytic_id.id if category_id.type == 'purchase' else False,
                'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'purchase' else False,
            }
            lines_account.append((0, 0, move_line_2))
            lines_account.append((0, 0, move_line_1))
        if amount > 0.0:
            move_vals = {
                'ref': 'Depreciacion de Activos Fijos '+category_id.name+' al '+str(depreciation_date_end),
                'date': depreciation_date or False,
                'journal_id': category_id.journal_id.id,
                'line_ids': lines_account,
            }
        else:
            move_vals = {}

        return move_vals

    # @api.multi
    def get_end_day(self,fecha):
        mes= (datetime.strptime(str(fecha), '%Y-%m-%d')).strftime('%m')
        anio= (datetime.strptime(str(fecha), '%Y-%m-%d')).strftime('%Y')
        year= (datetime.strptime(str(fecha), '%Y-%m-%d') - relativedelta(years=+1)).strftime('%Y')
        periodo = calendar.monthrange(int(anio),int(mes))
        return str(periodo[1])+'/'+mes+'/'+str(int(anio))

    # @api.multi
    def create_grouped_move(self, post_move=True):
        if not self.exists():
            return []

        created_moves = self.env['account.move']
        if self._prepare_move_grouped() != {}:
            move = self.env['account.move'].create(self._prepare_move_grouped())
            self.write({'move_id': move.id, 'move_check': True})
            created_moves |= move
        if self._prepare_move_grouped2() != {}:
            move2 = self.env['account.move'].create(self._prepare_move_grouped2())
            self.write({'move_check': True,'move_id2': move2.id,})
            created_moves |= move2
        if self._prepare_move_grouped3() != {}:
            move3 = self.env['account.move'].create(self._prepare_move_grouped3())
            self.write({'move_check': True,'move_id3': move3.id,})
            created_moves |= move3

        if post_move and created_moves:
            self.post_lines_and_close_asset()
            for move in created_moves:
                move.post()
        return [x.id for x in created_moves]
