{
    'name': 'Office Quest',
    'version': '19.0.1.0.0',
    'category': 'Gamification',
    'summary': 'Turn work into an RPG adventure',
    'author': 'Dipal Shrestha',
    'license': 'LGPL-3',
    'depends': ['base','sale','project','mail'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        'views/views.xml',
        'views/xp_log_views.xml',
        'views/project_task_views.xml',
        'data/cron.xml',
        'report/hero_card_report.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
}