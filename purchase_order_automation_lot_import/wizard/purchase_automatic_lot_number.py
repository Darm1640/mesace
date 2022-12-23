from odoo import api, fields, models, _
from xlrd import open_workbook
import xlrd
import base64
import csv
from io import BytesIO,StringIO
import io
from odoo.exceptions import UserError

class purchaseAuto(models.TransientModel):
	_name = "purchase.auto"
	_description = "Import Lot and Serial Number"


	file = fields.Binary("Upload File")
	file_name = fields.Char(string="File Name")

	select = fields.Selection([('csv', 'CSV'),('xls', 'XLS')], string="File Type", default='xls')

	def action_import_lot(self):
		purchase_orders = self.env['purchase.order'].browse(self._context.get('active_ids', []))
		purchase_orders.button_confirm()
		import_lot_serial = self.env['ir.config_parameter'].sudo().get_param('purchase_order_automation_lot_import.import_lot_serial')

		file_name = str(self.file_name)
		ext = ['csv','xls']
		extension = file_name.split('.')[1]
		if self.file:
			if extension not in ext or extension not in ext:
				raise UserError(_('Please upload only xls or csv file...!'))

		if import_lot_serial:
			if self.select=='xls':
				if extension !=  'xls':
					raise UserError(_('Please upload xls file...!'))

				doc=BytesIO()
				doc.write(base64.decodestring(self.file))
				workbook=xlrd.open_workbook(file_contents=doc.getvalue())
				sheet = workbook.sheet_by_index(0)

				move_ids = [picking.mapped('move_ids_without_package') for picking in purchase_orders.picking_ids][0]
				
				for move in move_ids:
					if move.product_id.tracking=='serial':
						move_lines_commands =[]
						
						count = 0
						for row_index in range(1, sheet.nrows):
							if move.product_id.name == sheet.cell(row_index,0).value and count <= move.product_uom_qty:
								location_dest = move.location_dest_id._get_putaway_strategy(move.product_id) or move.location_dest_id
								lot_name = sheet.cell(row_index,1).value
								move_lines_commands.append((0, 0, {
									'lot_name': lot_name,
									'qty_done': 1,
									'product_id': move.product_id.id,
									'product_uom_id': move.product_id.uom_id.id,
									'location_id': move.location_id.id,
									'location_dest_id': location_dest.id,
									'picking_id': move.picking_id.id,
								}))
								count += 1
						move.write({'move_line_ids': move_lines_commands})

					elif move.product_id.tracking=='lot':
						move_lines_commands2 = []
						for row_index in range(1, sheet.nrows):
							if move.product_id.name == sheet.cell(row_index,0).value:
								location_dest = move.location_dest_id._get_putaway_strategy(move.product_id) or move.location_dest_id
								lot_name = sheet.cell(row_index,1).value
								move_lines_commands2.append((0, 0, {
									'lot_name': lot_name,
									'qty_done': move.product_uom_qty,
									'product_id': move.product_id.id,
									'product_uom_id': move.product_id.uom_id.id,
									'location_id': move.location_id.id,
									'location_dest_id': location_dest.id,
									'picking_id': move.picking_id.id,
								}))
								move.write({'move_line_ids': move_lines_commands2})
								break

			elif self.select=='csv':
				if extension !=  'csv':
					raise UserError(_('Please upload csv file...!'))

				file_input = io.StringIO(base64.b64decode(self.file).decode("utf-8"))

				file_input.seek(0)
				csv_reader = csv.reader(file_input, delimiter=',')  

				file_reader = []
				file_reader.extend(csv_reader)

				move_ids =  [picking.mapped('move_ids_without_package') for picking in purchase_orders.picking_ids][0]
				for move in move_ids:
					if move.product_id.tracking=='serial':
						move_lines_commands3 =[]

						count = 0
						for each in file_reader:
							if move.product_id.name == each[0] and count <= move.product_uom_qty:
								location_dest = move.location_dest_id._get_putaway_strategy(move.product_id) or move.location_dest_id
								lot_name = each[1]
								move_lines_commands3.append((0, 0, {
									'lot_name': lot_name,
									'qty_done': 1,
									'product_id': move.product_id.id,
									'product_uom_id': move.product_id.uom_id.id,
									'location_id': move.location_id.id,
									'location_dest_id': location_dest.id,
									'picking_id': move.picking_id.id,
								}))
								count += 1
						move.write({'move_line_ids': move_lines_commands3})

					elif move.product_id.tracking=='lot':
						move_lines_commands4 = []
						for each in file_reader:
							if move.product_id.name == each[0]:
								location_dest = move.location_dest_id._get_putaway_strategy(move.product_id) or move.location_dest_id
								lot_name = each[1]
								move_lines_commands4.append((0, 0, {
									'lot_name': lot_name,
									'qty_done': move.product_uom_qty,
									'product_id': move.product_id.id,
									'product_uom_id': move.product_id.uom_id.id,
									'location_id': move.location_id.id,
									'location_dest_id': location_dest.id,
									'picking_id': move.picking_id.id,
								}))

								move.write({'move_line_ids': move_lines_commands4})
								break