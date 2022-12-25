# -*- coding: utf-8 -*-
from pytz import country_names
from odoo import SUPERUSER_ID, api, fields, models, _, exceptions
from odoo.exceptions import ValidationError, except_orm, Warning, UserError,RedirectWarning
import re
import logging
_logger = logging.getLogger(__name__)


#---------------------------Modelo RES-PARTNER / TERCEROS-------------------------------#
class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    type_account = fields.Selection([('A', 'Ahorros'), ('C', 'Corriente')], 'Tipo de Cuenta', required=True, default='A')
    is_main = fields.Boolean('Es Principal')
    
class ResPartner(models.Model):
    _inherit = 'res.partner'
    _order = 'name'

    #TRACK VISIBILITY OLD FIELDS
    vat = fields.Char(tracking=True)
    street = fields.Char(tracking=True)
    country_id = fields.Many2one(tracking=True)
    state_id = fields.Many2one(tracking=True)
    zip = fields.Char(tracking=True)
    phone = fields.Char(tracking=True)
    mobile = fields.Char(tracking=True)
    email = fields.Char(tracking=True)
    website = fields.Char(tracking=True)
    lang = fields.Selection(tracking=True)
    category_id = fields.Many2many(tracking=True)
    user_id = fields.Many2one(tracking=True)    
    comment = fields.Text(tracking=True)
    name = fields.Char(tracking=True)
    city = fields.Char(string='Descripción ciudad')

    #INFORMACION BASICA
    vat_co = fields.Char(
        string="Numero RUT/NIT/CC",
    )
    vat_ref = fields.Char(
        string="NIT Formateado",
        compute="_compute_vat_ref",
        readonly=True,
    )
    vat_vd = fields.Char(
        string=u"Digito Verificación", size=1, tracking=True
    )
    ciiu_id = fields.Many2one(
        string='Actividad CIIU',
        comodel_name='res.ciiu',
        domain=[('type', '!=', 'view')],
        help=u'Código industrial internacional uniforme (CIIU)'
    )

    taxes_ids = fields.Many2many(
        string="Customer taxes",
        comodel_name="account.tax",
        relation="partner_tax_sale_rel",
        column1="partner_id",
        column2="tax_id",
        domain="[('type_tax_use','=','sale')]",
        help="Taxes applied for sale.",
    )
    supplier_taxes_ids =  fields.Many2many(
        string="Supplier taxes",
        comodel_name="account.tax",
        relation="partner_tax_purchase_rel",
        column1="partner_id",
        column2="tax_id",
        domain="[('type_tax_use','=','purchase')]",
        help="Taxes applied for purchase.",
    )
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', default=lambda self: self.env.company.country_id.id)
    same_vat_partner_id = fields.Many2one('res.partner', string='Partner with same Tax ID', compute='_compute_no_same_vat_partner_id', store=False)
    x_type_thirdparty = fields.Many2many('lavish.type_thirdparty',string='Tipo de tercero', tracking=True, ondelete='restrict', domain="['|',('is_company','=',is_company),('is_individual','!=',is_company)]") 
    x_document_type = fields.Selection(string=u'Tipo de Documento',
        selection=[
            ('11', u'11 - Registro civil de nacimiento'),
            ('12', u'12 - Tarjeta de identidad'),
            ('13', u'13 - Cédula de ciudadanía'),
            ('21', u'21 - Tarjeta de extranjería'),
            ('22', u'22 - Cédula de extranjería'),
            ('31', u'31 - NIT/RUT'),
            ('41', u'41 - Pasaporte'),
            ('42', u'42 - Documento de identificación extranjero'),
            ('47', u'47 - PEP'),
            ('50', u'50 - NIT de otro pais'),
            ('91', u'91 - NUIP'),
        ],
        help = u'Identificacion del Cliente, segun los tipos definidos por la DIAN.', tracking=True)
    x_digit_verification = fields.Integer(string='Digito de verificación', tracking=True,compute='_compute_verification_digit', store=True)
    x_business_name = fields.Char(string='Nombre de negocio', tracking=True)
    x_first_name = fields.Char(string='Primer nombre', tracking=True)
    x_second_name = fields.Char(string='Segundo nombre', tracking=True)
    x_first_lastname = fields.Char(string='Primer apellido', tracking=True)
    x_second_lastname = fields.Char(string='Segundo apellido', tracking=True)
    is_ica = fields.Boolean(string='¿Es un Grupo Empresarial?', tracking=True)
    #UBICACIÓN PRINCIPAL
    x_city = fields.Many2one('lavish.city', string='Ciudad', tracking=True, ondelete='restrict')

    #CLASIFICACION
    x_organization_type = fields.Selection([('1', 'Empresa'),
                                            ('2', 'Universidad'),
                                            ('3', 'Centro de investigación'),
                                            ('4', 'Multilateral'),
                                            ('5', 'Gobierno'),
                                            ('6', 'ONG: Organización no Gubernamental')], string='Tipo de organización', tracking=True)
    x_work_groups = fields.Many2many('lavish.work_groups', string='Grupos de trabajo', tracking=True, ondelete='restrict')
    x_sector_id = fields.Many2one('lavish.sectors', string='Sector', tracking=True, ondelete='restrict')
    x_ciiu_activity = fields.Many2one('lavish.ciiu', string='Códigos CIIU', tracking=True, ondelete='restrict')

    #GRUPO EMPRESARIAL
    x_is_business_group = fields.Boolean(string='¿Es un Grupo Empresarial?', tracking=True)
    x_name_business_group = fields.Char(string='Nombre Grupo Empresarial', tracking=True)

    #VINCULACION 
    x_active_vinculation = fields.Boolean(string='Estado de la vinculación', tracking=True)
    x_date_vinculation = fields.Date(string="Fecha de vinculación", tracking=True)
    x_type_vinculation = fields.Many2many('lavish.vinculation_types', string='Tipo de vinculación', tracking=True, ondelete='restrict')
    #Campos Informativos
    x_acceptance_data_policy = fields.Boolean(string='Acepta política de tratamiento de datos', tracking=True)
    x_acceptance_date = fields.Date(string='Fecha de aceptación', tracking=True)
    x_not_contacted_again = fields.Boolean(string='No volver a ser contactado', tracking=True)
    x_date_decoupling = fields.Date(string="Fecha de desvinculación", tracking=True)
    x_reason_desvinculation_text = fields.Text(string='Motivo desvinculación') 
    
    #INFORMACION FINANCIERA
    x_asset_range = fields.Many2one('lavish.asset_range', string='Rango de activos', tracking=True, ondelete='restrict')
    x_date_update_asset = fields.Date(string='Fecha de última modificación', compute='_date_update_asset', store=True, tracking=True)
    x_company_size = fields.Selection([
                                        ('1', 'Mipyme'),
                                        ('2', 'Pyme'),
                                        ('3', 'Mediana'),
                                        ('4', 'Grande')
                                    ], string='Tamaño empresa', tracking=True)

    #INFORMACION TRIBUTARIA
    x_tax_responsibilities = fields.Many2many('lavish.responsibilities_rut', string='Responsabilidades Tributarias', tracking=True, ondelete='restrict')

    #INFORMACION COMERCIAL
    x_account_origin = fields.Selection([
                                        ('1', 'Campañas'),
                                        ('2', 'Eventos'),
                                        ('3', 'Referenciado'),
                                        ('4', 'Telemercadeo'),
                                        ('5', 'Web'),
                                        ('6', 'Otro')
                                    ], string='Origen de la cuenta', tracking=True)
    

    #INFORMACIÓN CONTACTO
    x_contact_type = fields.Many2many('lavish.contact_types', string='Tipo de contacto', tracking=True, ondelete='restrict')
    x_contact_job_title = fields.Many2one('lavish.job_title', string='Cargo', tracking=True, ondelete='restrict')
    x_contact_area = fields.Many2one('lavish.areas', string='Área', tracking=True, ondelete='restrict')
    
    #INFORMACION FACTURACION ELECTRÓNICA
    x_email_invoice_electronic = fields.Char(string='Correo electrónico para recepción electrónica de facturas', tracking=True)

    @api.onchange('x_city')
    def _onchange_city_id2(self):
        if self.x_city:
            self.city = self.x_city.name
            self.zip = self.x_city.zipcode
            self.state_id = self.x_city.state_id
        elif self._origin:
            self.city = False
            self.zip = False
            self.state_id = False
    #MANTENIMIENTO
    #is_work_place = fields.Boolean('Is Work Place?')
    def _display_address(self, without_company=False):
        address_format = self.country_id.address_format or \
            self._get_default_address_format()
        args = {
            'state_code': self.state_id.code or '',
            'state_name': self.state_id.name or '',
            'country_code': self.country_id.code or '',
            'country_name': self.country_id.name or '',
            'company_name': self.commercial_company_name or '',
            'city_name': self.city_id and self.city_id.display_name or '',
        }
        for field in self._address_fields():
            args[field] = getattr(self, field) or ''
        if without_company:
            args['company_name'] = ''
        elif self.commercial_company_name:
            address_format = '%(company_name)s\n' + address_format

        if self.x_document_type in ['31','13','22']:
            id_type = {}
            id_type['31'] = 'NIT'
            id_type['13'] = 'CC'
            id_type['22'] = 'CE'
            id_id = id_type[self.x_document_type]
        else:
            id_id = 'ID'

        res = address_format % args
        
        if self.vat_ref:
            res = "%s:%s\n%s" % (id_id, self.vat_ref, res)
        else:
            res = "%s:%s\n%s" % (id_id, self.vat_co, res)

        return res

    @api.depends('x_asset_range')
    def _date_update_asset(self):
        for record in self:
            record.x_date_update_asset = fields.Date.today()

    @api.depends('vat')
    def _compute_no_same_vat_partner_id(self):
        for partner in self:
            partner.same_vat_partner_id = ""
    
    @api.onchange("l10n_latam_identification_type_id")
    def onchange_document_type(self):
        if self.l10n_latam_identification_type_id.l10n_co_document_code == 'rut':
            self.x_document_type = '31'
        elif self.l10n_latam_identification_type_id.l10n_co_document_code == 'id_document':
            self.x_document_type = '13'
        elif self.l10n_latam_identification_type_id.l10n_co_document_code == 'id_card':
            self.x_document_type = '12'
        elif self.l10n_latam_identification_type_id.l10n_co_document_code == 'passport':
            self.x_document_type = '41'
        elif self.l10n_latam_identification_type_id.l10n_co_document_code == 'foreign_id_card':
            self.x_document_type = '22'
        elif self.l10n_latam_identification_type_id.l10n_co_document_code == 'external_id':
            self.x_document_type = '42'
        elif self.l10n_latam_identification_type_id.l10n_co_document_code == 'diplomatic_card':
            self.x_document_type = '42'
        elif self.l10n_latam_identification_type_id.l10n_co_document_code == 'residence_document':
            self.x_document_type = '42'
        elif self.l10n_latam_identification_type_id.l10n_co_document_code == 'civil_registration':
            self.x_document_type = '11'
        elif self.l10n_latam_identification_type_id.l10n_co_document_code == 'national_citizen_id':
            self.x_document_type = '13'
    def _address_fields(self):
        result = super(ResPartner, self)._address_fields()
        result = result + ['city_id']
        return result


    def _compute_vat_ref(self):
        """
        Compute vat_ref field
        """
        for partner in self:
            result_vat = None
            if partner.x_document_type == '31' and partner.vat_co and partner.vat_co.isdigit() and len(partner.vat_co.strip()) > 0:
                #result_vat = '{:,}'.format(int(partner.vat_co.strip())).replace(",", ".")
                partner.vat_ref = "%s" % (partner.vat)
            else:
                partner.vat_ref = partner.vat_co
                
    @api.onchange('vat_co','city_id','l10n_latam_identification_type_id')
    def _compute_concat_nit(self):
        """
        Concatenating and formatting the NIT number in order to have it
        consistent everywhere where it is needed
        @return: void
        """
        # Executing only for Document Type 31 (NIT)
        for partner in self:

            _logger.info('document')
            _logger.info(partner.l10n_latam_identification_type_id.name)
            if partner.l10n_latam_identification_type_id.name == 'NIT':
                # First check if entered value is valid
                _logger.info('if')
                # self._check_ident()
                #self._check_ident_num()

                # Instead of showing "False" we put en empty string
                if partner.vat_co == False:
                    partner.vat_co = ''
                else:
                    _logger.info('else')
                    partner.vat_vd = ''

                    # Formatting the NIT: xx.xxx.xxx-x
                    s = str(partner.vat_co)[::-1]
                    newnit = '.'.join(s[i:i + 3] for i in range(0, len(s), 3))
                    newnit = newnit[::-1]

                    nitList = [
                        newnit,
                        # Calling the NIT Function
                        # which creates the Verification Code:
                        self._check_dv(str(partner.vat_co).replace('-', '',).replace('.', '',))
                    ]

                    formatedNitList = []

                    for item in nitList:
                        if item != '':
                            formatedNitList.append(item)
                            partner.vat_vd = '-'.join(formatedNitList)

                    # Saving Verification digit in a proper field
                    for pnitem in self:
                        _logger.info(nitList[1])
                        _logger.info('nitlist')
                        pnitem.vat_vd = nitList[1]

    def _check_dv(self, nit):
        """
        Function to calculate the check digit (DV) of the NIT. So there is no
        need to type it manually.
        @param nit: Enter the NIT number without check digit
        @return: String
        """
        for item in self:
            if item.l10n_latam_identification_type_id.name != 'NIT':
                return str(nit)

            nitString = '0'*(15-len(nit)) + nit
            vl = list(nitString)
            result = (
                int(vl[0])*71 + int(vl[1])*67 + int(vl[2])*59 + int(vl[3])*53 +
                int(vl[4])*47 + int(vl[5])*43 + int(vl[6])*41 + int(vl[7])*37 +
                int(vl[8])*29 + int(vl[9])*23 + int(vl[10])*19 + int(vl[11])*17 +
                int(vl[12])*13 + int(vl[13])*7 + int(vl[14])*3
            ) % 11

            if result in (0, 1):
                return str(result)
            else:
                return str(11-result)
            
    @api.depends('vat')
    def _compute_verification_digit(self):
        #Logica para calcular digito de verificación
        multiplication_factors = [71, 67, 59, 53, 47, 43, 41, 37, 29, 23, 19, 17, 13, 7, 3]

        for partner in self:
            if partner.vat and partner.x_document_type == '31' and len(partner.vat) <= len(multiplication_factors):
                number = 0
                padded_vat = partner.vat

                while len(padded_vat) < len(multiplication_factors):
                    padded_vat = '0' + padded_vat

                # if there is a single non-integer in vat the verification code should be False
                try:
                    for index, vat_number in enumerate(padded_vat):
                        number += int(vat_number) * multiplication_factors[index]

                    number %= 11

                    if number < 2:
                        partner.x_digit_verification = number
                    else:
                        partner.x_digit_verification = 11 - number
                except ValueError:
                    partner.x_digit_verification = False
            else:
                partner.x_digit_verification = False

    #---------------Search
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if self._context.get('search_by_vat', False):
            if name:
                args = args if args else []
                args.extend(['|', ['name', 'ilike', name], ['vat', 'ilike', name]])
                name = ''
        return super(ResPartner, self).name_search(name=name, args=args, operator=operator, limit=limit)

    #Onchange
    # @api.onchange('x_type_thirdparty')
    # def _onchange_type_thirdparty(self):
    #     for record in self:
    #         if record.x_type_thirdparty:
    #             for i in record.x_type_thirdparty:
    #                 print(i.id)
    #                 if i.id == 2 and record.company_type == 'company':
    #                     raise UserError(_('Una compañia no puede estar catalogada como contacto, por favor verificar.')) 
    @api.onchange('country_id', 'vat_co', 'vat_vd', 'l10n_latam_identification_type_id')
    def _onchange_vat(self):
        if self.country_id and self.vat_co:
            if self.country_id.code:
                if self.vat_vd and self.l10n_latam_identification_type_id.l10n_co_document_code == 'rut':
                    self.vat = self.vat_co + "-" + self.vat_vd
                elif self.l10n_latam_identification_type_id.l10n_co_document_code  == 'foreign_id_card':
                    self.vat_vd = False
                    self.vat = self.vat_co 
                else:
                    self.vat_vd = False
                    self.vat = self.vat_co 
            else:
                msg = _('The Country has No ISO Code.')
                raise ValidationError(msg)
        elif not self.vat_co and self.vat:
            self.vat = False

    @api.constrains('vat', 'l10n_latam_identification_type_id', 'country_id')
    def check_vat(self):
        def _checking_required(partner):
            '''
            Este método solo aplica para Colombia y obliga a seleccionar
            un tipo de documento de identidad con el fin de determinar
            si es verificable por el algoritmo VAT. Si no se define,
            de todas formas el VAT se evalua como un NIT.
            '''
            return ((partner.l10n_latam_identification_type_id and \
                partner.l10n_latam_identification_type_id) or \
                not partner.l10n_latam_identification_type_id) == True

        msg = _('The Identification Document does not seems to be correct.')

        for partner in self:
            if not partner.vat:
                continue

            vat_country, vat_number = self._split_vat(partner.vat)

            if partner.l10n_latam_identification_type_id.name == 'Nit de otro país':
                vat_country = 'co'
            elif partner.country_id:
                vat_country = partner.country_id.code.lower()

            if not hasattr(self, 'check_vat_' + vat_country):
                continue

            #check = getattr(self, 'check_vat_' + vat_country)

            if vat_country == 'co':
                if not _checking_required(partner):
                    continue

            #if check and not check(vat_number):
            #   raise ValidationError(msg)

        return True

    # def check_vat_co(self, vat):
    #     '''
    #     Check VAT Routine for Colombia.
    #     '''
    #     # if type(vat) == str:
    #     #     vat = vat.replace('-', '', 1).replace('.', '', 2)

    #     if len(str(vat)) < 4:
    #         return False

    #     try:
    #         int(vat)
    #     except ValueError:
    #         return False

    #     # Validación Sin identificación del exterior
    #     # o para uso definido por la DIAN
    #     if len(str(vat)) == 9 and str(vat)[0:5] == '44444' \
    #         and int(str(vat)[5:]) <= 9000 \
    #         and int(str(vat)[5:]) >= 4001:

    #         return True

    #     prime = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]
    #     sum = 0
    #     vat_len = len(str(vat))

    #     for i in range(vat_len - 2, -1, -1):
    #         sum += int(str(vat)[i]) * prime[vat_len - 2 - i]

    #     if sum % 11 > 1:
    #         return str(vat)[vat_len - 1] == str(11 - (sum % 11))
    #     else:
    #         return str(vat)[vat_len - 1] == str(sum % 11)


    @api.constrains("vat_co", "x_document_type")
    def check_vat(self):
        """
        Check vat_co field
        """
        for partner in self:
            if partner.vat_co:
                if not re.match(r'^\d+$', partner.vat_co) and partner.x_document_type in ['31', '13']:
                    raise ValidationError(_('The vat_co number must be only numbers, there are characters invalid like letters or empty space'))

                partner.vat_co.strip()
                #partner.check_unique_constraint()

    # @api.onchange("vat_type", "vat_co", "vat_vd", )
    # def _onchange_vat_vd(self):
    #     self.ensure_one()
    #     if self.vat_type == '31' and self.vat_co and self.vat_vd:

    #         return {
    #             'warning': {
    #                 'title': _('Warning'),
    #                 'message': u'NIT/RUT [%s - %i] suministrado para "%s" no supera la prueba del dígito de verificacion, el valor calculado es %s!' %
    #                               (self.vat_co, self.vat_vd, self.name, self.compute_vat_vd(self.vat_co))
            #     }
            # }

    # def check_vat_co(self):
    #     """
    #     Check vat_co field
    #     """
    #     self.ensure_one()
    #     vat_vd = self.vat_vd
    #     computed_vat_vd = self.compute_vat_vd(self.vat_co)
    #     if int(vat_vd) != int(computed_vat_vd):
    #         return False
    #     return True


    @api.onchange('x_first_name', 'x_second_name', 'x_first_lastname', 'x_second_lastname')
    def _onchange_person_names(self):
        if self.company_type == 'person':
            names = [name for name in [self.x_first_name, self.x_second_name, self.x_first_lastname, self.x_second_lastname] if name]
            self.name = u' '.join(names)

    @api.depends('company_type', 'name', 'x_first_name', 'x_second_name', 'x_first_lastname', 'x_second_lastname')
    def copy(self, default=None):
        default = default or {}
        if self.company_type == 'person':
            default.update({
                'x_first_name': self.x_first_name and self.x_first_name + _('(copy)') or '',
                'x_second_name': self.x_second_name and self.x_second_name + _('(copy)') or '',
                'x_first_lastname': self.x_first_lastname and self.x_first_lastname + _('(copy)') or '',
                'x_second_lastname': self.x_second_lastname and self.x_second_lastname + _('(copy)') or '',
            })
        return super(ResPartner, self).copy(default=default)

    # @api.constrains("vat")
    # def check_unique_constraint(self):
    #     partner_ids = self.search([
    #         ('vat','=', self.vat),
    #         #('vat_type','=', self.vat_type),
    #         ('parent_id','=',False),
    #     ])
    #     partner_ids = partner_ids - self
        
    #     if len(partner_ids) > 0 and not self.parent_id:
    #         raise ValidationError(_("VAT %s is already registered for the contact %s") % (self.vat, ';'.join([partner_id.display_name for partner_id in partner_ids])))

    def person_name(self, vals):
        values = vals or {}
        person_field = ['x_first_name', 'x_second_name', 'x_first_lastname', 'x_second_lastname']
        person_names = set(person_field)
        values_keys = set(values.keys())

        if person_names.intersection(values_keys):
            names = []
            for x in person_field:
                if x in values.keys():
                    names += [values.get(x, False) and values.get(x).strip() or '']
                else:
                    names += [self[x] or '']
            name = ' '.join(names)
            if name.strip():
                values.update({
                    'name': name,
                })

        if values.get('name', False):
            values.update({
                'name': values.get('name').strip(),
            })

        return values

    def write(self, values):
        values = self.person_name(values)
        return super(ResPartner, self).write(values)

    @api.model
    def create(self, values):
        values = self.person_name(values)
        return super(ResPartner, self).create(values)

        
    @api.onchange('email')
    def _onchange_email(self):
        for record in self:
            if record.email:
                if not '@' in str(record.email):
                    self.email = False
                    raise UserError(_('El correo digitado no es valido, por favor verificar.'))

    # @api.onchange('vat')
    # def _onchange_vatnumber(self):
    #     for record in self:
    #         if record.vat:
    #             # lst_character = ['.',',','*','@','-','_','°','!','|','"','#','$','%','&','/','(',')','=','?','¡','¿','{','}','<','>','^','+','[',']','~']
    #             # for character in lst_character:
    #             #     if character in record.vat:
    #             #         raise UserError(_('El campo número de documento no debe contener caracteres especiales.'))                    
    #             # if record.x_document_type == '31' and len(record.vat) > 9:
    #             #     raise UserError(_('El campo número de documento no debe tener mas de 9 dígitos cuando el tipo de documento es NIT.'))   

    #             obj = self.search([('x_type_thirdparty','in',[1,3]),('vat','=',record.vat)])
    #             if obj:
    #                 self.vat = ""
    #                 raise UserError(_('Ya existe un Cliente con este número de NIT.'))                    
    #             objArchivado = self.search([('x_type_thirdparty','in',[1,3]),('vat','=',record.vat),('active','=',False)])
    #             if objArchivado:
    #                 self.vat = ""
    #                 raise UserError(_('Ya existe un Cliente con este número de NIT pero se encuentra archivado.')) 
    
    #-----------Validaciones

    # @api.constrains('vat')
    # def _check_vatnumber(self):
    #     for record in self:
    #         cant_vat = 0
    #         cant_vat_archivado = 0
    #         cant_vat_ind = 0
    #         cant_vat_archivado_ind = 0
    #         name_tercer =  ''
    #         user_create = ''
    #         if record.vat:
    #             obj = self.search([('is_company', '=', True),('vat','=',record.vat)])
    #             if obj:
    #                 for tercer in obj:
    #                     cant_vat = cant_vat + 1
    #                     if tercer.id != record.id:
    #                         name_tercer = tercer.name
    #                         user_create = tercer.create_uid.name

    #             objArchivado = self.search([('is_company', '=', True),('vat','=',record.vat),('active','=',False)])
    #             if objArchivado:
    #                 for tercer in objArchivado:
    #                     cant_vat_archivado = cant_vat_archivado + 1
    #                     if tercer.id != record.id:
    #                         name_tercer = tercer.name
    #                         user_create = tercer.create_uid.name

    #             obj_ind = self.search([('is_company', '=', False),('vat','=',record.vat)])
    #             if obj_ind:
    #                 for tercer in obj_ind:
    #                     cant_vat_ind = cant_vat_ind + 1
    #                     if tercer.id != record.id:
    #                         name_tercer = tercer.name
    #                         user_create = tercer.create_uid.name

    #             objArchivado_ind = self.search([('is_company', '=', False),('vat','=',record.vat),('active','=',False)])
    #             if objArchivado_ind:
    #                 for tercer in objArchivado_ind:
    #                     cant_vat_archivado_ind = cant_vat_archivado_ind + 1
    #                     if tercer.id != record.id:
    #                         name_tercer = tercer.name
    #                         user_create = tercer.create_uid.name
    #         if cant_vat > 1:
    #             raise ValidationError(_('Ya existe un Cliente ('+name_tercer+') con este número de NIT creado por '+user_create+'.'))                
    #         if cant_vat_archivado > 1:
    #             raise ValidationError(_('Ya existe un Cliente ('+name_tercer+') con este número de NIT pero se encuentra archivado, fue creado por '+user_create+'.'))                
    #         if cant_vat_ind > 1:
    #             raise ValidationError(_('Ya existe un Tercero ('+name_tercer+') con este número de ID creado por '+user_create+'.'))                
    #         if cant_vat_archivado_ind > 1:
    #             raise ValidationError(_('Ya existe un Tercero ('+name_tercer+') con este número de ID pero se encuentra archivado, fue creado por '+user_create+'.'))

    @api.constrains('bank_ids')
    def _check_bank_ids(self):
        for record in self:
            if len(record.bank_ids) > 0:
                count_main = 0
                for bank in record.bank_ids:
                    count_main += 1 if bank.is_main else 0
                if count_main > 1:
                    raise ValidationError(_('No puede tener más de una cuenta principal, por favor verificar.'))

    # @api.constrains('x_type_thirdparty','name','x_document_type','vat','street','state_id','country_id','x_city','phone','mobile','email')
    # def _check_fields_required(self):  
    #     if self.env.user.name != 'OdooBot' and self.env.user.login != '__system__': # Se omite esta validación con datos DEMO ESTANDAR DE ODOO
    #         for record in self:
    #             responsable = 'tercero'
    #             if record.parent_id:
    #                 name = ' '+record.name if record.name else ''
    #                 responsable = 'contacto'+name
                
    #             if not record.parent_id:
    #                 if not record.x_document_type:     
    #                     raise ValidationError(_('Debe seleccionar el tipo de documento del '+responsable+', por favor verificar.'))  
    #                 if not record.vat:           
    #                     raise ValidationError(_('Debe digitar el número de documento del '+responsable+', por favor verificar.'))  
    #                 if not record.phone and not record.mobile:
    #                     raise ValidationError(_('Debe digitar el telefono o móvil del '+responsable+', por favor verificar.'))  

    #             if not record.name:
    #                 raise ValidationError(_('Debe digitar el nombre del '+responsable+', por favor verificar.'))             
    #             if len(record.x_type_thirdparty)==0:
    #                 raise ValidationError(_('Debe seleccionar un tipo de tercero, por favor verificar.'))        
    #             if not record.street:
    #                 raise ValidationError(_('Debe digitar la dirección del '+responsable+', por favor verificar.'))  
    #             if not record.state_id:
    #                 raise ValidationError(_('Debe digitar el departamento del '+responsable+', por favor verificar.'))  
    #             if not record.x_city:
    #                 raise ValidationError(_('Debe digitar la ciudad del '+responsable+', por favor verificar.'))  
    #             if not record.country_id:
    #                 raise ValidationError(_('Debe digitar el país del '+responsable+', por favor verificar.'))  
    #             if not record.email:
    #                 raise ValidationError(_('Debe digitar el correo electrónico del '+responsable+', por favor verificar.')) 

