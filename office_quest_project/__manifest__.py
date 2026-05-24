{
    'name': 'Office Quest — Project',
    'version': '19.0.1.0.0',
    'category': 'Gamification',
    'summary': 'XP rewards for project task events',
    'author': 'Dipal Shrestha',
    'license': 'LGPL-3',
    'depends': [
        'office_quest',   # core engine
        'project',        # project.task model
    ],
    'data': [
        'views/project_task_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}