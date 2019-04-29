# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (C) 2012 OpenERP - Team de Localización Argentina.
# https://launchpad.net/~openerp-l10n-ar-localization
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Cambios, rsosa:
#
# - Se agrega un campo booleano para controlar la visualizacion del campo Fecha de Debito (debit_date).
# - El campo 'debit_date' se comento en la clase original y se agrega de nuevo por esta via..
# - Se comenta el campo 'state' de la clase original y se incluye de nuevo aqui con un nuevo estado agregado
#
#
##############################################################################


from odoo import fields, models, api, _


class account_issued_check(models.Model):
    _name = 'account.issued.check'
    _inherit = 'account.issued.check'

    debit_date = fields.Date('Date Debit', invisible=False, states={'draft': [('invisible', True)]})
    reconcile = fields.Boolean('Conciliar?', invisible=False, states={'draft': [('invisible', True)]})
    state = fields.Selection([('draft', 'Draft'),
                              ('handed', 'Handed'),
                              ('hrejected', 'Rechazado'),
                              ('payed', 'Pagado'),
                              ('cancel', 'Cancelled')],
                             string='State')

    move_id = fields.Many2one('account.move', 'Asiento contable', states={'cancel': [('invisible', True)]})
    asiento_conciliado = fields.One2many('account.move.line', related='move_id.line_ids', string='Asientos contables', readonly=True, states={'cancel': [('invisible', True)]})

    @api.multi
    def action_conciliar(self):
        '''
        Metodo para efectuar un nuevo asiento contable que rebaje la cuenta de Banco contra la cuenta
        transitoria, y de esta manera conciliar los saldos de las cuentas bancarias...
        '''




        issued_check_obj = self
        monto = issued_check_obj.amount
        cheq_obj = self.env['account.checkbook']
        cheq_brw = cheq_obj.browse(issued_check_obj.checkbook_id.id)
        if cheq_brw:
            cuenta_deudora = cheq_brw.cuenta_transitoria.id
            cuenta_acreedora = self.env['res.partner.bank'].browse(cheq_brw.account_bank_id.id).account_id.id

        voucher_obj = self.env['account.payment']
        voucher_brw = voucher_obj.browse(issued_check_obj.voucher_id.id)
        journal_id = voucher_brw.journal_id.id
       # if not journal_id:
        #     raise UserError(_("Necesito un diario."))
        #period_id = voucher_brw.period_id.id
        vals = {
            'date': issued_check_obj.debit_date,
         #   'period_id': period_id,
            'journal_id': journal_id,
            'line_ids': False,
        }
        vals.update({'journal_id': journal_id})
        move_obj = self.env['account.move']
        move_id = move_obj.create(vals)

        self.currency_={
            'account_id': cuenta_deudora,
            'company_id': self.receiving_partner_id.company_id.id,
            'currency_id': False,
            'date_maturity': False,
            'ref': voucher_brw.communication,
            # 'period_id': period_id,
            'date': issued_check_obj.debit_date,
            'partner_id': voucher_brw.partner_id.id,
            'move_id': move_id.id,
            'name': 'CONCILIACION CHEQUE ' + issued_check_obj.number,
            'journal_id': journal_id,
            'credit': 0.0,
            'debit': monto,
            'amount_currency': 0,
        }

        asiento= self.currency_
        move_line_obj = self.env['account.move.line']
        move_line_id1 = move_line_obj.create(asiento)
        asiento['account_id'] = cuenta_acreedora
        asiento['credit'] = monto
        asiento['debit'] = 0.0
        move_line_id2 = move_line_obj.create(asiento)
        #if move_line_id1:
            # move_line_ids1.write(asiento)
            #self._cr.execute = 'UPDATE account_move_line SET debit=%s where id=%s' % (monto, move_line_id1)
            #sql = 'UPDATE account_move_line SET credit=%s where id=%s' % (monto, move_line_id1.id)
            #self._cr.execute(sql)

        #if move_line_id2:
            # move_line_ids2.write(asiento)
            #self._cr.execute= 'UPDATE account_move_line SET credit=%s where id=%s' % (monto, move_line_id2)
            #TODO sql = 'UPDATE account_move_line SET credit=%s where id=%s' % (monto, move_line_id2)
            #TODO self._cr.execute(sql)
        if move_line_id1 and move_line_id2:
            res = {'state': 'payed', 'move_id': move_id.id,}
                #issued_check_obj.write(self)
            self.write(res)
        return True

    @api.multi
    def action_validate_checks(self):
            move = (account_issued_check, self)
            if move:
                for ch in self:
                    ch.write({'state': 'handed'})
                    # self.env['account.issued.check']
            return move



class account_move(models.Model):
    _inherit = 'account.move'

    @api.multi
    def assert_balanced(self):
        if not self.ids:
            return True
        mlo = self.env['account.move.line'].search([('move_id', '=',self.ids[0])])
        if not mlo.reconcile:
            super(account_move, self).assert_balanced(fields)
        return True
