# coding: utf-8
###########################################################################
from odoo import api
from odoo import fields, models
from odoo import exceptions
from odoo.tools.translate import _


class AccountInvoice(models.Model):
    '''Esta clase es para crear en la factura el saldo de anticipo del cliente o proveedor'''
    _inherit = 'account.invoice'

    account_advance_ids = fields.One2many('account.advanced.payment','invoice_id')
    partner_id = fields.Many2one('res.partner')
    sum_amount_available = fields.Monetary('Advance available')
    currency_id = fields.Many2one('res.currency', string='Currency')


    @api.onchange('partner_id')
    def _onchange_amount_available(self):
        self.sum_amount_available = 0
        advance_obj = self.env['account.advanced.payment']
        advance_bw = advance_obj.search([('partner_id', '=', self.partner_id.id),
                                         ('state', '=', 'available')])

        for advance in advance_bw:
            self.sum_amount_available += advance.amount_available

        return