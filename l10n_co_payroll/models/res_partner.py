from xmlrpc.client import boolean
from odoo import models, fields

class ResPartner(models.Model):
    _inherit = "res.partner"

    is_management = fields.Boolean("Administradora protección social")
    management_id = fields.Many2one('res.partner.management', string='Administradora')
    
    fe_primer_apellido = fields.Char(
        string='Primer apellido',
    )
    fe_segundo_apellido = fields.Char(
        string='Segundo apellido',
        default=''
    )
    fe_primer_nombre = fields.Char(
        string='Primer nombre',
    )
    fe_segundo_nombre = fields.Char(
        string='Segundo nombre',
        default=''
    )
    fe_razon_social = fields.Char(
        string='Razón social',
        default=''
    )
    fe_tipo_documento = fields.Selection(
        selection=[
            ('11', 'Registro civil'),
            ('12', 'Tarjeta de identidad'),
            ('13', 'Cédula de ciudadanía'),
            ('21', 'Tarjeta de extranjería'),
            ('22', 'Cédula de extranjería'),
            ('31', 'NIT'),
            ('41', 'Pasaporte'),
            ('42', 'Documento de identificación extranjero'),
            ('47', 'PEP (permiso especial de permanencia)'),
            ('50', 'NIT de otro país'),
            ('91', 'NUIP'),
        ],
        string='Tipo de documento',
    )
    fe_nit = fields.Char(
        string='Número de documento',
    )
    fe_digito_verificacion = fields.Selection(
        selection=[
            ('0', '0'),
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4'),
            ('5', '5'),
            ('6', '6'),
            ('7', '7'),
            ('8', '8'),
            ('9', '9'),
            ('No aplica', 'No aplica'),
        ],
        string='Dígito de verificación',
        default='No aplica'
    )
    fe_es_compania = fields.Selection(
        selection=[
            ('1', 'Jurídica'),
            ('2', 'Natural'),
        ],
        string='Tipo de persona',
        default='1',
    )
    cities = fields.Many2one('l10n_co_cei.city')
    postal_id2 = fields.Many2one('l10n_co_cei.postal_code', string="Código Postal")
class NewCity(models.Model):
    _name = 'l10n_co_cei.city'
    _description = 'Ciudades de Colombia'
    _rec_name = 'city_name'

    #region Campos
    city_code = fields.Char()
    city_name = fields.Char()

    state_id = fields.Many2one('res.country.state')
class ResCountryState(models.Model):
    _inherit = 'res.country.state'
    # region Campos
    state_code = fields.Char()

    cities_ids = fields.One2many('l10n_co_cei.city','state_id',string='Ciudades')

    fe_habilitada_compania = fields.Boolean(
        string='FE Compañía',
       # compute='compute_fe_habilitada_compania',
        store=False,
        copy=False
    )
class ResCountry(models.Model):
    _inherit = 'res.country'
    #region Campos
    iso_name = fields.Char()
    alpha_code_three = fields.Char()
    numeric_code = fields.Char()
    codigo_dian_exogena = fields.Char()
    
class PostalCode(models.Model):
    _name = 'l10n_co_cei.postal_code'
    _description = "Códigos Postales"

    # region Campos
    cp_data = None

    name = fields.Char(
        string='Código Postal',
        required=True
    )
    city_id = fields.Integer(
        string='Ciudad'
    )
    state_id = fields.Integer(
        string='Departamento'
    )
    country_id = fields.Integer(
        string='Pais'
    )

