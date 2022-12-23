# -*- coding: utf-8 -*-

from odoo import models, fields, api

class stock_location(models.Model):
    _inherit = 'stock.location'

    _qty_fields = (
        'qty_available',
        'virtual_available',
        'incoming_qty',
        'outgoing_qty',
        'price_unit',
    )

    def _compute_qty_available(self):
        """
        Compute method for qty_available, virtual_available, incoming_qty, outgoing_qty

        The method depends on current context: which product comes (it might be either a product
        variant or a product template)
        """
        self.qty_available = 0
        self.virtual_available = 0
        self.incoming_qty = 0
        self.outgoing_qty = 0
        self.price_unit = 0
        product_id = self._context.get('product_id', False)
        template_id = self._context.get('template_id', False)
        if product_id or template_id:
            source = self.env['product.{}'.format('product' if product_id else 'template')].browse(
                product_id if product_id else template_id
            )
            for field in self._qty_fields:
                for rec in self:
                    if field =='price_unit':
                        if product_id:
                            query= 'pp.id ='+str(source.id)+' and sq.location_id='+str(rec.id)
                        else:
                            query= 'pp.product_tmpl_id ='+str(source.id)+'  and sq.location_id='+str(rec.id)
                        self.env.cr.execute('''
                        SELECT
                        sq.unit_cost
                        FROM as_valuation_location sq
                        INNER JOIN stock_location sl on sq.location_id=sl.id
                        INNER JOIN product_product pp on sq.product_id=pp.id
                        WHERE 
                        '''+query+'''order by sq.create_date desc''')
                        costo = [i for i in self.env.cr.fetchall()]
                        if costo:
                            costo_value=float(costo[0][0])
                        else:
                            costo_value=0.00
                        rec.price_unit=costo_value
                        rec.update({'price_unit': costo_value})
                    else:
                        rec.__setattr__(field, source.with_context(location=[rec.id]).__getattribute__(field))


    qty_available = fields.Float(
        string='Quantity On Hand',
        compute="_compute_qty_available",
        help='Quantity On Hand for product specified on the context',
    )
    virtual_available = fields.Float(
        string='Forecast Quantity',
        compute="_compute_qty_available",
        help='Forecast Quantity for product specified on the context',
    )
    incoming_qty = fields.Float(
        string='Incoming',
        compute="_compute_qty_available",
        help='Incoming for product specified on the context',
    )
    outgoing_qty = fields.Float(
        string='Outgoing',
        compute="_compute_qty_available",
        help='Outgoing for product specified on the context',
    )
    price_unit = fields.Float(
        string='Costo',
        compute="_compute_qty_available",
        help='Outgoing for product specified on the context',
    )

    def _return_balances(self):
        """
        The methot to return stocks by location and product

        Returns:
         * dict with keys: _qty_fields and zero

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        res = {}
        product_id = self._context.get('product_id', False)
        template_id = self._context.get('template_id', False)
        if product_id or template_id:
            source = self.env['product.{}'.format('product' if product_id else 'template')].browse(
                product_id if product_id else template_id
            )
            for field in self._qty_fields:
                if field =='price_unit':
                    if product_id:
                        query= 'pp.id ='+str(source.id)+' and sq.location_id='+str(self.id)
                    else:
                        query= 'pp.product_tmpl_id ='+str(source.id)+'  and sq.location_id='+str(self.id)
                    self.env.cr.execute('''
                    SELECT
                    sq.price_unit
                    FROM as_valuation_location sq
                    INNER JOIN stock_location sl on sq.location_id=sl.id
                    INNER JOIN product_product pp on sq.product_id=pp.id
                    WHERE 
                    '''+query+'''order by sq.create_date desc''')
                    costo = [i for i in self.env.cr.fetchall()]
                    if costo:
                        costo_value=float(costo[0][0])
                    else:
                        costo_value=0.00
                    self.price_unit=costo_value
                    self.update({'price_unit': costo_value})
                else:
                    balance = source.with_context(location=[self.id]).__getattribute__(field)
                    res.update({field: balance})
        return res

    @api.model
    def prepare_elements_for_hierarchy(self, args):
        """
        The method which returns hierarchy of locations based on this locations dict

        1. Filter inviable (zero-inventory) locations

        2. Get all missing parents. They might miss for 2 reasons:
           * A user doesn't have access to this location. That's why we are under sudo()
           * It is a view location. We do not pass view locations, since they might relate
             to virtual or partner locations
           Now as location_ids we have all locations to show (union of stated locations and missing parents)

        3. Build hierachy of locations with levels and calculated inventories.
           The latter is needed since virtual parents should reflect inventories of its childred

        Args:
         * args - dict
          ** elements - dict of stock.location values:
           *** id
           *** name
           *** qty_available
           *** virtual_available
           *** incoming_qty
           *** outgoing_qty

        Methods:
         * _return_parent_ids
         * _parse_hierarchy

        Returns:
         * args - dict - sorted by parents
          ** elements - dict of stock.location values:
           *** id
           *** name
           *** qty_available
           *** virtual_available
           *** incoming_qty
           *** outgoing_qty
           *** location - the parent
           *** level - level of hierarchy for interface purposes
           *** no_children - boolean (whether this location has shown children)
        """
        elements = args.get("elements")
        # 1
        clean_elements = []
        for elem in elements:
            for qty_field in self._qty_fields:
                if elem.get(qty_field) != 0:
                    clean_elements.append(elem)
                    break
        # 2
        element_ids = [elem['id'] for elem in clean_elements]
        location_ids = self.env["stock.location"].browse(element_ids)
        parent_ids = self.env["stock.location"]
        for location in location_ids:
            parent_ids = parent_ids | location.sudo()._return_parent_ids()
        location_ids = parent_ids | location_ids
        # 3
        new_elements = list(reversed(location_ids.sudo()._parse_hierarchy(clean_elements=clean_elements)))
        return new_elements

    def _return_parent_ids(self):
        """
        Method helper to return all parent location of this recursively

        Returns:
         * stock.location rerordset

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        parent_ids = self.env["stock.location"]
        if self.location_id:
            parent_ids += self.location_id
            parent_ids += self.location_id._return_parent_ids()
        return parent_ids

    def _parse_hierarchy(self, clean_elements):
        """
        Method helper to return location values in simple-parser format

        Args:
         * clean_elements - list of dicts (look at prepare_elements_for_hierarchy 'elements')

        Methods:
         * _prepare_vals_recursively

        Returns:
         * list of dicts
           ** id
           ** name
           ** qty_available
           ** virtual_available
           ** incoming_qty
           ** outgoing_qty
           *** location - the parent
           *** level - level of hierarchy for interface purposes
           *** no_children - boolean (whether this location has shown children)
        """
        res = []
        no_parent_location_ids = self.filtered(lambda loc: not loc.location_id)
        for parent in no_parent_location_ids:
            res += parent._prepare_vals_recursively(clean_elements=clean_elements, permitted_locations=self)
        return res

    def _prepare_vals_recursively(self, clean_elements, permitted_locations, level=0):
        """
        Method helper to parse value for each location recursively
        We firstly go thorugh children, since we need to accumulate values for parents. That's why the list should be
        reversed to use

        Args:
         * clean_elements - list of dicts (the same format as _parse_hierarchy returns)
         * permitted_locations - stock.location recordset  (locations which we really need to consider)
         * level - int

        Methods:
         * _return_inventory_level()

        Returns:
         * list of dicts
           ** id
           ** name
           ** qty_available
           ** virtual_available
           ** incoming_qty
           ** outgoing_qty
           *** location - the parent
           *** level - level of hierarchy for interface purposes
           *** no_children - boolean (whether this location has shown children)

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        child_location_ids = permitted_locations.filtered(lambda loc: loc.location_id.id == self.id)
        res = []
        for child in child_location_ids:
            res += child._prepare_vals_recursively(
                clean_elements=clean_elements,
                permitted_locations=permitted_locations,
                level=level+1,
        )
        # 1
        own_values = self._return_inventory_level(
            clean_elements=clean_elements,
            child_res=res,
            level=level,
        )
        res.append(own_values)
        return res

    def _return_inventory_level(self, clean_elements, child_res, level):
        """
        Method to define inventory level. There are 2 ways:
         1. Either we take it from js already
         2. Or we should calculate sum of child params, since this location was not on form yet

        Args:
         * clean_elements - list of dicts (the same format as _parse_hierarchy returns)
         * child_res - values of prepared children (the same format as _parse_hierarchy returns)
         * level - int

        Returns:
         * dict
           ** id
           ** name
           ** qty_available
           ** virtual_available
           ** incoming_qty
           ** outgoing_qty
           *** location - the parent
           *** level - level of hierarchy for interface purposes
           *** no_children - boolean (whether this location has shown children)

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        value = {
            "location_id": self.location_id.id,
            "level": level,
            "no_children": len(child_res) == 0 and True or False,
        }
        existing_elements = [elem for elem in clean_elements if elem.get("id") == self.id]
        # 1
        if len(existing_elements) > 0:
            value.update(existing_elements[0])
        # 2
        else:
            value.update({
                "id": self.id,
                "name": self.name,
            })
            child_elements = [elem for elem in child_res if elem.get("location_id") == self.id]
            for qty_field in self._qty_fields:
                value[qty_field] = 0

            for elem in child_elements:
                for qty_field in self._qty_fields:
                    value[qty_field] += elem.get(qty_field, 0)
        return value
