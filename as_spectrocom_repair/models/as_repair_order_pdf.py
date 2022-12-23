# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class as_repair_pdf(models.Model):
    _inherit = 'repair.order'

    fecha_confirmar=fields.Date(string="Fecha Inicial")
    fecha_finalizar=fields.Date(string="Fecha final")
    
    def action_validate(self):
        res = super(as_repair_pdf, self).action_validate() 
        self.fecha_confirmar= fields.Date.context_today(self)
        return res
    
    def action_repair_end(self):
        """ Writes repair order state to 'To be invoiced' if invoice method is
        After repair else state is set to 'Ready'.
        @return: True
        """
        self.fecha_finalizar= fields.Date.context_today(self)
        if self.filtered(lambda repair: repair.state != 'under_repair'):
            raise UserError(_("Repair must be under repair in order to end reparation."))
        for repair in self:
            repair.write({'repaired': True})
            vals = {'state': 'done'}
            vals['move_id'] = repair.action_repair_done().get(repair.id)
            if not repair.invoice_id and repair.invoice_method == 'after_repair':
                vals['state'] = '2binvoiced'
            repair.write(vals)
        return True