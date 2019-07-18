# -*- coding: utf-8 -*-
{
    'name': "Intelectra Account Invoice Report",

    'summary': """Intelectra_Module_Account_Invoice_Report""",

    'description': """
       Reporte para facturas y facturas sin pago en Facturas de Clientes.
       Colaboradores: Yamile Rayme
    """,
    'version': '1.0',
    'author': 'Tysamnca',
    'category': 'Tools',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'report/account_invoice_report.xml',
        'report/account_invoice_report_me.xml',
        'report/account_invoice_with_payment_report.xml',
        'report/account_invoice_with_payment_report_me.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
    'application': True,
}