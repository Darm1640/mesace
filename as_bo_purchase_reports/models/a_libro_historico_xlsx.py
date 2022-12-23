# # -*- coding: utf-8 -*-

import datetime
from datetime import datetime
import pytz
from odoo import models,fields
from datetime import datetime, timedelta
from time import mktime

class a_libro_historico_xlsx(models.AbstractModel):
    _name = 'as.libro.historico.compras'