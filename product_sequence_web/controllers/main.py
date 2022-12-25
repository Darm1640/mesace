# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


import logging
from datetime import datetime

from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.http import request

_logger = logging.getLogger(__name__)

    
class WebsiteSale(http.Controller):

    def _get_search_order(self, post):
        # OrderBy will be parsed in orm and so no direct sql injection
        # id is added to be sure that order is a unique sort key
        order = post.get('order') or 'website_sequence ASC'
        return 'is_published desc, %s, id desc' % order


    