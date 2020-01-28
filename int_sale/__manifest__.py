# encoding: UTF-8
# Create:  jeduardo** 26/08/2017 **  **
# type of the change:  Creacion
# Comments: Creacion del modulo de calling
#Contiene un diccionario en Python para agregar las descripciones del módulo, como autor, versión, etc.
{
    'name': 'int_sale',
    'version':'1.0',
    'category': 'Sale',
    'summary':'',
    'description': '''\
Adecuaciones al modulo de ventas
============================

V1.1.1.\n
Adecuaciones al modulo de ventas del Cliente Intelectra\n
''',
    'author': 'TYSAMNCA',
    'website': 'https://www.tysamnca.com',
    #data, es una lista donde se agregan todas las vistas del módulo, es decir los archivos.xml y archivos.csv.
    'data': [
            'views/sale_order.xml',
            'views/res_users.xml',
            'report/sale_report_templates.xml',
            ],
    #depends,  es una lista donde se agregan los módulos que deberían estar instalados (Módulos dependencia) para que el modulo pueda ser instalado en Odoo.
    'depends': ['base','sale','project'],
    'js': [],
    'css': [],
    'qweb' : [],
    #'installable': True,
    #'auto_install': False,
    'application': True,
}