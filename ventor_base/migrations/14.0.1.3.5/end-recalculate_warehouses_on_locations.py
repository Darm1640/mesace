# Odoo:
from odoo import SUPERUSER_ID, _, api


def migrate(cr, version):
    """Update warehouse_id for all locations"""

    env = api.Environment(cr, SUPERUSER_ID, {})
    all_locations = env['stock.location'].with_context(active_test=False).search([
            ('warehouse_id', '=', False),
            ])
    all_locations.action_update_warehouse()
