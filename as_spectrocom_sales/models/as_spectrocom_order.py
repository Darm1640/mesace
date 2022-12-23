from odoo import models, fields, api
class SaleOrderCampos(models.Model):
    _inherit = 'sale.order'
    as_alias_lugar=fields.Char(string="Alias del cliente y lugar", required=True)
    as_numeracion_interna = fields.Char('Numeracion Interna', help=u'Numeración interna de ventas confirmadas.', copy=False)
    as_codigo_proyecto=fields.Char(string="Codigo de Proyecto")
    # as_cont_id=fields.Integer('',copy=False,default=0)

    def action_confirm(self):
        result = super(SaleOrderCampos,self).action_confirm()
        self.as_numeracion_interna = self.env['ir.sequence'].next_by_code('sale.order.interna') or 'New'
        self.as_codigo_proyecto = str(self.mayusculas_carcter()+'-'+self.mayusculas_caracteres()+'-'+self.as_numeracion_interna)
        return result
    
    def mayusculas_carcter(self):
        result = ''
        for p in self.user_id.name.split():
            result+= p[0].upper() + ''
        return result
    
    def mayusculas_caracteres(self):
        result = ''
        for p in self.as_alias_lugar.split():
            result+= p[0].upper() + ''
        return result

    # def write(self, vals):
    #     vals.update({'as_cont_id':self.as_cont_id+1})
    #     # vals(['as_cont_id']+1
    #     res = super(SaleOrderCampos,self).write(vals)
    #     return res
    #     # res.update({
    #     #     'as_cont_id': name,
    #     # })