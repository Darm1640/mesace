from odoo import api, fields, models, _
from odoo.exceptions import UserError
from . import as_siat_utility as as_utility
import json
import base64
from dateutil.relativedelta import relativedelta
from odoo.tests.common import SavepointCase, HttpSavepointCase, tagged, Form
from werkzeug.urls import url_encode
import random
import dateutil.parser
from datetime import timedelta, datetime
import xml.etree.ElementTree as ET

class as_account_move(models.Model):
    _inherit = 'account.move'

    def _default_sistema(self):
        type_inv = self._context.get('default_move_type') or self._context.get('move_type')
        if type_inv == 'out_invoice' and len(self.env.user.as_system_certificate) >0:
            return self.env.user.as_system_certificate[0]

    def _default_sucursal(self):
        type_inv = self._context.get('default_move_type') or self._context.get('move_type')
        if type_inv == 'out_invoice' and len(self.env.user.as_branch_office) >0:
            return self.env.user.as_branch_office[0]

    def _default_pdv(self):
        type_inv = self._context.get('default_move_type') or self._context.get('move_type')
        if type_inv == 'out_invoice' and len(self.env.user.as_pdv_ids) >0:
            return self.env.user.as_pdv_ids[0]

    #datos de clientes
    as_complemento_nit = fields.Char(string="Complemento")
    # Campos requeridos para la generacion del CUF
    as_codigo_sistema = fields.Many2one('as.siat.codigo.sistema', string="Codigo Sistema", default=_default_sistema)
    as_branch_office = fields.Many2one('as.siat.sucursal', string="Sucursal", default=_default_sucursal)
    as_pdv_id = fields.Many2one('as.siat.punto.venta', string="Punto de Venta", default=_default_pdv)
    as_invoice_number = fields.Integer(string="Numero de factura", default=0,copy=False)
    # Campos obtenodps de 'as.siat.catalogos'
    as_fiscal_document_code = fields.Many2one('as.siat.catalogos', string="Tipo documento fiscal", domain="[('as_group', '=', 'TIPO_FACTURA')]", default=lambda self: self.env['as.siat.catalogos'].search([('as_group', '=', 'TIPO_FACTURA'),('as_code','=','1')],limit=1),copy=False)
    as_sector_type = fields.Many2one('as.siat.catalogos', string="Tipo documento sector", domain="[('as_group', '=', 'DOCUMENTO_SECTOR')]",  default=lambda self: self.env['as.siat.catalogos'].search([('as_group', '=', 'DOCUMENTO_SECTOR'),('as_code','=','1')],limit=1),copy=False)
    as_emission_type = fields.Many2one('as.siat.catalogos', string="Tipo emision", domain="[('as_group', '=', 'EMISION')]",  default=lambda self: self.env['as.siat.catalogos'].search([('as_group', '=', 'EMISION'),('as_code','=','1')],limit=1),copy=False)
    as_payment_method = fields.Many2one('as.siat.catalogos', string="Metodo pago", domain="[('as_group', '=', 'METODO_PAGO')]",  default=lambda self: self.env['as.siat.catalogos'].search([('as_group', '=', 'METODO_PAGO'),('as_code','=','6')],limit=1),copy=False)
    as_tarjeta_name = fields.Char(string="Activar tarjeta",related="as_payment_method.name")
    as_id_code = fields.Many2one('as.siat.catalogos', string="Tipo documento identidad", domain="[('as_group', '=', 'DOCUMENTO_IDENTIDAD')]",  default=lambda self: self.env['as.siat.catalogos'].search([('as_group', '=', 'DOCUMENTO_IDENTIDAD'),('as_code','=','1')],limit=1))
    as_motivo_anulacion = fields.Many2one('as.siat.catalogos', string="Tipo documento identidad", domain="[('as_group', '=', 'MOTIVO_ANULACION')]",  default=lambda self: self.env['as.siat.catalogos'].search([('as_group', '=', 'MOTIVO_ANULACION'),('as_code','=','1')],limit=1))
    as_tipo_cambio = fields.Integer(string="Tipo cambio", default=1.0)
    as_numero_tarjeta = fields.Char(string="Numero de tarjeta")
    as_monto_gift = fields.Float(string="Monto Gift Card")
    as_descuento_adicional = fields.Float(string="Descuento Adicional",copy=False)
    as_codigo_excepcion = fields.Integer(string="Código Excepción",default=0)
    as_cuf = fields.Char(string="CUF",copy=False)
    as_idtransaccion = fields.Char(string="ID Transaccional",copy=False)
    as_idpedido = fields.Char(string="ID del Pedido",copy=False)
    as_monto_total_original = fields.Char(string="Monto total original")
    as_cancel_cont = fields.Boolean(string="Ha sido cancelada la factura",default=False,copy=False)
    as_monto_efectivo_credito_debito = fields.Char(string="Monto efectivo credito-debito",default="13")
    as_state_siat = fields.Selection(selection=[
        ('not_sent', 'Pendiente Enviar'),
        ('accepted', 'Aceptado'),
        ('objected', 'Enviado con Reporte'),
        ('rejected', 'Rechazado'),
        ('cancel', 'Anulado'),
    ], string='Estado SIAT',default="not_sent",copy=False)
    as_mensaje_siat = fields.Char(string="Mensaje SIAT",copy=False)
    as_code_siat = fields.Char(string="Recepción SIAT",copy=False)
    as_ambiente = fields.Boolean(string="Ambiente")
    as_name_inv = fields.Char(string="Nombre de Reporte")
    as_xml_invoice = fields.Binary('Factura XML',copy=False)
    as_xml_recepcion = fields.Binary('Recepción XML',copy=False)
    as_cont_cafc = fields.Many2one('as.cafc', string="CAFC",copy=False)
    as_numero_tarjeta_str = fields.Char(string="Numero de tarjeta")
    as_leyenda = fields.Char(string="Leyenda")
    as_fecha_edit = fields.Boolean(string="Fecha Editable", default=False,copy=False)
    as_fecha_factura = fields.Datetime(string="Fecha Factura", default=datetime.now(),copy=False)
    as_fecha_emision = fields.Char(string="Fecha/hora factura",copy=False)
    as_factor = fields.Float(string="Descuento adicional unitario", store=True)
    as_creada = fields.Boolean(string="Creada",copy=False)
    as_cufd = fields.Char(string="CUFD",copy=False)
    as_evento = fields.Many2one('as.send.massive.invoice', string="Evento Relacionado",copy=False)
    as_existe = fields.Boolean(string="Obtener del API",copy=False)

    # def button_draft(self):
    #     # OVERRIDE to update the cancel date.
    #     for move in self:
    #         if move.state == 'posted' and move.as_state_siat == 'accepted':
    #             raise UserError(_("No puede Volver a borrador una factura aceptada por el SIAT."))
    #     res = super(as_account_move, self).button_draft()
    #     return res

   
    def as_action_invoice_regularizar(self):
        if self.state == 'posted' and self.as_state_siat == 'accepted':
            raise UserError(_("No puede pasar a Regularizar una factura aceptada por el SIAT."))
        return super(as_account_move, self).as_action_invoice_regularizar()  
    
    def as_action_invoice_regularizar_move(self):
        if self.state == 'posted' and self.as_state_siat == 'accepted':
            raise UserError(_("No puede pasar a Regularizar una factura aceptada por el SIAT."))
        return super(as_account_move, self).as_action_invoice_regularizar_move() 


    @api.onchange('as_numero_tarjeta_str')
    def as_get_format_tarjeta(self):
        for invoice in self:
            if invoice.as_numero_tarjeta_str:
                if len(invoice.as_numero_tarjeta_str) < 16 or len(invoice.as_numero_tarjeta_str) >16:
                    raise UserError(_("numero de tarjeta debe tener 16 caracteres."))

                invoice.as_numero_tarjeta = invoice.as_numero_tarjeta_str[:4]+'00000000'+invoice.as_numero_tarjeta_str[12:]

    @api.onchange('as_branch_office')
    def as_get_ambiente(self):
        for invoice in self:
            mensaje = ''
            json = {}
            respuesta = as_utility.as_process_json('Consultar Cliente',json,self.env.user.id,self.as_codigo_sistema.as_token_ahorasoft,'Consultar Cliente')
            if respuesta[0] and respuesta[1]['success']:
                if 'partner' in respuesta[1]:
                    if respuesta[1]['partner']:
                        if respuesta[1]['partner']['ambiente'] == '1':
                            invoice.as_ambiente = True
                        else:
                            invoice.as_ambiente = False
            else:
                invoice.as_ambiente = False

    @api.depends('as_branch_office','as_pdv_id','as_invoice_number','vat')
    def as_get_name_report(self):
        for inv in self:
            inv.as_name_inv = 'FACTURA_'+str(inv.as_nit)+str(inv.as_invoice_number)+str(inv.as_sector_type.as_code)+str(inv.as_emission_type.as_code)


    def as_button_cancel(self):
        if self.move_type in ('out_invoice','out_refund'):
            #FECHA DE LIMITE DE CANCELAR FACTURAS
            if self.as_cancel_cont:
                raise UserError(_("Ya la Factura ha sido cancelada una vez."))
            as_date_limit = int(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_number_end_invoice'))
            previous_month = fields.Date.today() + relativedelta(months=1)
            if not as_date_limit:
                raise UserError(_("Debe completar su fecha limite de cancelacion de facturas."))
            fecha_limite = self.invoice_date + relativedelta(months=1)
            fecha_limite = fecha_limite.strftime('%Y-%m-')+str(as_date_limit)
            if fields.Date.from_string(fecha_limite) < fields.Date.today():
                raise UserError(_("La factura no se puede cancelar, sobrepasa el limite establecido su fecha limite fue %s.")%fecha_limite)
            for invoice in self:
                if not invoice.as_motivo_anulacion:
                    raise UserError(_("Debe completar el motivo para anular la factura."))

                if invoice.state == 'cancel':
                    factura = {
                        "idtransaccion": invoice.as_idtransaccion,
                        "codigoMotivo": invoice.as_motivo_anulacion.as_code,
                    
                    }
                    self.message_post(body = str(json.dumps(factura)), content_subtype='html')  
                    if self.move_type == 'out_invoice':
                        respuesta = as_utility.as_process_json('Cancelar Factura',factura,self.env.user.id,invoice.as_codigo_sistema.as_token_ahorasoft,'Cancelar Factura')
                    elif self.move_type == 'out_refund':
                        respuesta = as_utility.as_process_json('Cancelar NDC',factura,self.env.user.id,invoice.as_codigo_sistema.as_token_ahorasoft,'Cancelar NDC')

                    if respuesta[0] and respuesta[1]['success']:
                        if 'factura' in respuesta[1]:
                            valores = respuesta[1]['factura']
                            if valores['codigoEstado'] == '905':
                                invoice.as_state_siat = 'cancel'
                                invoice.state = 'cancel'
                                invoice.as_mensaje_siat = valores['codigoDescripcion']
                                invoice.as_xml_recepcion = base64.encodebytes(respuesta[1]['mensaje'].encode('UTF-8'))
                                mensaje = as_utility.as_format_success(respuesta[1]['mensaje'])
                                self.message_post(body = str(mensaje), content_subtype='html') 
                            else:
                                invoice.as_state_siat = 'rejected'
                                invoice.state="posted"
                                invoice.as_mensaje_siat = valores['codigoDescripcion']
                                invoice.as_xml_recepcion = base64.encodebytes(respuesta[1]['mensaje'].encode('UTF-8'))
                                if type(valores['mensajesList']) == type([]):
                                    for error in valores['mensajesList']:
                                        mensaje = as_utility.as_format_error(error['codigo']+': '+error['descripcion'])
                                        self.message_post(body = str(mensaje), content_subtype='html') 
                                else:
                                    mensaje = as_utility.as_format_error(valores['mensajesList']['codigo']+': '+valores['mensajesList']['descripcion'])
                                    self.message_post(body = str(mensaje), content_subtype='html') 
                    else:
                        invoice.state="posted"
                        invoice.as_state_siat = 'objected'
                        mensaje = as_utility.as_format_error(respuesta[1])
                        mensaje2 = respuesta[1]['mensaje']
                        invoice.as_mensaje_siat = mensaje2
                        self.message_post(body = str(mensaje), content_subtype='html')  
            self.env.cr.commit()


    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit',
        'as_descuento_adicional',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id')
    def _compute_amount(self):
        for move in self:

            if move.payment_state == 'invoicing_legacy':
                # invoicing_legacy state is set via SQL when setting setting field
                # invoicing_switch_threshold (defined in account_accountant).
                # The only way of going out of this state is through this setting,
                # so we don't recompute it here.
                move.payment_state = move.payment_state
                continue

            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            total_tax = 0.0
            total_tax_currency = 0.0
            total_to_pay = 0.0
            total_residual = 0.0
            total_residual_currency = 0.0
            total = 0.0
            total_currency = 0.0
            currencies = move._get_lines_onchange_currency().currency_id

            for line in move.line_ids:
                if move.is_invoice(include_receipts=True):
                    # === Invoices ===

                    if not line.exclude_from_invoice_tab:
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.tax_line_id:
                        # Tax amount.
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.account_id.user_type_id.type in ('receivable', 'payable'):
                        # Residual amount.
                        total_to_pay += line.balance
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            if move.move_type == 'entry' or move.is_outbound():
                sign = 1
            else:
                sign = -1
            move.amount_untaxed = sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed)
            move.amount_tax = sign * (total_tax_currency if len(currencies) == 1 else total_tax)

            move.amount_total = (sign * (total_currency if len(currencies) == 1 else total)) - move.as_descuento_adicional
            move.amount_residual = -sign * (total_residual_currency if len(currencies) == 1 else total_residual) - move.as_descuento_adicional
            move.amount_untaxed_signed = -total_untaxed
            move.amount_tax_signed = -total_tax
            move.amount_total_signed = abs(total) if move.move_type == 'entry' else -total
            move.amount_residual_signed = total_residual - move.as_descuento_adicional
            if move.move_type == 'out_refund':
                if move.as_descuento_adicional > 0:
                    total = move.as_descuento_adicional*0.13
                    move.as_monto_efectivo_credito_debito = str(round(move.amount_tax - total,2))
                    move.as_monto_total_original = str(round(move.amount_untaxed+float(move.amount_tax - total)+total,2))
                else:
                    move.as_monto_total_original = str(move.amount_total)
                    move.as_monto_efectivo_credito_debito = str(move.amount_tax)

            currency = len(currencies) == 1 and currencies or move.company_id.currency_id

            # Compute 'payment_state'.
            new_pmt_state = 'not_paid' if move.move_type != 'entry' else False

            if move.is_invoice(include_receipts=True) and move.state == 'posted':

                if currency.is_zero(move.amount_residual):
                    reconciled_payments = move._get_reconciled_payments()
                    if not reconciled_payments or all(payment.is_matched for payment in reconciled_payments):
                        new_pmt_state = 'paid'
                    else:
                        new_pmt_state = move._get_invoice_in_payment_state()
                elif currency.compare_amounts(total_to_pay, total_residual) != 0:
                    new_pmt_state = 'partial'

            if new_pmt_state == 'paid' and move.move_type in ('in_invoice', 'out_invoice', 'entry'):
                reverse_type = move.move_type == 'in_invoice' and 'in_refund' or move.move_type == 'out_invoice' and 'out_refund' or 'entry'
                reverse_moves = self.env['account.move'].search([('reversed_entry_id', '=', move.id), ('state', '=', 'posted'), ('move_type', '=', reverse_type)])

                # We only set 'reversed' state in cas of 1 to 1 full reconciliation with a reverse entry; otherwise, we use the regular 'paid' state
                reverse_moves_full_recs = reverse_moves.mapped('line_ids.full_reconcile_id')
                if reverse_moves_full_recs.mapped('reconciled_line_ids.move_id').filtered(lambda x: x not in (reverse_moves + reverse_moves_full_recs.mapped('exchange_move_id'))) == move:
                    new_pmt_state = 'reversed'

            move.payment_state = new_pmt_state

    def as_get_leyenda(self):
        for invoice in self:
            code = random.randint(1, 16)
            leyenda = self.env['as.siat.catalogos'].search([('as_group', '=', 'LEYENDAS_FACTURA'),('as_code', '=', str(code))],limit=1)
            invoice.as_leyenda = leyenda.name

    @api.depends('partner_id')
    @api.onchange('partner_id')
    def as_get_partner(self):
        for move in self:
            if move.partner_id.as_identification.as_code == '1':
                move.as_complemento_nit = move.partner_id.as_complemento_nit
            else:
                move.as_complemento_nit = False
            move.as_nit = move.partner_id.vat
            move.as_razon_social = move.partner_id.as_razon_social
            move.as_id_code = move.partner_id.as_identification
            move.as_get_leyenda()

    def action_post(self):
        res = super(as_account_move, self).action_post()
        if self.move_type in ('out_invoice','out_refund') and not self.as_contable and not self.as_si_contable:
            try:
                nit = int(self.as_nit)
            except Exception as e:
                raise UserError(_("El nit no puede contener caracteres debe ser numerico"))

            if float(self.as_nit) <= float(0):
                raise UserError(_("El nit no puede estar en CERO"))
            if self.as_cont_cafc and self.as_emission_type.as_code != '2':
                raise UserError(_("No se puede emitir facturas con CAFC y tipo de emision diferente a OFFLINE"))

            self.verificar_nit()
            if self.as_cont_cafc:
                self.as_invoice_number = self.as_cont_cafc.as_proximo
                self.as_cont_cafc.as_proximo = self.as_cont_cafc.as_proximo+1

            if self.verificar_comunicacion():
                self.as_generate_invoice(False)
                paquetes = self.env['as.send.massive.invoice'].search([('state','=','draft'),('as_automatico','=',True)])
                for pack in paquetes:
                    pack.state = 'cola'
            else:
                self.as_generate_invoice(True)
    
            if self.as_emission_type.as_code == '1' and not self.as_existe:
                self.as_recepciona_invoice()
            if self.state == 'posted' and not self.as_cont_cafc:
                self.as_adjustment_invoice()
                self.action_move_send()

        return res

    def verificar_comunicacion(self):
        for invoice in self:
            mensaje = ''
            json = {}
            as_out_line = bool(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_out_line'))
            if not as_out_line:
                respuesta = as_utility.as_process_json('Verifica Comunicación',json,self.env.user.id,self.as_codigo_sistema.as_token_ahorasoft,'Verifica Comunicación')
                if respuesta[0] and respuesta[1]['success']:
                    return True
                else:
                    return False
            else:
                return False

    def verificar_nit(self):
        for invoice in self:
            mensaje = ''
            json = {
                    "nit": self.as_nit,
                    "nitParaVerificacion": invoice.as_nit,
                    "codigoPuntoVenta": str(invoice.as_pdv_id.as_code),
                    "codigoSucursal": str(invoice.as_branch_office.as_office_number)
                }
            respuesta = as_utility.as_process_json('NIT',json,self.env.user.id,self.as_codigo_sistema.as_token_ahorasoft,'Comprobar NIT')
            if respuesta[0] and respuesta[1]['success']:
                if 'values' in respuesta[1]:
                    if respuesta[1]['values']:
                        invoice.as_codigo_excepcion = 0
                    else:
                        invoice.as_codigo_excepcion = 1
                mensaje = as_utility.as_format_success(respuesta[1]['mensaje'])
            else:
                if 'values' in respuesta[1]:
                    invoice.as_codigo_excepcion = 1
                mensaje = as_utility.as_format_success(respuesta[1]['mensaje'])

    def as_get_package_contingencia(self,evento,values):
        for inv in self:
            #se busca el paquete para proceder a enviarlo
            paquete = self.env['as.send.massive.invoice'].search([
                ('as_fiscal_document_code','=',inv.as_fiscal_document_code.id),
                ('as_sector_type','=',inv.as_sector_type.id),
                ('as_pdv_id','=',inv.as_pdv_id.id),
                ('as_cont_cudf','=',inv.as_cufd),
                ('state','=','draft'),
                ('as_automatico','=',True),
                ],limit=1)
            if paquete:
                Facturas_paquete = []
                cont = 0
                for invoice in paquete.as_invoice_move_ids:
                    Facturas_paquete.append(invoice.id)
                    cont+=1
                Facturas_paquete.append(self.id)
                cont+=1
                paquete.as_invoice_move_ids = Facturas_paquete
                paquete.name += str(inv.as_invoice_number)+','
                paquete.as_cont_note += str(inv.name)+','
                date_fin = inv.as_fecha_factura + relativedelta(seconds=1)
                paquete.as_cont_date_end = date_fin
                paquete.as_cantidad = cont
                inv.as_evento = paquete

            else:
                date_inicio = inv.as_fecha_factura - relativedelta(seconds=1)
                date_fin = inv.as_fecha_factura + relativedelta(seconds=1)
                evento = self.env['as.siat.catalogos'].search([('as_group', '=', 'EVENTOS_SIGNIFICATIVOS'),('as_code','=','2')],limit=1)
                vals = {
                    'name': 'Contingencia Facturas '+str(inv.as_invoice_number)+',',
                    'as_type_mode': 'packet',
                    'as_codigo_sistema': inv.as_branch_office.as_system_id.id,
                    'as_sucursal': inv.as_branch_office.id,
                    'as_pdv_id': inv.as_pdv_id.id,
                    'as_invoice_move_ids': [inv.id],
                    'as_cont_date_start': date_inicio,
                    'as_cont_date_end': date_fin,
                    'as_cont_reason': evento.id,
                    'as_cont_cudf': inv.as_cufd,
                    'as_cont_cafc': False,
                    'as_cont_note': 'Evento Generado automaticamente para factura '+str(inv.name)+', ',
                    'as_cantidad': 1,
                    'as_fiscal_document_code': inv.as_fiscal_document_code.id,
                    'as_sector_type': inv.as_sector_type.id,
                    'state': 'draft',
                    'as_automatico': True,
                    'as_emission_type': values.id,

                }
                inv.as_evento = self.env['as.send.massive.invoice'].create(vals)

    def as_generate_invoice(self,automatico):
        for invoice in self:
            #emsamblamos lineas
            line_invoice = []
            if invoice.move_type == 'out_invoice':
                for line in invoice.invoice_line_ids:
                    if not line.display_type:
                        vals =  {
                            "actividadEconomica": self.as_get_str(line.product_id.as_actividad.as_code),
                            "codigoProductoSin": self.as_get_str(line.product_id.as_product_service.as_code),
                            "codigoProducto": self.as_get_str(line.product_id.default_code),
                            "descripcion": self.as_get_str(line.name),
                            "cantidad": self.as_get_str(line.quantity),
                            "unidadMedida": self.as_get_str(line.product_uom_id.as_uom.as_code),
                            "precioUnitario": self.as_get_str(line.price_unit),
                            "montoDescuento": self.as_get_int(line.as_discount_amount),
                            "subTotal": self.as_get_str(line.price_total),
                            "numeroSerie": self.as_get_int(line.product_id.as_numero_serie),
                            "numeroImei": self.as_get_int(line.product_id.as_numero_imei),
                        }
                        line_invoice.append(vals)
                factura = {
                    "codigoSucursal": self.as_get_str(invoice.as_branch_office.as_office_number),
                    "codigoPuntoVenta": self.as_get_str(invoice.as_pdv_id.as_code),
                    "nombreRazonSocial": self.as_get_str(invoice.as_razon_social),
                    "codigoTipoDocumentoIdentidad": self.as_get_str(invoice.as_id_code.as_code),
                    "numeroDocumento": self.as_get_str(invoice.as_nit),
                    "complemento": self.as_get_str(invoice.as_complemento_nit),
                    "codigoCliente": self.as_get_str(invoice.partner_id.id),
                    "codigoMetodoPago": self.as_get_str(invoice.as_payment_method.as_code),
                    "codigoEmision": self.as_get_str(invoice.as_emission_type.as_code),
                    "numeroTarjeta": self.as_get_str(invoice.as_numero_tarjeta),
                    "montoTotal": self.as_get_str(invoice.amount_total),
                    "montoTotalSujetoIva": self.as_get_str(invoice.amount_total),
                    "codigoMoneda": self.as_get_str(invoice.currency_id.as_currencysiat.as_code),
                    "tipoCambio": self.as_get_str(invoice.as_tipo_cambio),
                    "montoGiftCard": self.as_get_str(invoice.as_monto_gift),
                    "descuentoAdicional": self.as_get_str(invoice.as_descuento_adicional),
                    "codigoExcepcion": self.as_get_str(invoice.as_codigo_excepcion),
                    "montoTotalMoneda": self.as_get_str(invoice.amount_total),
                    "usuario": self.as_get_str(invoice.user_id.name),
                    "leyenda": self.as_get_str(invoice.as_leyenda),
                    "tipoFacturaDocumento": self.as_get_str(invoice.as_fiscal_document_code.as_code),
                    "codigoDocumentoSector": self.as_get_str(invoice.as_sector_type.as_code),
                    "detalle": line_invoice
                }
                if automatico:
                    values = self.env['as.siat.catalogos'].search([('as_group', '=', 'EMISION'),('as_code','=','2')],limit=1)
                    self.as_emission_type = values.id
                    factura['codigoEmision'] = '2'
                    self.as_state_siat = 'not_sent'
                    self.as_fecha_edit = True
                    self.as_fecha_factura = datetime.now()
                    # glosa = str(values.name)+' AUTOMATICO'
                    # self.as_get_package_contingencia(glosa,values)
                if self.as_idtransaccion:
                    factura['numeroFactura'] = invoice.as_invoice_number
                    fecha = str(as_utility.date2timezone(dateutil.parser.parse(str(invoice.as_fecha_factura - relativedelta(hours=4)))))
                    invoice.as_fecha_emision = fecha
                    factura['fechaEmision'] = invoice.as_fecha_emision
                if self.as_emission_type.as_code == '2':
                    if self.as_cont_cafc:
                        factura['numeroFactura'] = invoice.as_invoice_number
                        factura['cafc'] = invoice.as_cont_cafc.name
                    if not invoice.as_fecha_edit:
                        invoice.as_fecha_factura = datetime.now()
                    fecha = str(as_utility.date2timezone(dateutil.parser.parse(str(invoice.as_fecha_factura - relativedelta(hours=4)))))
                    invoice.as_fecha_emision = fecha
                    factura['fechaEmision'] = invoice.as_fecha_emision
                self.message_post(body = str(json.dumps(factura)), content_subtype='html')  
                has_inv = invoice.as_generate_hash()
                id_invoice = invoice.id
                if self.as_existe:
                    factura = {
                        'idtransaccion': self.as_idtransaccion,
                    }
                    respuesta = as_utility.as_process_json('Factura Consulta',factura,self.env.user.id,invoice.as_codigo_sistema.as_token_ahorasoft,'Crear Factura',hash_inv=has_inv,number=id_invoice)
                else:
                    respuesta = as_utility.as_process_json('Factura',factura,self.env.user.id,invoice.as_codigo_sistema.as_token_ahorasoft,'Crear Factura',hash_inv=has_inv,number=id_invoice)
            elif invoice.move_type == 'out_refund':
                for line in invoice.reversed_entry_id.invoice_line_ids:
                    if not line.display_type:
                        #armando las lineas de factura devuelta
                        vals =  {
                            "actividadEconomica": self.as_get_str(line.product_id.as_actividad.as_code),
                            "codigoProductoSin": self.as_get_str(line.product_id.as_product_service.as_code),
                            "codigoProducto": self.as_get_str(line.product_id.default_code),
                            "descripcion": self.as_get_str(line.name),
                            "cantidad": self.as_get_str(line.quantity),
                            "unidadMedida": self.as_get_str(line.product_uom_id.as_uom.as_code),
                            "precioUnitario": self.as_get_str(line.price_unit),
                            "montoDescuento": self.as_get_int(line.as_discount_amount),
                            "subTotal": self.as_get_str(line.price_total),
                            "codigoDetalleTransaccion": "1",
                        }
                        line_invoice.append(vals)
                for line in invoice.invoice_line_ids:
                    if not line.display_type:
                        vals =  {
                            "actividadEconomica": self.as_get_str(line.product_id.as_actividad.as_code),
                            "codigoProductoSin": self.as_get_str(line.product_id.as_product_service.as_code),
                            "codigoProducto": self.as_get_str(line.product_id.default_code),
                            "descripcion": self.as_get_str(line.name),
                            "cantidad": self.as_get_str(line.quantity),
                            "unidadMedida": self.as_get_str(line.product_uom_id.as_uom.as_code),
                            "precioUnitario": self.as_get_str(line.price_unit),
                            "montoDescuento": self.as_get_int(line.as_discount_amount),
                            "subTotal": self.as_get_str(line.price_total),
                            "codigoDetalleTransaccion": "2",
                        }
                        line_invoice.append(vals)
                factura = {
                    "codigoSucursal": self.as_get_str(invoice.as_branch_office.as_office_number),
                    "codigoPuntoVenta": self.as_get_str(invoice.as_pdv_id.as_code),
                    "nombreRazonSocial": self.as_get_str(invoice.as_razon_social),
                    "codigoTipoDocumentoIdentidad": self.as_get_str(invoice.as_id_code.as_code),
                    "numeroDocumento": self.as_get_str(invoice.as_nit),
                    "complemento": self.as_get_str(invoice.as_complemento_nit),
                    "codigoCliente": self.as_get_str(invoice.partner_id.id),
                    "codigoEmision": self.as_get_str(invoice.as_emission_type.as_code),
                    "numeroFactura": self.as_get_str(invoice.reversed_entry_id.as_invoice_number),
                    "numeroAutorizacionCuf": self.as_get_str(invoice.reversed_entry_id.as_cuf),
                    "fechaEmisionFactura": self.as_get_str(invoice.reversed_entry_id.as_fecha_emision),
                    "montoTotalOriginal": self.as_get_str(invoice.reversed_entry_id.amount_total),
                    "montoTotalDevuelto": self.as_get_str(invoice.amount_total),
                    "montoDescuentoCreditoDebito": self.as_get_str('0.00'),
                    "montoEfectivoCreditoDebito": self.as_get_str(invoice.as_monto_efectivo_credito_debito),
                    "montoDescuento": self.as_get_str(invoice.as_descuento_adicional),
                    "codigoExcepcion": self.as_get_str(invoice.as_codigo_excepcion),
                    "leyenda": self.as_get_str(invoice.as_leyenda),
                    "usuario": self.as_get_str(invoice.user_id.name),
                    "tipoFacturaDocumento": self.as_get_str(invoice.as_fiscal_document_code.as_code),
                    "codigoDocumentoSector": self.as_get_str(invoice.as_sector_type.as_code),
                    "detalle": line_invoice
                }
                if self.as_idtransaccion:
                    factura['numeroFactura'] = invoice.as_invoice_number
                self.message_post(body = str(json.dumps(factura)), content_subtype='html')  
                has_inv = invoice.as_generate_hash()
                id_invoice = invoice.id
                respuesta = as_utility.as_process_json('NDC',factura,self.env.user.id,invoice.as_codigo_sistema.as_token_ahorasoft,'Crear NDC',hash_inv=has_inv,number=id_invoice)

            if respuesta[0] and respuesta[1]['success']:
                if 'factura' in respuesta[1]:
                    valores = respuesta[1]['factura']
                    invoice.as_cuf = valores['cuf']
                    invoice.as_idtransaccion = valores['idtransaccion']
                    invoice.as_idpedido = valores['idpedido']
                    invoice.as_invoice_number = valores['invoicenumber']
                    invoice.as_cufd = valores['as_cufd']
                    invoice.as_creada = True
                    invoice.as_xml_invoice = base64.encodebytes(valores['xml'].encode('UTF-8'))
                    if automatico:
                        values = self.env['as.siat.catalogos'].search([('as_group', '=', 'EMISION'),('as_code','=','2')],limit=1)
                        glosa = str(values.name)+' AUTOMATICO'
                        self.as_get_package_contingencia(glosa,values)
                    if self.as_existe:
                        invoice.as_state_siat = 'accepted'
                        res_xml = ET.fromstring(valores['xml'].encode('UTF-8'))
                        invoice.as_fecha_factura = res_xml.find('.//cabecera/fechaEmision').text.replace('T',' ').split('.')[0]
                        invoice.as_fecha_emision =res_xml.find('.//cabecera/fechaEmision').text 

                mensaje = as_utility.as_format_success(respuesta[1]['mensaje'])
            else:
                invoice.state="draft"
                mensaje = as_utility.as_format_error(respuesta[1])
            self.message_post(body = str(mensaje), content_subtype='html')  
            self.env.cr.commit()

    def as_generate_hash(self):
        for inv in self:
            self.env.cr.execute("""select max(as_invoice_number) from account_move where as_cont_cafc is null""")
            max_number_invoice = self.env.cr.fetchall()[0][0]
            as_invoice_number =  int(max_number_invoice or 0) + 1  
            value = str(as_invoice_number)+'/'+str(inv.invoice_date)
            return value


    def as_recepciona_invoice(self):
        for invoice in self:
            #emsamblamos lineas
            line_invoice = []
            factura = {
                "idtransaccion": invoice.as_idtransaccion,
               
            }
            self.message_post(body = str(json.dumps(factura)), content_subtype='html')  
            if invoice.move_type == 'out_invoice':
                respuesta = as_utility.as_process_json('Recepción de Factura',factura,self.env.user.id,invoice.as_codigo_sistema.as_token_ahorasoft,'Recepción de Factura')
            elif invoice.move_type == 'out_refund':
                respuesta = as_utility.as_process_json('Recepción de NDC',factura,self.env.user.id,invoice.as_codigo_sistema.as_token_ahorasoft,'Recepción de NDC')
            if respuesta[0] and respuesta[1]['success']:
                if 'factura' in respuesta[1]:
                    valores = respuesta[1]['factura']
                    valor_update = respuesta[1]['value']
                    if valores['codigoEstado'] == '908':
                        invoice.as_state_siat = 'accepted'
                        invoice.as_mensaje_siat = valores['codigoDescripcion']
                        invoice.as_code_siat = valores['codigoRecepcion']
                        invoice.as_cuf = valor_update['cuf']
                        invoice.as_cufd = valor_update['cufd']
                        invoice.as_xml_invoice = base64.encodebytes(valor_update['xml'].encode('UTF-8')) 
                        invoice.as_invoice_number = valor_update['numeroFactura']
                        invoice.as_fecha_factura = valor_update['fecha_factura'].replace('T',' ')
                        invoice.as_fecha_emision = valor_update['fecha_emision']
                        invoice.as_xml_recepcion = base64.encodebytes(respuesta[1]['mensaje'].encode('UTF-8'))
                        mensaje = as_utility.as_format_success(respuesta[1]['mensaje'])
                        self.message_post(body = str(mensaje), content_subtype='html') 
                    else:
                        invoice.as_state_siat = 'rejected'
                        invoice.state="draft"
                        invoice.as_mensaje_siat = valores['codigoDescripcion']
                        invoice.as_xml_recepcion = base64.encodebytes(respuesta[1]['mensaje'].encode('UTF-8'))
                        if type(valores['mensajesList']) == type([]):
                            for error in valores['mensajesList']:
                                mensaje = as_utility.as_format_error(error['codigo']+': '+error['descripcion'])
                                self.message_post(body = str(mensaje), content_subtype='html') 
                        else:
                            mensaje = as_utility.as_format_error(valores['mensajesList']['codigo']+': '+valores['mensajesList']['descripcion'])
                            self.message_post(body = str(mensaje), content_subtype='html') 
            else:
                invoice.state="draft"
                invoice.as_state_siat = 'objected'
                mensaje = as_utility.as_format_error(respuesta[1])
                mensaje2 = respuesta[1]['mensaje']
                invoice.as_mensaje_siat = mensaje2
                self.message_post(body = str(mensaje), content_subtype='html')  
            self.env.cr.commit()


    def as_get_str(self,valor):
        if valor:
            if type(valor) == type(0.0):
                return str('{:.2f}'.format(valor))
            return str(valor)
        else:
            return None

    def as_get_int(self,valor):
        if valor:
            return valor
        else:
            return 0

    def button_cancel(self):
        res = super(as_account_move, self).button_cancel()
        for inv in self:
            if inv.move_type in ('out_invoice','out_refund') and not self.as_contable and not self.as_si_contable:
                inv.as_button_cancel()
                if inv.state == 'cancel':
                    inv.action_move_send()
        return res

    # def as_cancel_move(self):
    #     res = super().as_cancel_move()
    #     if self.move_type in ('out_invoice','out_refund'):
    #         self.as_button_cancel()
    #         if self.state == 'cancel':
    #             self.action_move_send()
    #     return res

    def action_move_send(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template_id = self._find_mail_template()
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        attachment = self.env['ir.attachment'].search([('res_id','=',self.id)])
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'account.move',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
            'default_attachment_ids': attachment.ids,
        }
        # return {
        #     'type': 'ir.actions.act_window',
        #     'view_mode': 'form',
        #     'res_model': 'mail.compose.message',
        #     'views': [(False, 'form')],
        #     'view_id': False,
        #     'target': 'new',
        #     'context': ctx,
        # }
        if self.partner_id.email:
            wiz = Form(self.env['mail.compose.message'].with_context(ctx)).save()
            wiz.action_send_mail()
            self.message_post(body = "<b style='color:green;'>Enviado correo al cliente "+str(self.partner_id.name)+"</b>")
        else:
            self.message_post(body = "<b style='color:red;'>Correo no Enviado "+str(self.partner_id.name)+" no posee email.</b>")

    def action_invoice_sent(self):
        self.action_move_send()

    def _find_mail_template(self, force_confirmation_template=False):
        if self.state == 'cancel':
            template_id = self.env['ir.model.data'].xmlid_to_res_id('as_bo_invoice_client.account_cancel_templateP', raise_if_not_found=False)
        else:
            template_id = self.env['ir.model.data'].xmlid_to_res_id('as_bo_invoice_client.account_move_mail_templateP', raise_if_not_found=False)
        return template_id

    def _get_share_url(self, redirect=False, signup_partner=False, share_token=None):
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

    # def action_move_send(self):
    #     self.ensure_one()
    #     template_id = self._find_mail_template()
    #     lang = self.env.context.get('lang')
    #     template = self.env['mail.template'].browse(template_id)
    #     attachment = self.env['ir.attachment'].search([('res_id','=',self.id)])
    #     if template.lang:
    #         lang = template._render_lang(self.ids)[self.id]
    #     ctx = {
    #         'default_model': 'account.move',
    #         'default_res_id': self.ids[0],
    #         'default_use_template': bool(template_id),
    #         'default_template_id': template_id,
    #         'default_composition_mode': 'comment',
    #         'custom_layout': "mail.mail_notification_paynow",
    #         'force_email': True,
    #         'default_attachment_ids': attachment.ids,
    #     }

    #     wiz = Form(self.env['mail.compose.message'].with_context(ctx)).save()
    #     wiz.action_send_mail()
    #     self.message_post(body = "<b style='color:green;'>Enviado correo al cliente "+str(self.partner_id.name)+"</b>")


    # def _find_mail_template(self, force_confirmation_template=False):
    #     if self.state == 'cancel':
    #         template_id = self.env['ir.model.data'].xmlid_to_res_id('as_bo_invoice_client.account_cancel_templateP', raise_if_not_found=False)
    #     else:
    #         template_id = self.env['ir.model.data'].xmlid_to_res_id('as_bo_invoice_client.account_move_mail_templateP', raise_if_not_found=False)
    #     return template_id

    def as_adjustment_invoice(self):
        self.as_get_name_report()
        if self.as_name_inv:
            name = self.as_name_inv
            # XML
            invoices = self.env['ir.attachment'].search([('name', '=', name and _("%s.pdf") % name)])
            content = self.env.ref('as_bo_invoice_report.as_bo_invoice_report_qr')._render_qweb_pdf(self.id)[0]
            modelo = 'account.move'
            if not invoices:
                self.env['ir.attachment'].create({
                    'name': name and _("%s.pdf") % name,
                    'type': 'binary',
                    'datas': base64.b64encode(content),
                    'res_model': modelo,
                    'res_id': self.id,
                    'mimetype': 'application/pdf',
                })
            else:
                invoices.unlink()
                self.env['ir.attachment'].create({
                    'name': name and _("%s.pdf") % name,
                    'type': 'binary',
                    'datas': base64.b64encode(content),
                    'res_model': modelo,
                    'res_id': self.id,
                    'mimetype': 'application/pdf',
                })
            # PDF
            invoices = self.env['ir.attachment'].search([('name', '=', name and _("%s.xml") % name)])
            content = self.as_xml_invoice
            if not invoices:
                self.env['ir.attachment'].create({
                    'name': name and _("%s.xml") % name,
                    'type': 'binary',
                    'datas': content,
                    'res_model': modelo,
                    'res_id': self.id,
                    'mimetype': 'text/xml'
                })
            else:
                invoices.unlink()
                self.env['ir.attachment'].create({
                    'name': name and _("%s.xml") % name,
                    'type': 'binary',
                    'datas': content,
                    'res_model': modelo,
                    'res_id': self.id,
                    'mimetype': 'text/xml'
                })

    # def write(self, vals):
    #     res = super().write(vals)
    #     for line in self.invoice_line_ids:
    #         line.as_discount_amount = line.as_discount_inversa2()
    #     return res

    def as_generate_invoice_regenerar(self,automatico):
        for invoice in self:
            #emsamblamos lineas
            line_invoice = []
            if invoice.move_type == 'out_invoice':
                for line in invoice.invoice_line_ids:
                    if not line.display_type:
                        vals =  {
                            "actividadEconomica": self.as_get_str(line.product_id.as_actividad.as_code),
                            "codigoProductoSin": self.as_get_str(line.product_id.as_product_service.as_code),
                            "codigoProducto": self.as_get_str(line.product_id.default_code),
                            "descripcion": self.as_get_str(line.name),
                            "cantidad": self.as_get_str(line.quantity),
                            "unidadMedida": self.as_get_str(line.product_uom_id.as_uom.as_code),
                            "precioUnitario": self.as_get_str(line.price_unit),
                            "montoDescuento": self.as_get_int(line.as_discount_amount),
                            "subTotal": self.as_get_str(line.price_total),
                            "numeroSerie": self.as_get_int(line.product_id.as_numero_serie),
                            "numeroImei": self.as_get_int(line.product_id.as_numero_imei),
                        }
                        line_invoice.append(vals)
                factura = {
                    "codigoSucursal": self.as_get_str(invoice.as_branch_office.as_office_number),
                    "codigoPuntoVenta": self.as_get_str(invoice.as_pdv_id.as_code),
                    "nombreRazonSocial": self.as_get_str(invoice.as_razon_social),
                    "codigoTipoDocumentoIdentidad": self.as_get_str(invoice.as_id_code.as_code),
                    "numeroDocumento": self.as_get_str(invoice.as_nit),
                    "complemento": self.as_get_str(invoice.as_complemento_nit),
                    "codigoCliente": self.as_get_str(invoice.partner_id.id),
                    "codigoMetodoPago": self.as_get_str(invoice.as_payment_method.as_code),
                    "codigoEmision": self.as_get_str(invoice.as_emission_type.as_code),
                    "numeroTarjeta": self.as_get_str(invoice.as_numero_tarjeta),
                    "montoTotal": self.as_get_str(invoice.amount_total),
                    "montoTotalSujetoIva": self.as_get_str(invoice.amount_total),
                    "codigoMoneda": self.as_get_str(invoice.currency_id.as_currencysiat.as_code),
                    "tipoCambio": self.as_get_str(invoice.as_tipo_cambio),
                    "montoGiftCard": self.as_get_str(invoice.as_monto_gift),
                    "descuentoAdicional": self.as_get_str(invoice.as_descuento_adicional),
                    "codigoExcepcion": self.as_get_str(invoice.as_codigo_excepcion),
                    "montoTotalMoneda": self.as_get_str(invoice.amount_total),
                    "usuario": self.as_get_str(invoice.user_id.name),
                    "leyenda": self.as_get_str(invoice.as_leyenda),
                    "tipoFacturaDocumento": self.as_get_str(invoice.as_fiscal_document_code.as_code),
                    "codigoDocumentoSector": self.as_get_str(invoice.as_sector_type.as_code),
                    "detalle": line_invoice
                }
                factura['numeroFactura'] = invoice.as_invoice_number
                fecha = str(as_utility.date2timezone(dateutil.parser.parse(str(invoice.as_fecha_factura - relativedelta(hours=4)))))
                invoice.as_fecha_emision = fecha
                factura['fechaEmision'] = invoice.as_fecha_emision
                self.message_post(body = str(json.dumps(factura)), content_subtype='html')  
                has_inv = invoice.as_generate_hash()
                id_invoice = invoice.id
                respuesta = as_utility.as_process_json('Factura',factura,self.env.user.id,invoice.as_codigo_sistema.as_token_ahorasoft,'Crear Factura',hash_inv=has_inv,number=id_invoice)


                if respuesta[0] and respuesta[1]['success']:
                    if 'factura' in respuesta[1]:
                        valores = respuesta[1]['factura']
                        invoice.as_cuf = valores['cuf']
                        invoice.as_idtransaccion = valores['idtransaccion']
                        invoice.as_idpedido = valores['idpedido']
                        invoice.as_invoice_number = valores['invoicenumber']
                        invoice.as_cufd = valores['as_cufd']
                        invoice.as_xml_invoice = base64.encodebytes(valores['xml'].encode('UTF-8'))
                    mensaje = '<b style="color:green">REGENERADO XML DE FACTURA</b> '+as_utility.as_format_success(respuesta[1]['mensaje'])
                else:
                    invoice.state="draft"
                    mensaje = as_utility.as_format_error(respuesta[1])
                self.message_post(body = str(mensaje), content_subtype='html')  
                self.env.cr.commit()

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.as_get_partner()
        return res

class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    sequence_view = fields.Integer(related="sequence")

    def _get_computed_name(self):
        self.ensure_one()

        if not self.product_id:
            return ''

        if self.partner_id.lang:
            product = self.product_id.with_context(lang=self.partner_id.lang)
        else:
            product = self.product_id

        values = []
        if product.name:
            values.append(product.name)
        if self.journal_id.type == 'sale':
            if product.description_sale:
                values.append(product.description_sale)
        elif self.journal_id.type == 'purchase':
            if product.description_purchase:
                values.append(product.description_purchase)
        return '\n'.join(values)

    as_codigo_detalle_transaccion = fields.Char(default="1")

class AccountMoveReversal(models.TransientModel):
    """
    Account move reversal wizard, it cancel an account move by reversing it.
    """
    _inherit = 'account.move.reversal'

    def reverse_moves(self):
        as_date_limit = int(self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_limit_nota'))
        for move_reverse in self.move_ids:
            previous_month = move_reverse.invoice_date + relativedelta(months=as_date_limit)
            ahora = fields.Date.today()
            if previous_month < ahora:
                raise UserError(_("El tiempo de generación de documentos de ajuste, excede los meses permitidos."))
        move = super().reverse_moves()
        return move

    def _prepare_default_reversal(self, move):
        res = super()._prepare_default_reversal(move)
        res['as_fiscal_document_code'] = move.env['as.siat.catalogos'].search([('as_group', '=', 'TIPO_FACTURA'),('as_code','=','3')],limit=1).id
        res['as_sector_type'] = move.env['as.siat.catalogos'].search([('as_group', '=', 'DOCUMENTO_SECTOR'),('as_code','=','24')],limit=1).id
        res['as_invoice_number'] = ''
        res['as_cuf'] = ''
        res['as_creada'] = False
    
        if move.as_descuento_adicional > 0:
            descuento = move.as_descuento_adicional/(sum(move.invoice_line_ids.mapped('quantity')))
            res['as_factor'] = descuento


        return res


class aS_sale_order(models.Model):
    """ Esta clase agrega los campos razon social y nit a sale_order """
    _inherit = 'sale.order'

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        res["as_razon_social"] = self.partner_id.as_razon_social
        res["as_nit"] = self.partner_id.vat
        return res

class AsPaymentMultiLine(models.Model):
    _inherit = 'as.payment.multi.line'
    
    as_numero_documento = fields.Char(string="Nro de factura", compute='_compute_num_fact')

    def _compute_num_fact(self):
        for rec in self:
            rec.as_numero_documento = rec.as_invoice_id.as_invoice_number