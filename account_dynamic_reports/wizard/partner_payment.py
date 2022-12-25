from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta, date
import calendar
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import json
import io
from odoo.tools import date_utils

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

FETCH_RANGE = 2500
import logging

_logger = logging.getLogger(__name__)
DATE_DICT = {
    '%m/%d/%Y': 'mm/dd/yyyy',
    '%Y/%m/%d': 'yyyy/mm/dd',
    '%m/%d/%y': 'mm/dd/yy',
    '%d/%m/%Y': 'dd/mm/yyyy',
    '%d/%m/%y': 'dd/mm/yy',
    '%d-%m-%Y': 'dd-mm-yyyy',
    '%d-%m-%y': 'dd-mm-yy',
    '%m-%d-%Y': 'mm-dd-yyyy',
    '%m-%d-%y': 'mm-dd-yy',
    '%Y-%m-%d': 'yyyy-mm-dd',
    '%f/%e/%Y': 'm/d/yyyy',
    '%f/%e/%y': 'm/d/yy',
    '%e/%f/%Y': 'd/m/yyyy',
    '%e/%f/%y': 'd/m/yy',
    '%f-%e-%Y': 'm-d-yyyy',
    '%f-%e-%y': 'm-d-yy',
    '%e-%f-%Y': 'd-m-yyyy',
    '%e-%f-%y': 'd-m-yy'
}


