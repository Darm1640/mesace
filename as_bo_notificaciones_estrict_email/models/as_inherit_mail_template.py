# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime, timedelta
from time import mktime
from odoo.exceptions import UserError, RedirectWarning, ValidationError, MissingError
import time
from odoo import api, fields, models, _
from datetime import datetime, timedelta

class clase_mail_template(models.Model):
    _inherit = 'mail.template'
    
    as_self_id = fields.Char('ID', compute='_id_creado', readonly=True)
    
    def _id_creado(self):
        for x in self:
            if x.id:
                self.as_self_id = x.id
        return self.as_self_id
    