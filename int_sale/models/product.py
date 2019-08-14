# -*- coding: utf-8 -*-
from odoo import fields, models
class sale_order(models.Model):
    _inherit = 'product.template'

    component = fields.Boolean(help="Este campo indica si el producto registrado es un componente.")