class InsPartnerPayment(models.TransientModel):
    _name = "ins.partner.payment"

    @api.onchange('date_range', 'financial_year')
    def onchange_date_range(self):
        if self.date_range:
            date = datetime.today()
            if self.date_range == 'today':
                self.date_from = date.strftime("%Y-%m-%d")
                self.date_to = date.strftime("%Y-%m-%d")
            if self.date_range == 'this_week':
                day_today = date - timedelta(days=date.weekday())
                self.date_from = (
                    day_today - timedelta(days=date.weekday())).strftime("%Y-%m-%d")
                self.date_to = (day_today + timedelta(days=6)
                                ).strftime("%Y-%m-%d")
            if self.date_range == 'this_month':
                self.date_from = datetime(
                    date.year, date.month, 1).strftime("%Y-%m-%d")
                self.date_to = datetime(
                    date.year, date.month, calendar.mdays[date.month]).strftime("%Y-%m-%d")
            if self.date_range == 'this_quarter':
                if int((date.month - 1) / 3) == 0:  # First quarter
                    self.date_from = datetime(
                        date.year, 1, 1).strftime("%Y-%m-%d")
                    self.date_to = datetime(
                        date.year, 3, calendar.mdays[3]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 1:  # Second quarter
                    self.date_from = datetime(
                        date.year, 4, 1).strftime("%Y-%m-%d")
                    self.date_to = datetime(
                        date.year, 6, calendar.mdays[6]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 2:  # Third quarter
                    self.date_from = datetime(
                        date.year, 7, 1).strftime("%Y-%m-%d")
                    self.date_to = datetime(
                        date.year, 9, calendar.mdays[9]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 3:  # Fourth quarter
                    self.date_from = datetime(
                        date.year, 10, 1).strftime("%Y-%m-%d")
                    self.date_to = datetime(
                        date.year, 12, calendar.mdays[12]).strftime("%Y-%m-%d")
            if self.date_range == 'this_financial_year':
                if self.financial_year == 'january_december':
                    self.date_from = datetime(
                        date.year, 1, 1).strftime("%Y-%m-%d")
                    self.date_to = datetime(
                        date.year, 12, 31).strftime("%Y-%m-%d")
                if self.financial_year == 'april_march':
                    if date.month < 4:
                        self.date_from = datetime(
                            date.year - 1, 4, 1).strftime("%Y-%m-%d")
                        self.date_to = datetime(
                            date.year, 3, 31).strftime("%Y-%m-%d")
                    else:
                        self.date_from = datetime(
                            date.year, 4, 1).strftime("%Y-%m-%d")
                        self.date_to = datetime(
                            date.year + 1, 3, 31).strftime("%Y-%m-%d")
                if self.financial_year == 'july_june':
                    if date.month < 7:
                        self.date_from = datetime(
                            date.year - 1, 7, 1).strftime("%Y-%m-%d")
                        self.date_to = datetime(
                            date.year, 6, 30).strftime("%Y-%m-%d")
                    else:
                        self.date_from = datetime(
                            date.year, 7, 1).strftime("%Y-%m-%d")
                        self.date_to = datetime(
                            date.year + 1, 6, 30).strftime("%Y-%m-%d")
            date = (datetime.now() - relativedelta(days=1))
            if self.date_range == 'yesterday':
                self.date_from = date.strftime("%Y-%m-%d")
                self.date_to = date.strftime("%Y-%m-%d")
            date = (datetime.now() - relativedelta(days=7))
            if self.date_range == 'last_week':
                day_today = date - timedelta(days=date.weekday())
                self.date_from = (
                    day_today - timedelta(days=date.weekday())).strftime("%Y-%m-%d")
                self.date_to = (day_today + timedelta(days=6)
                                ).strftime("%Y-%m-%d")
            date = (datetime.now() - relativedelta(months=1))
            if self.date_range == 'last_month':
                self.date_from = datetime(
                    date.year, date.month, 1).strftime("%Y-%m-%d")
                self.date_to = datetime(
                    date.year, date.month, calendar.mdays[date.month]).strftime("%Y-%m-%d")
            date = (datetime.now() - relativedelta(months=3))
            if self.date_range == 'last_quarter':
                if int((date.month - 1) / 3) == 0:  # First quarter
                    self.date_from = datetime(
                        date.year, 1, 1).strftime("%Y-%m-%d")
                    self.date_to = datetime(
                        date.year, 3, calendar.mdays[3]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 1:  # Second quarter
                    self.date_from = datetime(
                        date.year, 4, 1).strftime("%Y-%m-%d")
                    self.date_to = datetime(
                        date.year, 6, calendar.mdays[6]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 2:  # Third quarter
                    self.date_from = datetime(
                        date.year, 7, 1).strftime("%Y-%m-%d")
                    self.date_to = datetime(
                        date.year, 9, calendar.mdays[9]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 3:  # Fourth quarter
                    self.date_from = datetime(
                        date.year, 10, 1).strftime("%Y-%m-%d")
                    self.date_to = datetime(
                        date.year, 12, calendar.mdays[12]).strftime("%Y-%m-%d")
            date = (datetime.now() - relativedelta(years=1))
            if self.date_range == 'last_financial_year':
                if self.financial_year == 'january_december':
                    self.date_from = datetime(
                        date.year, 1, 1).strftime("%Y-%m-%d")
                    self.date_to = datetime(
                        date.year, 12, 31).strftime("%Y-%m-%d")
                if self.financial_year == 'april_march':
                    if date.month < 4:
                        self.date_from = datetime(
                            date.year - 1, 4, 1).strftime("%Y-%m-%d")
                        self.date_to = datetime(
                            date.year, 3, 31).strftime("%Y-%m-%d")
                    else:
                        self.date_from = datetime(
                            date.year, 4, 1).strftime("%Y-%m-%d")
                        self.date_to = datetime(
                            date.year + 1, 3, 31).strftime("%Y-%m-%d")
                if self.financial_year == 'july_june':
                    if date.month < 7:
                        self.date_from = datetime(
                            date.year - 1, 7, 1).strftime("%Y-%m-%d")
                        self.date_to = datetime(
                            date.year, 6, 30).strftime("%Y-%m-%d")
                    else:
                        self.date_from = datetime(
                            date.year, 7, 1).strftime("%Y-%m-%d")
                        self.date_to = datetime(
                            date.year + 1, 6, 30).strftime("%Y-%m-%d")

    @api.model
    def _get_default_date_range(self):
        return self.env.company.date_range

    @api.model
    def _get_default_financial_year(self):
        return self.env.company.financial_year

    @api.model
    def _get_default_company(self):
        return self.env.company

    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, 'Partner Payment'))
        return res

    financial_year = fields.Selection(
        [('april_march', '1 April to 31 March'),
         ('july_june', '1 july to 30 June'),
         ('january_december', '1 Jan to 31 Dec')],
        string='Financial Year', default=_get_default_financial_year)

    date_range = fields.Selection(
        [('today', 'Today'),
         ('this_week', 'This Week'),
         ('this_month', 'This Month'),
         ('this_quarter', 'This Quarter'),
         ('this_financial_year', 'This Financial Year'),
         ('yesterday', 'Yesterday'),
         ('last_week', 'Last Week'),
         ('last_month', 'Last Month'),
         ('last_quarter', 'Last Quarter'),
         ('last_financial_year', 'Last Financial Year')],
        string='Date Range', default=_get_default_date_range
    )
    payment_type = fields.Selection(
        [('outbound', 'Send Money'),
         ('inbound', 'Receive Money')],
        string='Payment Type',required=False
    )
    partner_type = fields.Selection(
        [('customer', 'Customer'),
         ('supplier', 'Supplier')],
        string='Partner Type', required=False
    )
    reconciled = fields.Selection([('reconciled','Reconciled Only'),
                                   ('unreconciled','Unreconciled Only')],
                                  string='Reconcile Type')
    date_from = fields.Date(
        string='Start date',
    )
    date_to = fields.Date(
        string='End date',
    )
    account_ids = fields.Many2many(
        'account.account', string='Accounts'
    )
    journal_ids = fields.Many2many(
        'account.journal', string='Journals',
    )
    partner_ids = fields.Many2many(
        'res.partner', string='Partners'
    )
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=_get_default_company
    )
    include_details = fields.Boolean(
        string='Include Details', default=True
    )
    type = fields.Selection([('receivable','Receivable Accounts Only'),
                              ('payable','Payable Accounts Only')], string='Type')
    display_accounts = fields.Selection(
        [('all', 'All'),
         ('balance_not_zero', 'With balance not equal to zero')], string='Display accounts',
        default='balance_not_zero', required=True
    )
    @api.model
    def create(self, vals):
        ret = super(InsPartnerPayment, self).create(vals)
        return ret

    def write(self, vals):

        if vals.get('date_range'):
            vals.update({'date_from': False, 'date_to': False})
        if vals.get('date_from') and vals.get('date_to'):
            vals.update({'date_range': False})

        if vals.get('partner_ids'):
            vals.update({'partner_ids': vals.get('partner_ids')})
        if vals.get('partner_ids') == []:
            vals.update({'partner_ids': [(5,)]})
        if vals.get('journal_ids'):
            vals.update({'journal_ids': vals.get('journal_ids')})
        if vals.get('journal_ids') == []:
            vals.update({'journal_ids': [(5,)]})
        if vals.get('account_ids'):
            vals.update({'account_ids': vals.get('account_ids')})
        if vals.get('account_ids') == []:
            vals.update({'account_ids': [(5,)]})

        ret = super(InsPartnerPayment, self).write(vals)
        return ret

    def validate_data(self):
        if self.date_from > self.date_to:
            raise ValidationError(_('"Date from" must be less than or equal to "Date to"'))
        return True

    def process_filters(self):
        ''' To show on report headers'''

        data = self.get_filters(default_filters={})

        filters = {}

        filters['partner_type'] = ''
        if data.get('partner_type') == 'customer':
            filters['partner_type'] = 'Customers'
        if data.get('partner_type') == 'supplier':
            filters['partner_type'] = 'Suppliers'

        filters['payment_type'] = ''
        if data.get('payment_type') == 'inbound':
            filters['payment_type'] = 'Received Money'
        if data.get('payment_type') == 'outbound':
            filters['payment_type'] = 'Send Money'


        if data.get('journal_ids', []):
            filters['journals'] = self.env['account.journal'].browse(data.get('journal_ids', [])).mapped('code')
        else:
            filters['journals'] = ['All']
        if data.get('account_ids', []):
            filters['accounts'] = self.env['account.account'].browse(data.get('account_ids', [])).mapped('code')
        else:
            filters['accounts'] = ['All']

        if data.get('partner_ids', []):
            filters['partners'] = self.env['res.partner'].browse(data.get('partner_ids', [])).mapped('name')
        else:
            filters['partners'] = ['All']

        if data.get('date_from', False):
            filters['date_from'] = data.get('date_from')
        if data.get('date_to', False):
            filters['date_to'] = data.get('date_to')

        filters['reconciled'] = '-'
        if data.get('reconciled') == 'reconciled':
            filters['reconciled'] = 'Yes'
        if data.get('reconciled') == 'unreconciled':
            filters['reconciled'] = 'No'

        if data.get('company_id'):
            filters['company_id'] = data.get('company_id')
        else:
            filters['company_id'] = ''

        if data.get('include_details'):
            filters['include_details'] = True
        else:
            filters['include_details'] = False

        filters['journals_list'] = data.get('journals_list')
        filters['accounts_list'] = data.get('accounts_list')
        filters['partners_list'] = data.get('partners_list')
        #filters['category_list'] = data.get('category_list')
        filters['company_name'] = data.get('company_name')

        return filters

    def build_where_clause(self, data=False):
        if not data:
            data = self.get_filters(default_filters={})

        if data:

            WHERE = '(1=1)'

            if data.get('reconciled') == 'reconciled':
                WHERE += ' AND pay.move_reconciled_state'
            if data.get('reconciled') == 'unreconciled':
                WHERE += ' AND NOT pay.move_reconciled_state'

            if data.get('payment_type'):
                WHERE += " AND pay.payment_type = '%s'"%(data.get('payment_type'))

            if data.get('partner_type'):
                WHERE += " AND pay.partner_type = '%s'" % (data.get('partner_type'))

            if data.get('journal_ids', []):
                WHERE += ' AND j.id IN %s' % str(tuple(data.get('journal_ids')) + tuple([0]))

            if data.get('account_ids', []):
                WHERE += ' AND a.id IN %s' % str(tuple(data.get('account_ids')) + tuple([0]))

            if data.get('partner_ids', []):
                WHERE += ' AND p.id IN %s' % str(tuple(data.get('partner_ids')) + tuple([0]))

            if data.get('company_id', False):
                WHERE += ' AND com.id = %s' % data.get('company_id')

            WHERE += " AND m.state IN ('posted')"

            # if data.get('target_moves') == 'posted_only':
            #     WHERE += " AND m.state = 'posted'"
            return WHERE


    def build_detailed_move_lines(self, payment=0, internal_type='payment', fetch_range=FETCH_RANGE):
        '''
        It is used for showing detailed move lines as sub lines. It is defered loading compatable
        :param offset: It is nothing but page numbers. Multiply with fetch_range to get final range
        :param payment: Integer - Payment ID
        :param fetch_range: Global Variable. Can be altered from calling model
        :return: count(int-Total rows without offset), offset(integer), move_lines(list )
        '''
        move_lines = []
        aml_lines = []
        payments = self.env['account.payment'].browse(payment)
        for payment in payments:
            for line in payment.move_id.line_ids:
                if line.account_id.reconcile:
                    aml_lines.append(line.id)

        for aml in self.env['account.move.line'].browse(aml_lines):
            # Debit ids
            for debit_line in aml.matched_debit_ids:
                matched_lines = {
                    'date': debit_line.credit_move_id.date,
                    'ref': debit_line.debit_move_id.move_id.name,
                    'description': debit_line.credit_move_id.payment_id.ref or
                                    debit_line.credit_move_id.payment_id.payment_reference or
                                   debit_line.credit_move_id.ref or
                                   debit_line.credit_move_id.name,
                    'doc_amount': debit_line.debit_move_id.balance,
                    'knock_off_amount': debit_line.amount,
                    'knock_off_in_currency': debit_line.credit_move_id.amount_currency,
                    'move_id': debit_line.credit_move_id.move_id.id,
                    'analytic_account_id': debit_line.credit_move_id.analytic_account_id and
                                    debit_line.credit_move_id.analytic_account_id.id,
                    'analytic_account_string': debit_line.credit_move_id.analytic_account_id and
                                           debit_line.credit_move_id.analytic_account_id.name or '',
                    'analytic_tags_ids': [' ,'.join(tag.name) for tag in
                                          debit_line.credit_move_id.analytic_tag_ids],
                    'currency_id': debit_line.credit_move_id.payment_id.currency_id.id,
                    'currency_symbol': debit_line.credit_move_id.payment_id.currency_id.symbol,
                    'currency_precision': debit_line.credit_move_id.payment_id.currency_id.rounding,
                    'currency_position': debit_line.credit_move_id.payment_id.currency_id.position,
                    'company_currency_id': debit_line.credit_move_id.payment_id.company_id.currency_id.id,
                    'company_currency_symbol': debit_line.credit_move_id.payment_id.company_id.currency_id.symbol,
                    'company_currency_position': debit_line.credit_move_id.payment_id.company_id.currency_id.position,
                    'company_currency_precision': debit_line.credit_move_id.payment_id.company_id.currency_id.rounding,
                }
                move_lines.append(matched_lines)
            # Credit ids
            for credit_line in aml.matched_credit_ids:
                matched_lines = {
                    'date': credit_line.debit_move_id.date,
                    'ref': credit_line.credit_move_id.move_id.name,
                    'description': credit_line.debit_move_id.payment_id.ref or
                                    credit_line.debit_move_id.ref or
                                    credit_line.debit_move_id.name,
                    'doc_amount': credit_line.credit_move_id.balance,
                    'knock_off_amount': credit_line.amount,
                    'knock_off_in_currency': credit_line.debit_move_id.amount_currency,
                    'move_id': credit_line.debit_move_id.move_id.id,
                    'analytic_account_id': credit_line.debit_move_id.analytic_account_id and
                                    credit_line.debit_move_id.analytic_account_id.id,
                    'analytic_account_string': credit_line.debit_move_id.analytic_account_id and
                                           credit_line.debit_move_id.analytic_account_id.name or '',
                    'analytic_tags_ids': [', '.join(tag.name) for tag in
                                          credit_line.debit_move_id.analytic_tag_ids],
                    'currency_id': credit_line.debit_move_id.payment_id.currency_id.id,
                    'currency_symbol': credit_line.debit_move_id.payment_id.currency_id.symbol,
                    'currency_precision': credit_line.debit_move_id.payment_id.currency_id.rounding,
                    'currency_position': credit_line.debit_move_id.payment_id.currency_id.position,
                    'company_currency_id': credit_line.debit_move_id.payment_id.company_id.currency_id.id,
                    'company_currency_symbol': credit_line.debit_move_id.payment_id.company_id.currency_id.symbol,
                    'company_currency_position': credit_line.debit_move_id.payment_id.company_id.currency_id.position,
                    'company_currency_precision': credit_line.debit_move_id.payment_id.company_id.currency_id.rounding,
                }
                move_lines.append(matched_lines)
        return move_lines

    def process_data(self):
        '''
        It is the method for showing summary details of each accounts. Just basic details to show up
        Three sections,
        1. Initial Balance
        2. Current Balance
        3. Final Balance
        :return:
        '''
        cr = self.env.cr

        data = self.get_filters(default_filters={})


        ################## data from Receipts##########################################

        WHERE = self.build_where_clause(data)

        move_lines = []

        WHERE_FULL = WHERE + " AND m.date >= '%s'" % data.get('date_from') + " AND m.date <= '%s'" % data.get(
            'date_to')
        sql = ('''
            SELECT
                pay.id AS payid,
                pay.partner_id AS partner_id,
                m.date AS payment_date,
                pay.currency_id,
                m.name AS lname,
                pay.payment_type AS payment_type,
                pay.payment_reference AS journal_entry,
                m.ref AS ref,
                m.journal_id AS journal,
                m.payment_state AS reco_state,
                'payment' AS internal_type,
                j.code AS journal_code,
                c.symbol AS currency_symbol,
                c.position AS currency_position,
                c.rounding AS currency_precision,
                cc.id AS company_currency_id,
                cc.symbol AS company_currency_symbol,
                cc.rounding AS company_currency_precision,
                cc.position AS company_currency_position,
                p.name AS partner_name,
                COALESCE(pay.amount,0) AS amount_currency,
                ABS(COALESCE(pay.unreconciled_amount,0)) AS amount_unreconciled
            FROM account_payment pay
            LEFT JOIN res_currency c ON (pay.currency_id=c.id)
            LEFT JOIN res_partner p ON (pay.partner_id=p.id)
            LEFT JOIN account_move m ON (pay.move_id=m.id)
            JOIN account_journal j ON (m.journal_id=j.id)
            LEFT JOIN res_company com ON (j.company_id=com.id)
            LEFT JOIN res_currency cc ON (com.currency_id=cc.id)
            WHERE %s
            ORDER BY m.date asc, pay.partner_id 
        ''') % WHERE_FULL
        cr.execute(sql)
        for row in cr.dictfetchall():
            move_lines.append(row)
        return move_lines

    def get_page_list(self, total_count):
        '''
        Helper function to get list of pages from total_count
        :param total_count: integer
        :return: list(pages) eg. [1,2,3,4,5,6,7 ....]
        '''
        page_count = int(total_count / FETCH_RANGE)
        if total_count % FETCH_RANGE:
            page_count += 1
        return [i+1 for i in range(0, int(page_count))] or []

    def get_filters(self, default_filters={}):

        self.onchange_date_range()
        company_id = self.env.company
        company_domain = [('company_id', '=', company_id.id)]
        partner_company_domain = [('parent_id','=', False),
                                    '|',
                                    ('customer_rank', '>', 0),
                                    ('supplier_rank', '>', 0),
                                    '|',
                                    ('company_id', '=', company_id.id),
                                    ('company_id', '=', False)]

        journals = self.journal_ids if self.journal_ids else self.env['account.journal'].search(company_domain)
        accounts = self.account_ids if self.account_ids else self.env['account.account'].search(company_domain)
        partners = self.partner_ids if self.partner_ids else self.env['res.partner'].search(partner_company_domain)
        #categories = self.partner_category_ids if self.partner_category_ids else self.env['res.partner.category'].search([])

        filter_dict = {
            'journal_ids': self.journal_ids.ids,
            'account_ids': self.account_ids.ids,
            'partner_ids': self.partner_ids.ids,
            'company_id': self.company_id and self.company_id.id or False,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'reconciled': self.reconciled,
            'partner_type': self.partner_type,
            'payment_type': self.payment_type,
            'include_details': self.include_details,
            'journals_list': [(j.id, j.name) for j in journals],
            'accounts_list': [(a.id, a.name) for a in accounts],
            'partners_list': [(p.id, p.name) for p in partners],
            'company_name': self.company_id and self.company_id.name,
        }
        filter_dict.update(default_filters)
        return filter_dict

    def get_report_datas(self, default_filters={}, call_from=False):
        '''
        Main method for pdf, xlsx and js calls
        :param default_filters: Use this while calling from other methods. Just a dict
        :return: All the datas for GL
        '''
        if self.validate_data():
            filter = self.process_filters()
            account_lines = self.process_data()
            _logger.info('\n\n%r',account_lines)
            if call_from:
                for line in account_lines:
                    sub_lines = self.build_detailed_move_lines(payment=line['payid'], internal_type=line['internal_type'])
                    line.update({'sub_lines': sub_lines})
            return filter, account_lines

    def action_pdf(self):
        filters, account_lines = self.get_report_datas(call_from=True)
        return self.env.ref(
            'account_dynamic_reports'
            '.action_print_partner_payment').with_context(landscape=True).report_action(
            self, data={'Ledger_data': account_lines,
                        'Filters': filters
                        })

    def action_xlsx(self):
        ''' Button function for Xlsx '''
        data = self.read()
        as_on_date = fields.Date.from_string(self.date_to).strftime(
            self.env['res.lang'].search([('code', '=', self.env.user.lang)])[0].date_format)
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'ins.partner.payment',
                        'options': json.dumps(data[0], default=date_utils.json_default),
                        'output_format': 'xlsx',
                        'report_name': 'Ageing as On - %s' % (as_on_date),
                        },
            'report_type': 'xlsx'
        }

    def get_xlsx_report(self, data, response):
        # Initialize
        #############################################################
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Partner Ageing')
        sheet.set_zoom(95)
        sheet_2 = workbook.add_worksheet('Filters')
        sheet_2.protect()

        record = self.env['ins.partner.payment'].browse(data.get('id', [])) or False
        filter, account_lines = record.get_report_datas()
        
        # Formats
        ############################################################
        sheet.set_column(0, 0, 12)
        sheet.set_column(1, 1, 18)
        sheet.set_column(2, 2, 30)
        sheet.set_column(3, 3, 18)
        sheet.set_column(4, 4, 30)
        sheet.set_column(5, 5, 18)
        sheet.set_column(6, 6, 12)
        sheet.set_column(7, 7, 15)
        sheet.set_column(8, 8, 10)
        sheet.set_column(9, 9, 10)

        sheet_2.set_column(0, 0, 35)
        sheet_2.set_column(1, 1, 25)
        sheet_2.set_column(2, 2, 25)
        sheet_2.set_column(3, 3, 25)
        sheet_2.set_column(4, 4, 25)
        sheet_2.set_column(5, 5, 25)
        sheet_2.set_column(6, 6, 25)


        sheet.freeze_panes(4, 0)
        sheet.screen_gridlines = False
        sheet_2.screen_gridlines = False
        sheet_2.protect()
        sheet.set_zoom(75)
        """ Add cell formats to current workbook.
        Available formats:
         * format_title
         * format_header
        """
        format_title = workbook.add_format({
            'bold': True,
            'align': 'center',
            'font_size': 12,
            'font': 'Arial',
            'border': False
        })
        format_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial',
            # 'border': True
        })
        content_header = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            'border': True,
            'font': 'Arial',
        })
        content_header_date = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'border': True,
            'align': 'center',
            'font': 'Arial',
        })
        line_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'center',
            'top': True,
            'bottom': True,
            'font': 'Arial',
            'bg_color': '#FFC7CE'
        })
        line_header_date = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'center',
            'top': True,
            'bottom': True,
            'font': 'Arial',
            'bg_color': '#FFC7CE'
        })
        line_header_light = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            'text_wrap': True,
            'font': 'Arial',
            'valign': 'top'
        })
        line_header_light_date = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial',
        })
        line_header_light_initial = workbook.add_format({
            'italic': True,
            'font_size': 10,
            'align': 'center',
            'bottom': True,
            'font': 'Arial',
            'valign': 'top'
        })
        line_header_light_ending = workbook.add_format({
            'italic': True,
            'font_size': 10,
            'align': 'center',
            'top': True,
            'font': 'Arial',
            'valign': 'top'
        })
        lang = self.env.user.lang
        lang_id = self.env['res.lang'].search([('code', '=', lang)])[0]
        currency_id = self.env.company.currency_id
        line_header.num_format = currency_id.excel_format
        line_header_light.num_format = currency_id.excel_format
        line_header_light_initial.num_format = currency_id.excel_format
        line_header_light_ending.num_format = currency_id.excel_format
        line_header_light_date.num_format = DATE_DICT.get(
            lang_id.date_format, 'dd/mm/yyyy')
        content_header_date.num_format = DATE_DICT.get(
            lang_id.date_format, 'dd/mm/yyyy')
        line_header_date.num_format = DATE_DICT.get(
            lang_id.date_format, 'dd/mm/yyyy')


        # Write data
        ################################################################
        row_pos_2 = 0
        row_pos = 0
        sheet.merge_range(0, 0, 0, 8, 'Partner payment' + ' - ' + data['company_id'][1], format_title)

        # Write filters
        sheet_2.write(row_pos_2, 0, _('Date from'), format_header)
        datestring = fields.Date.from_string(str(filter['date_from'])).strftime(lang_id.date_format)
        sheet_2.write(row_pos_2, 1, datestring or '', content_header_date)
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Date to'), format_header)
        datestring = fields.Date.from_string(str(filter['date_to'])).strftime(lang_id.date_format)
        sheet_2.write(row_pos_2, 1, datestring or '', content_header_date)
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Target moves'), format_header)
        sheet_2.write(row_pos_2, 1, filter['type'], content_header)
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Display accounts'), format_header)
        sheet_2.write(row_pos_2, 1, filter['display_accounts'], content_header)
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Reconciled'), format_header)
        sheet_2.write(row_pos_2, 1, filter['reconciled'], content_header)
        row_pos_2 += 1
        # sheet_2.write(row_pos_2, 0, _('Payment type'), format_header)
        # sheet_2.write(row_pos_2, 1, filter['payment_type'], content_header)
        # row_pos_2 += 1
        # Journals
        row_pos_2 += 2
        sheet_2.write(row_pos_2, 0, _('Journals'), format_header)
        j_list = ', '.join([lt or '' for lt in filter.get('journals')])
        sheet_2.write(row_pos_2, 1, j_list, content_header)
        # Partners
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Partners'), format_header)
        p_list = ', '.join([lt or '' for lt in filter.get('partners')])
        sheet_2.write(row_pos_2, 1, p_list, content_header)
        # Partner Tags
        # row_pos_2 += 1
        # sheet_2.write(row_pos_2, 0, _('Partner Tag'), format_header)
        # p_list = ', '.join([lt or '' for lt in filter.get('categories')])
        # sheet_2.write(row_pos_2, 1, p_list, content_header)
        # Accounts
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Accounts'), format_header)
        a_list = ', '.join([lt or '' for lt in filter.get('accounts')])
        sheet_2.write(row_pos_2, 1, a_list, content_header)
       
       
        # Write Ledger details
        # row_pos += 3
        # if filter.get('include_details'):
        #     sheet.write(row_pos, 0, _('Date'), format_header)
        #     sheet.write(row_pos, 1, _('Number'), format_header)
        #     sheet.write(row_pos, 2, _('Partner'), format_header)
        #     sheet.write(row_pos, 3, _('Journal'), format_header)
        #     sheet.write(row_pos, 4, _('Journal Entry'), format_header)
        #     sheet.write(row_pos, 5, _('Reconciled?'), format_header)
        #     sheet.write(row_pos, 6, _('Amount'), format_header)
        #     sheet.write(row_pos, 7, _('Unreconciled Amount'), format_header)
        # if account_lines:
        #     for line in account_lines:
        #         row_pos += 1
        #         datestring = fields.Date.from_string(str(account_lines[line].get('payment_date'))).strftime(lang_id.date_format)
        #         sheet.write(row_pos, 0, datestring or '', line_header_date)
        #         sheet.write(row_pos, 1, account_lines[line].get('lname') or '', line_header)
        #         sheet.write(row_pos, 2, account_lines[line].get('partner_name') or '', line_header)
        #         sheet.write(row_pos, 3, account_lines[line].get('journal_code') or '', line_header)
        #         sheet.write(row_pos, 4, account_lines[line].get('ref') or '', line_header)
        #         sheet.write(row_pos, 5, account_lines[line].get('reco_state'), line_header)
        #         sheet.write(row_pos, 6, float(account_lines[line].get('amount_currency') or 0, line_header))
        #         sheet.write(row_pos, 7, float(account_lines[line].get('amount_unreconciled') or 0, line_header))
                
                # if filter.get('include_details', False):
                #     count, offset, sub_lines = record.build_detailed_move_lines(offset=0, partner=line, fetch_range=1000000)

                # for sub_line in sub_lines:
                #     row_pos += 1
                #     sheet.write(row_pos, 1, _('Date'),format_header)
                #     sheet.write(row_pos, 2, _('Reference'),format_header)
                #     sheet.write(row_pos, 3, _('Description'),format_header)
                #     sheet.write(row_pos, 4, _('Analytic Account'),format_header)
                #     sheet.write(row_pos, 5, _('Analytic Tags'),format_header)
                #     sheet.write(row_pos, 6, _('Doc Amount'), format_header)
                #     sheet.write(row_pos, 7, _('Knock-off Amount'),format_header)
                #     row_pos += 1
                #     datestring = fields.Date.from_string(str( sub_line.get('date'))).strftime(lang_id.date_format)
                #     sheet.write(row_pos, 1, datestring or '',  line_header_light_date)
                #     sheet.write(row_pos, 2, sub_line.get('ref') or '',line_header_light)
                #     sheet.write(row_pos, 3, sub_line.get('description') or '', line_header_light)
                #     sheet.wwrite(row_pos, 4, sub_line.get('analytic_account_string') or '', line_header_light)
                #     sheet.write(row_pos, 5, sub_line.get('analytic_tag_ids') or '', line_header_light)
                #     sheet.write(row_pos, 6, sub_line.get('doc_amount', '0') or 0, line_header_light)
                #     sheet.write(row_pos, 7, sub_line.get('knock_off_amount', '0') or 0, line_header_light)
                #     _logger.info('\n\n%r',sub_lines)
                # #row_pos += 1
        # Close and return
        #################################################################
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()


    def action_view(self):
        res = {
            'type': 'ir.actions.client',
            'name': 'PP View',
            'tag': 'dynamic.pp',
            'context': {'wizard_id': self.id}
        }
        return res
