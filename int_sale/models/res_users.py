# -*- coding: utf-8 -*-
#Este archivo agrega el campo para insertar la firma propia de cada usuario para el reporde de presupuestos
from odoo import fields, models
class sale_order(models.Model):
    _inherit = 'res.users'

    firm = fields.Binary(attachment=True,help="This field contains the image used as a signature for this contact. Signature will be available in the budget report.")