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
#    Cambios, rsosa:
#
#    - Se sobreescribe el metodo 'first_move_line_get' para incluir el ID de la
#      cuenta transitoria de Banco a la hora de realizar un pago con cheque
#
##############################################################################

from odoo import fields, models, api, exceptions,_
from email.utils import formataddr
from odoo.addons import decimal_precision as dp
from odoo.exceptions import Warning
import re
from ast import literal_eval



class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'





    @api.model
    def _default_note(self):
        return self.env['ir.config_parameter'].sudo().get_param('purchase.notes')


    name_id = fields.Many2one('res.users', 'Responsable', default=lambda s: s._uid)
    phone = fields.Char(size=12, related='name_id.phone')
    email = fields.Char(size=100, related='name_id.email')
    name = fields.Char('Nº de Orden de Compra', required=True, index=True, copy=False, default='New')
    rif_purchase = fields.Char(string="RIF", size=15, required=True, related='partner_id.vat')
    Type_of_provider = fields.Selection([
        ('national', 'Nacionales'),
        ('national_div', 'Nacionales con divisas '),
        ('international', 'Internacional ')
    ], "Tipo de Proveedor", required=True, size=15 )
    project_id = fields.Many2one('project.project',
                                 string='Proyecto',
                                 default=lambda self: self.env.context.get('default_project_id'),
                                 index=True,
                                 track_visibility='onchange',
                                 change_default=True)
    date_offer= fields.Datetime(string="Fecha de Oferta", size=50)
    observations = fields.Char(string="Observaciones", size=50)
    date_created= fields.Datetime('Creado en', index=True, copy=False,
                                 default=fields.Datetime.now)
    email_formatted = fields.Char(
        'Formatted Email', compute='_compute_email_formatted',
        help='Format email address "Name <email@domain>"')

    Payment_Methods = fields.Many2one('settings.intelectra', string='Metodos de Pago', size=13)

    delivery_time = fields.Many2one('settings.intelectra.delivery', string='Tiempo de Entrega', size=13)

    place_of_delivery = fields.Many2one('settings.intelectra.place', string='Lugar de Entrega', size=13)

    date_planned = fields.Datetime(string='Scheduled Date', compute='_compute_date_planned', store=True, index=True)

    amount_untaxed = fields.Monetary(string='Subtotal', store=True, readonly=True, compute='_amount_all',
                                     track_visibility='always')
    amount_tax = fields.Monetary(string='I.V.A. (16%)', store=True, readonly=True, compute='_amount_all')

    amount_total = fields.Monetary(string='Precio Total', store=True, readonly=True, compute='_amount_all')

    notes = fields.Text('Terms and Conditions', default=_default_note)


    @api.model
    def _default_note(self):
        return self.env['ir.config_parameter'].sudo().get_param('purchase.notes')

    @api.depends('email')
    def _compute_email_formatted(self):
        for partner in self:
            partner.email_formatted = formataddr((partner.name or u"False", partner.email or u"False"))



class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    name = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10)
    product_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True)
    taxes_id = fields.Many2many('account.tax', string='Taxes',
                                domain=['|', ('active', '=', False), ('active', '=', True)])
    product_uom = fields.Many2one('product.uom', string='Unit', required=True)
    product_image = fields.Binary(
        'Product Image', related="product_id.image",
        help="Non-stored related field to allow portal user to see the image of the product he has ordered")
    move_ids = fields.One2many('stock.move', 'purchase_line_id', string='Reservation', readonly=True,
                               ondelete='set null', copy=False)
    price_unit = fields.Float(string='Unit Price', required=True, digits=dp.get_precision('Product Price'))

    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)

    order_id = fields.Many2one('purchase.order', string='Order Reference', index=True, required=True,
                               ondelete='cascade')
    state = fields.Selection(related='order_id.state', store=True)

    invoice_lines = fields.One2many('account.invoice.line', 'purchase_line_id', string="Bill Lines", readonly=True,
                                    copy=False)
    # Replace by invoiced Qty
    qty_invoiced = fields.Float(compute='_compute_qty_invoiced', string="Billed Qty",
                                digits=dp.get_precision('Product Unit of Measure'), store=True)
    qty_received = fields.Float(compute='_compute_qty_received', string="Received Qty",
                                digits=dp.get_precision('Product Unit of Measure'), store=True)

    partner_id = fields.Many2one('res.partner', related='order_id.partner_id', string='Partner', readonly=True,
                                 store=True)
    currency_id = fields.Many2one(related='order_id.currency_id', store=True, string='Currency', readonly=True)
    date_order = fields.Datetime(related='order_id.date_order', string='Order Date', readonly=True)

    move_dest_ids = fields.One2many('stock.move', 'created_purchase_line_id', 'Downstream Moves')
    product_id = fields.Many2one('product.product', string='Items/Código de producto', domain=[('purchase_ok', '=', True)],
                                 change_default=True, required=True)




class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    notes = fields.Text(string="Terms & Conditions",config_parameter='purchase.notes')
    use_purchase_note = fields.Boolean(string='Default Terms & Conditions',config_parameter='purchase.use_purchase_note')

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            use_purchase_note=self.env['ir.config_parameter'].get_param('purchase.notes', default=False))
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param("purchase.notes", self.notes)


class generalsettingsintelectra(models.Model):
    _name = 'settings.intelectra'
    _rec_name = 'Payment_Methods'



    Payment_Methods = fields.Char(string='Metodos de Pago')


class generalsettingsintelectradelivery(models.Model):
    _name = 'settings.intelectra.delivery'
    _rec_name = 'delivery_time'


    delivery_time = fields.Char(string='Tiempo de Entrega')


class generalsettingsintelectraplace(models.Model):
    _name = 'settings.intelectra.place'
    _rec_name = 'place_of_delivery'

    place_of_delivery = fields.Char(string='Lugar de Entrega')


class Partner(models.Model):
    _inherit ="res.partner"




    country_id = fields.Many2one('res.country', string='Country')
    vat = fields.Char(string='Rif', help="Tax Identification Number. "
                                         "Fill it if the company is subjected to taxes. "
                                         "Used by the some of the legal statements.")



    @api.onchange('country_id')
    def _compute_country(self):
        if not self.country_id:
            country_id = self.env['res.country'].search([('code', 'like', 'VE')])
            self.country_id =country_id.id
        return








