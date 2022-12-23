from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class AsTemplateProject(models.Model):
    """Modelo para almacenar plantillas de cotizaciones con correlativo"""
    _name = 'as.template.project'
    _description = "Modelo para almacenar plantillas de cotizaciones con correlativo"

    name = fields.Char(string="Titulo")
    as_numeracion_interna = fields.Char('Numeracion Interna', copy=False)
    as_alias=fields.Char(string="Alias Cargo vendedor", required=True)
    as_alias_lugar=fields.Char(string="Alias del cliente y lugar", required=True)
    as_cont_project = fields.Integer(string="Cantidad de Cotizaciones",default=0)
    as_sales_ids = fields.One2many('sale.order', 'as_template_id', string='Ventas')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['as_cont_project']=0
            if not self.env.user.as_sequence_id:
                raise UserError("El usuario debe poseer secuencia para ventas") 
            vals['as_numeracion_interna']=  self.env.user.as_sequence_id.next_by_id()
        result = super(AsTemplateProject, self).create(vals_list)
        name_project = ''
        for sale in result.as_sales_ids:
            result.as_numeracion_interna = sale.as_numeracion_interna
            result.as_alias_lugar = str(sale.partner_id.as_code)+str(sale.as_alias_lugar)
        result.name = str(result.as_alias)+'-'+str(result.as_alias_lugar)+'-'+str(result.as_numeracion_interna)+'-'+str(result.as_cont_project)
        return result

    def write(self, vals):
        res = super(AsTemplateProject, self).write(vals)
        return res

    def get_name_project(self):
        self.as_cont_project = len(self.as_sales_ids)-1
        self.name =  str(self.as_alias)+'-'+str(self.as_alias_lugar)+'-'+str(self.as_numeracion_interna)+'-'+str(self.as_cont_project)
