# -*- coding: utf-8 -*-
from odoo import fields, models,api
import time

class sale_order(models.Model):
    _inherit = 'sale.order'

    """def _get_user_id(self):
        user_id = self.env['hr.employee'].search([('user_id','=',self._uid)])
        if user_id:
            return user_id
        else:
            return None"""

    type_of_sale = fields.Many2one('type.of.sale')
    rif = fields.Char(related='partner_id.vat',string ='Rif')
    direction = fields.Char(related='partner_id.street',size=500)
    contact = fields.Many2one('res.partner')
    phone = fields.Char(related='partner_id.phone')
    email = fields.Char(related='partner_id.email')
    project = fields.Many2one('project.project')
    date_time = fields.Date('Date', default=time.strftime('%Y-%m-%d'))
    site = fields.Char('Place of delivery')
    #date_time_emit = fields.Datetime('Date Issue')
    name_seller = fields.Many2one('res.users', default=lambda s: s._uid)
    email_seller = fields.Char(related='name_seller.email')
    phone_seller = fields.Char(related='name_seller.phone')

class type_sale(models.Model):
    _name = 'type.of.sale'

    name = fields.Char('Nombre',size=100)