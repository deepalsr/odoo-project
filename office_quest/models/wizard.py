from odoo import models, fields


class AwardXpWizard(models.TransientModel):
    _name = 'game.award.xp.wizard'
    _description = 'Award or Deduct XP Wizard'

    profile_id = fields.Many2one(
        comodel_name='game.profile',
        string='Hero',
        required=True,
    )
    xp_amount = fields.Integer(
        string='XP Amount',
        default=50,
        help='Use a negative value to deduct XP',
    )
    reason = fields.Char(
        string='Reason',
        required=True,
    )
    source = fields.Selection([
        ('manual', 'Manual Award'),
        ('sale_confirm', 'Sale Confirmed'),
        ('sale_cancel', 'Sale Cancelled'),
        ('task_done', 'Task Completed'),
        ('task_cancel', 'Task Cancelled'),
        ('task_deadline', 'Missed Deadline'),
        ('cron', 'Weekly Bonus'),
    ], string='Source', default='manual', readonly=True)
    task_id = fields.Many2one(
        comodel_name='project.task',
        string='Related Task',
        readonly=True,
    )

    def action_award_xp(self):
        self.ensure_one()
        self.profile_id.apply_xp(
            self.xp_amount,
            self.reason,
            source=self.source,
            task_id=self.task_id.id if self.task_id else None,
        )
        return {'type': 'ir.actions.act_window_close'}