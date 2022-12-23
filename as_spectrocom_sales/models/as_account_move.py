# -*- coding: utf-8 -*-
from datetime import datetime
import time
import calendar
from dateutil.relativedelta import relativedelta
from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round, ormcache
import logging
import json

import datetime
from datetime import datetime, timedelta, date
from time import mktime
_logger = logging.getLogger(__name__)

class AccountMoveLine(models.Model):
    _inherit="account.move.line"

    as_descripcion = fields.Char(string='Descripción Prefactura')
    as_move_type = fields.Selection(related="move_id.move_type")
    as_price_total_aux = fields.Monetary(string='Total Auxiliar', store=True, readonly=False,currency_field='currency_id')
    as_price_unit_aux = fields.Float(string="Precio", digits=(8,10))
    
    @api.onchange("as_price_total_aux", "quantity")
    def precio_unitario_con_precio_total_aux(self):
        for discount in self:
            if discount.as_price_total_aux != 0:
                discount.as_price_unit_aux = float("{0:.3f}".format(discount.as_price_total_aux)) / float("{0:.3f}".format(discount.quantity))
                discount.price_unit = discount.as_price_unit_aux
    
    def _get_price_total_and_subtotal(self, price_unit=None, quantity=None, discount=None, currency=None, product=None, partner=None, taxes=None, move_type=None):
        self.ensure_one()
        if self.move_id.move_type=='in_invoice':
            price_unit=self.as_price_unit_aux
        res=super(AccountMoveLine, self)._get_price_total_and_subtotal(price_unit, quantity, discount, currency, product, partner, taxes, move_type)
        return res 
    

