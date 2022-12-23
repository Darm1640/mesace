from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from werkzeug.urls import url_encode
import time
import datetime
from datetime import datetime, timedelta, date
from time import mktime
from dateutil.relativedelta import relativedelta

class as_sale_order(models.Model):
    _inherit = 'sale.order'


    def action_confirm(self):
        res = super(as_sale_order, self).action_confirm()
        valor = 0
        if self.opportunity_id != False:
            id_crm=self.env['crm.lead'].sudo().search([('id', '=', self.opportunity_id.id)])
            if id_crm:
                if self.state == 'sale':
                    if id_crm.stage_id != 4:
                        id_crm.stage_id = 4  
        return res
