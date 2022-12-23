# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import babel.dates
from dateutil.relativedelta import relativedelta
import itertools
import json
import logging

from setuptools import Require
from odoo import api, fields, models, _
from odoo.addons.web.controllers.main import clean_action
from datetime import datetime
from odoo.tests.common import Form
from odoo.exceptions import UserError
from werkzeug.urls import url_encode

class HrExpense(models.Model):
    _inherit = "hr.expense"

    analytic_account_id = fields.Many2one('account.analytic.account', string='Cuenta analítica', check_company=True, required=True)
    # def _proyectos_asociados(self):
    #     # if self.employee_id:
    #     # purchase_with_cost= self.env['project.task'].sudo().search([('as_viaticos_id.as_empleado.id', '=', self.employee_id)])
    #     # proyectos = self.env['project.task'].sudo().search([('id', '=',self.project_id )])
    #     viaticos = self.env['as.viaticos'].sudo().search([('as_empleado', '=', self.employee_id.id)])
    #     ids_not=[]  
    #     for purchase in viaticos:
    #         # if purchase.as_viaticos_id:
    #         ids_not.append(purchase.as_project_id.id)
    #     return [('id', 'in', tuple(ids_not))]

    def _compute_is_editable(self):
        is_account_manager = self.env.user.has_group('account.group_account_user') or self.env.user.has_group('account.group_account_manager')
        for expense in self:
            if expense.state == 'draft' or expense.sheet_id.state in ['draft', 'submit']:
                expense.is_editable = True
            elif expense.sheet_id.state == 'approve':
                expense.is_editable = is_account_manager
            else:
                expense.is_editable = True

    def _get_account_move_line_values(self):
        move_line_values_by_expense = {}
        for expense in self:
            move_line_name = expense.employee_id.name + ': ' + expense.name.split('\n')[0][:64]
            account_src = expense._get_expense_account_source()
            account_dst = expense._get_expense_account_destination()
            account_date = expense.sheet_id.accounting_date or expense.date or fields.Date.context_today(expense)

            company_currency = expense.company_id.currency_id

            move_line_values = []
            taxes = expense.tax_ids.with_context(round=True).compute_all(expense.unit_amount, expense.currency_id, expense.quantity, expense.product_id)
            total_amount = 0.0
            total_amount_currency = 0.0
            if not expense.employee_id.user_id:
                raise UserError(_("No puede generar un asiento con empleado sin ficha de usuario."))
            partner_id = expense.employee_id.user_id.partner_id.id

            # source move line
            balance = expense.currency_id._convert(taxes['total_excluded'], company_currency, expense.company_id, account_date)
            amount_currency = taxes['total_excluded']
            move_line_src = {
                'name': move_line_name,
                'quantity': expense.quantity or 1,
                'debit': balance if balance > 0 else 0,
                'credit': -balance if balance < 0 else 0,
                'amount_currency': amount_currency,
                'account_id': account_src.id,
                'product_id': expense.product_id.id,
                'product_uom_id': expense.product_uom_id.id,
                'analytic_account_id': expense.analytic_account_id.id,
                'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)],
                'expense_id': expense.id,
                'partner_id': partner_id,
                'tax_ids': [(6, 0, expense.tax_ids.ids)],
                'tax_tag_ids': [(6, 0, taxes['base_tags'])],
                'currency_id': expense.currency_id.id,
            }
            move_line_values.append(move_line_src)
            total_amount -= balance
            total_amount_currency -= move_line_src['amount_currency']

            # taxes move lines
            for tax in taxes['taxes']:
                balance = expense.currency_id._convert(tax['amount'], company_currency, expense.company_id, account_date)
                amount_currency = tax['amount']

                if tax['tax_repartition_line_id']:
                    rep_ln = self.env['account.tax.repartition.line'].browse(tax['tax_repartition_line_id'])
                    base_amount = self.env['account.move']._get_base_amount_to_display(tax['base'], rep_ln)
                    base_amount = expense.currency_id._convert(base_amount, company_currency, expense.company_id, account_date)
                else:
                    base_amount = None

                move_line_tax_values = {
                    'name': tax['name'],
                    'quantity': 1,
                    'debit': balance if balance > 0 else 0,
                    'credit': -balance if balance < 0 else 0,
                    'amount_currency': amount_currency,
                    'account_id': tax['account_id'] or move_line_src['account_id'],
                    'tax_repartition_line_id': tax['tax_repartition_line_id'],
                    'tax_tag_ids': tax['tag_ids'],
                    'tax_base_amount': base_amount,
                    'expense_id': expense.id,
                    'partner_id': partner_id,
                    'currency_id': expense.currency_id.id,
                    'analytic_account_id': expense.analytic_account_id.id if tax['analytic'] else False,
                    'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)] if tax['analytic'] else False,
                }
                total_amount -= balance
                total_amount_currency -= move_line_tax_values['amount_currency']
                move_line_values.append(move_line_tax_values)

            # destination move line
            move_line_dst = {
                'name': move_line_name,
                'debit': total_amount > 0 and total_amount,
                'credit': total_amount < 0 and -total_amount,
                'account_id': account_dst,
                'date_maturity': account_date,
                'amount_currency': total_amount_currency,
                'currency_id': expense.currency_id.id,
                'expense_id': expense.id,
                'partner_id': partner_id,
            }
            move_line_values.append(move_line_dst)

            move_line_values_by_expense[expense.id] = move_line_values
        return move_line_values_by_expense

    def _get_expense_account_destination(self):
        self.ensure_one()
        account_dest = self.env['account.account']
        if self.payment_mode == 'company_account':
            if not self.sheet_id.bank_journal_id.payment_credit_account_id:
                raise UserError(_("No se encontró ninguna cuenta de pagos pendientes para el diario %s, configure una.") % (self.sheet_id.bank_journal_id.name))
            account_dest = self.sheet_id.bank_journal_id.payment_credit_account_id.id
        else:
            if not self.employee_id.sudo().address_home_id:
                raise UserError(_("No se encontró la dirección particular del empleado %s, configure una.") % (self.employee_id.name))
            if not self.employee_id.sudo().user_id or not self.employee_id.sudo().user_id.partner_id:
                raise UserError(_("No se encontró la ficha de ususario o contacto particular del empleado %s, configure una.") % (self.employee_id.name))            
            partner = self.employee_id.sudo().user_id.partner_id
            account_dest = partner.as_account_viatic.id or partner.parent_id.as_account_viatic.id
        return account_dest
        
    @api.onchange('employee_id')
    def _proyectos_asociados(self):
        self.ensure_one()
        # Set partner_id domain
        viaticos = self.env['as.viaticos'].sudo().search([('as_empleado', '=', self.employee_id.id)])
        ids_not=[]  
        for purchase in viaticos:
            # if purchase.as_viaticos_id:
            ids_not.append(purchase.as_project_id.id)
        # return [('id', 'in', tuple(ids_not))]

        return {'domain': {'project_id': [('id', 'in', tuple(ids_not))]}}

    project_id = fields.Many2one('project.task', string="Proyecto", required=True)
    employee_id = fields.Many2one('hr.employee', compute='_compute_employee_id', string="Employee",
        store=True, required=False, readonly=False, tracking=True,
        states={'approved': [('readonly', False)], 'done': [('readonly', False)]},
        default=None, domain=lambda self: self._get_employee_id_domain(), check_company=True)
    as_presupuesto_line = fields.Many2one('as.viaticos', sstring="Linea de Presupuesto")

    @api.model_create_multi
    def create(self, vals):
        hr_expense = super(HrExpense, self).create(vals)
        if hr_expense:
            hr_expense.as_get_presupuesto()
        return hr_expense

    def as_get_presupuesto(self):
        expense = self.env['as.viaticos'].sudo().search([('as_empleado', '=', self.employee_id.id),('as_name', '=', self.product_id.id),('as_project_id', '=', self.project_id.id)],limit=1)
        if expense:
            self.as_presupuesto_line = expense
        else:
            self.as_presupuesto_line = False

    def as_update_amount(self):
        for expense in self:
            if expense.state == 'approved':
                expense.as_presupuesto_line.as_ejecutado = expense.total_amount
                expense.as_presupuesto_line.onchange_diferencia()

