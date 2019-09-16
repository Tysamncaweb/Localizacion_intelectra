# coding: utf-8
###########################################################################

import time

#from odoo.report import report_sxw
#from odoo.tools.translate import _
from odoo import models, api, _
from odoo.exceptions import UserError, Warning, ValidationError

class IvaReport(models.AbstractModel):
    _name = 'report.l10n_ve_withholding_iva.template_wh_vat'
    #_name = 'report.l10n_ve_withholding_iva.template_wh_vat'

    #_inherit = 'report.abstract_report'
    #_template = 'l10n_ve_withholding_iva.template_wh_vat'

    @api.model
    def get_report_values(self, docids, data=None):
        if not docids:
            raise UserError(_("You need select a data to print."))
        data = {'form': self.env['account.wh.iva'].browse(docids)}
        res = dict()
        return {
            'data': data['form'],
            'model': self.env['report.l10n_ve_withholding_iva.template_wh_vat'],
            'lines': res, #self.get_lines(data.get('form')),
            #date.partner_id
        }

    def get_period(self, date):
        if not date:
            raise Warning (_("You need date."))
        split_date = date.split('-')
        return str(split_date[1]) + '/' + str(split_date[0])

    def get_date(self, date):
        if not date:
            raise Warning(_("You need date."))
        split_date = date.split('-')
        return str(split_date[2]) + '/' + (split_date[1]) + '/' + str(split_date[0])

    #def get_direction(self, partner):
    #    direction = ''
    #    direction = ((partner.street and partner.street + ', ') or '') +\
    #                ((partner.street2 and partner.street2 + ', ') or '') +\
    #                ((partner.city and partner.city + ', ') or '') +\
    #                ((partner.state_id.name and partner.state_id.name + ',')or '')+ \
    #                ((partner.country_id.name and partner.country_id.name + '') or '')
        #if direction == '':
        #    raise ValidationError ("Debe ingresar los datos de direccion en el proveedor")
            #direction = 'Sin direccion'
    #    return direction

    def get_tipo_doc(self, tipo=None):
        if not tipo:
            return []
        types = {'out_invoice': '1', 'in_invoice': '1', 'out_refund': '2',
                 'in_refund': '2'}
        return types[tipo]

        # DATOS DEL AGENTE DE RETENCIÓN
        # Direccion del agente retenido
    def get_direction(self, value):
            direction = 'Sin direccion'
            if 'out' in value.type:
                direction = ((value.partner_id.street and value.partner_id.street + ', ') or '') + \
                            ((value.partner_id.street2 and value.partner_id.street2 + ', ') or '') + \
                            ((value.partner_id.city and value.partner_id.city + ', ') or '') + \
                            ((value.partner_id.state_id.name and value.partner_id.state_id.name + ',') or '') + \
                            ((value.partner_id.country_id.name and value.partner_id.country_id.name + '') or '')
            else:
                direction = ((value.company_id.partner_id.street and value.company_id.partner_id.street + ', ') or '') + \
                            ((
                             value.company_id.partner_id.street2 and value.company_id.partner_id.street2 + ', ') or '') + \
                            ((value.company_id.partner_id.city and value.company_id.partner_id.city + ', ') or '') + \
                            ((
                             value.company_id.partner_id.state_id.name and value.company_id.partner_id.state_id.name + ',') or '') + \
                            ((
                             value.company_id.partner_id.country_id.name and value.company_id.partner_id.country_id.name + '') or '')
            return direction

    def get_retenido_name(self, value):
            res = ''
            if 'out' in value.type:
                res = value.partner_id.name
            else:
                res = value.company_id.partner_id.name
            return res

    def get_retenido_vat(self, value):
            res = ''
            if 'out' in value.type:
                if value.partner_id.vat:
                    res = value.partner_id.vat[2:] if 'VE' in value.partner_id.vat else value.partner_id.vat
            else:
                if value.company_id.partner_id.vat:
                    res = value.company_id.partner_id.vat[
                          2:] if 'VE' in value.company_id.partner_id.vat else value.company_id.partner_id.vat
            return res

    def get_retenido_phone(self, value):
            res = ''
            if 'out' in value.type:
                if value.partner_id.vat:
                    res = value.partner_id.phone
            else:
                if value.company_id.partner_id.vat:
                    res = value.company_id.partner_id.phone
            return res

        # DATOS DEL AGENTE DE RETENIDO
    def get_retencion_name(self, value):
            res = ''
            if 'out' in value.type:
                res = value.company_id.partner_id.name
            else:
                res = value.partner_id.name
            return res

    def get_retencion_vat(self, value):
            res = ''
            if 'out' in value.type:
                if value.company_id.partner_id.vat:
                    res = value.company_id.partner_id.vat[
                          2:] if 'VE' in value.company_id.partner_id.vat else value.company_id.partner_id.vat
            else:
                if value.partner_id.vat:
                    res = value.partner_id.vat[2:] if 'VE' in value.partner_id.vat else value.partner_id.vat
            return res

    def get_retencion_dir(self, value):
            direction = 'Sin direccion'
            if 'out' in value.type:
                direction = ((value.company_id.partner_id.street and value.company_id.partner_id.street + ', ') or '') + \
                            ((
                             value.company_id.partner_id.street2 and value.company_id.partner_id.street2 + ', ') or '') + \
                            ((value.company_id.partner_id.city and value.company_id.partner_id.city + ', ') or '') + \
                            ((
                                 value.company_id.partner_id.state_id.name and value.company_id.partner_id.state_id.name + ',') or '') + \
                            ((
                                 value.company_id.partner_id.country_id.name and value.company_id.partner_id.country_id.name + '') or '')
            else:
                direction = ((value.partner_id.street and value.partner_id.street + ', ') or '') + \
                            ((value.partner_id.street2 and value.partner_id.street2 + ', ') or '') + \
                            ((value.partner_id.city and value.partner_id.city + ', ') or '') + \
                            ((value.partner_id.state_id.name and value.partner_id.state_id.name + ',') or '') + \
                            ((value.partner_id.country_id.name and value.partner_id.country_id.name + '') or '')

            return direction

    def get_retencion_phone(self, value):
            res = ''
            if 'out' in value.type:
                res = value.company_id.partner_id.phone
            else:
                res = value.partner_id.phone
            return res
