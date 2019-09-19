# -*- coding: utf-8 -*-
from odoo import fields, models,api
import time

class sale_order(models.Model):
    _inherit = 'sale.order'

    type_of_sale = fields.Selection([
        ('directas', 'Ventas Directas'),
        ('especiales', 'Ventas Especiales'),
        ('otra', 'Otras Ventas')
    ], "Tipos de Ventas", required=True, size=15 )
    type_of_other = fields.Many2one('type.of.sale')
    rif = fields.Char(related='partner_id.vat',string ='Rif')
    direction = fields.Char(related='partner_id.street',size=500)
    contact = fields.Many2one('res.partner')
    phone = fields.Char(related='partner_id.phone')
    email = fields.Char(related='partner_id.email')
    project = fields.Many2one('project.project')
    date_time = fields.Date('Date', default=time.strftime('%Y-%m-%d'))
    site = fields.Char('Place of delivery')
    name_seller = fields.Many2one('res.users', default=lambda s: s._uid)
    email_seller = fields.Char(related='name_seller.email')
    phone_seller = fields.Char(related='name_seller.phone')


class type_sale(models.Model):
    _name = 'type.of.sale'

    name = fields.Char('Nombre',size=100)