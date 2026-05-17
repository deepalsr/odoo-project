{
    'name': 'Expense Tracker',
    'version': '1.1',
    'category': 'Human Resources',
    'summary': 'Track expenses with manager approval',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/expense_view.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}