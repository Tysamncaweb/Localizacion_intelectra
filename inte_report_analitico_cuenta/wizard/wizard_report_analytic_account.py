# coding: utf-8

###############################################################################

from odoo.osv import  osv
from odoo.tools.translate import _
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from datetime import datetime, date
from odoo.exceptions import ValidationError


class WizardReportAnalytic(models.TransientModel):
    _name = 'wizard.report.analytic.account'
    _description = "Wizard Report Analytic Account"

    move_dest = fields.Selection(selection=[('all', 'Todos asientos'),
                                            ('validate', _('Todos los asientos validados'))],
        string='Destiny Move',
        required=True,
        default='all',
        help="Destiny Move help")

    cuentas_contables = fields.Selection(
        string= "Mostrar Cuenta",
        selection=[('all', 'Todas las cuentas'),
                   ('move', 'Cuentas con movimiento'),
                   ('saldo_cero','Con saldo distinto a cero')
                  ], default='all'
    )

    date_start = fields.Date('Fecha inicio')
    date_end = fields.Date('Fecha fin')
    num_cuenta_contables = fields.Many2one('account.account')
    company = fields.Many2one('res.company')
    saldo_inicial = fields.Boolean('Saldo inicial',default=False)
    currency_id = fields.Many2one('res.currency')
    ordenado_fecha = fields.Boolean(string="Ordenado por:")
    cuenta_especifica = fields.Boolean(string= "Cuenta especifica")
    report = fields.Binary('Prepared file', filters='.xls', readonly=True)

    @api.onchange('cuentas_contables','cuenta_especifica')
    def _onchange_cuentas(self):
        if self.cuentas_contables == 'all' and self.cuenta_especifica== True:
            self.cuenta_especifica = False
            self.num_cuenta_contables = ""

    '''@api.onchange('date_start','date_end')
    def _onchange_fecha(self):
        fecha_inicio = self.date_start
        fecha_fin = self.date_end

        if datetime.strptime(fecha_inicio, DATE_FORMAT) >= datetime.strptime(fecha_fin, DATE_FORMAT):
            raise ValidationError('Advertencia! La fecha de inicio no puede ser superior a la fecha final')'''

    def _get_date_analitico(self):
        if self.date_start == False and self.date_end == False:

            self.date_start = '1900-01-01'
            self.date_end = fields.Date.today()

        elif self.date_start == False and self.date_end != False:
            self.date_start = '1900-01-01'

        elif self.date_start != False and self.date_end == False:
            self.date_end = fields.Date.today()

    '''def _get_currency_analitico(self):
        currency_obj = self.env['res.currency']
        if not self.currency_id:
            currency_obj = currency_obj.search([])
        return currency_obj'''

    def _get_cuentas_contables(self):
        num_cuentas_contables_obj = self.env['account.account']
        if self.cuentas_contables == 'all':
            #num_cuentas_contables_obj = num_cuentas_contables_obj.search([])
            pass
        else:
            num_cuentas_contables_obj = self.num_cuenta_contables
        return num_cuentas_contables_obj
    def print_analitico_xls(self):
        report_obj = self.env['report.inte_report_analitico_cuenta.report_analytic_por_cuenta']
        #datos = report_obj._get_account_move_entry()


    def print_analitico_pdf(self):
        self._get_date_analitico()
        #currency = self._get_currency_analitico()
        num_cuentas_contables = self._get_cuentas_contables()

        fecha_inicio = self.date_start
        fecha_fin = self.date_end

        if datetime.strptime(fecha_inicio, DATE_FORMAT) >= datetime.strptime(fecha_fin, DATE_FORMAT):
            raise ValidationError('Advertencia! La fecha de inicio no puede ser superior a la fecha final')

        datas = [] #self.read(self.ids)[0]
        ids = []
        data = {
            'ids': ids,
            'model': 'report.inte_report_analitico_cuenta.report_analytic_por_cuenta',
            'form': {
                'datas': datas,
                'move_dest': self.move_dest,
                'cuentas_contables': self.cuentas_contables,
                'date_start': self.date_start,
                'date_end': self.date_end,
                'num_cuenta_contables': num_cuentas_contables.id,
                'empresa': self.company.id,
                'saldo_inicial': self.saldo_inicial,
                'currency_id': self.currency_id.id,
                'ordenado_fecha': self.ordenado_fecha,
                'cuenta_especifica': self.cuenta_especifica
                },
        }
        return self.env.ref('inte_report_analitico_cuenta.action_reporte_analitico').report_action(self, data=data, config=False)


