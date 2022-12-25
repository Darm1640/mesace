from . import controllers
from . import models

from odoo import api, SUPERUSER_ID
def _update_partner_response(env):
	env.cr.execute("""
		UPDATE account_move set email_response='accepted'
		WHERE ei_is_valid IS TRUE 
			AND (ei_issue_date < (NOW() AT TIME ZONE 'UTC' - interval '3 days')::DATE)
		""")

def _account_post_init(cr, registry):
	env = api.Environment(cr, SUPERUSER_ID, {})
	_update_partner_response(env)