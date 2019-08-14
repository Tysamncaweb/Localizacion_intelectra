# -*- coding: utf-8 -*-
from odoo import api, models

class SaleOrderReport(models.AbstractModel):
    _name = 'report.int_sale.report_saleorder_inherit'
    #report.nombre de la carpeta.id del template(report_saleorder_document)

    @api.multi
    def get_report_values(self, docids, data=None):
        name_materials = []
        docs = self.env['sale.order'].browse(docids)
        ids_line = self.env['sale.order.line'].search([('order_id','=',docs.id)])
        for ids in ids_line:
            product = ids.product_id.id
            mrp_bom = self.env['mrp.bom'].search([('product_id','=',product)])
            mrp_bom_line = self.env['mrp.bom.line'].search([('bom_id', '=', mrp_bom.id)])
            for bom_ids in mrp_bom_line:
                name_materials.append(bom_ids.product_id.name)

        return {
            'doc_ids': docs.ids,
            'model':self.env['report.int_sale.report_saleorder_inherit'],
            'doc_model': 'sale.order',
            'docs': docs,
            'var':'Hola Mundo'
        }