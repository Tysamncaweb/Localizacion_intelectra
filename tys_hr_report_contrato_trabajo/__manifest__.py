# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Reporte Contrato de Trabajo',
    'version' : '2.0',
    'summary': 'Generate a work contract report',
    'sequence': 30,
    'description': """
This module generates a work contract report for INTELECTRA company
Colaboradores: María Carreño 
    """,

    'category': 'Human Resources',
    'website': 'http://www.tysamnca.com',
    'depends' : ['hr_payroll'],
    'data': [
        'report/tys_hr_report_contrato_trabajo.xml',

    ],
    'qweb': [
        #"static/src/xml/account_reconciliation.xml",
        #"static/src/xml/account_payment.xml",
        #"static/src/xml/account_report_backend.xml",
        #"static/src/xml/account_dashboard_setup_bar.xml",
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}