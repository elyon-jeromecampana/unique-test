# -*- coding: utf-8 -*-
{
    'name': "BIR Compliance",

    'summary': "BIR Compliance Module",

    'description': """
        Long description of module's purpose
    """,

    'author': "Jerome Campana, Elyon Solutions International Inc.",
    'website': "www.elyon-solutions.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'reports/bir_form_2307.xml',
        'reports/paper_format.xml',
        'reports/bir_form_2550M.xml',
        'reports/bir_form_2550Q.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