class HrExpensesheet(models.Model):
    _inherit = "hr.expense.sheet"
    
    as_nro = fields.Char(string='Numero Correlativo')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals_product in vals_list:
            secuence =  self.env['ir.sequence'].next_by_code('as.gastos.code')
            vals_product['as_nro'] = secuence
        templates = super(HrExpensesheet, self).create(vals_list)
        return templates

    def approve_expense_sheets(self):
        hr_expense = super(HrExpensesheet, self).approve_expense_sheets()
        for expense in self:
            for expense_line in expense.expense_line_ids:
                expense_line.as_get_presupuesto()
                expense_line.as_update_amount()

        return hr_expense
    def _lineas_ordenadas(self):
        order_lines= self.env['hr.expense'].sudo().search([('sheet_id','=',self.id)])
        return order_lines

class Task(models.Model):
    _inherit = "project.task"
    
    as_responsable = fields.Char('Nombre del Responsable')
    as_worker_signature = fields.Binary(string='Firma del Responsable')
    as_cliente = fields.Char('Nombre del Cliente')
    as_customer_signature = fields.Binary(string='Firma del Cliente')
    as_fiscal = fields.Char('Nombre del Fiscal')
    as_fiscal_signature = fields.Binary(string='Firma del Fiscal')
    as_diff = fields.Float(string='Diferencia',compute="_as_compute_diff")
    
    # def datos_viaticos(self):
    #     viaticos_line= self.env['as.viaticos'].sudo().search([('as.project.id','=',self.id)])
    #     return viaticos_line
    def _as_compute_diff(self):
        diff = 0.0
        for viatico in self.as_viaticos_id:
            diff+= viatico.as_diferencia
        self.as_diff = diff

    def as_get_notification(self):
        projects = self.env['project.task'].sudo().search([])
        for project in projects:
            project._as_compute_diff()
            if project.as_diff > 0.0:
                project.as_send_email()

    def as_send_email(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template_id = self._find_mail_template_send()
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        partners = self.env['res.users.role'].sudo().search([('name','=','Tesoreria')])
        as_partner = []
        for partner in partners:
            for line in partner.line_ids:
                as_partner.append(line.user_id.partner_id.id)
        ctx = {
            'default_model': 'project.task',
            'default_res_id': self.ids[0],
            'default_partner_ids': as_partner,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
        }
        wiz =  {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

        wiz = Form(self.env['mail.compose.message'].with_context(ctx)).save()
        wiz.action_send_mail()
        self.message_post(body = "<b style='color:green;'>Enviado correo</b>")


    def _find_mail_template_send(self, force_confirmation_template=False):
        template_id = self.env['ir.model.data'].xmlid_to_res_id('as_spectrocom_project.as_template_project_email', raise_if_not_found=False)
        return template_id


    def _get_share_url(self, redirect=False, signup_partner=False, share_token=None):
        """
        Build the url of the record  that will be sent by mail and adds additional parameters such as
        access_token to bypass the recipient's rights,
        signup_partner to allows the user to create easily an account,
        hash token to allow the user to be authenticated in the chatter of the record portal view, if applicable
        :param redirect : Send the redirect url instead of the direct portal share url
        :param signup_partner: allows the user to create an account with pre-filled fields.
        :param share_token: = partner_id - when given, a hash is generated to allow the user to be authenticated
            in the portal chatter, if any in the target page,
            if the user is redirected to the portal instead of the backend.
        :return: the url of the record with access parameters, if any.
        """
        self.ensure_one()
        params = {
            'model': self._name,
            'res_id': self.id,
        }
        if hasattr(self, 'access_token'):
            params['access_token'] = self._portal_ensure_token()
        if share_token:
            params['share_token'] = share_token
            params['hash'] = self._sign_token(share_token)
        if signup_partner and hasattr(self, 'partner_id') and self.partner_id:
            params.update(self.partner_id.signup_get_auth_param()[self.partner_id.id])

        return '%s?%s' % ('/mail/view' if redirect else self.access_url, url_encode(params))

    def _compute_expense_count(self):
        result = self.env['hr.expense'].search([('project_id','=',self.id)])
        for order in self:
            order.expense_count = len(result)

    def _compute_request_count(self):
        result = self.env['as.request.materials'].search([('as_project_id','=',self.id)])
        for order in self:
            order.request_count = len(result)

    def _compute_picking_count(self):
        result = self.env['stock.picking'].search([('project_id','=',self.id)])
        for order in self:
            order.picking_count = len(result)

    def _compute_purchase_count(self):
        result = self.env['purchase.order'].search([('as_project_id','=',self.id)])
        for order in self:
            order.as_purchase_count = len(result)

    def _compute_budget_count(self):
        result = self.env['crossovered.budget'].search([('as_project_id','=',self.id)])
        for budget in self:
            budget.as_budget_count = len(result)

    @api.depends('timesheet_ids','as_tipo_presupuesto','planned_hours')
    def _as_compute_employee_time(self):
        total_eventual = 0.0
        total_fijo = 0.0
        for project in self:
            for timesheet in project.timesheet_ids:
                if timesheet.employee_id.contract_id:
                    contract = timesheet.employee_id.contract_id
                    if contract.structure_type_id.wage_type == 'hourly':
                        total_eventual+= contract.hourly_wage * timesheet.unit_amount
                    else:
                        if contract.resource_calendar_id:
                            total_fijo+= (contract.wage/30/contract.resource_calendar_id.hours_per_day) * timesheet.unit_amount
                        else:
                            total_fijo+= (contract.wage/30/8) * timesheet.unit_amount

            project.as_employee_event = total_eventual
            project.as_employee_mensual = total_fijo


    
    as_employee_event = fields.Float(string='Costo de empleados eventuales', store=True, readonly=True, compute='_as_compute_employee_time')
    as_employee_mensual = fields.Float(string='Costo de empleados internos', store=True, readonly=True, compute='_as_compute_employee_time')


    expense_count = fields.Integer(compute='_compute_expense_count')
    request_count = fields.Integer(compute='_compute_request_count')
    picking_count = fields.Integer(compute='_compute_picking_count')
    as_purchase_count = fields.Integer(compute='_compute_purchase_count')
    as_budget_count = fields.Integer(compute='_compute_budget_count')
    picking_type_id = fields.Many2one('stock.picking.type', 'Tipo Operación para solicitudes')

    as_viaticos_id = fields.One2many('as.viaticos', 'as_project_id', string="Viaticos")
    as_fecha_salida = fields.Datetime(string="Fecha salida")
    as_fecha_llegada = fields.Datetime(string="Fecha llegada")
    as_presupuesto = fields.Float(string="Presupuesto planificado")
    as_presupuesto_viaticos = fields.Float('Presupuesto tentativo viaticos')
    as_codigo = fields.Char('Codigo')

    as_tipo_presupuesto = fields.Selection(selection=[('Fijo','Fijo'),('Frecuencia','Frecuencia')],default='Fijo', string="Tipo presupuesto")
    as_frecuencia = fields.Selection(selection=[('Mensual','Mensual'),('Trimestral','Trimestral'),('Anual','Anual')],default='Mensual', string="Frecuencia")
    as_monto = fields.Float(string='Monto')

    as_budget_id = fields.One2many('crossovered.budget', 'as_project_id', string="Budget")

    def write(self, vals):
        vals['as_codigo'] = self.project_sale_order_id.sudo().as_template_id.name
        res = super(Task, self).write(vals)

        return res
    
    def button_presupuesto(self):
        self.env['crossovered.budget'].create({
                    'name': self.name,
                    'date_from': datetime.strftime(datetime.now(), '%Y-%m-%d'),
                    'date_to': datetime.strftime(datetime.now(), '%Y-%m-%d'),
                    'as_project_id':self.id
                })

    @api.onchange('as_viaticos_id')
    def onchange_diferencia(self):
        aux = 0
        for line in self.as_viaticos_id:
            aux += line.as_presupuestado
        self.as_presupuesto_viaticos = aux
        
    def generate_request_material(self):
        for project in self:
            so_vals = {
                'as_picking_type_id': project.picking_type_id.id,
                'as_location_id': project.picking_type_id.default_location_src_id.id,
                'as_location_dest_id': project.picking_type_id.default_location_dest_id.id,
                'as_project_id': project.id,
                'as_origin': project.name,
                'state': 'draft',
            }
            request_materials = self.env['as.request.materials'].create(so_vals)

    def generate_request_purchase(self):
        for project in self:
            so_vals = {
                'as_project_id': project.id,
                'partner_id': project.partner_id.id,
            }
            request_materials = self.env['purchase.order'].create(so_vals)

    def action_hr_expense(self):
        self.ensure_one()
        action_hr_expense = self.env.ref('hr_expense.hr_expense_actions_my_unsubmitted')
        action = action_hr_expense.read()[0]
        action['context'] = {}
        result = self.env['hr.expense'].search([('project_id','=',self.id)])
        action['domain'] = [('id', 'in', result.ids)]
        return action

    def action_request_expense(self):
        self.ensure_one()
        action_hr_expense = self.env.ref('as_spectrocom_project.as_request_materials_action')
        action = action_hr_expense.read()[0]
        action['context'] = {}
        result = self.env['as.request.materials'].search([('as_project_id','=',self.id)])
        action['domain'] = [('id', 'in', result.ids)]
        return action

    def action_picking_expense(self):
        self.ensure_one()
        action_pickings = self.env.ref('stock.action_picking_tree_all')
        action = action_pickings.read()[0]
        action['context'] = {}
        result = self.env['stock.picking'].search([('project_id','=',self.id)])
        action['domain'] = [('id', 'in', result.ids)]
        return action

    def action_purchase_order(self):
        self.ensure_one()
        action_pickings = self.env.ref('purchase.purchase_form_action')
        action = action_pickings.read()[0]
        action['context'] = {}
        result = self.env['purchase.order'].search([('as_project_id','=',self.id)])
        action['domain'] = [('id', 'in', result.ids)]
        return action

    def action_budget(self):
        self.ensure_one()
        action_pickings = self.env.ref('account_budget.act_crossovered_budget_view')
        action = action_pickings.read()[0]
        action['context'] = {}
        result = self.env['crossovered.budget'].search([('as_project_id','=',self.id)])
        action['domain'] = [('id', 'in', result.ids)]
        return action
    
class AsProject(models.Model):
    _inherit = 'project.project'

    def _plan_get_stat_button(self):
        stat_buttons = super(AsProject, self)._plan_get_stat_button()
        purchase_orders = self.env['purchase.order'].search([('as_project_id.project_id','in',self.ids)])
        if purchase_orders:
            stat_buttons.append({
                'name': _('Compras'),
                'count': len(purchase_orders),
                'icon': 'fa fa-table',
                'action': _to_action_data(
                    action=self.env.ref('purchase.purchase_form_action').sudo(),
                    domain=[('id', 'in', purchase_orders.ids)],
                    context={'create': False, 'edit': False, 'delete': False}
                )
            })
        return stat_buttons

    def _plan_prepare_values(self):
        values = super(AsProject, self)._plan_prepare_values()
        as_compras = 0.0
        as_eventual = 0.0
        as_mensual = 0.0
        as_viatico = 0.0
        as_planificado = 0.0
        as_ejecutado = 0.0
        as_diferencia = 0.0
        purchase_orders = self.env['purchase.order'].search([('as_project_id.project_id','in',self.ids)])
        for compra in purchase_orders:
            as_compras+=compra.currency_id._convert(
                        compra.amount_total,
                        self.env.user.company_id.currency_id,
                        compra.company_id,
                        compra.date_order,
                    )
        as_task_ids = self.env['project.task'].search([('project_id','in',self.ids)])
        for task in as_task_ids:
            as_eventual += task.as_employee_event
            as_mensual += task.as_employee_mensual
            # as_viatico += task.as_presupuesto_viaticos
            as_planificado += task.as_presupuesto
            for planificado in task.as_viaticos_id:
                as_viatico+= planificado.as_ejecutado
        values['dashboard']['profit']['total'] = values['dashboard']['profit']['total']+as_compras+as_eventual+as_mensual+as_viatico
        as_ejecutado = values['dashboard']['profit']['total'] - values['dashboard']['profit']['invoiced']
        as_diferencia += as_planificado-as_ejecutado
        values['dashboard']['profit']['as_eventual'] = as_eventual
        values['dashboard']['profit']['as_mensual'] = as_mensual
        values['dashboard']['profit']['as_viatico'] = as_viatico
        values['dashboard']['profit']['as_planificado'] = as_planificado
        values['dashboard']['profit']['as_ejecutado'] = as_ejecutado
        values['dashboard']['profit']['as_diferencia'] = as_diferencia
        values['dashboard']['profit']['as_purchase'] = as_compras
        return values

def _to_action_data(model=None, *, action=None, views=None, res_id=None, domain=None, context=None):
    # pass in either action or (model, views)
    if action:
        assert model is None and views is None
        act = clean_action(action.read()[0], env=action.env)
        model = act['res_model']
        views = act['views']
    # FIXME: search-view-id, possibly help?
    descr = {
        'data-model': model,
        'data-views': json.dumps(views),
    }
    if context is not None: # otherwise copy action's?
        descr['data-context'] = json.dumps(context)
    if res_id:
        descr['data-res-id'] = res_id
    elif domain:
        descr['data-domain'] = json.dumps(domain)
    return descr

class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"
    as_proyecto_id=fields.Many2one('project.task', string="Proyecto")
    as_date_row = fields.Datetime(string='Fecha y Hora de Registro', default=fields.Datetime.now)
    name = fields.Char('Expense Report Summary', required=True, tracking=True)
    as_cuenta_analitica = fields.Many2one('account.analytic.account', string="Cuenta Analitica", required=True)
    
#    as_location_dest_id = fields.Many2one('stock.location', "Ubicación Destino",
#         default=lambda self: self.env['stock.picking.type'].browse(self._context.get('default_picking_type_id')).default_location_dest_id, required=True)
    
    @api.onchange("as_proyecto_id")
    def cambiar_valores_tipo_operacion(self):
        aux = 0
        for line in self:
            line.as_cuenta_analitica=line.as_proyecto_id.as_analytic_account_id.id
    
    @api.onchange('employee_id','as_proyecto_id')
    def obtner_titulo(self):
        if self.employee_id and self.as_proyecto_id:
            self.name= str(self.employee_id.name + ' - '+ self.as_proyecto_id.name)
    
    @api.constrains('expense_line_ids', 'employee_id')
    def _check_employee(self):
        for sheet in self:
            employee_ids = sheet.expense_line_ids.mapped('employee_id')
            if len(employee_ids) > 1 or (len(employee_ids) == 1 and employee_ids != sheet.employee_id):
                continue

    # @api.model_create_multi
    # def create(self, vals_list):
        
    #     for vals_product in vals_list:
    #         vals_product['as_date_row']=fields.Datetime.now()
    #     templates = super(HrExpenseSheet, self).create(vals_list)
    #     return templates

    def lineas_empleados(self, requerido):
        diario=''
        busines = self.env['hr.expense'].search([('sheet_id','=',self.id)])
        if busines:
            for y in busines:
                if y.employee_id:
                    diario+=y.employee_id.name + ', '
        json={
            'empleados':diario
        }
        diario = json[str(requerido)]
        return diario

    def crear_facturas(self):
        for i in self.expense_line_ids:
            i.action_create_invoice()