class ResCountry(models.Model):
    _inherit = 'res.country'

    code_dian = fields.Char(
        string='DIAN Code',
        required=False,
        readonly=False
    )

    def name_get(self):
        rec = []
        for recs in self:
            name = '%s [%s]' % (recs.name or '', recs.code or '')
            rec += [ (recs.id, name) ]
        return rec

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """
        Se hereda metodo name search y se sobreescribe para hacer la busqueda 
        por el codigo del pais
        """
        if not args:
            args = []
        args = args[:]
        ids = []
        if name:
            ids = self.search([('code_dian', '=like', name + "%")] + args, limit=limit)
            if not ids:
                ids = self.search([('code', operator, name)] + args,limit=limit)
                if not ids:
                    ids = self.search([('name', operator, name)] + args,limit=limit)
        else:
            ids = self.search(args, limit=100)

        if ids:
            return ids.name_get()
        return self.name_get()

class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    code_department = fields.Char(string="Code department")
    code_d = fields.Char(string="Code department")
    def name_get(self):
        rec = []
        for recs in self:
            name = '%s [%s]' % (recs.name or '', recs.code or '')
            rec += [ (recs.id, name) ]
        return rec

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """
        Se hereda metodo name search y se sobreescribe para hacer la busqueda 
        por el codigo del estado/departamento
        """
        if not args:
            args = []
        args = args[:]
        ids = []
        if name:
            ids = self.search([('code', '=like', name + "%")] + args, limit=limit)
            if not ids:
                ids = self.search([('name', operator, name)] + args,limit=limit)
        else:
            ids = self.search(args, limit=100)

        if ids:
            return ids.name_get()
        return self.name_get()

