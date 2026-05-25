from odoo import models, fields


class XpLog(models.Model):
    _name = 'game.xp.log'
    _description = 'XP Event Log'
    _order = 'create_date desc'

    profile_id = fields.Many2one(
        comodel_name='game.profile',
        string='Hero',
        required=True,
        ondelete='cascade',
    )
    xp_change = fields.Integer(string='XP Change', required=True)
    reason = fields.Char(string='Reason', required=True)

    # Char instead of Selection — any source string works.
    # Examples: 'python_hook', 'mixin_manual', 'cron', 'manual'
    source = fields.Char(
        string='Source',
        default='manual',
    )

    performed_by = fields.Many2one(
        comodel_name='res.users',
        string='Performed By',
        default=lambda self: self.env.user,
        readonly=True,
    )
    task_id = fields.Many2one(
        comodel_name='project.task',
        string='Related Task',
        ondelete='set null',
    )