class ReportAnalyticForAccount(models.AbstractModel):

    _name = 'report.inte_report_analitico_cuenta.report_analytic_por_cuenta'

    @api.model
    def get_report_values(self, docids, data=None):

        ids = data['ids']
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        move_dest = data['form']['move_dest']
        cuentas_contables = data['form']['cuentas_contables']
        num_cuenta_contables = data['form']['num_cuenta_contables']
        empresa = data['form']['empresa']
        saldo_inicial = data['form']['saldo_inicial']
        currency_id = data['form']['currency_id']
        ordenado_fecha = data['form']['ordenado_fecha']
        cuenta_especifica = data['form']['cuenta_especifica']

        docs = []
        num_cuenta_contables_obj = self.env['account.account']

        # Todas las cuentas
        if cuentas_contables == 'all':
            num_cuenta_contables_obj = num_cuenta_contables_obj.search([])
        #todas las cuentas con cuentas con movimiento
        elif cuentas_contables == 'move' and cuenta_especifica == False:
            num_cuenta_contables_obj = num_cuenta_contables_obj.search([])
        #todas las cuentas con saldo diferente a cero
        elif cuentas_contables == 'saldo_cero' and cuenta_especifica == False:
            num_cuenta_contables_obj = num_cuenta_contables_obj.search([])
        #cuenta especifica con movimiento
        elif cuentas_contables == 'move' and cuenta_especifica == True:
            num_cuenta_contables_obj = num_cuenta_contables_obj.browse(num_cuenta_contables)
        #cuenta especifica con saldo distinto a cero
        elif cuentas_contables == 'saldo_cero' and cuenta_especifica == True:
            num_cuenta_contables_obj = num_cuenta_contables_obj.browse(num_cuenta_contables)

        # accounts = docs if self.model == 'account.account' else self.env['account.account'].search([])
        currency = self._get_moneda(currency_id)
        accounts_res = self._get_account_move_entry(num_cuenta_contables_obj, saldo_inicial, ordenado_fecha, cuentas_contables,move_dest,date_start,date_end,empresa,currency)
        datos_cuentas = self._datos_cuentas_contables(cuentas_contables, num_cuenta_contables)
        ordenado_fecha = self._get_orden(ordenado_fecha)

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'docs': docs,
            'move_dest': move_dest,
            'cuentas_contables': cuentas_contables,
            'num_cuenta_contables': num_cuenta_contables,
            'empresa': empresa,
            'saldo_inicial': saldo_inicial,
            'currency': currency,
            'ordenado_fecha': ordenado_fecha,
            'datos_cuentas': datos_cuentas[0],
            'Account': accounts_res
        }

    @api.model
    def _datos_cuentas_contables(self,cuentas_contables,num_cuenta_contables):
        '''Se obtienen los datos de las cuentas contables para la cabecera del reporte'''
        datos_cuentas = []
        if cuentas_contables == 'all':
            datos_cuentas.append({'codigo': "Todos los códigos",
                                  'nombre': "Todas las cuentas"})
        else:
            account_obj = self.env['account.account']
            account_brw = account_obj.browse(num_cuenta_contables)

            datos_cuentas.append({'codigo': account_brw.code,
                                  'nombre':account_brw.name})
        return datos_cuentas

    @api.model
    def _get_orden(self,ordenado_fecha):
        if ordenado_fecha == True:
            ordenado_fecha = "Fecha"
        else:
            ordenado_fecha = "ninguno"
        return ordenado_fecha

    @api.model
    def _get_moneda(self,currency_id):
        currency_brw = []
        if not currency_id:
            currency_obj = self.env['res.currency'].search([])
            for c in currency_obj:
                currency_brw.append({'codigo': c.id,'nombre':c.name})
        else:
            currency_obj = self.env['res.currency'].browse(currency_id)
            for c in currency_obj:
                currency_brw.append({'codigo': c.id,'nombre':c.name})
        return currency_brw

    def _get_account_move_entry(self, accounts, init_balance, sortby, display_account, move_dest,date_start,date_end,empresa,currency):
        """
        :param:
                accounts: the recordset of accounts
                init_balance: boolean value of initial_balance
                sortby: sorting by date or partner and journal
                display_account: type of account(receivable, payable and both)
                move_dest : tipo de asientos (validados=validate y todos=all)

        Returns a dictionary of accounts with following key and value {
                'code': account code,
                'name': account name,
                'debit': sum of total debit amount,
                'credit': sum of total credit amount,
                'balance': total balance,
                'amount_currency': sum of amount_currency,
                'move_lines': list of move line
        }
        """

        # seleccionar los tipos de asientos (todos o solo validados)
        if move_dest == 'all':
            state = 'all'
        else:
            state= 'posted'

        cr = self.env.cr
        MoveLine = self.env['account.move.line']
        move_lines = {x: [] for x in accounts.ids}

        # Prepare initial sql query and Get the initial move lines
        if init_balance:
            init_tables, init_where_clause, init_where_params = MoveLine.with_context(date_from=date_start, date_to=date_end, initial_bal=True, state=state,company_id=empresa)._query_get()
            init_wheres = [""]
            if init_where_clause.strip():
                init_wheres.append(init_where_clause.strip())
            init_filters = " AND ".join(init_wheres)
            filters = init_filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')
            sql = ("""SELECT 0 AS lid, l.account_id AS account_id, l.date AS ldate, '' AS lcode, NULL AS amount_currency, '' AS lref, 'Initial Balance' AS lname, COALESCE(SUM(l.debit),0.0) AS debit, COALESCE(SUM(l.credit),0.0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance, '' AS lpartner_id,\
                m.name AS move_name, m.id AS mmove_id, '' AS currency_code,\
                NULL AS currency_id,\
                '' AS invoice_id, '' AS invoice_type, '' AS invoice_number,\
                '' AS partner_name, a.id AS analytic_id, l.analytic_account_id AS analytic_account_id, a.code AS analytic_account_code, a.name AS analytic_account_name\
                FROM account_move_line l\
                LEFT JOIN account_move m ON (l.move_id=m.id)\
                LEFT JOIN res_currency c ON (l.currency_id=c.id)\
                LEFT JOIN res_partner p ON (l.partner_id=p.id)\
                LEFT JOIN account_invoice i ON (m.id =i.move_id)\
                LEFT JOIN account_analytic_account a ON (l.analytic_account_id = a.id)
                JOIN account_journal j ON (l.journal_id=j.id)\
                WHERE l.account_id IN %s""" + filters + ' GROUP BY l.account_id, a.id, l.analytic_account_id, m.name, m.id, l.date')
            params = (tuple(accounts.ids),) + tuple(init_where_params)
            cr.execute(sql, params)
            for row in cr.dictfetchall():
                move_lines[row.pop('account_id')].append(row)

        sql_sort = 'l.date, l.move_id'
        if sortby == 'sort_journal_partner':
            sql_sort = 'j.code, p.name, l.move_id'


        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = MoveLine.with_context(date_from=date_start, date_to=date_end, initial_bal=False, state=state, company_id=empresa)._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        filters = filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')

        # Get move lines base on sql query and Calculate the total balance of move lines
        sql = ('''SELECT l.id AS lid, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id, l.amount_currency, l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,\
            m.name AS move_name, c.symbol AS currency_code, p.name AS partner_name, a.id AS analytic_id, l.analytic_account_id AS analytic_account_id, a.code AS analytic_account_code, a.name AS analytic_account_name\
            FROM account_move_line l\
            JOIN account_move m ON (l.move_id=m.id)\
            LEFT JOIN res_currency c ON (l.currency_id=c.id)\
            LEFT JOIN res_partner p ON (l.partner_id=p.id)\
            LEFT JOIN account_analytic_account a ON (l.analytic_account_id = a.id)\
            JOIN account_journal j ON (l.journal_id=j.id)\
            JOIN account_account acc ON (l.account_id = acc.id) \
            WHERE l.account_id IN %s ''' + filters + ''' GROUP BY l.id, l.account_id, l.date, j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, c.symbol, p.name, a.id, l.analytic_account_id ORDER BY ''' + sql_sort)
        params = (tuple(accounts.ids),) + tuple(where_params)
        cr.execute(sql, params)

        for row in cr.dictfetchall():
            balance = 0
            for line in move_lines.get(row['account_id']):
                balance += line['debit'] - line['credit']
            row['balance'] += balance
            move_lines[row.pop('account_id')].append(row)

        # Calculate the debit, credit and balance for Accounts
        account_res = []
        for account in accounts:
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            res['code'] = account.code
            res['name'] = account.name
            res['move_lines'] = move_lines[account.id]
            for line in res.get('move_lines'):
                res['debit'] += line['debit']
                res['credit'] += line['credit']
                res['balance'] = line['balance']
            if display_account == 'all':
                account_res.append(res)
            if display_account == 'move' and res.get('move_lines'):
                account_res.append(res)
            if display_account == 'saldo_cero' and not currency.is_zero(res['balance']):
                account_res.append(res)

        return account_res





