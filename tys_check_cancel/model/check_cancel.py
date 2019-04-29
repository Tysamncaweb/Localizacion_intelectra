# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Modulo que permite la anulacion de cheques antes de ser emitidos
#    autor: Tysamnca.
#
##############################################################################

from odoo import fields, models, api, _
from odoo.exceptions import UserError,Warning
import logging
_logger = logging.getLogger(__name__)
import time

class account_issued_check(models.Model):
    _inherit = 'account.issued.check'

    @api.multi
    def onchange_number(self, number):

        def anulado(num):
            if not num:
                return False
            check_cancel_obj = self.env['check.cancel']
            check_cancel_number = check_cancel_obj.search([('number','=',num)])
            if check_cancel_number:
                return True
            else:
                return False

        def usado(num):
            if not num:
                return False
            issued_check_obj = self.env['account.issued.check']
            issued_check_number = issued_check_obj.search([('number','=',num)])
            if issued_check_number:
                return True
            else:
                return False

        res = {}
        number_str = str(number)
        if len(number_str) != 8:
            res = {'value':{'number': 0}}
        else:
            while anulado(number) or usado(number):
                number = str(((number) + 1))
            res.update({'value':{'number':number}})
        return res


class check_cancel(models.Model):

    _name = 'check.cancel'
    _description = 'Permite la anulacion de numeros de cheques antes de su emision'


    number = fields.Char('Check Number', required=True, select=True, readonly=True, states={'draft': [('readonly', False)]})
    actual = fields.Char('Current Check', size=8)
    ultimo = fields.Char('Last Check', size=8)
    checkbook_ids = fields.Char('Chequera')
    checkbook_id = fields.Many2one('account.checkbook')
    check_endorsed = fields.Boolean('Endorsed', required=True, states={'draft': [('invisible', False)]})
    user_id = fields.Many2one('res.users','User')
    date = fields.Date('Date Cancel', required=True)
    notas = fields.Text('Notes',states={'draft': [('invisible', False)]})
    state = fields.Selection([('draft','Draft'),('cancel','Canceled')], string='State', default='draft')
    bank_id = fields.Many2one('res.bank', 'Bank')
    account_bank_id = fields.Many2one('res.partner.bank', 'Destiny Account', required=True)
    numbers_id = fields.Many2one('account.issued.check')
    checks_id = fields.Boolean('checks', default = False)
    numbers = fields.Char()


    checkbook_state = None

    @api.multi
    def _get_checkbook_id(self):
        res={}
        checkbook_pool = self.env['account.checkbook']
        res = checkbook_pool.search([('state', '=', 'active')])
        if res:
            return res.id
        else:
            return False

    @api.multi
    def onchange_checkbook(self, checkbook_id):
        res = {}
        if not checkbook_id:
            return {}
        chequera = self.env['account.checkbook'].browse(checkbook_id)
        if chequera:
            actual = chequera.actual_number
            ultimo = chequera.range_hasta
            global checkbook_state
            checkbook_state= chequera.state
            return {'value': {'actual': actual, 'number': actual, 'ultimo': ultimo}}
        else:
            return {}

    _defaults = {
            'user_id': lambda s, cr, u, c: u,
            'date': lambda *a: time.strftime('%Y-%m-%d'),
            'state': 'draft',
                 }

    @api.onchange('bank_id')
    def onchange_bank_id_1(self):
        self.account_bank_id = False
        self.checkbook_ids = False
        self.number = False
        self.checks_id = False


    @api.onchange('account_bank_id')
    def onchange_bank_id_2(self):
        if self.account_bank_id:
            #var = self.account_bank_id.id
            #bank_account = self.env['res.partner.bank'].search([('bank_id','=',var)])
            #global checkbook
            checkbook = self.env['account.checkbook'].search([('account_bank_id','=',self.account_bank_id.id),('state','=','active')])
            self.checkbook_id = checkbook
            if self.checkbook_id:
                return {'value': {'checkbook_ids': self.checkbook_id.name}}
            else:
                warning = {
                    'title': _('Advertencia'),
                    'message': _('Esta cuenta bancaria no tiene chequera asignada')
                }
                return {'value': {'checkbook_ids': False}, 'warning': warning}


    @api.onchange('checks_id','numbers_id')
    def validate_number(self):
        if self.checks_id == False and self.numbers_id:
            self.number = self.numbers_id.number
        elif self.checks_id == True:
            self.ultimo = self.checkbook_id.range_hasta
            if self.checkbook_id.state == 'used':
                warning = {'title': _('Advertencia'),'message': _('Esta chequera fue utilizada completamente')}
                return {'warning': warning}
            else:
                range = self.env['account.checkbook'].search([('name', '=', self.checkbook_ids)])
                range_from = range.range_desde
                range_to = range.range_hasta
                warning = {'title': _("Aviso"),'message': _('Esta Chequera empieza con el cheque %s y termina con el cheque %s' % (range_from, range_to))}
                return {'warning': warning}


    @api.multi
    def name_get(self):
        res = []
        #res = super(check_cancel, self).name_get()
        #if self._context.get('come_form', False) and self._context.get('come_form', False) == self._name:
        for number in self:
            res.append((number.id, 'Cheque N°: %s' % (number.number)))
        return res

    #@api.model
    #def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #    context = {"come_form": "check.cancel"}
    #    self.with_context(context)


    @api.multi
    def wkf_cancel(self):
        if self.checks_id == True:
            if self.numbers.find(',') != -1:
                checks_to_cancel = self.numbers.split(',')
                for check in checks_to_cancel:
                    self.cancel_check(check)
                warning = {'title': _("Aviso"),'message': _('Se han anulado los cheques %s' % (self.numbers))}
                return {'warning': warning}
            elif self.numbers.find('-') != -1:
                checks_to_cancel = self.numbers.split('-')
                checks_to_cancel = self.value_conti_create(checks_to_cancel)
                for check in checks_to_cancel:
                    self.cancel_check(check)
                warning = { 'title': _("Aviso"),'message': _('Se han Anulado la secuencia de cheques %s' % (self.numbers))}
                return {'warning': warning}
            else:
                self.cancel_check(self.number)
                warning = {'title': _("Aviso"), 'message': _('Se ha anulado el cheque numero %s' % (self.numbers))}
                return {'warning': warning}
        else:
            check = self.number
            self.cancel_check(check)
            warning = {'title': _("Aviso"), 'message': _('Se ha anulado el cheque numero %s' % (self.numbers))}
            return {'warning': warning}


    @api.multi
    def cancel_check(self, nbr):
        if self.id:
            #estado = self.browse(self.id)
            #number = estado.number
            if self.state == 'draft':
                self.write({'state': 'cancel'})
            checks = self.env['check.cancel'].search([('number', '=', nbr), ('state', '=', 'draft')])
            if checks.state == 'draft':
                checks.update({'state': 'cancel'})
            checks = self.env['account.issued.check'].search([('number', '=', nbr), ('state', '=', 'draft')])
            if checks.state == 'cancel':
                raise UserError(_('El cheque numero %s, ya fue anulado o esta marcado para ser anulado' % (nbr)))
            else:
                checks.update({'state': 'cancel'})
            #id_chequera = self.browse(self.ids).checkbook_id.id
            chequeras=self.env['account.checkbook']
            chequera_obj = chequeras.browse(self.checkbook_id.id)
            if chequera_obj.actual_number == nbr:
                if chequera_obj.actual_number == chequera_obj.range_hasta:
                    chequera_obj.write({'state':'used'})
                else:
                    siguiente = int(nbr) + 1
                    siguiente = str(siguiente)
                    chequera_obj.write({
                        'actual_number': siguiente.zfill(len(nbr))})
        return True


    @api.model
    def create(self,values):
        numss = []
        local_numbers = values.get('number',None)
        nums = values.get('number',0)
        if nums.find(',') != -1:
            nums = nums.split(',')
            res = self.value_create(nums,values)
        elif nums.find('-') != -1:
            nums = nums.split('-')
            nums = self.value_conti_create(nums)
            res = self.value_create(nums,values)
        else:# solo un cheque
            numss.append(nums)
            res = self.value_create(numss, values)
        res.update({'numbers': local_numbers})
        return res

    @api.multi
    def value_conti_create(self,nums):
        check_list = []
        nmbs = str(nums[0])
        num_inicio = nums[0]
        num_fin = nums[1]
        num_inicio = int(num_inicio)
        nums_check = num_inicio
        num_fin =int(num_fin)
        total = (num_fin - num_inicio)+1
        for x in range(total):
            nums_check = str(nums_check).zfill(len(nmbs))
            check_list.append(nums_check)
            nums_check = int(nums_check)
            nums_check = nums_check + 1
        return check_list

    @api.multi
    def value_create(self,nums,values):
        local_checkbook = values.get('checkbook_id',False)
        range = self.env['account.checkbook'].search([('id','=',local_checkbook)])
        range_from = range.range_desde
        range_to = range.range_hasta
        for checks in nums:
            checks = str(checks)
            values['number'] = checks
            estado = self.env['check.cancel'].search([('number', '=', checks)])
            estados = estado.state
            if estados == 'cancel' or estados == 'draft':
                raise UserError(_('El cheque %s ya fue anulado o esta marcado para ser anulado') % (checks))
            numero = values.get('number', 0)
            #actual = values.get('actual', 0)
            if len(str(numero)) != 8:
                raise UserError(_('El numero %s introducido debe ser de 8 digitos' % (numero)))
            else:
                if range_from > numero or range_to < numero:
                    raise UserError(_('El cheque introducido no pertenece a esta chequera o la secuencia no es la correcta'))
            res = super(check_cancel, self).create(values)
        return res

    @api.multi
    def write(self, values):
        #number_edit = values.get('number', 0)
        #actual_edit = values.get('actual',0)
        #if number_edit and not number_edit == actual_edit:
        #        raise UserError(_('El numero introducido no pertenece a esta chequera'))
        return super(check_cancel, self).write(values)

    def wkf_undo(self):
        self.write({'state' : 'draft'})
        return True

class account_third_check(models.Model):

    _inherit = 'account.third.check'

    _defaults = {

        'company_id': lambda self, c: self.pool.get('res.users').browse( c).company_id.id,
    }
