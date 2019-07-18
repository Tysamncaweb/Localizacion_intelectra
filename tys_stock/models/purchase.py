# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchasesAdaptation(models.Model):
    #_name = 'purchase.order.line'
    _inherit = 'purchase.order.line'

    @api.multi
    def _prepare_stock_moves(self, picking):
        res = super(PurchasesAdaptation, self)._prepare_stock_moves(picking)
        if self.product_id.default_code:
            res[0]['default_code'] = self.product_id.default_code
        return res






