from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from pytz import timezone

import base64
import io
import xlsxwriter

class hr_birthday_list(models.TransientModel):
    _name = "hr.birthday.list"
    _description = "Listado de cumpleaños"

    branch = fields.Many2many('lavish.res.branch', string='Sucursal')
    company = fields.Many2many('res.company',string='Compañías', required=True, default=lambda self: self.env.company.ids)
    month = fields.Selection([('0', 'Todos'),
                            ('1', 'Enero'),
                            ('2', 'Febrero'),
                            ('3', 'Marzo'),
                            ('4', 'Abril'),
                            ('5', 'Mayo'),
                            ('6', 'Junio'),
                            ('7', 'Julio'),
                            ('8', 'Agosto'),
                            ('9', 'Septiembre'),
                            ('10', 'Octubre'),
                            ('11', 'Noviembre'),
                            ('12', 'Diciembre')        
                            ], string='Mes', required=True)

    excel_file = fields.Binary('Excel')
    excel_file_name = fields.Char('Excel filename')

    def name_get(self):
        result = []
        for record in self:            
            result.append((record.id, "Listado de cumpleaños"))
        return result

    def get_month(self):
        if self.month == '0':
            month = [1,2,3,4,5,6,7,8,9,10,11,12]
        else: 
            month = [int(self.month)]
        return month

    def get_info_birthday(self,month):
        domain = [('birthday','!=',False)]
        if len(self.company) > 0:
            domain.append(('company_id','in',self.company.ids))
        if len(self.branch) > 0:
            domain.append(('branch_id','in',self.branch.ids))
        obj_employee = self.env['hr.employee'].search(domain).filtered(lambda x: x.birthday.month == int(month))
        return obj_employee

    def get_name_month(self,month_number):
        #Mes
        month = ''
        month = 'Enero' if month_number == 1 else month
        month = 'Febrero' if month_number == 2 else month
        month = 'Marzo' if month_number == 3 else month
        month = 'Abril' if month_number == 4 else month
        month = 'Mayo' if month_number == 5 else month
        month = 'Junio' if month_number == 6 else month
        month = 'Julio' if month_number == 7 else month
        month = 'Agosto' if month_number == 8 else month
        month = 'Septiembre' if month_number == 9 else month
        month = 'Octubre' if month_number == 10 else month
        month = 'Noviembre' if month_number == 11 else month
        month = 'Diciembre' if month_number == 12 else month

        return month

    def get_date_text(self,date,calculated_week=0,hide_year=0):
        #Mes
        month = self.get_name_month(date.month)
        #Dia de la semana
        week = ''
        week = 'Lunes' if date.weekday() == 0 else week
        week = 'Martes' if date.weekday() == 1 else week
        week = 'Miercoles' if date.weekday() == 2 else week
        week = 'Jueves' if date.weekday() == 3 else week
        week = 'Viernes' if date.weekday() == 4 else week
        week = 'Sábado' if date.weekday() == 5 else week
        week = 'Domingo' if date.weekday() == 6 else week

        if hide_year == 0:
            if calculated_week == 0:
                date_text = date.strftime('%d de '+month+' del %Y')
            else:
                date_text = date.strftime(week+', %d de '+month+' del %Y')
        else:
            if calculated_week == 0:
                date_text = date.strftime('%d de '+month)
            else:
                date_text = date.strftime(week+', %d de '+month)

        return date_text

    def generate_report(self):
        datas = {
             'id': self.id,
             'model': 'hr.birthday.list'             
            }

        return {
            'type': 'ir.actions.report',
            'report_name': 'lavish_hr_employee.report_birthday_list',
            'report_type': 'qweb-pdf',
            'datas': datas        
        }      

    def generate_birthday_excel(self):
        query_where = ''
        if self.month == '0':
            query_where = "where a.company_id in (" + str(self.company.ids).replace('[','').replace(']','') + ") "
        else:
            query_where = "where a.company_id in (" + str(self.company.ids).replace('[','').replace(']','') + ") and date_part('month',a.birthday) = " + self.month
        # Filtro Sucursal
        str_ids_branch = ''
        for i in self.branch:
            str_ids_branch = str(i.id) if str_ids_branch == '' else str_ids_branch + ',' + str(i.id)
        if str_ids_branch == '' and len(self.env.user.branch_ids.ids) > 0:
            for i in self.env.user.branch_ids.ids:
                str_ids_branch = str(i) if str_ids_branch == '' else str_ids_branch + ',' + str(i)
        if str_ids_branch != '':
            query_where = query_where + f"and zrb.id in ({str_ids_branch}) "
        # ----------------------------------Ejecutar consulta
        query_report = f'''
                    select c.name,b.vat,b.name as name_employee,zrb."name" as branch,a.birthday
                    from hr_employee as a
                    Inner join res_partner as b on b.id = a.partner_encab_id
                    Inner join res_company c on c.id = a.company_id 
                    inner join res_partner d on d.id = c.partner_id
                    inner join lavish_res_branch as zrb on a.branch_id = zrb.id
                    %s
					order by date_part('month',a.birthday),date_part('day',a.birthday)
                    '''%(query_where)

        self._cr.execute(query_report)
        result_query = self._cr.dictfetchall()
        if len(result_query) == 0:
            raise ValidationError(_('No se encontraron datos con los filtros seleccionados, por favor verificar.'))
        # Generar EXCEL
        filename = 'Reporte Listado de Cumpleaños'
        stream = io.BytesIO()
        book = xlsxwriter.Workbook(stream, {'in_memory': True})

        # Columnas
        columns = ['Compañia', 'Identificación', 'Nombres','Sucursal','Fecha de cumpleaños']
        sheet = book.add_worksheet('Listado de Cumpleaños')

        # Agregar textos al excel
        text_title = 'Listado de Cumpleaños'
        text_generate = 'Informe generado el %s' % (datetime.now(timezone(self.env.user.tz)))
        cell_format_title = book.add_format({'bold': True, 'align': 'left'})
        cell_format_title.set_font_name('Calibri')
        cell_format_title.set_font_size(15)
        cell_format_title.set_bottom(5)
        cell_format_title.set_bottom_color('#1F497D')
        cell_format_title.set_font_color('#1F497D')
        sheet.merge_range('A1:E1', text_title, cell_format_title)
        cell_format_text_generate = book.add_format({'bold': False, 'align': 'left'})
        cell_format_text_generate.set_font_name('Calibri')
        cell_format_text_generate.set_font_size(10)
        cell_format_text_generate.set_bottom(5)
        cell_format_text_generate.set_bottom_color('#1F497D')
        cell_format_text_generate.set_font_color('#1F497D')
        sheet.merge_range('A2:E2', text_generate, cell_format_text_generate)
        # Formato para fechas
        date_format = book.add_format({'num_format': 'dd/mm/yyyy'})

        # Agregar columnas
        aument_columns = 0
        for column in columns:
            sheet.write(2, aument_columns, column)
            aument_columns = aument_columns + 1

            # Agregar query
            aument_columns = 0
            aument_rows = 3
            for query in result_query:
                for row in query.values():
                    width = len(str(row)) + 10
                    if str(type(row)).find('date') > -1:
                        sheet.write_datetime(aument_rows, aument_columns, row, date_format)
                    else:
                        sheet.write(aument_rows, aument_columns, row)
                    # Ajustar tamaño columna
                    sheet.set_column(aument_columns, aument_columns, width)
                    aument_columns = aument_columns + 1
                aument_rows = aument_rows + 1
                aument_columns = 0

            # Convertir en tabla
            array_header_table = []
            for i in columns:
                dict = {'header': i}
                array_header_table.append(dict)

            sheet.add_table(2, 0, aument_rows-1, len(columns)-1, {'style': 'Table Style Medium 2', 'columns': array_header_table})
            # Guadar Excel
            book.close()

            self.write({
                'excel_file': base64.encodestring(stream.getvalue()),
                'excel_file_name': filename,
            })

            action = {
                'name': 'Listado de Cumpleaños',
                'type': 'ir.actions.act_url',
                'url': "web/content/?model=hr.birthday.list&id=" + str(
                    self.id) + "&filename_field=excel_file_name&field=excel_file&download=true&filename=" + self.excel_file_name,
                'target': 'self',
            }
            return action