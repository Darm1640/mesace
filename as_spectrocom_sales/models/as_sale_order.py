# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from functools import partial
from dateutil.relativedelta import relativedelta
from itertools import groupby
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare
from werkzeug.urls import url_encode
import logging
_logger = logging.getLogger(__name__)

class SaleOrderCampos(models.Model):
    _inherit = 'sale.order'

    as_alias_lugar=fields.Char(string="Lugar", required=True)
    as_template_id = fields.Many2one('as.template.project', string='Código',copy=False)
    as_cont_id=fields.Integer('Versión',copy=False,default=0)
    as_proposal_id = fields.Many2one('as.proposal', string='Plantilla de Campos')
    as_proposal2_id = fields.Many2one('as.proposal', string='Plantilla de Campos')
    as_conditions_lines = fields.Many2many('as.proposal.conditions.sale', string='Condiciones de la Propuesta')
    as_instructive_lines = fields.One2many('as.instructive.sale', 'as_sale_id', string='Instructiva de Trabajo')
    as_numeracion_interna = fields.Char(related="as_template_id.as_numeracion_interna",string='Código correlativo')
    as_bussiness_id = fields.Many2one('as.business.unit', string='Linea de Negocio')
    as_type_id = fields.Many2one('as.type.service', string='Tipos de Servicio')
    as_texto = fields.Char(string='Texto')
    as_instructive_lines_2 = fields.One2many('as.instructive.sale.2', 'as_sale_id', string='Instructiva de Trabajo almaceble')
    as_bandera = fields.Boolean(string="Bandera",default=True)
    # as_proposal2_id_2 = fields.Many2one('as.proposal', string='Plantilla de Campos')
    # payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms', check_company=True,default=lambda self: self.env['account.payment.term'].search([('name', '=', '')]),required=True)
        # self.as_numeracion_interna = self.env['ir.sequence'].next_by_code('sale.order.interna') or 'New'
        # self.as_codigo_proyecto = str(self.mayusculas_carcter()+'-'+self.mayusculas_caracteres()+'-'+self.as_numeracion_interna)
    as_subscription_template_id = fields.Many2one('sale.subscription.template', string='Plantilla de suscripción')
    as_is_suscripcion = fields.Boolean(string="Es obligatorio suscripcion",default=False)
    as_referencia=fields.Char(string="Referencia",default='Ninguna')
    as_ruta = fields.Many2one('stock.location.route',string="Ruta")
    as_cotizacion_con_resumen = fields.Selection([
        ('con_resumen', 'Cotizacion con resumen'),
        ('sin_resumen', 'Cotizacion sin resumen')
    ], string='Tipo cotizacion', default='con_resumen')
    as_account_v_autorizado = fields.Many2one('account.move', string='Asiento Venta Autorizada',copy=False)
    user_id = fields.Many2one(
        'res.users', string='Vendedor', index=True, tracking=2, default=lambda self: self.env.user,
        domain=False)
    as_dias_vencimiento = fields.Integer(string='Dias de Vencimiento', compute='_compute_dias_vencimiento')
    # as_dias_vencimiento = fields.Date(string='Dias de Vencimiento', readonly=True, index=True, copy=False,
    #     states={'draft': [('readonly', False)]})

    def _compute_dias_vencimiento(self):
        for order in self:
            order.as_dias_vencimiento = 0
            hoy =  fields.Datetime.now() - relativedelta(hours=4)
            if order.date_order and order.as_saldo > 0.0:
                result = order.date_order - hoy
                order.as_dias_vencimiento = result.days

    
    def _create_invoices(self, grouped=False, final=False, date=None):
        """
        Funcion heredada para la funcion de crear facturas desde las ventas para poder agregar por detras el campo as_venta_ids los ids de las ventas en cuestion
        """
        if not self.env['account.move'].check_access_rights('create', False):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except AccessError:
                return self.env['account.move']

        # 1) Create invoices.
        invoice_vals_list = []
        ventas = []
        invoice_item_sequence = 0 # Incremental sequencing to keep the lines order on the invoice.
        for order in self:
            ventas.append(order.id)
            order = order.with_company(order.company_id)
            current_section_vals = None
            down_payments = order.env['sale.order.line']

            invoice_vals = order._prepare_invoice()
            invoiceable_lines = order._get_invoiceable_lines(final)

            if not any(not line.display_type for line in invoiceable_lines):
                continue

            invoice_line_vals = []
            down_payment_section_added = False
            for line in invoiceable_lines:
                if not down_payment_section_added and line.is_downpayment:
                    # Create a dedicated section for the down payments
                    # (put at the end of the invoiceable_lines)
                    invoice_line_vals.append(
                        (0, 0, order._prepare_down_payment_section_line(
                            sequence=invoice_item_sequence,
                        )),
                    )
                    dp_section = True
                    invoice_item_sequence += 1
                invoice_line_vals.append(
                    (0, 0, line._prepare_invoice_line(
                        sequence=invoice_item_sequence,
                    )),
                )
                invoice_item_sequence += 1

            invoice_vals['invoice_line_ids'] += invoice_line_vals
            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise self._nothing_to_invoice_error()

        # 2) Manage 'grouped' parameter: group by (partner_id, currency_id).
        if not grouped:
            new_invoice_vals_list = []
            invoice_grouping_keys = self._get_invoice_grouping_keys()
            for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: [x.get(grouping_key) for grouping_key in invoice_grouping_keys]):
                origins = set()
                payment_refs = set()
                refs = set()
                ref_invoice_vals = None
                for invoice_vals in invoices:
                    if not ref_invoice_vals:
                        ref_invoice_vals = invoice_vals
                    else:
                        ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                    origins.add(invoice_vals['invoice_origin'])
                    payment_refs.add(invoice_vals['payment_reference'])
                    refs.add(invoice_vals['ref'])
                ref_invoice_vals.update({
                    'ref': ', '.join(refs)[:2000],
                    'invoice_origin': ', '.join(origins),
                    'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
                })
                new_invoice_vals_list.append(ref_invoice_vals)
            invoice_vals_list = new_invoice_vals_list

        # 3) Create invoices.

        # As part of the invoice creation, we make sure the sequence of multiple SO do not interfere
        # in a single invoice. Example:
        # SO 1:
        # - Section A (sequence: 10)
        # - Product A (sequence: 11)
        # SO 2:
        # - Section B (sequence: 10)
        # - Product B (sequence: 11)
        #
        # If SO 1 & 2 are grouped in the same invoice, the result will be:
        # - Section A (sequence: 10)
        # - Section B (sequence: 10)
        # - Product A (sequence: 11)
        # - Product B (sequence: 11)
        #
        # Resequencing should be safe, however we resequence only if there are less invoices than
        # orders, meaning a grouping might have been done. This could also mean that only a part
        # of the selected SO are invoiceable, but resequencing in this case shouldn't be an issue.
        if len(invoice_vals_list) < len(self):
            SaleOrderLine = self.env['sale.order.line']
            for invoice in invoice_vals_list:
                sequence = 1
                for line in invoice['invoice_line_ids']:
                    line[2]['sequence'] = SaleOrderLine._get_invoice_line_sequence(new=sequence, old=line[2]['sequence'])
                    sequence += 1

        # Manage the creation of invoices in sudo because a salesperson must be able to generate an invoice from a
        # sale order without "billing" access rights. However, he should not be able to create an invoice from scratch.
        moves = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals_list)
        moves.as_venta_ids = ventas

        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        if final:
            moves.sudo().filtered(lambda m: m.amount_total < 0).action_switch_invoice_into_refund_credit_note()
        for move in moves:
            move.message_post_with_view('mail.message_origin_link',
                values={'self': move, 'origin': move.line_ids.mapped('sale_line_ids.order_id')},
                subtype_id=self.env.ref('mail.mt_note').id
            )
        return moves

    @api.depends('order_line.invoice_lines')
    def _get_invoiced(self):
        for order in self:
            invoices = order.order_line.invoice_lines.move_id.filtered(lambda r: r.move_type in ('out_invoice', 'out_refund'))
            sales = self.env['account.move'].sudo().search([('as_venta_ids','in',[order.id])])
            for sal in sales:
                invoices |= sal
            order.invoice_ids = invoices
            order.invoice_count = len(invoices)

    @api.onchange('as_ruta')
    def obtenr_rutas(self):
        a=0
        for sol in self.order_line:
            sol.route_id = self.as_ruta 
    
    
    def action_cancel(self):
        if self.picking_ids:
            for picking in self.picking_ids:
                if picking.state != 'cancel':
                    picking.action_cancel()

        if self.invoice_ids:
            for invoice in self.invoice_ids:
                if invoice.state != 'cancel':
                    if invoice.state == 'posted':
                        raise UserError(_("No se puede cancelar la venta debido a que existen facturas puclicadas relacionadas a la venta"))
                    payment_ids = self.get_payment_ids(invoice)
                    if payment_ids:
                        for payment in payment_ids:
                            if payment.state in ['posted','reconciled']:
                                payment.action_draft()
                                payment.action_cancel()
                    invoice.button_draft()
                    invoice.button_cancel()
                    
        for line in self.order_line:
            line.qty_delivered = 0
        
        return self.write({'state': 'cancel'})
    
    def crear_cotizacion(self):
        return {
            'name': _('Duplicar venta'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'as.duplicate.sale',
            'view_id': False,
            'target': 'new'
        }

    def _get_invoiceable_lines(self, final=False):
        """Return the invoiceable lines for order `self`."""
        down_payment_line_ids = []
        invoiceable_line_ids = []
        pending_section = None
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        for line in self.order_line:
            if line.display_type == 'line_section':
                # Only invoice the section if one of its lines is invoiceable
                pending_section = line
                continue
            if line.display_type != 'line_note' and float_is_zero(line.qty_to_invoice, precision_digits=precision):
                # if line.qty_to_invoice == 0:
                #     line.qty_to_invoice = 1
                line.qty_to_invoice = line.product_uom_qty
                # continue
            if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final) or line.display_type == 'line_note':
                if line.is_downpayment:
                    # Keep down payment lines separately, to put them together
                    # at the end of the invoice, in a specific dedicated section.
                    down_payment_line_ids.append(line.id)
                    continue
                if pending_section:
                    invoiceable_line_ids.append(pending_section.id)
                    pending_section = None
                if line.price_unit > 0:
                    invoiceable_line_ids.append(line.id)

        return self.env['sale.order.line'].browse(invoiceable_line_ids + down_payment_line_ids)

    def _prepare_invoice(self):
        vals = super(SaleOrderCampos, self)._prepare_invoice()
        vals['currency_id'] = 62
        return vals

    @api.onchange('order_line')
    def as_onchange_suscription(self):
        for order in self:
            obligatorio = False
            for line in order.order_line:
                if line.product_id.recurring_invoice:
                    obligatorio = True
                    break
            order.as_is_suscripcion = obligatorio

    def _split_subscription_lines(self):
        """Split the order line according to subscription templates that must be created."""
        self.ensure_one()
        res = dict()
        new_sub_lines = self.order_line.filtered(lambda l: not l.subscription_id and l.product_id.subscription_template_id and l.product_id.recurring_invoice)
        # templates = new_sub_lines.mapped('product_id').mapped('subscription_template_id')
        templates = self.as_subscription_template_id
        for template in templates:
            # lines = self.order_line.filtered(lambda l: l.product_id.subscription_template_id == template and l.product_id.recurring_invoice)
            lines = self.order_line.filtered(lambda l: l.product_id.recurring_invoice)
            res[template] = lines
        return res

    def as_action_vta_autorizada(self):
        for sale in self:
            if not sale.invoice_ids:
                sale.state = 'autotizada'
                sale.invoice_status = 'to invoice'
                sale.as_generar_asiento_Venta()
            else:
                raise UserError(_("No se puede autorizar una venta facturada"))

    def as_generar_asiento_Venta(self):
        for sale in self:
            accoun_obj = self.env['account.move']
            account_line_obj = self.env['account.move.line']
            journal = self.env['account.journal'].search([('as_is_v_autorizada','=',True)],limit=1)
            if not journal:
                raise UserError(_("Se debe crear un diario y marcarlo para venta autorizada"))
            line_sale = sale.order_line.filtered(lambda line: line.display_type == False)
            if len(line_sale[0]) <= 0:
                raise UserError(_("No se puede obtener las lineas de la venta"))
            account_id = line_sale[0].product_id.categ_id.property_account_income_categ_id.id
            account_id2 = sale.partner_id.property_account_receivable_id.id
            pur_date = fields.datetime.now()
            vals = {
                'journal_id' : journal.id,
                'currency_id' : self.env.user.company_id.currency_id.id,
                'move_type':'entry',
                'date':pur_date,
                'ref' : 'Venta Autorizada/'+sale.name+'/'+str(pur_date.strftime('%d/%m/%Y')),
            }
            pur_id = accoun_obj.create(vals)
            res = {
                'move_id': pur_id.id,
                'name': 'Venta Autorizada/'+sale.name+'/'+str(pur_date.strftime('%d/%m/%Y')),
                'partner_id': sale.partner_id.id,
                'account_id': account_id2,
                'analytic_account_id': sale.analytic_account_id.id,
                'date_maturity':pur_date,
                'debit': sale.amount_total,
                'credit': 0.0,
                'amount_currency': sale.amount_total,
                'currency_id': self.env.user.company_id.currency_id.id,
                }
            account_line_obj.with_context(check_move_validity=False).create(res)
            res = {
                'move_id': pur_id.id,
                'name': 'Venta Autorizada/'+sale.name+'/'+str(pur_date.strftime('d/m/Y')),
                'partner_id': sale.partner_id.id,
                'analytic_account_id': sale.analytic_account_id.id,
                'account_id': account_id,
                'date_maturity':pur_date,
                'debit': 0.0,
                'credit': sale.amount_total,
                'amount_currency': sale.amount_total,
                'currency_id': self.env.user.company_id.currency_id.id,
                }
            account_line_obj.with_context(check_move_validity=False).create(res)
            pur_id.action_post()
            sale.as_account_v_autorizado = pur_id
        return pur_id




    def as_get_instructive_lines(self,sale):
        """funcion para generar lienas d einstrutiva de trabajo"""
        type_Service=[]
        type_Service_aux=[]
        for line in sale.as_instructive_lines:
            type_Service.append(line.as_type_id.id)
        for line in sale.order_line:
            fecha = line.product_id.product_tmpl_id.as_type_id.id
            if fecha:
                if fecha not in type_Service:
                    type_Service.append(fecha)
                    type_Service_aux.append(fecha)
        for tipe in type_Service_aux:
            if line.display_type != 'line_section':
                vals_val = {
                    'name': sale.as_template_id.name,
                    'as_template_id': sale.as_template_id.id,
                    'as_type_id': tipe, 
                'as_type_id': tipe, 
                    'as_type_id': tipe, 
                    'as_partner_id': sale.partner_id.id,
                    'as_lugar': sale.as_alias_lugar,
                    'as_sale_id': sale.id,
                    'as_product_id':line.product_id.id
                }
                sale.as_instructive_lines.create(vals_val)
        #quitamos los que el usuario haya elimiando de las lineas de la venta
        types_line = []
        for line in sale.order_line:
            instr_id = line.product_id.product_tmpl_id.as_type_id.id
            types_line.append(instr_id)
        for line_in in sale.as_instructive_lines:
            if line_in.as_type_id.id not in types_line:
                line_in.unlink()
        #reenumeramos la secuencia
        cont = 0
        for tipe_seq in sale.as_instructive_lines:
            cont+=1
            tipe_seq.sequence=cont

    def as_get_instructive_lines_2(self,sale):
        """funcion para generar lienas d einstrutiva de trabajo"""
        type_Service=[]
        type_Service_aux=[]
        types_line = []
        for line in sale.order_line:
            instr_id = line.product_id.name
            types_line.append(instr_id)
        for line_in in sale.as_instructive_lines_2:
            # if line_in.as_nombre_item not in types_line:
            line_in.unlink()
        for line in sale.as_instructive_lines_2 :
            type_Service.append(line.as_type_id.id)
        for line in sale.order_line:
            if line.display_type != 'line_section':
           
                vals_val = {
                    'sequence_2': line.product_id.default_code,
                    'as_nombre_item': line.product_id.name,
                    'as_numero_parte':line.product_id.product_part_num,
                    'as_modelo':line.product_id.product_model_id.name,
                    'as_marca':line.product_id.product_brand_id.name,
                    'as_unidad':line.product_uom.name,
                    'as_cant':line.product_uom_qty,
                    # 'as_template_id': sale.as_template_id.id,
                    # 'as_type_id': tipe, 
                    # 'as_partner_id': sale.partner_id.id,
                    'as_lugar': 'Fixeado',
                    'as_sale_id': sale.id,
                    # 'as_product_id':line.product_id.id
                }
                self.env['as.instructive.sale.2'].create(vals_val)
        #quitamos los que el usuario haya elimiando de las lineas de la venta
        
        
        # #reenumeramos la secuencia
        # cont = 0
        # for tipe_seq in sale.as_instructive_lines_2 :
        #     cont+=1
        #     tipe_seq.sequence=cont

    def write(self, vals):
        result = super(SaleOrderCampos, self).write(vals)
        # if self.order_line:
        #     if self.order_line[0].product_id.type == 'product' or self.order_line[0].product_id.type == 'consu':
        #         self.as_get_instructive_lines(self)
        #     else:
        #         self.as_get_instructive_lines(self)
        employee = self.env['hr.employee'].search([('user_id','=',self.user_id.id)],limit=1)
        return result

    @api.onchange('as_alias_lugar')
    @api.depends('as_alias_lugar')
    def as_onchange_alias_lugar(self):
        for sale in self:
            if sale.as_alias_lugar:
                sale.as_alias_lugar = str(sale.as_alias_lugar).upper()
                if len(sale.as_alias_lugar) > 10:
                    raise UserError('No puede superar los 10 Caracteres')
            

    def action_confirm(self):
        result = super(SaleOrderCampos,self).action_confirm()
        if not self.as_assets:
            if not self.as_template_id and self:
                raise UserError('No puede confirmarse la venta, la misma no posee codigo de proyecto')
            if not self.as_instructive_lines:
                raise UserError('No puede confirmarse la venta, la misma no posee fecha planificada, descripcion del proyecto y presupuesto')
            if self.order_line[0].product_template_id.service_tracking == 'task_in_project':
                for instructiva_trabajo in self.as_instructive_lines:
                    if instructiva_trabajo.as_note == False:
                        raise UserError('No puede confirmarse la venta, verifique que la instructiva de trabajo contenga una descripcion')
        return result

    def info_sucursal(self, requerido):
        info = ''
        diccionario_dosificacion= {}
        diccionario_dosificacion = {
            'nombre_empresa' : self.company_id.name or '',
            'nit' : self.company_id.vat or '',
            'direccion1' : self.company_id.street or '',
            'telefono' : self.company_id.phone or '',
            'ciudad' : self.company_id.city or '',
            'sucursal' : self.company_id.city or '',
            'pais' : self.company_id.country_id.name or '',
            'actividad' :  self.company_id.name or '',
            'fechal' : self.company_id.phone or '',

        }
        info = diccionario_dosificacion[str(requerido)]
        return info

    @api.onchange('as_proposal_id')
    def get_as_proposal_id(self):
        """generar condiciones propuestas"""
        for sale in self:   
            aux = sale.as_proposal_id.as_conditions_lines
            line_proposal = []
            vals = {}
            sale.as_conditions_lines = []
            # sale.write({'as_conditions_lines': [(0, 0, {})]}) 
            # self.env.cr.execute("delete from as_proposal_conditions_sale WHERE as_sale_id = "+ str(sale.id.origin))
            if sale.as_proposal_id.as_conditions_lines:
                for proposal in sale.as_proposal_id.as_conditions_lines:
                    vals_val = {
                        'name': proposal.name,
                        'as_valor': proposal.as_valor,
                        # 'as_sale_id': sale.id,
                        'as_proposal_id': sale.as_proposal_id.id,
                    }
                    aux = self.env['as.proposal.conditions.sale'].create(vals_val)
                    line_proposal.append(aux.id)
            sale.as_conditions_lines = line_proposal

    def boton_add(self):
        """boton agregar"""
        for sale in self:   
            aux = sale.as_proposal_id.as_conditions_lines
            aux2 = sale.as_proposal_id.as_conditions_lines
            line_proposal = []
            vals = {}
            sale.as_conditions_lines = []

            for proposal in sale.as_conditions_lines:
                line_proposal.append(proposal.id)
            vals_val = {
                'name': sale.as_texto,
                'as_valor': '',
                # 'as_sale_id': sale.id,
                'as_proposal_id': False,
            }
                
            aux = self.env['as.proposal.conditions.sale'].create(vals_val)
            line_proposal.append(aux.id)

        sale.as_conditions_lines = line_proposal
        sale.as_texto = ''

    @api.onchange('as_proposal2_id')
    def get_as_proposal2_id(self):
        for sale in self:
            for proposal in sale.as_instructive_lines:
                proposal.as_note = sale.as_proposal2_id.as_note
                proposal.as_template_id = sale.as_template_id

    def mayusculas_carcter(self):
        result = ''
        for p in self.user_id.name.split():
            result+= p[0].upper() + ''
        return result
    
    def mayusculas_caracteres(self):
        result = ''
        for p in self.as_alias_lugar.split():
            result+= p[0].upper() + ''
        return result

    def as_split_literal(self,value):
        result = ''
        if value == False:
            value = 'N/H'
        for p in value:
            if len(p) > 0:
                result+= p.upper() + ''
        return result

    # def as_split_literal(self,value):
    #     result = ''
    #     for p in value.split(' '):
    #         if len(p) > 0:
    #             result+= p[0].upper() + ''
    #     return result

    def as_generate_project(self):
        for sale in self:
            if not sale.partner_id:
                raise UserError("La cotización debe tener un cliente asociado") 
            if not sale.user_id:
                raise UserError("La cotización debe tener un Vendedor asociado") 
            employee = self.env['hr.employee'].search([('user_id','=',sale.user_id.id)])
            if not employee:
                raise UserError("El vendedor no posee plantilla de empleado") 
            if not employee.job_id:
                raise UserError("El vendedor no posee puesto de trabajo en plantilla de empleado") 
            if sale.as_template_id:
                raise UserError("La cotización ya posee un correlativo de proyecto asociado") 
            name_project = self.env['as.template.project'].create({
                'as_alias': self.as_split_literal(employee.as_codigo_empleado), 
                # 'as_alias': self.as_split_literal(employee.job_id.name), 
                'as_alias_lugar': str(sale.partner_id.as_code)+str(sale.as_alias_lugar), 
                'as_sales_ids': [sale.id], 
            })
            sale.as_template_id = name_project            
             
    @api.model
    def create(self, vals):
        res = super(SaleOrderCampos, self).create(vals)
        # res['name'] = res['name'] + ' - ' +res['partner_id']['name']
        # if res.order_line[0].product_id.type == 'product' or res.order_line[0].product_id.type == 'consu':
        #     res.as_get_instructive_lines(res)
        #     res.as_bandera = False
        # if len(res.order_line) > 1:
        #     if res.order_line[1].product_id.type == 'product' or res.order_line[1].product_id.type == 'consu':
        #         res.as_get_instructive_lines(res)
        #         res.as_bandera = False
        # else:
        #     res.as_get_instructive_lines(res)
        for sale in res:
            if not sale.partner_id:
                raise UserError("La cotización debe tener un cliente asociado") 
            if not sale.user_id:
                raise UserError("La cotización debe tener un Vendedor asociado") 
            employee = self.env['hr.employee'].search([('user_id','=',sale.user_id.id)])
            if not employee:
                raise UserError("El vendedor no posee plantilla de empleado") 
            if not employee.job_id:
                raise UserError("El vendedor no posee puesto de trabajo en plantilla de empleado") 
            if sale.as_template_id:
                raise UserError("La cotización ya posee un correlativo de proyecto asociado") 
            name_project = self.env['as.template.project'].create({
                'as_alias': self.as_split_literal(employee.as_codigo_empleado), 
                # 'as_alias': self.as_split_literal(employee.job_id.name), 
                'as_alias_lugar': str(sale.partner_id.as_code)+str(sale.as_alias_lugar), 
                'as_sales_ids': [sale.id], 
            })
            # sale.as_template_id = name_project
            res['as_template_id'] = name_project

        return res

    @api.onchange('as_alias_lugar','partner_id')
    def change_alias_lugar(self):
        """Crear alias de cliente"""
        if self.state == 'draft':
            employee = self.env['hr.employee'].search([('user_id','=',self.user_id.id)])
            if employee.job_id.name:
                equis = self.as_split_literal(employee.as_codigo_empleado) + '-' + str(self.partner_id.as_code)+str(self.as_alias_lugar) + '-' + str(self.as_numeracion_interna)+ '-' + '0'
                # equis = self.as_split_literal(employee.job_id.name) + '-' + str(self.partner_id.as_code)+str(self.as_alias_lugar) + '-' + str(self.as_numeracion_interna)+ '-' + '0'
                id = str(self.as_template_id.id)
                if id != 'False':
                    actual = ("""update as_template_project set name='"""+str(equis)+"""' where id = '"""+id+"""'""")
                    _logger.debug(actual)
                    self.env.cr.execute(actual)
        else:
            raise UserError("No se puede modificar el lugar, debido a que ya no se encuentra en estado cotización")

    def get_cargo(self):
        """obtener cargo de empleado asociado a comercial"""
        for sale in self:
            employee = self.env['hr.employee'].search([('user_id','=',sale.user_id.id)])
            return employee.job_id.name

    as_purchase_count_sale = fields.Integer(compute='_compute_purchase_count_sale')
    
    def generate_request_purchase(self):
        for ventas in self:
            so_vals = {
                'as_sale_id': ventas.id,
                'partner_id': ventas.partner_id.id,
                'order_line': []
            #     'order_line': [(0, 0, {
            #     'name': self.order_line.name,
            #     'product_id': self.order_line.product_id.id,
            #     'product_qty': self.order_line.product_uom_qty,
            #     'product_uom': self.order_line.product_uom.id,
            #     'taxes_id': self.order_line.product_id.taxes_id.ids,
            #     'price_unit': self.order_line.price_unit,
            #     'date_planned': fields.Date.today(),
            # })]
            }
            # so_vals['order_line'] = []
            for line in self.order_line:
                if line.product_id.type == 'product':
                    order_line_vals = (0, 0, {
                        'date_planned': fields.Date.today(),
                        'name': line.product_id.display_name,
                        'price_unit': line.price_unit,
                        'product_id': line.product_id.id,
                        'product_qty': line.product_uom_qty,
                        'product_uom': line.product_uom.id,
                    })
                    so_vals['order_line'].append(order_line_vals)
                    # so_vals.append(order_line_vals)
            request_materials = self.env['purchase.order'].create(so_vals)

    def _compute_purchase_count_sale(self):
        result = self.env['purchase.order'].search([('as_sale_id','=',self.id)])
        for order in self:
            order.as_purchase_count_sale = len(result)

    def action_purchase_order_sale(self):
        self.ensure_one()
        action_pickings = self.env.ref('purchase.purchase_form_action')
        action = action_pickings.read()[0]
        action['context'] = {}
        result = self.env['purchase.order'].search([('as_sale_id','=',self.id)])
        action['domain'] = [('id', 'in', result.ids)]
        return action

    def as_generate_sale_draft(self):
        """genera cotizacion en borrador"""
        if self.as_template_id:
            sale_order = self.env['sale.order']
            for sale in self.as_template_id.as_sales_ids.sorted(lambda x: x.id):
                sale_order = sale
            sale_copy = sale_order.copy()
            sale_copy.as_template_id = self.as_template_id
            action = sale_copy.env['ir.actions.act_window']._for_xml_id("sale.action_quotations")
            action['context'] = {'default_res_model': 'sale.order', 'default_as_template_id': sale_copy.as_template_id.id}
            sales_template = []
            for sale in sale_copy.as_template_id.as_sales_ids:
                sales_template.append(sale.id)
            sales_template.append(sale_copy.id)
            sale_copy.as_template_id.as_sales_ids = sales_template
            sale_copy.as_template_id.get_name_project()
            sale_copy.as_cont_id = len(sale_copy.as_template_id.as_sales_ids)-1
            action['domain'] = [('as_template_id', '=', sale_copy.as_template_id.id)]

            for sale_val in self.as_template_id.as_sales_ids.sorted(lambda x: x.id):
                if sale_val.id != sale_copy.id:
                    sale_val.state = 'cancel'
        else:
            raise UserError("La cotización no posee un correlativo de proyecto asociado")
        return action

    def get_line_business_name(self):
        """generar lineas de negocios"""
        lines_unidad = []
        cont = 0
        total_us = 0
        total_bob = 0
        conta_posi = 0
        cont_t = 0
        total_obedece = 0
        line_sale = self.order_line.filtered(lambda sol: sol.price_unit > 0.0 or sol.as_show_price or sol.display_type in ('line_section','line_note'))
        for line in line_sale:
            cont_t +=1
            if line.display_type not in ('line_section','line_note'):
                cont += 1 
                if conta_posi-1 < len(line_sale):
                    if str(line_sale[conta_posi-1].display_type) in ('line_section'):
                        if lines_unidad != []:
                            vals = {
                                'type':'total',
                                'num':cont,
                                'default_code': line.product_id.default_code,
                                'name': 'Subtotal',
                                'total_us': total_us,
                                'total_bob': total_bob,
                                'total_obedece': total_obedece,
                            }
                            lines_unidad.append(vals)
                            total_us = 0
                            total_bob = 0
                        vals = {
                                'type':'section',
                                'name': line_sale[conta_posi-1].name,
                                
                            
                        }
                        lines_unidad.append(vals)
                if line.currency_id.id == 2:
                    total_us += line.price_unit * line.product_uom_qty
                    total_bob += line.price_unit * line.product_uom_qty * 6.96
                else:
                    total_us += line.as_total_us
                    total_bob += line.as_total_bob
                vals = {
                    'type':'line',
                    'num':cont,
                    'default_code': line.product_id.default_code,
                    'name': line.name,
                    'udm': line.product_uom.name,
                    'product_uom_qty': line.product_uom_qty,
                    'price_unit': line.price_unit,
                    'total_us': line.as_total_us,
                    'total_bob': line.as_total_bob,
                    'total_obedece': line.price_total,
                }
                lines_unidad.append(vals)
                if conta_posi+1 < len(line_sale):
                    if str(line_sale[conta_posi+1].display_type) in ('line_note'):
                        vals = {
                                'type':'note',
                                # 'name': str(line_sale[conta_posi+1].name).replace("\n","<br/>"),
                                'name':line_sale[conta_posi+1].name
                        }
                        lines_unidad.append(vals)
            if cont_t == len(line_sale):
                vals = {
                    'type':'total',
                    'num':cont,
                    'default_code': line.product_id.default_code,
                    'name': 'Subtotal',
                    'total_us': total_us,
                    'total_bob': total_bob,
                    'total_obedece': total_obedece,
                }
                lines_unidad.append(vals)
            conta_posi +=1

        return lines_unidad

    def get_line_business_total(self,unidad):
        """obtener total de lineas de negocios"""
        lines_unidad = []
        cont = 0
        total_us = 0
        total_bob = 0
        for line in self.order_line:
            if line.product_id.product_tmpl_id.as_type_id.id == unidad:
                cont += 1 
                total_us += line.as_total_us
                total_bob += line.as_total_bob

        return (total_us,total_bob)


    def get_business_type(self):
        business_type = self.env['as.type.service'].search([])
        return business_type    
    
    def get_total_line_business(self):
        totales = []
        total_us = 0.0
        total_bob = 0.0
        business_type = self.env['as.type.service'].search([])
        for type_service in business_type:
            if self.get_line_business_total(type_service.id)[0] > 0 and self.get_line_business_total(type_service.id)[1] > 0:
                total_us+=self.get_line_business_total(type_service.id)[0]
                total_bob+=self.get_line_business_total(type_service.id)[1]
                vals = {
                    'type' : 'line',
                    'name' : type_service.name,
                    'total_us' : self.get_line_business_total(type_service.id)[0],
                    'total_bob' : self.get_line_business_total(type_service.id)[1],
                }
                totales.append(vals)
        if totales != []:
            vals = {
                'type' : 'total',
                'name' : type_service.name,
                'total_us' : total_us,
                'total_bob' : total_bob,
            }
            totales.append(vals)
        return totales

    def get_total_line_business_aux(self):
        totales = []
        x = 0
        y = 0
        cont = 0
        bs = []
        sus = []
        nombres = [{
                    'name':'inicio',
                    'total_us':0.0,
                    'total_us_aux':0.0,
                    'total_bob':0.0,
                    'total_bob_aux':0.0,
                }]
        cont_aux = 0
        
        currency_dolar = self.env['res.currency'].search([('id','=',2)])
        currency_bob = self.env['res.currency'].search([('id','=',62)])
        for line in self.order_line:
            usd = 0
            bob = 0
            if line.display_type == 'line_section':
                
                
                nombres.append({
                    'name':line.name.upper(),
                    'total_us':0.0,
                    'total_bob':0.0,
                    'total_us_aux':0.0,
                    'total_bob_aux':0.0,
                })
                cont_aux += 1
            else:
                if line.currency_id.id == 2:
                    subtotal = line.price_unit
                    bob += currency_dolar._convert(subtotal,
                        currency_bob,
                        self.company_id,
                        self.date_order,
                         round=True
                    )*line.product_uom_qty
                    nombres[cont_aux]['total_us_aux']+= subtotal * line.product_uom_qty
                    nombres[cont_aux]['total_us']+= subtotal* line.product_uom_qty
                    nombres[cont_aux]['total_bob_aux']+= bob
                    nombres[cont_aux]['total_bob']+= bob
                else:
                    subtotal = line.price_unit
                    usd += currency_bob._convert(subtotal,
                        currency_dolar,
                        self.company_id,
                        self.date_order,
                        round=True
                    )*line.product_uom_qty
                    nombres[cont_aux]['total_us_aux']+= usd
                    nombres[cont_aux]['total_us']+= usd
                    nombres[cont_aux]['total_bob_aux']+= subtotal * line.product_uom_qty
                    nombres[cont_aux]['total_bob']+= subtotal * line.product_uom_qty
        return nombres 

    def as_get_totales(self):
        total_us = 0.0
        total_bob = 0.0
        for line in self.get_total_line_business_aux():
            # total_us += line['total_us'] 
            # total_bob += line['total_bob'] 
            total_us += line['total_us_aux'] 
            total_bob += line['total_bob_aux'] 
        return total_us,total_bob


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    as_total_bob = fields.Float('Total BOB')
    as_total_us = fields.Float('Total $us')
    as_utilidad = fields.Float('Utilidad %')
    as_mayor_precio_compra = fields.Float('Mayor precion de compra')
    as_stock_fisico_actual = fields.Float(string="Stock Actual", compute='_detalle_producto')
    as_bussiness_id = fields.Many2one('as.business.unit', string='Linea de Negocio')
    as_type_id = fields.Many2one('as.type.service', string='Tipos de Servicio')
    as_show_price = fields.Boolean(string='Mostrar en cotización')

    @api.onchange('product_id')
    def obtener_rutas_formulario(self):
        for sol in self:
            if sol.order_id.as_ruta:
                sol.route_id = sol.order_id.as_ruta

    
    @api.model
    def create(self, vals):
        line = super(SaleOrderLine, self).create(vals)
        line.get_total_price()
        # line.product_id_change()
        return line
            
    @api.onchange('product_id')
    def product_id_change(self):
        """extraer caracteristicas del producto cuando el mismo se seleccione"""
        result = super(SaleOrderLine, self).product_id_change()
        for line in self:
            if line.product_id:
                line.as_bussiness_id = line.product_id.product_tmpl_id.as_bussiness_id
                line.as_type_id = line.product_id.product_tmpl_id.as_type_id
                line.name = str(line.product_id.name)
            if line.product_id.product_brand_id:
                line.name += ' Marca: '+str(line.product_id.product_brand_id.name)
            if line.product_id.product_model_id:
                line.name += ' Modelo: '+str(line.product_id.product_model_id.name)
            if line.product_id.product_part_num:
                line.name += 'Nro. Parte: '+str(line.product_id.product_part_num)
        return result


    @api.onchange('product_id','product_uom_qty','price_unit')
    @api.depends('product_id','product_uom_qty','price_unit')
    def get_total_price(self):
        """funciion de computo de conversiones de moneda"""
        if self.order_id.currency_id.id == 2:
            currency_two = self.env['res.currency'].search([('id','=',62)])
            self.as_total_us = self.price_unit * self.product_uom_qty

            costo = (self.product_id.standard_price*self.order_id.currency_id.rate)
            precio = (self.price_unit)
            total = precio * self.product_uom_qty
            if self.price_unit == 0:
                self.as_utilidad = 0

            if total == 0:
                self.as_utilidad = 0
            else:
                # self.as_utilidad = (self.product_id.standard_price*self.order_id.currency_id.rate)
                self.as_utilidad = ((total-(costo*self.product_uom_qty))/total)*100
            # self.as_total_bob = self.order_id.currency_id._convert(
            #             abs((self.price_unit * 6.96)* self.product_uom_qty),
            #             currency_two,
            #             self.order_id.company_id,
            #             self.order_id.date_order,
            #         )
            self.as_total_bob = (self.price_unit* 6.96) * self.product_uom_qty
        else:
            x = 1
            currency_two = self.env['res.currency'].search([('id','=',2)])
            self.as_total_bob = self.price_unit * self.product_uom_qty
            if self.price_unit == 0:
                self.as_utilidad = 0
            else:
                self.as_utilidad = ((self.price_unit-self.product_id.standard_price)/self.price_unit)*100
            self.as_total_us = self.order_id.currency_id._convert(
                        abs(self.as_total_bob),
                        currency_two,
                        self.order_id.company_id,
                        self.order_id.date_order,
                    )
        product_template = self.env['product.template'].search([('id','=',self.product_id.product_tmpl_id.id)])
        aux = []
        for x in product_template.seller_ids:
            aux.append(x.price)
        if aux:
            self.as_mayor_precio_compra = max(aux)

    @api.onchange('product_id','route_id')
    def as_get_stock(self):
        """Extraer las rutas disponibles para el producto"""
        rutas_habilitadas = self.user_has_groups('sale_stock.group_route_so_lines')
        for record in self:
            if record:
                # if record.order_id.partner_id:
                for producto in record:
                    # if record.display_name == producto._origin.display_name:
                        # _logger.info('\n\n %r \n\n', [moduleObj,record.route_id])
                        #se comento lo refente a stock virtual
                        cantidad = self.product_id.qty_available
                        #previsto = producto.product_id.virtual_available
                        if (producto._origin.product_id.id and record.route_id.rule_ids):
                            ruta = record.route_id.rule_ids[0].location_src_id.id
                            for route in record.route_id.rule_ids:
                                if route.sequence == 1:
                                    ruta=route.location_src_id.id
                            cantidad= self.product_id.qty_available
                            #previsto =  producto.product_id.with_context(location=[ruta]).virtual_available
                            record.as_stock_fisico_actual = cantidad
                        else:
                            # Cuando tengamos el modulo de inventarios pero no estemos trabajando con rutas, mostraremos la cantidad total del producto en todas las ubicaciones
                            if rutas_habilitadas != False:
                                cant_almacen_producto = self.env['stock.quant'].search([('product_id','=',producto._origin.product_id.id)])
                                stock_total = 0
                                #stock_virtual_total = 0
                                if cant_almacen_producto:
                                    for cant_total_almacenada in cant_almacen_producto:
                                        stock_total = cant_total_almacenada.quantity + stock_total
                                        #stock_virtual_total = cant_total_almacenada.reserved_quantity + stock_virtual_total
                                cantidad = stock_total if cant_almacen_producto else 0.0
                                #previsto = stock_virtual_total if cant_almacen_producto else 0.0
                                record.as_stock_fisico_actual = cantidad
                            else:
                                record.as_stock_fisico_actual = self.product_id.qty_available
                        record.as_stock_fisico_actual = cantidad

    @api.onchange('product_id','route_id')
    def _detalle_producto(self):
        rutas_habilitadas = self.user_has_groups('sale_stock.group_route_so_lines')
        for record in self:
            """Extraer las rutas disponibles para el producto"""
            if record:
                # if record.order_id.partner_id:
                for producto in record:
                    if record.display_name == producto._origin.display_name:
                        # _logger.info('\n\n %r \n\n', [moduleObj,record.route_id])
                        #se comento lo refente a stock virtual
                        cantidad = producto._origin.product_id.qty_available
                        #previsto = producto.product_id.virtual_available
                        if (producto._origin.product_id.id and record.route_id.rule_ids):
                            ruta = record.route_id.rule_ids[0].location_src_id.id
                            for route in record.route_id.rule_ids:
                                if route.sequence == 1:
                                    ruta=route.location_src_id.id
                            cantidad= producto._origin.product_id.with_context(location=[ruta]).qty_available
                            #previsto =  producto.product_id.with_context(location=[ruta]).virtual_available
                            record.as_stock_fisico_actual = cantidad
                        else:
                            # Cuando tengamos el modulo de inventarios pero no estemos trabajando con rutas, mostraremos la cantidad total del producto en todas las ubicaciones
                            if rutas_habilitadas != False:
                                cant_almacen_producto = self.env['stock.quant'].search([('product_id','=',producto._origin.product_id.id)])
                                stock_total = 0
                                #stock_virtual_total = 0
                                if cant_almacen_producto:
                                    for cant_total_almacenada in cant_almacen_producto:
                                        stock_total = cant_total_almacenada.quantity + stock_total
                                        #stock_virtual_total = cant_total_almacenada.reserved_quantity + stock_virtual_total
                                cantidad = stock_total if cant_almacen_producto else 0.0
                                #previsto = stock_virtual_total if cant_almacen_producto else 0.0
                                record.as_stock_fisico_actual = cantidad
                            else:
                                record.as_stock_fisico_actual = producto._origin.product_id.qty_available
                        record.as_stock_fisico_actual = cantidad
                            #record.as_stock_virtual_actual = previsto
                            
    def get_stock_virtual(self):
        
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'as.stock.product',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': {'default_sale_line_id': self.id },
            }
    
    def as_add_nota(self):
        """Agregar nota en lineas de venta si producto tiene nota """

        lineas_venta = self.env['sale.order.line'].search([('order_id','=',self.order_id.id)])
        contador_venta = 0
        for i in lineas_venta:
            i.sequence = contador_venta
            contador_venta += 2

        for sale_line in self:
            if sale_line.product_template_id.description:
                cont = sale_line.sequence + 1
                diccionario = {
                    'order_id':sale_line.order_id.id,
                    'name':sale_line.product_template_id.description,
                    'display_type':'line_note',
                    'sequence':cont
                    }
                sale_line.env['sale.order.line'].create(diccionario)

    def _timesheet_service_generation(self):
        """ Para las líneas de servicio, cree la tarea o el proyecto. Si ya existe, simplemente enlaza
            el existente a la línea.
            Nota: Si el SO fue confirmado, cancelado, configurado como borrador y luego confirmado, evite crear un
            nuevo proyecto / tarea. Esto explica las búsquedas en 'sale_line_id' en proyecto / tarea. Esto también
            implícito si se ha modificado la línea de la tarea generada, podemos volver a generarla..
        """
        so_line_task_global_project = self.filtered(lambda sol: sol.is_service and sol.product_id.service_tracking == 'task_global_project')
        so_line_new_project = self.filtered(lambda sol: sol.product_id.service_tracking in ['project_only', 'task_in_project','no'])

        # search so lines from SO of current so lines having their project generated, in order to check if the current one can
        # create its own project, or reuse the one of its order.
        map_so_project = {}
        if so_line_new_project:
            order_ids = self.mapped('order_id').ids
            so_lines_with_project = self.search([('order_id', 'in', order_ids), ('project_id', '!=', False), ('product_id.service_tracking', 'in', ['project_only', 'task_in_project']), ('product_id.project_template_id', '=', False)])
            map_so_project = {sol.order_id.id: sol.project_id for sol in so_lines_with_project}
            so_lines_with_project_templates = self.search([('order_id', 'in', order_ids), ('project_id', '!=', False), ('product_id.service_tracking', 'in', ['project_only', 'task_in_project']), ('product_id.project_template_id', '!=', False)])
            map_so_project_templates = {(sol.order_id.id, sol.product_id.project_template_id.id): sol.project_id for sol in so_lines_with_project_templates}

        # search the global project of current SO lines, in which create their task
        map_sol_project = {}
        if so_line_task_global_project:
            map_sol_project = {sol.id: sol.product_id.with_company(sol.company_id).project_id for sol in so_line_task_global_project}

        def _can_create_project(sol):
            if not sol.project_id:
                if sol.product_id.project_template_id:
                    return (sol.order_id.id, sol.product_id.project_template_id.id) not in map_so_project_templates
                elif sol.order_id.id not in map_so_project:
                    return True
            return False

        def _determine_project(so_line):
            """Determine el proyecto para esta línea de orden de venta.
            Las reglas son diferentes según el service_tracking:

            - 'project_only': el project_id solo puede provenir de la propia línea de la orden de venta
            - 'task_in_project': el project_id proviene de la línea de la orden de venta solo si no se configuró ningún project_id
              en la orden de venta principal"""

            if so_line.product_id.service_tracking == 'project_only':
                return so_line.project_id
            elif so_line.product_id.service_tracking == 'task_in_project':
                return so_line.order_id.project_id or so_line.project_id
            elif so_line.product_id.service_tracking == 'no':
                return so_line.project_id

            return False

        # task_global_project: create task in global project
        for so_line in so_line_task_global_project:
            if not so_line.task_id:
                if map_sol_project.get(so_line.id):
                    so_line._timesheet_create_task(project=map_sol_project[so_line.id])

        # project_only, task_in_project: create a new project, based or not on a template (1 per SO). May be create a task too.
        # if 'task_in_project' and project_id configured on SO, use that one instead
        for so_line in so_line_new_project:
            project = _determine_project(so_line)
            if not project and _can_create_project(so_line):
                project = so_line._timesheet_create_project()
                if so_line.product_id.project_template_id:
                    map_so_project_templates[(so_line.order_id.id, so_line.product_id.project_template_id.id)] = project
                else:
                    map_so_project[so_line.order_id.id] = project
            elif not project:
                # Attach subsequent SO lines to the created project
                so_line.project_id = (
                    map_so_project_templates.get((so_line.order_id.id, so_line.product_id.project_template_id.id))
                    or map_so_project.get(so_line.order_id.id)
                )
            if so_line.product_id.service_tracking == 'task_in_project':
                if not project:
                    if so_line.product_id.project_template_id:
                        project = map_so_project_templates[(so_line.order_id.id, so_line.product_id.project_template_id.id)]
                    else:
                        project = map_so_project[so_line.order_id.id]
                if not so_line.task_id:
                    so_line._timesheet_create_task(project=project)