# -*- coding: utf-8 -*-
from  odoo import models, fields, api, _
import logging
import base64
import os, zipfile
from io import BytesIO
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)




class HospitalRIPS(models.Model):
	_name = "hospital.rips"
	_description = "Hospital RIPS"

	name = fields.Char(string="N° Radicado", default="/", required=True, readonly=True)
	state = fields.Selection(selection=[('draft',"Draft"),('confirmed','Confirmed'),('done',"Done"),('cancel','Cancel')], 
		readonly=True, string="Status", default='draft')
	date_from = fields.Date(string="Date From", required=True, copy=False,
		readonly=True, states={'draft':[('readonly',False)]})
	date_to = fields.Date(string="Date To", required=True, copy=False,
		readonly=True, states={'draft':[('readonly',False)]})

	partner_id = fields.Many2one('res.partner', string="Cliente", required=True,
		readonly=True, states={'draft':[('readonly',False)]})
	team = fields.Many2one('crm.team', string="Regional", required=True,
		readonly=True, states={'draft':[('readonly',False)]})

	ratication_date = fields.Date(string="Radication Date", readonly=True) 
	rips_directo = fields.Boolean(string="RIPS Directo", help='Esta opción permite generar Rips sin haber facturado atenciones.',
		readonly=True, states={'draft':[('readonly',False)]})
	contrato_id = fields.Many2one('doctor.contract.insurer', string='Contrato',
		required=True, help='Contrato por el que se atiende al cliente.',
		readonly=True, states={'draft':[('readonly',False)]})

	invoices_ids = fields.Many2many('account.move', 'account_move_hospital_rips_rel', 'move_id', 'rips_id', string="Invoices", copy=False,
		domain="[('move_type', '=', 'out_invoice'),('state','!=','draft')]")
	invoice_count = fields.Integer(string="Invoice Count", compute="_invoice_values", store=True)
	amount_residual = fields.Float(string="Amount Due", compute="_invoice_values", store=True)
	amount_total = fields.Float(string="Amount Total", compute="_invoice_values", store=True)

	# attachment_rips_ids = fields.Many2many('ir.attachment', 'attachment_fo_company_rel', 'attch_id', 'rips_id', string='RIPS', copy=False)

	tipo_afiliacion = fields.Selection(selection=[
        ('contributory', 'Contributivo'), 
        ('subsidized', 'Subsidiado'), 
        ('linked', 'Vinculado')], string="Tipo De Regimen", required=True,
        readonly=True, states={'draft':[('readonly',False)]})

	archive_zip = fields.Binary(string="Archive ZIP")
	archive_zip_name = fields.Char(string="Archive ZIP Name")

	company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company,
		readonly=True, states={'draft':[('readonly',False)]})
	cea_code = fields.Char(related="company_id.cod_prestadorservicio", 
		store=True, string="Código Prestador Servicio", required=True)

	@api.depends('invoices_ids')
	def _invoice_values(self):
		for rops in self:
			rops.invoice_count = len(rops.invoices_ids.ids)
			rops.amount_residual = sum(i.amount_residual for i in rops.invoices_ids)
			rops.amount_total = sum(i.amount_total for i in rops.invoices_ids)

	def action_generate(self):
		self.invoices_ids = False
		invoices = self.env['account.move'].search([
				('rip_id','=',False),
				('team_id','=',self.team.id),
				('company_id','=',self.company_id.id),
				('invoice_date','>=',self.date_from),
				('invoice_date','<=',self.date_to),
				('state','in',['posted','validate']),
				('move_type','in',['out_invoice']),
				('partner_id','=', self.partner_id.id),
				('patient_id.tipo_afiliacion', '=', self.tipo_afiliacion)])
		self.invoices_ids = [(6,0, invoices.ids or [])]

	def action_confirm(self):
		if self.name == '/':
			code = self.env['ir.sequence'].next_by_code("account.rips")
			self.write({'name': code, 
					'state': 'confirmed', 
					'ratication_date': fields.Date.context_today(self)})

	def action_done(self):
		self._cr.execute('UPDATE account_move SET rip_id=%s WHERE id IN %s', (self.id,tuple(self.invoices_ids.ids)))
		self.write({'state': 'done'})

	def action_cancel(self):
		self.write({'state': 'cancel'})

	def action_generate_zip(self):
		files = self._generate_files()
		zipfiles = self.make_zip(files)
		zipfiles.seek(0)
		self.archive_zip = base64.b64encode(zipfiles.read())
		self.archive_zip_name = f"{self.name}.zip"

	def make_zip(self, files):
		output = BytesIO()
		with zipfile.ZipFile(output, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
			for f in files:
				zf.writestr(f[0], f[1])
		return output

	def _generate_files(self):
		files = []
		dic = {
			'US': [[],""],
			'AF': "",
			'AT': "",
			'CT': {'US':0,'AF':0,'AT':0}
		}
		tipo_afiliacion = {
			'contributory': '1',
			'subsidized': '2',
			'linked': '3'
		}
		dic['CT']['AF'] = len(self.invoices_ids.ids)

		for inv in self.invoices_ids:
			partner = inv.partner_id
			patient = inv.patient_id
			company = self.company_id

			tipo_doc = (patient.tdoc or "").upper()
			numero_id = patient.vat
			#codigo_entidad = patient.eps.entity_code
			codigo_entidad = ""
			if tipo_afiliacion == "contributory":
				codigo_entidad = "ESSC207"
			else:
				codigo_entidad = "ESS207"
			tipo_usuario = tipo_afiliacion[patient.tipo_afiliacion]
			primer_apellido = (patient.lastname or "").upper()
			segundo_apellido = (patient.lastname2 or "").upper()
			primer_nombre = (patient.firstname or "").upper()
			segundo_nombre  = (patient.othernames or "").upper()
			edad = relativedelta(inv.invoice_date, patient.birthday)
			edad = edad.years
			uom_edad = 1
			sexo = patient.sexo
			cod_dpto = patient.state_id.code
			cod_municipio = patient.city_id.cod_m
			zona_residencia = patient.zona
			if patient.id not in dic['US'][0]:
				dic['US'][1] += "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" %(
					tipo_doc,
					numero_id,
					codigo_entidad,
					tipo_usuario,
					primer_apellido,
					segundo_apellido,
					primer_nombre,
					segundo_nombre,
					edad,
					uom_edad,
					sexo,
					cod_dpto,
					cod_municipio,
					zona_residencia)
				dic['CT']['US'] += 1
			dic["US"][0].append(patient.id)
			numero_factura =  inv.name
			fecha_expedito = (inv.invoice_date).strftime('%d/%m/%Y') 
			fecha_inicio = fecha_expedito
			fecha_fin = fecha_expedito
			nombre_entidad_admin = patient.eps.name
			numero_contrato = self.contrato_id.contract_code
			plan_beneficio = "POS-S"
			nro_poliza = ""
			copago = 0
			comision = 0
			descuento = 0
			tipo_servicio = "1"
			valor_neto = '{:.2f}'.format(inv.ei_amount_total_no_withholding)
			dic['AF'] += "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" %(
						company.partner_id.identification_document,
						company.partner_id.name,
						"NI",
						company.partner_id.identification_document,
						numero_factura,
						fecha_expedito,
						fecha_inicio,
						fecha_fin,
						codigo_entidad,
						nombre_entidad_admin,
						numero_contrato,
						plan_beneficio,
						nro_poliza,
						copago,
						comision,
						descuento,
						valor_neto)
			for line in inv.invoice_line_ids:
				taxes = line.tax_ids.filtered(lambda t: t.edi_tax_id.code == '01')
				valor_iva = 0.0
				valor_total = 0.0
				reemplazar = "!#$%^&*()-.,_"
				if taxes:
					taxes_total = taxes.compute_all(line.price_unit,
							quantity=line.quantity, currency=inv.currency_id, product=line.product_id, partner=partner, is_refund=inv.move_type in ('out_refund','in_refund'))
					taxes_unit = taxes.compute_all(line.price_unit,
							quantity=1.0, currency=inv.currency_id, product=line.product_id, partner=partner, is_refund=inv.move_type in ('out_refund','in_refund'))
					valor_iva = taxes_unit['taxes'][0]['amount']
					valor_total = taxes_total['total_included']
				# quite un %s
				dic['AT'] += "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" %(
					numero_factura,
					company.partner_id.identification_document,
					tipo_doc,
					numero_id,
					inv.authorization_number,
					tipo_servicio,
					line.product_id.default_code,
					(line.product_id.name).replace('.','').replace(',','').replace('(','').replace(')','').replace('#','').replace('-',''),
					'{:.0f}'.format(line.quantity),
					'{:.2f}'.format(line.price_unit),
					#'{:.2f}'.format(valor_iva),
					'{:.2f}'.format(valor_total)
					)
			dic['CT']['AT'] += len(inv.invoice_line_ids)

		type_ct = ""
		for k,v in dic['CT'].items():
			type_ct += "%s,%s,%s,%s\n" %(
				company.partner_id.identification_document,
				(self.ratication_date).strftime('%d/%m/%Y'),
				"%s%s" %(k,self.name),
				v
				)
		_logger.info('\n\n %r \n\n', type_ct)
		# for k,v in dic.items():
		code = self.name == '/' and '0' or self.name
		file_txt = self.with_context(lines=dic["US"][1][0:-1]).document_print('txt')
		files.append((f'US{code}.txt',file_txt))
		file_txt = self.with_context(lines=dic["AF"][0:-1]).document_print('txt')
		files.append((f'AF{code}.txt',file_txt))
		file_txt = self.with_context(lines=dic["AT"][0:-1]).document_print('txt')
		files.append((f'AT{code}.txt',file_txt))
		file_txt = self.with_context(lines=type_ct[0:-1]).document_print('txt')
		files.append((f'CT{code}.txt',file_txt))

		return files

	def document_print(self, function_name=False):
		output = BytesIO()
		output = self._init_buffer(output, function_name)
		output.seek(0)
		return output.read()

	def _generate_txt(self, output, function_name):
		content = getattr(self, "_get_datas_report_%s" %function_name)(output)
		output.write(content.encode())

	def _get_datas_report_txt(self, output):
		lines = self._context.get('lines') or ""
		return lines

	def _init_buffer(self, output, function_name='xlsx'):
		getattr(self, '_generate_%s' %(function_name or ''))(output, function_name)
		return output

	def action_view_invoice(self):
		return True