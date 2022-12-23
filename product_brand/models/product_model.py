from odoo import api, fields, models


class ProductModel(models.Model):
    _name="product.model"
    _description="modelo del producto"
    _order = "name"

    name = fields.Char("Nombre del Modelo", required=True)
    description = fields.Text('Descripción')
   
    products_count = fields.Integer(
        string="Numero de productos", compute="_compute_products_count"
    )
    def _compute_products_count(self):
        product_model = self.env["product.template"]
        groups = product_model.read_group(
            [("product_model_id", "in", self.ids)],
            ["product_model_id"],
            ["product_model_id"],
            lazy=False,
        )
        data = {group["product_model_id"][0]: group["__count"] for group in groups}
        for brand in self:
            brand.products_count = data.get(brand.id, 0)
