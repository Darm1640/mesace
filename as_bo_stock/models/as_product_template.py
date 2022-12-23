# -*- coding: utf-8 -*-
from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class product_template(models.Model):
    _inherit = 'product.template'

    def write(self, vals):
        for obj in self:
            log_cambios = """<span>Cambios realizados</span><br/>
                        <table>
                            <tr>
                                <th style="border : 1px solid grey; padding : 5px; text-align : left;"><b>Campo</b></td>
                                <th style="border : 1px solid grey; padding : 5px; text-align : left;"><b>Valor anterior</b></td>
                                <th style="border : 1px solid grey; padding : 5px; text-align : left;"><b>Valor nuevo</b></td>
                            </tr>
                        """
            for line in vals:
                _logger.debug("\n\nfield type: %s\n\n", str(type(vals[str(line)])))
                if self._fields[line].type == 'many2one':
                    anterior = eval("obj."+str(line)).name
                else:
                    anterior = eval("obj."+str(line))

                anterior = str(anterior) if str(type(anterior)) not in ("<type 'str'>", "<type 'unicode'>") else anterior
                if self._fields[line].type not in ('one2many','many2many'):
                    if self._fields[line].type == 'many2one':
                        nuevo = (str(vals[str(line)]) if str(type(vals[str(line)])) not in ("<type 'str'>", "<type 'unicode'>") else vals[str(line)])
                        if nuevo != 'False':
                            nuevo = self.env[self._fields[line].comodel_name].search([('id','=',nuevo)])
                            nuevo = nuevo.name
                            _logger.debug("\n SALIDA: %s\n", nuevo)
                            log_cambios += """
                            <tr>
                                <td style="border : 1px solid grey; padding : 5px; text-align : left;">"""+str(self._fields[line].string)+"""</td>
                                <td style="border : 1px solid grey; padding : 5px; text-align : left;">"""+anterior+"""</td>
                                <td style="border : 1px solid grey; padding : 5px; text-align : left;">"""+nuevo+"""</td>
                            </tr>
                            """
                        else:
                            _logger.debug("\n SALIDA: %s\n")
                            log_cambios += """
                            <tr>
                                <td style="border : 1px solid grey; padding : 5px; text-align : left;">"""+str(self._fields[line].string)+"""</td>
                                <td style="border : 1px solid grey; padding : 5px; text-align : left;">"""+anterior+"""</td>
                                <td style="border : 1px solid grey; padding : 5px; text-align : left;">""""""</td>
                            </tr>
                            """
                    else:
                        nuevo = (str(vals[str(line)]) if str(type(vals[str(line)])) not in ("<type 'str'>", "<type 'unicode'>") else vals[str(line)])
                        _logger.debug("\n SALIDA: %s\n", nuevo)
                        log_cambios += """
                        <tr>
                            <td style="border : 1px solid grey; padding : 5px; text-align : left;">"""+str(self._fields[line].string)+"""</td>
                            <td style="border : 1px solid grey; padding : 5px; text-align : left;">"""+anterior+"""</td>
                            <td style="border : 1px solid grey; padding : 5px; text-align : left;">"""+nuevo+"""</td>
                        </tr>
                        """


                    log_cambios += "</table>"
                    obj.message_post(body=log_cambios)
        result = super(product_template, self).write(vals)
        return result

    def _compute_location_ids(self):
        """
        Compute method for location_ids - as all internal locations

        Extra info:
         * To show only viable location (with positive inventories) we filter locations already in js
         * We should include inactive locations, since configurable inputs are deactivated
         * No restrictionon company_id, since it managed by security rules
        """
        for product_id in self:
            location_ids = self.env["stock.location"].search([
                ('usage', '=', 'internal'),
                "|",
                    ("active", "=", True),
                    ("active", "=", False),
            ])
            product_id.location_ids = [(6, 0, location_ids.ids)]
    
    def action_prepare_xlsx_balance(self):
        """
        The method to make .xlsx table of stock balances

        1. Prepare workbook and styles
        2. Prepare header row
          2.1 Get column name like 'A' or 'S' (ascii char depends on counter)
        3. Prepare each row of locations
        4. Create an attachment

        Returns:
         * action of downloading the xlsx table

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        if not xlsxwriter:
            raise UserError(_("The Python library xlsxwriter is installed. Contact your system administrator"))
        # 1
        file_path = tempfile.mktemp(suffix='.xlsx')
        workbook = xlsxwriter.Workbook(file_path)
        styles = {
            'main_header_style': workbook.add_format({
                'bold': True,
                'font_size': 11,
                'border': 1,
            }),
            'main_data_style': workbook.add_format({
                'font_size': 11,
                'border': 1,
            }),
        }
        worksheet = workbook.add_worksheet(u"{}#{}.xlsx".format(self.name, fields.Date.today()))
        # 2
        cur_column = 0
        for column in [_("Ubicacion"), _("Costo"), _("Stock"), _("Prevista"), _("Entrante"), _("Saliente")]:
            worksheet.write(0, cur_column, column, styles.get("main_header_style"))
            # 2.1
            col_letter = chr(cur_column + 97).upper()
            column_width = cur_column == 0 and 60 or 8
            worksheet.set_column('{c}:{c}'.format(c=col_letter), column_width)
            cur_column += 1
        # 3
        elements = []
        for loc in self.location_ids:
            balances = loc._return_balances()
            if balances:
                elements.append({
                    "name": loc.name,
                    "id": loc.id,
                    "value": balances.get("value"),
                    "qty_available": balances.get("qty_available"),
                    "incoming_qty": balances.get("incoming_qty"),
                    "outgoing_qty": balances.get("outgoing_qty"),
                    "virtual_available": balances.get("virtual_available"),
                })
        elements = self.env["stock.location"].prepare_elements_for_hierarchy(args={"elements": elements})
        row = 1
        for loc in elements:
            spaces = ""
            level = loc.get("level")
            itera = 0
            while itera != level:
                spaces += "    "
                itera += 1
            instance = (
                spaces + loc.get("name"),
                loc.get("value"),
                loc.get("qty_available"),
                loc.get("virtual_available"),
                loc.get("incoming_qty"),
                loc.get("outgoing_qty"),
            )
            for counter, column in enumerate(instance):
                value = column
                worksheet.write(
                    row,
                    counter,
                    value,
                    styles.get("main_data_style")
                )
            row += 1
        workbook.close()
        # 4
        with open(file_path, 'rb') as r:
            xls_file = base64.b64encode(r.read())
        att_vals = {
            'name':  u"{}#{}.xlsx".format(self.name, fields.Date.today()),
            'type': 'binary',
            'datas': xls_file,
            'datas_fname': u"{}#{}.xlsx".format(self.name, fields.Date.today()),
        }
        attachment_id = self.env['ir.attachment'].create(att_vals)
        self.env.cr.commit()
        action = {
            'type': 'ir.actions.act_url',
            'url': '/web/content/{}?download=true'.format(attachment_id.id,),
            'target': 'self',
        }
        return action

