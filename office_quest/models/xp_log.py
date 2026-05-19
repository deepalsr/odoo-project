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
    source = fields.Selection([
        ('manual', 'Manual Award'),
        ('sale_confirm', 'Sale Confirmed'),
        ('sale_cancel', 'Sale Cancelled'),
        ('task_done', 'Task Completed'),
        ('task_cancel', 'Task Cancelled'),
        ('task_deadline', 'Missed Deadline'),
        ('cron', 'Weekly Bonus'),
    ], string='Source', default='manual')
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

