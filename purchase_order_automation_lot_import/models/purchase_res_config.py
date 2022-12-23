# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ResConfigSettings(models.TransientModel): 
	_inherit = 'res.config.settings'

	import_lot_serial  = fields.Boolean(string="Import Lot/Serial and Picking Qty Done")

	@api.model
	def get_values(self):
		res = super(ResConfigSettings, self).get_values()
		config_parameter = self.env['ir.config_parameter'].sudo()
		import_lot_serial = config_parameter.get_param('purchase_order_automation_lot_import.import_lot_serial')
		res.update(import_lot_serial=import_lot_serial)
		return res

	def set_values(self):
		res = super(ResConfigSettings, self).set_values()
		self.env['ir.config_parameter'].sudo().set_param('purchase_order_automation_lot_import.import_lot_serial', self.import_lot_serial)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: