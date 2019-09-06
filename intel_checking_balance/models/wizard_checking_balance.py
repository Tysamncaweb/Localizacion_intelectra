# -*- coding: utf-8 -*-
import locale
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import timedelta, date, datetime
from io import BytesIO
import xlwt, base64
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class modificacion_name_get(models.Model):
    _inherit = 'res.currency.rate'

    @api.multi
    def name_get(self):
        result = []
        for res in self:
            name = str(res.rate_real) + ' - ' + str(res.hora)
            result.append((res.id, name))
        return result

class RetentionISLR(models.Model):
    _name = 'checking.balance'
    _description = 'Open checking Balance'

    target_movement = fields.Selection([
        (0, 'Todos los asientos validados'),
        (1, 'Todos los asientos')
    ], required=True, string="Movimientos Destino")

    show_accounts = fields.Selection([
        (0, 'Con movimientos'),
        (1, 'Con saldo distinto a 0')
    ], string="Mostrar Cuentas", required=True)

    report_format = fields.Selection([
        (0, 'PDF'),
        (1, 'XLS')
    ], string="Formato del Reporte", required=True)
    company = fields.Many2one('res.company', required=True)
    start_date = fields.Date(required=True,)
    end_date = fields.Date(required=True, default=fields.Datetime.now)
    balance = fields.Boolean(default=False)
    currency_id = fields.Many2one('res.currency', required=True)
    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    report = fields.Binary('Descargar xls', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=32)
    tasa = fields.Many2one('res.currency.rate', string="Tasa Monetaria", required=True)

    @api.multi
    def cuentas(self, move_validate, cuenta, b, unico, repetido, currency, currency_line):
        for a in move_validate:
            cuenta.append({
                'codigo': a.account_id.code,
                'name': a.account_id.name,
                'amount': a.move_id.amount * currency_line.rate_real,
                'debit': a.debit * currency_line.rate_real,
                'credit': a.credit * currency_line.rate_real,
                'saldo': (a.debit - a.credit) * currency_line.rate_real,
            })
            b = sorted(cuenta, key=lambda k: k['codigo'])

        for vars in b:
            if unico:
                cont = 0
                for vars2 in unico:
                    if (vars.get('codigo') == vars2.get('codigo') and vars.get('name') == vars2.get('name')):
                        repetido.append(vars)
                        cont += 1
                if cont == 0:
                    unico.append(vars)
            else:
                unico.append(vars)

        for cuentas in unico:
            for unidad in repetido:
                if (cuentas['name'] == unidad['name']) and (cuentas['codigo'] == unidad['codigo']):
                    cuentas.update({'amount': unidad.get('amount') + cuentas.get('amount'),
                                    'debit': unidad.get('debit') + cuentas.get('debit'),
                                    'credit': unidad.get('credit') + cuentas.get('credit'),
                                    'saldo': unidad.get('saldo') + cuentas.get('saldo')})
        return unico

    @api.multi
    def SaldoDistintoCero(self, unico):
        sd0 = []
        for a in unico:
            if a['saldo'] > 0.00:
                sd0.append({
                    'codigo': a['codigo'],
                    'name': a['name'],
                    'amount': locale.format_string("%f", a['amount'], grouping=True)[:-4],
                    'debit': locale.format_string("%f", a['debit'], grouping=True)[:-4],
                    'credit': locale.format_string("%f", a['credit'], grouping=True)[:-4],
                    'saldo': locale.format_string("%f", a['saldo'], grouping=True)[:-4]
                })
        return sd0

    @api.multi
    def format_new(self, unico):
        new = []
        locale.setlocale(locale.LC_ALL, '')
        for a in unico:
            new.append({
                'codigo': a['codigo'],
                'name': a['name'],
                'amount': locale.format_string("%f", a['amount'], grouping=True)[:-4],
                'debit': locale.format_string("%f", a['debit'], grouping=True)[:-4],
                'credit': locale.format_string("%f", a['credit'], grouping=True)[:-4],
                'saldo': locale.format_string("%f", a['saldo'], grouping=True)[:-4]
            })
        return new

    @api.multi
    def suma_totales(self, unico):
        suma_debit = 0
        suma_credit = 0
        suma_saldo = 0
        suma = []
        for f in unico:
            suma_debit += f['debit']
            suma_credit += f['credit']
            suma_saldo += f['saldo']
        suma.append({
            'suma_debit': locale.format_string("%f", suma_debit, grouping=True)[:-4],
            'suma_credit': locale.format_string("%f", suma_credit, grouping=True)[:-4],
            'suma_saldo': locale.format_string("%f", suma_saldo, grouping=True)[:-4],
        })

        return suma
    @api.multi
    def generate_checking_balance(self, data):
        if self.report_format == False:
            data = {
                'ids': self.ids,
                'model': 'report.intel_checking_balance.report_checking_balance',
                'form': {
                    'date_start': self.start_date,
                    'date_stop': self.end_date,
                    'currency_id': self.currency_id.name,
                    'currency_id1': self.currency_id.id,
                    'target_movement': self.target_movement,
                    'show_accounts': self.show_accounts,
                    'report_format':self.report_format,
                    'company': self.company.id,
                    'balance': self.balance,
                    'tasa': self.tasa.id,
                    },
                'context': self._context
            }
            return self.env.ref('intel_checking_balance.action_report_checking_balance').report_action(self, data=data, config=False)
        else:
            unico = []
            today = datetime.now()
            hoy = date.today()
            format_new = "%d/%m/%Y"
            hoy_date = datetime.strftime(hoy, format_new)
            start_date = datetime.strftime(datetime.strptime(self.start_date,DEFAULT_SERVER_DATE_FORMAT),format_new)
            end_date = datetime.strftime(datetime.strptime(self.end_date,DEFAULT_SERVER_DATE_FORMAT),format_new)
            hora = today.hour
            minute = today.minute
            if minute < 10:
                time = str(hora) + ':' + '0' + str(minute)
            else:
                time = str(hora) + ':' + str(minute)


            self.ensure_one()
            fp = BytesIO()
            wb = xlwt.Workbook(encoding='utf-8')
            writer = wb.add_sheet('Nombre de hoja')

            header_content_style = xlwt.easyxf("font: name Helvetica size 80 px, bold 1, height 400;")
            sub_header_style = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170; borders: left thin, right thin, top thin, bottom thin;")
            sub_header_style_bold = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170;")
            sub_header_content_style = xlwt.easyxf("font: name Helvetica size 10 px, height 170;")
            line_content_style = xlwt.easyxf("font: name Helvetica, height 170; align: horiz right;")
            line_content_style_totales = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170; borders: left thin, right thin, top thin, bottom thin; align: horiz right;")

            row = 1
            col = 0

            #writer.write_merge(row, row, 0, header_cols, "Información de contactos",)
            writer.row(row).height = 500
            writer.write_merge(row, row, 2, 4, str(self.company.name), header_content_style)



            row +=1

            writer.write_merge(row, row, 2, 4, "Número de identificación Fiscal:", sub_header_style_bold)
            writer.write_merge(row, row, 5, 6, str(self.company.vat), sub_header_content_style)
            row +=1

            writer.write_merge(row, row, 10,10, "Fecha:", sub_header_style_bold)

            writer.write_merge(row, row, 11, 11, hoy_date, sub_header_content_style)
            row +=1

            writer.write_merge(row, row, 10,10, "Hora:", sub_header_style_bold)
            writer.write_merge(row, row, 11,11,  time, sub_header_content_style)
            row += 2
            writer.row(row).height = 500
            writer.write_merge(row, row, 5, 9, "Balance de Comprobación", header_content_style)
            row +=1

            writer.write_merge(row, row, 5, 5, "Desde:", sub_header_style_bold)
            writer.write_merge(row, row, 6, 6, start_date, sub_header_content_style)

            writer.write_merge(row, row, 8, 8, "Hasta:", sub_header_style_bold)
            writer.write_merge(row, row, 9, 9, end_date, sub_header_content_style)
            row += 1
            writer.write_merge(row, row, 7, 7, "Moneda:", sub_header_style_bold)
            writer.write_merge(row, row, 8, 8, str(self.currency_id.name), sub_header_content_style)
            row +=2
            col= 1

            writer.write_merge(row, row, 1, 4, "Cuenta", sub_header_style)
            if self.balance == True:
                writer.write_merge(row, row, 5, 6, "Saldo Inicial", sub_header_style )
            else:
                writer.write_merge(row, row, 5, 6, "", sub_header_style)
            writer.write_merge(row, row, 7, 8, "Débito", sub_header_style )
            writer.write_merge(row, row, 9, 10, "Crédito", sub_header_style)
            writer.write_merge(row, row, 11, 12, "Saldo", sub_header_style)


            account_account = self.env['account.account'].search([('id', '!=', 0)])
            currency = self.env['res.currency'].search([('id', '=', self.currency_id.id)])
            currency_line = self.env['res.currency.rate'].search([('id', '=', self.tasa.id)])
            # TODOS LOS ASIENTOS VALIDADOS CON MOVIMIENTOS
            if self.target_movement == False and self.show_accounts == False:
                for account in account_account:
                    move_validate = self.env['account.move.line'].search([('account_id', '=', account.id),
                                                                          ('move_id.state', '=', 'posted'),
                                                                          ('company_id', '=', self.company.id),
                                                                          ('date', '>=', self.start_date),
                                                                          ('date', '<=', self.end_date)])
                    if move_validate:
                        cuenta = []
                        b = []
                        repetido = []
                        unico = self.cuentas(move_validate, cuenta, b, unico, repetido, currency, currency_line)

                suma = self.suma_totales(unico)
                cuentas = self.format_new(unico)

            # TODOS LOS ASIENTOS VALIDADOS CON SALDO DISTINTO A 0
            if self.target_movement == False and self.show_accounts == 1:
                for account in account_account:
                    move_validate = self.env['account.move.line'].search([('account_id', '=', account.id),
                                                                          ('move_id.state', '=', 'posted'),
                                                                          ('company_id', '=', self.company.id),
                                                                          ('date', '>=', self.start_date),
                                                                          ('date', '<=', self.end_date)])
                    if move_validate:
                        cuenta = []
                        b = []
                        repetido = []
                        unico = self.cuentas(move_validate, cuenta, b, unico, repetido, currency, currency_line)

                suma = self.suma_totales(unico)
                cuentas = self.SaldoDistintoCero(unico)

            # TODOS LOS ASIENTOS CON MOVIMIENTOS
            if self.target_movement == 1 and self.show_accounts == False:
                for account in account_account:
                    move_validate = self.env['account.move.line'].search([('account_id', '=', account.id),
                                                                          ('company_id', '=', self.company.id),
                                                                          ('date', '>=', self.start_date),
                                                                          ('date', '<=', self.end_date)])
                    if move_validate:
                        cuenta = []
                        b = []
                        repetido = []
                        unico = self.cuentas(move_validate, cuenta, b, unico, repetido, currency, currency_line)
                suma = self.suma_totales(unico)
                cuentas = self.format_new(unico)

            # TODOS LOS ASIENTOS CON SALDO DISTINTO A 0
            if self.target_movement == 1 and self.show_accounts == 1:
                for account in account_account:
                    move_validate = self.env['account.move.line'].search([('account_id', '=', account.id),
                                                                          ('company_id', '=', self.company.id),
                                                                          ('date', '>=', self.start_date),
                                                                          ('date', '<=', self.end_date)])
                    if move_validate:
                        cuenta = []
                        b = []
                        repetido = []
                        unico = self.cuentas(move_validate, cuenta, b, unico, repetido, currency, currency_line)

                suma = self.suma_totales(unico)
                cuentas = self.SaldoDistintoCero(unico)

            for a in cuentas:
                row += 1
                writer.write_merge(row, row, 1, 1, a['codigo'],sub_header_content_style )
                writer.write_merge(row, row, 2, 4, a['name'], sub_header_content_style)
                if self.balance == True:
                    writer.write_merge(row, row, 5, 6, a['amount'], line_content_style)
                else:
                    writer.write_merge(row, row, 5, 6, "", line_content_style)
                writer.write_merge(row, row, 7, 8, a['debit'], line_content_style)
                writer.write_merge(row, row, 9, 10, a['credit'], line_content_style)
                writer.write_merge(row, row, 11, 12, a['saldo'], line_content_style)

            for g in suma:
                row +=1
                writer.write_merge(row, row, 1, 4, "Total", sub_header_style)
                writer.write_merge(row, row, 7, 8, g['suma_debit'], line_content_style_totales)
                writer.write_merge(row, row, 9, 10, g['suma_credit'], line_content_style_totales)
                writer.write_merge(row, row, 11, 12, g['suma_saldo'], line_content_style_totales)

            col = 1



            wb.save(fp)

            out = base64.encodestring(fp.getvalue())
            self.write({'state': 'get', 'report': out, 'name': 'balance_Comprobación.xls'})



            return {
                'type': 'ir.actions.act_window',
                'res_model': 'checking.balance',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,
                'views': [(False, 'form')],
                'target': 'new',
            }


class ReportRetentionISLR(models.AbstractModel):
    _name = 'report.intel_checking_balance.report_checking_balance'

    @api.model
    def get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        end_date = data['form']['date_stop']
        currency_id = data['form']['currency_id']
        currency_id1 = data['form']['currency_id1']
        target_movement = data['form']['target_movement']
        show_accounts = data['form']['show_accounts']
        company = data['form']['company']
        balance = data['form']['balance']
        tasa = data['form']['tasa']
        report_format = data['form']['report_format']
        today = datetime.now()
        hora = today.hour
        minute = today.minute
        if minute < 10:
            time = str(hora) + ':' + '0' + str(minute)
        else:
            time = str(hora) + ':' + str(minute)

        unico = []


        account_account = self.env['account.account'].search([('id', '!=', 0)])
        currency = self.env['res.currency'].search([('id', '=', currency_id1)])


        # TODOS LOS ASIENTOS VALIDADOS CON MOVIMIENTOS
        if target_movement == False and show_accounts == False:
            for account in account_account:
                move_validate = self.env['account.move.line'].search([('account_id', '=', account.id),
                                                                  ('move_id.state', '=', 'posted'),
                                                                  ('company_id', '=', company),
                                                                  ('date', '>=', date_start),
                                                                  ('date', '<=', end_date)])
                if move_validate:
                    cuenta = []
                    b = []
                    repetido = []
                    unico = self.cuentas(move_validate, cuenta, b, unico, repetido, currency, tasa)

            suma = self.suma_totales(unico)


        #TODOS LOS ASIENTOS VALIDADOS CON SALDO DISTINTO A 0
        if target_movement == False and show_accounts == 1:
            for account in account_account:
                move_validate = self.env['account.move.line'].search([('account_id', '=', account.id),
                                                                  ('move_id.state', '=', 'posted'),
                                                                  ('company_id', '=', company),
                                                                  ('date', '>=', date_start),
                                                                  ('date', '<=', end_date)])
                if move_validate:
                    cuenta = []
                    b = []
                    repetido = []
                    unico = self.cuentas(move_validate, cuenta, b, unico, repetido, currency, tasa)

            suma = self.suma_totales(unico)

        # TODOS LOS ASIENTOS CON MOVIMIENTOS
        if target_movement == 1 and show_accounts == False:
            for account in account_account:
                move_validate = self.env['account.move.line'].search([('account_id', '=', account.id),
                                                                      ('company_id', '=', company),
                                                                      ('date', '>=', date_start),
                                                                      ('date', '<=', end_date)])
                if move_validate:
                    cuenta = []
                    b = []
                    repetido = []
                    unico = self.cuentas(move_validate, cuenta, b, unico, repetido, currency, tasa)
            suma = self.suma_totales(unico)

        # TODOS LOS ASIENTOS CON SALDO DISTINTO A 0
        if target_movement == 1 and show_accounts == 1:
            for account in account_account:
                move_validate = self.env['account.move.line'].search([('account_id', '=', account.id),
                                                                  ('company_id', '=', company),
                                                                  ('date', '>=', date_start),
                                                                  ('date', '<=', end_date)])
                if move_validate:
                    cuenta = []
                    b = []
                    repetido = []
                    unico = self.cuentas(move_validate, cuenta, b, unico, repetido, currency, tasa)

            suma = self.suma_totales(unico)

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'end_date': end_date,
            'start_date': date_start,
            'today': today,
            'currency_id': currency_id,
            'balance': balance,
            'hora': time,
            'cuentas': unico,
            'suma': suma,
        }
    @api.multi
    def cuentas(self, move_validate, cuenta, b, unico, repetido, currency, tasa):
        currency_line = self.env['res.currency.rate'].search([('id', '=', tasa)])
        for a in move_validate:
            cuenta.append({
                'codigo': a.account_id.code,
                'name': a.account_id.name,
                'amount': a.move_id.amount*currency_line.rate_real,
                'debit': a.debit*currency_line.rate_real,
                'credit': a.credit*currency_line.rate_real,
                'saldo': (a.debit - a.credit)*currency_line.rate_real,
            })
            b = sorted(cuenta, key=lambda k: k['codigo'])

        for vars in b:
            if unico:
                cont = 0
                for vars2 in unico:
                    if (vars.get('codigo') == vars2.get('codigo') and vars.get('name') == vars2.get('name')):
                        repetido.append(vars)
                        cont += 1
                if cont == 0:
                    unico.append(vars)
            else:
                unico.append(vars)

        for cuentas in unico:
            for unidad in repetido:
                if (cuentas['name'] == unidad['name']) and (cuentas['codigo'] == unidad['codigo']):
                    cuentas.update({'amount': unidad.get('amount') + cuentas.get('amount'),
                                    'debit': unidad.get('debit') + cuentas.get('debit'),
                                    'credit': unidad.get('credit') + cuentas.get('credit'),
                                    'saldo': unidad.get('saldo') + cuentas.get('saldo')})
        return unico

    @api.multi
    def SaldoDistintoCero(self, unico):
        sd0 = []
        for a in unico:
            if a['saldo'] > 0.00:
                sd0.append({
                    'codigo': a['codigo'],
                    'name': a['name'],
                    'amount': a['amount'],
                    'debit': a['debit'],
                    'credit': a['credit'],
                    'saldo': a['saldo'],
                })
        return sd0

    @api.multi
    def suma_totales(self, unico):
        suma_debit = 0
        suma_credit = 0
        suma_saldo = 0
        suma = []
        for f in unico:
            suma_debit += f['debit']
            suma_credit += f['credit']
            suma_saldo += f['saldo']
        suma.append({
            'suma_debit': suma_debit,
            'suma_credit': suma_credit,
            'suma_saldo': suma_saldo,
        })

        return suma