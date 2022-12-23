
from odoo import models, fields, api, _
from datetime import datetime
import time
from dateutil.relativedelta import relativedelta
import calendar
from datetime import datetime, timedelta
from odoo.exceptions import UserError, RedirectWarning, ValidationError, MissingError

class EmployeeBonus(models.Model):
    _name = 'as.generate.bonus.discount'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Employee Bonus discount'

    name = fields.Char(string="Titulo", required=True)
    as_tipo = fields.Selection([
        ('bonus', 'Abono'),
        ('discount', 'Descuento'),
       ], 'Tipo', 
        default='bonus')
    state = fields.Selection([
        ('draft', 'BORRADOR'),
        ('done', 'ASIGNADO'),
        ('close', 'PAGADO'),
        ('cancel', 'CANCELADO'),
       ], 'Estado', 
        default='draft')
    as_bonus_discount_ids = fields.One2many( 'as.employee.bonus', 'as_generator',string='Empleados',  required=True, )
    as_summary_ids = fields.One2many( 'as.bonus.discount.line', 'as_generator',string='Empleados',  required=True, )
    as_type = fields.Selection([('anticipo', 'Anticipo'),('prestamos', 'Prestamos'),('quincena', 'Aguinaldo'),('Desembolso', 'Desembolso'),('Diferencia', 'Diferencia'),('quiquenio', 'Anticipo Quinquenio'),('dividendo', 'Anticipo Dividendos'),('individual', 'Anticipo Individual'),('multi_pago', 'Multipago Quincena')], string="Tipo Documento para Tesoreria", required=True)
    as_cantidad = fields.Integer(string="Cantidad")
    as_date_start = fields.Date('Fecha Inicio')
    as_action_pay = fields.Boolean('Seleccionar todo')
    as_caja_line_id = fields.Many2many('as.payment.multi', string="Linea de Caja")
    as_asiento_count = fields.Integer(compute="_invoice_count")
    
    def as_get_bonus_cancel(self):
        for order in self:
            order.state = 'cancel'
            for line in order.as_summary_ids:
                line.state = 'cancel'
            for move in order.as_caja_line_id:
                move.state='cancel'
                if move.account_move_id:
                    move.account_move_id.as_cancel_move()
            for line_discount in order.as_bonus_discount_ids:
                line_discount.state = 'cancel'


    
    @api.onchange('as_summary_ids')
    def obtener_numeracion(self):
        total = self.as_summary_ids
        cont = 1
        for res in total:
            res.as_sequencia = cont
            cont+=1
    
    def _invoice_count(self):
        for rec in self:
            rec.ensure_one()
            cajas = []
            for mov in self.as_caja_line_id:
                cajas.append(mov.account_move_id.id)
            rec.as_asiento_count = len(cajas)

    def action_view_asiento(self):
        self.ensure_one()
        action_pickings = self.env.ref('account.action_move_journal_line')
        action = action_pickings.read()[0]
        action['context'] = {}
        cajas = []
        for mov in self.as_caja_line_id:
            cajas.append(mov.account_move_id.id)
        action['domain'] = [('id', 'in', cajas)]
        return action

    @api.onchange('as_action_pay')
    def as_get_selector1(self):
        for emp in self:
            for line in emp.as_summary_ids:
                line.as_pagar = emp.as_action_pay

    @api.onchange('as_cantidad')
    def as_get_selector(self):
        for emp in self:
            for line in emp.as_summary_ids:
                line.as_cantidad = emp.as_cantidad
                line.as_get_date_end()

    @api.onchange('as_date_start')
    def as_get_selector2(self):
        for emp in self:
            for line in emp.as_summary_ids:
                line.as_date_start = emp.as_date_start
                line.as_get_date_end()

    def get_action_employee(self):
        
            return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'as.hr.employees',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': {'default_as_generador_id': self.id },
            }
    
    def as_get_autorizar(self):
        for emp in self:
            for line in emp.as_bonus_discount_ids:
                line.get_confirm()
                line.get_apprv_dept_manager()
                line.get_apprv_hr_manager()

    def as_get_bonus_payment(self):
        lineas = len(self.as_bonus_discount_ids)
        lineas_aprobadas = len(self.as_bonus_discount_ids.filtered(lambda line: line.state == 'dapproved_hr_manager'))
        if lineas != lineas_aprobadas:
            raise UserError(_("Todas las lineas de Aplicación en nomina deben estar aprobadas por HR"))
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'as.payment.bonus',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': {'default_as_generador_id': self.id },
            }

    def as_get_bonus_payroll(self):
        for gene in self:
            for gene_line in gene.as_summary_ids:
                cont = 0
                for month in range(0,gene_line.as_cantidad):
                    dates = gene_line.as_get_date(gene_line.as_date_start,cont)
                    self.env['as.employee.bonus'].create({
                        'employee_id': gene_line.as_employee_id.id,
                        'job_id': gene_line.as_employee_id.job_id.id,
                        'reason_id': gene_line.reason_id.id,
                        'department_id': gene_line.as_employee_id.department_id.id,
                        'bonus_amount': gene_line.as_bonus_amount,
                        'currency_id': gene_line.currency_id.id,
                        'notes': gene_line.as_generator.name,
                        'as_date_start': dates[0],
                        'as_date_end': dates[1],
                        'as_tipo': gene.as_tipo,
                        'as_modalidad': gene_line.as_modalidad,
                        'as_generator': gene.id,
                    })
                    cont+=1
                gene_line.state = 'done'
            cantidad = len(gene.as_summary_ids)
            cantidad2 = len(gene.as_summary_ids.filtered(lambda r: r.state == 'done'))
            if cantidad == cantidad2:
                gene.state = 'done'

    def as_get_report_pdf_in_close(self):
        return self.env.ref('as_bo_hr_bonus_discount.as_reporte_pdf_quincena').report_action(self)
    
    def as_get_report_excel_in_close(self):
        return self.env.ref('as_bo_hr_bonus_discount.as_bo_report_quincena').report_action(self)

    def as_obtener_fecha(self):
        fecha = (datetime.now() - timedelta(hours=4)).strftime('%d/%m/%Y')
        return fecha
    
    def obtener_bono_total(self):
        contador = 0
        abono_total = 0.0
        if self.as_summary_ids:
            for linea_caja in self.as_summary_ids:
                if linea_caja.as_bonus_amount:
                    abono_total+=linea_caja.as_bonus_amount
        return abono_total
    
    def obtener_registros(self):
        contador = 0
        abono_total = 0.0
        if self.as_summary_ids:
            for linea_caja in self.as_summary_ids:
                if linea_caja.as_bonus_amount:
                    abono_total+=linea_caja.as_bonus_amount
                contador+=1
        return contador
    
        
    
