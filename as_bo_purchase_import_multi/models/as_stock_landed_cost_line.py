from odoo import SUPERUSER_ID
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError, MissingError
#Generacion del QR
import qrcode

from odoo import api, fields, models, tools, _
from odoo.addons.stock_landed_costs.models import product
from odoo.exceptions import UserError, RedirectWarning, ValidationError
# import odoo.addons.decimal_precision as dp
from odoo.tools.float_utils import float_round, float_is_zero
import logging
_logger = logging.getLogger(__name__)

class LandedCostLine(models.Model):
    _inherit = 'stock.landed.cost.lines'

    as_cost_price = fields.Float(string='Costo Estimado')

    # @api.multi
    def cancel_fac_cost(self):
        for datos in self:
            datos.as_invoice_id.action_invoice_cancel()
            datos.as_invoice_id = False
            datos.unlink()
            
    #crear factura de importacion
    def action_create_invoice(self):
        """Create the invoice associated to the PO.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoice_vals_list = []
        for order in self:
            order = order.with_company(order.env.user.company_id)
            # Invoice values.
            invoice_vals = order._prepare_invoice()
            # Invoice line values (keep only necessary sections).
          
            if not float_is_zero(order.price_unit, precision_digits=precision):
                invoice_vals['invoice_line_ids'].append((0, 0, order._prepare_account_move_line()))
            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise UserError(_('There is no invoiceable line. If a product has a control policy based on received quantity, please make sure that a quantity has been received.'))

        # 3) Create invoices.
        moves = self.env['account.move']
        AccountMove = self.env['account.move'].with_context(default_move_type='in_invoice')
        for vals in invoice_vals_list:
            moves |= AccountMove.with_company(vals['company_id']).create(vals)
            # factura_obj.action_invoice_open()
        self.as_invoice_id = moves.id
        self.cost_id._verifica_calculo()
        moves.action_post()
        return moves

    def _prepare_invoice(self):
        """Prepare the dict of values to create the new invoice for a purchase order.
        """
        self.ensure_one()
        move_type = self._context.get('default_move_type', 'in_invoice')
        # journal = self.env['account.move'].with_context(default_move_type=move_type)._get_default_journal()
        journal = self.as_journal_id
        if not journal:
            raise UserError(_('No ha seleccionado un diario.'))
        if self.as_nit == False and self.as_facturado == True:
            raise UserError(_('Por favor ingrese nit') )
        if self.as_razon_social == False and self.as_facturado == True:
            raise UserError(_('Por favor ingrese razon social') )
        if self.as_codigo_control == False and self.as_facturado == True:
            raise UserError(_('Por favor ingrese codigo de control') )
        if self.as_tipo_factura == False and self.as_facturado == True:
            raise UserError(_('Por favor ingrese tipo de factura') )
        if self.as_numero_autorizacion == False and self.as_facturado == True:
            raise UserError(_('Por favor ingrese numero de autorizacion') )
        if self.as_numero_factura == False and self.as_facturado == True:
            raise UserError(_('Por favor ingrese numero de factura') )
        if self.as_facturado == True:
            tipo_factura='Factura'
        else:
            tipo_factura='Prefactura/Recibo'
        invoice_vals = {
            'move_type': move_type,
            'journal_id':journal.id,
            'currency_id': self.env.user.company_id.currency_id.id,
            'invoice_user_id': self.env.user.id,
            'invoice_origin': self.cost_id.name,
            'invoice_line_ids': [],
            'company_id': self.env.user.company_id.id,
            'partner_id': self.as_supplier_costo.id,
            'date_invoice' : self.as_fecha_factura,
            'as_tipo_documento' : tipo_factura,
            'as_nit' : self.as_nit,
            'as_razon_social' : self.as_razon_social,
            'as_numero_factura_compra' : self.as_numero_factura,
            'as_codigo_control_compra' : self.as_codigo_control,
            'as_numero_autorizacion_compra' : self.as_numero_autorizacion,
            'as_tipo_factura' : self.as_tipo_factura.id,
            'as_impuesto_especifico' : self.as_monto_excento,
            # 'as_tipo_retencion' : self.as_tipo_retencion.id,
            'invoice_origin' : self.cost_id.name,
            # 'state':'posted',
            'invoice_date':self.as_fecha_factura,
            'as_contable':True,
        }
        return invoice_vals

class AdjustmentResumenLines(models.Model):
    _inherit = 'as.stock.valuation.summary.lines'

    as_qty = fields.Float(string='Cant. Recibida')