class AccountMove(models.Model):
    _inherit="account.move"

    as_venta_ids = fields.Many2many('sale.order', store=True, string='Relacion ventas')

    def action_post(self):
        res = super(AccountMove, self).action_post()
        for lineas in self.as_venta_ids :
            lineas.invoice_status = 'invoiced'
        # if self.move_type == 'out_invoice':
        #     for lineas in self.invoice_line_ids:
        #         lineas.as_descripcion = str(self.as_invoice_number) + ' ' + self.partner_id.name + ' ' + lineas.as_descripcion
        return res

    @api.onchange('invoice_line_ids')
    def as_change_sequence(self):
        cont = 1
        for res in self.invoice_line_ids:
            res.sequence = cont
            cont += 1

    @api.model
    def _get_default_currency2(self):
        ''' Get the default currency from either the journal, either the default journal's company. '''
        journal = self._get_default_journal()
        if not journal:
            currency = self.env.user.company_id.currency_id
        else:
            currency = journal.currency_id or journal.company_id.currency_id
        return currency

    currency_id = fields.Many2one('res.currency', store=True, readonly=True, tracking=True, required=True,
        states={'draft': [('readonly', False)]},
        string='Divisa',
        default=_get_default_currency2)
    as_etapa = fields.Selection([
            ('Prefactura','Prefactura'),
            ('Prefactura en revisión','Prefactura en revisión'),
            ('Prefactura aprobada','Prefactura aprobada'),
            ('Prefactura enviada','Prefactura enviada'),
            ('Aprobado cliente','Aprobado cliente'),
        ],
        string="Etapa")
    as_fecha_prefactura = fields.Date(string="Fecha Prefactura",)
    as_conditions_lines = fields.Many2many('as.proposal.conditions.sale', string='Condiciones de la Propuesta')
    as_texto = fields.Char(string='Texto')
    as_proposal_id = fields.Many2one('as.proposal', string='Plantilla de Campos')


    @api.model
    def _search_default_journal(self, journal_types):
        journal = super(AccountMove, self)._search_default_journal(journal_types)
        if journal_types[0] == 'purchase' and self._context.get('create_bill') == None:
            journal=False
        return journal
        
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

    # def _recompute_tax_lines(self, recompute_tax_base_amount=False):
        
    #     self.ensure_one()
    #     res=super(AccountMove, self)._recompute_tax_lines(recompute_tax_base_amount)

    #     in_draft_mode = self != self._origin

    #     def _serialize_tax_grouping_key(grouping_dict):
    #         ''' Serialize the dictionary values to be used in the taxes_map.
    #         :param grouping_dict: The values returned by '_get_tax_grouping_key_from_tax_line' or '_get_tax_grouping_key_from_base_line'.
    #         :return: A string representing the values.
    #         '''
    #         return '-'.join(str(v) for v in grouping_dict.values())

    #     def _compute_base_line_taxes(base_line):
    #         precio_auxiliar = 0.0
    #         if self.move_type=='in_invoice' and base_line.as_price_unit_aux >0:
    #             move = base_line.move_id
    #             precio_auxiliar = base_line.as_price_unit_aux
    #         else:
    #             move = base_line.move_id
    #             precio_auxiliar = base_line.price_unit
                
    #         if move.is_invoice(include_receipts=True):
    #             handle_price_include = True
    #             sign = -1 if move.is_inbound() else 1
    #             quantity = base_line.quantity
    #             is_refund = move.move_type in ('out_refund', 'in_refund')
    #             price_unit_wo_discount = sign * precio_auxiliar * (1 - (base_line.discount / 100.0))
    #         else:
    #             handle_price_include = False
    #             quantity = 1.0
    #             tax_type = base_line.tax_ids[0].type_tax_use if base_line.tax_ids else None
    #             is_refund = (tax_type == 'sale' and base_line.debit) or (tax_type == 'purchase' and base_line.credit)
    #             price_unit_wo_discount = base_line.amount_currency

    #         balance_taxes_res = base_line.tax_ids._origin.with_context(force_sign=move._get_tax_force_sign()).compute_all(
    #             price_unit_wo_discount,
    #             currency=base_line.currency_id,
    #             quantity=quantity,
    #             product=base_line.product_id,
    #             partner=base_line.partner_id,
    #             is_refund=is_refund,
    #             handle_price_include=handle_price_include,
    #         )

    #         if move.move_type == 'entry':
    #             repartition_field = is_refund and 'refund_repartition_line_ids' or 'invoice_repartition_line_ids'
    #             repartition_tags = base_line.tax_ids.flatten_taxes_hierarchy().mapped(repartition_field).filtered(lambda x: x.repartition_type == 'base').tag_ids
    #             tags_need_inversion = (tax_type == 'sale' and not is_refund) or (tax_type == 'purchase' and is_refund)
    #             if tags_need_inversion:
    #                 balance_taxes_res['base_tags'] = base_line._revert_signed_tags(repartition_tags).ids
    #                 for tax_res in balance_taxes_res['taxes']:
    #                     tax_res['tag_ids'] = base_line._revert_signed_tags(self.env['account.account.tag'].browse(tax_res['tag_ids'])).ids

    #         return balance_taxes_res

     
    #     return res
    
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

    @api.onchange('invoice_date')
    def as_get_escritura(self):
        for res in self:
            if res.move_type == 'out_invoice':
                escritura = ''
                if res.invoice_date:
                    escritura += res.invoice_date.strftime('%m')+'-'+res.invoice_date.strftime('%Y')+' '
                if res.invoice_origin:
                    sale = self.env['sale.order'].search([('name','=',res.invoice_origin)])
                    if sale:
                        escritura+=sale.as_template_id.name

                res.as_escritura_prefactura = escritura


    @api.model
    def create(self, vals):
        res = super().create(vals)
        for line in res.invoice_line_ids:
            line.as_descripcion = line.as_descripcion
        # res.as_get_escritura()
        return res

    def write(self, vals):
        res = super().write(vals)
        for line in self.invoice_line_ids:
            line.as_descripcion = line.as_descripcion
        return res

    def get_sale(self):
        """Funcion para extraer la venta relacionada a la factura"""
        sale = self.env['sale.order'].search([('name','=',self.invoice_origin)])
        return sale

    def get_payment(self):
        """obtener todos los pagos de una factura"""
        payment = {}
        account_payment = self.env['account.payment']
        if json.loads(self.invoice_payments_widget):
            payment = json.loads(self.invoice_payments_widget)
            for payment_inv in payment['content']:
                payment_id = int(payment_inv['account_payment_id'])
                account_payment |=self.env['account.payment'].search([('id','=',payment_id),('state','=','posted')])
        return account_payment

    def as_get_date_literal(self,fecha):
        """retornar fecha en literal"""
        dia = datetime.strptime(str(fecha), '%Y-%m-%d').strftime('%d')
        mes = self.get_mes(datetime.strptime(str(fecha), '%Y-%m-%d').strftime('%m'))
        ano = datetime.strptime(str(fecha), '%Y-%m-%d').strftime('%Y')
        return str(dia)+' de '+ str(mes)+' de '+str(ano)

    def get_mes(self,mes):
        """extraer mes en literal"""
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

    def _lineas_ordenadas(self):
        """Extraer lineas ordenadas a partir de configuracion"""
        type_order = self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_type_order_report')
        if not type_order or type_order == 'Ninguno':
            order_lines =self.invoice_line_ids
        else:
            order_lines= self.env['account.move.line'].sudo().search([('order_id','=',self.id)],order=(str(type_order)+" asc"))
        return order_lines

    def concatenar_proyecto(self, requerido):
        concatenar=''
        datos_sale_order = self.env['sale.order'].search([('name','=',self.invoice_origin)])
        if datos_sale_order:
            concatenar+= ', ' + str(datos_sale_order.as_template_id.name) + ' '
        json={
            'proyecto':concatenar
        }
        concatenar = json[str(requerido)]
        return concatenar
    def concatenar_ot(self, requerido):
        concatenar=''
        datos_sale_order = self.env['sale.order'].search([('name','=',self.invoice_origin)])
        datos_project_task = self.env['project.task'].search([('sale_order_id','=',datos_sale_order.id)])
        if datos_project_task:
            concatenar+=', ' + str(datos_project_task.as_ot) + ' '
        json={
            'ot':concatenar
        }
        concatenar = json[str(requerido)]
        return concatenar
    
    def concatenar_materiales(self, requerido):
        concatenar=''
        datos_sale_order = self.env['sale.order'].search([('name','=',self.invoice_origin)])
        datos_project_task = self.env['project.task'].search([('sale_order_id','=',datos_sale_order.id)])
        datos_reques_materials = self.env['as.request.materials'].search([('as_project_id','=',datos_project_task.id)])
        if datos_reques_materials:
            concatenar+=', ' + str(datos_reques_materials.name) + ' '
        json={
            'material':concatenar
        }
        concatenar = json[str(requerido)]
        return concatenar
    
    def extraer_ot(self, requerido):
        concatenar=''
        datos_sale_order = self.env['sale.order'].search([('name','=',self.invoice_origin)])
        datos_project_task = self.env['project.task'].search([('sale_order_id','=',datos_sale_order.id)])
        if datos_project_task:
            concatenar+=str(datos_project_task.as_ot)
        json={
            'campo_ot':concatenar
        }
        concatenar = json[str(requerido)]
        return concatenar


    def extraer_informacion_usuario(self,requerido):
        concatenar=''
        nombre = ''
        datos_empleado = self.env['hr.employee'].search([('user_id','=',self.create_uid.id)])
        if datos_empleado:
            nombre+=str(datos_empleado.name)
            concatenar+=str(datos_empleado.job_id.name)
        else:
            nombre=''
            concatenar=''
        json={
            'nombre':nombre,
            'puesto':concatenar
        }
        concatenar = json[str(requerido)]
        return concatenar
    
    def extraer_telefono_usuario(self,requerido):
        concatenar=''
        datos_empleado = self.env['hr.employee'].search([('user_id','=',self.create_uid.id)])
        if datos_empleado:
            concatenar+=str(datos_empleado.mobile_phone)
        json={
            'telefono':concatenar
        }
        concatenar = json[str(requerido)]
        return concatenar
    
    def extraer_correo_usuario(self,requerido):
        concatenar=''
        datos_empleado = self.env['hr.employee'].search([('user_id','=',self.create_uid.id)])
        if datos_empleado:
            concatenar+=str(datos_empleado.work_email)
        json={
            'correo':concatenar
        }
        concatenar = json[str(requerido)]
        return concatenar
    
    def extraer_tipo_moneda(self,requerido):
        value=0
        concatenar=''
        datos_sale_order = self.env['sale.order'].search([('name','=',self.invoice_origin)])
        if datos_sale_order:
            concatenar=str(datos_sale_order.currency_id.name)
        else:
            concatenar=''
        json={
            'moneda':concatenar
        }
        concatenar = json[str(requerido)]
        return concatenar

    def _message_auto_subscribe_notify(self, partner_ids, template):
        """ Evitar notificaciones a responsables de documentos
        """
        if not self or self.env.context.get('mail_auto_subscribe_no_notify'):
            return
        if not self.env.registry.ready:  # Don't send notification during install
            return

        view = self.env['ir.ui.view'].browse(self.env['ir.model.data'].xmlid_to_res_id(template))

        for record in self:
            pass