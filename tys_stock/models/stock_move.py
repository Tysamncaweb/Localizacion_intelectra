# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockMoveAdaptation(models.Model):
    _name = 'stock.move'
    _inherit = 'stock.move'

    default_code = fields.Char()

    @api.onchange('product_id')
    def _onchange_code(self):
        if self.product_id:
            self.default_code = self.product_id.default_code

    def _action_assign(self):
        res = super(StockMoveAdaptation, self)._action_assign()
        for move in self:
            if move:
                move.write({'default_code': move.product_id.default_code,})
        return res