class AsBonusDiscountLine(models.Model):
    _name = 'as.bonus.discount.line'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Resumen de Programación de descuentos y abonos'

    @api.model
    def get_currency(self):
        return self.env.user.company_id.currency_id

    as_pagar = fields.Boolean('Pagar')
    as_employee_id = fields.Many2one( 'hr.employee', string='Empleados',  required=True, )
    as_cantidad = fields.Integer(string="Cantidad")
    as_date_start = fields.Date('Fecha Inicio')
    as_date_end = fields.Date('Fecha Fin')
    state = fields.Selection([
        ('draft', 'BORRADOR'),
        ('close', 'PAGADO'),
        ('done', 'ASIGNADO'),
        ('cancel', 'CANCELADO'),
       ], 'Estado', 
        default='draft')
    as_modalidad = fields.Selection([
        ('manual', 'Manual'),
        ('auto', 'Automatico'),
       ], 'Tipo', 
        default='manual')
    as_bonus_amount = fields.Float(
        string='Importe de la bonificación',
        required=True,
    )
    reason_id = fields.Many2one(
        'as.bonus.reason', 
        string='Motivo de bonificación',required=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=get_currency,
        string='Moneda',
    )
    as_generator = fields.Many2one(
        'as.generate.bonus.discount', 
        'Generador', 
        required=True,
    )
    as_sequencia = fields.Integer(string='N°', help="Otorga la secuencia")


    @api.onchange('as_cantidad','as_date_start')
    def as_get_date_end(self):
        for gene in self:
            if gene.as_date_start:
                gene.as_date_end = gene.as_date_start + relativedelta(months=gene.as_cantidad)
                gene.as_date_end = gene.as_date_end - relativedelta(days=1)


    def as_get_date(self,date,cont):
        date_result = date + relativedelta(months=cont)
        mes = date_result.strftime('%m')
        anio = date_result.strftime('%Y')
        periodo2 = calendar.monthrange(int(anio),int(mes))
        date_start = anio+'-'+mes+'-'+'01'
        date_end = anio+'-'+mes+'-'+str(periodo2[1])
        return date_start,date_end