class ResCity(models.Model):
    _inherit = 'res.city'

    name = fields.Char(translate=False)
    code = fields.Char(string="Code")
    code_dian = fields.Char(string="Code")
    postal_code = fields.Char(string=u'Postal code',)

    def name_get(self):
        rec = []
        for recs in self:
            name = '%s / %s [%s]' % (recs.name or '', recs.state_id.name or '', recs.code or '')
            rec += [ (recs.id, name) ]
        return rec

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """
        Se hereda metodo name search y se sobreescribe para hacer la busqueda 
        por el codigo de la ciudad
        """
        if not args:
            args = []
        args = args[:]
        ids = []
        if name:
            ids = self.search([('code', '=like', name + "%")] + args, limit=limit)
            if not ids:
                ids = self.search([('name', operator, name)] + args,limit=limit)
        else:
            ids = self.search(args, limit=100)

        if ids:
            return ids.name_get()
        return self.name_get()

class ResBank(models.Model):
    _inherit = 'res.bank'

    city_id = fields.Many2one('res.city', string="City of Address")
    bank_code = fields.Char(string='Bank Code')            

class ResCompany(models.Model):
    _inherit = 'res.company'

    def _get_default_partner(self):
        res_partner = self.env['res.partner'].sudo()
        partner_id = res_partner.browse(1)
        return partner_id.id

    city_id = fields.Many2one('res.city', compute="_compute_address", inverse="_inverse_city_id", string="City of Address")
    vat_vd = fields.Integer(compute="_compute_address", inverse="_inverse_vat_vd", string="Verification digit")
    default_partner_id = fields.Many2one('res.partner', string="Default partner", required=True, default=_get_default_partner)

    default_taxes_ids = fields.Many2many(
        string="Customer taxes",
        comodel_name="account.tax",
        relation="company_default_taxes_rel",
        column1="product_id",
        column2="tax_id",
        domain="[('type_tax_use','=','sale')]",
        help="Taxes applied for sale.",
    )
    default_supplier_taxes_ids = fields.Many2many(
        string="Supplier taxes",
        comodel_name="account.tax",
        relation="company_default_supplier_taxes_rel",
        column1="product_id",
        column2="tax_id",
        domain="[('type_tax_use','=','purchase')]",
        help="Taxes applied for purchase.",
    )

    def _get_company_address_fields(self, partner):
        result = super(ResCompany, self)._get_company_address_fields(partner)
        result['city_id'] = partner.city_id.id
        result['vat_vd'] = partner.vat_vd
        return result

    def _inverse_vat_vd(self):
        for company in self:
            company.partner_id.vat_vd = company.vat_vd
            company.default_partner_id.vat_vd = company.vat_vd


    def _inverse_city_id(self):
        for company in self:
            company.partner_id.city_id = company.city_id
            company.default_partner_id.city_id = company.city_id

    def _inverse_street(self):
        result = super(ResCompany, self)._inverse_street()
        for company in self:
            company.default_partner_id.street = company.street

    def _inverse_country(self):
        result = super(ResCompany, self)._inverse_country()
        for company in self:
            company.default_partner_id.country_id = company.country_id    