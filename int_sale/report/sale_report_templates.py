# -*- coding: utf-8 -*-
from odoo import api, models

class SaleOrderReport(models.AbstractModel):
    _name = 'report.int_sale.report_saleorder_inherit'
    #report.nombre de la carpeta.id del template(report_saleorder_document)

    @api.multi
    def get_report_values(self, docids, data=None):
        ids_product = []
        name_materials = []
        layout_category_ids = []
        layout_category_ids_suma = []
        docs = self.env['sale.order'].browse(docids)
        category = self.env['sale.layout_category'].search([('id','!=',0)])
        for id in category:
            layout_category_ids.append({'id':id.id,'name':id.name,})
        ids_line = self.env['sale.order.line'].search([('order_id','=',docs.id)])

        for ids in ids_line:
            product = ids.product_id.id
            layout_category_ids_suma.append({'id': ids.layout_category_id.id, 'name': ids.layout_category_id.name})
            ids_product.append({'id':product,
                                'code':ids.name,
                                'cant':ids.product_uom_qty,
                                'unid':ids.product_uom.name,
                                'price_unit':ids.price_unit,
                                'price':ids.price_subtotal,
                                'category':ids.layout_category_id.id,
                                'category_name':ids.layout_category_id.name})
            product_product = self.env['product.product'].search([('id','=',product)])
            product_tmpl_id= product_product.product_tmpl_id.id
            mrp_bom = self.env['mrp.bom'].search([('product_tmpl_id','=',product_tmpl_id)])
            mrp_bom_line = self.env['mrp.bom.line'].search([('bom_id', '=', mrp_bom.id)])

            for bom_ids in mrp_bom_line:
                name_materials.append({
                    'id':product,
                    'code':bom_ids.product_id.default_code,
                    'name':bom_ids.product_id.name,
                    'cant':bom_ids.product_qty,
                    'unid':bom_ids.product_uom_id.name,
                    'category_mat':ids.layout_category_id.id})

            for l in ids_product:
                    var = 0
                    for o in name_materials:
                        if o['id'] == l['id']:
                                var = 1

        return {
            'doc_ids': docs.ids,
            'model':self.env['report.int_sale.report_saleorder_inherit'],
            'doc_model': 'sale.order',
            'docs': docs,
            'name_materials':name_materials,
            'ids_product':ids_product,
            'mrp_bom_line':mrp_bom_line,
            'ids_line':ids_line,
            'layout_category_ids':layout_category_ids,
        }