{
    'name': 'Office Quest — Sale',
    'version': '19.0.1.0.0',
    'category': 'Gamification',
    'summary': 'XP rewards for sale order events',
    'author': 'Dipal Shrestha',
    'license': 'LGPL-3',
    'depends': [
        'office_quest',   # core engine
        'sale',           # sale.order model
    ],
    'data': [],
    'installable': True,
    'application': False,   # sub-module, not a standalone app
    'auto_install': False,  # user installs manually
}