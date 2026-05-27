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
        help='Positive to award, negative to deduct.',
    )
    reason = fields.Char(
        string='Reason',
        required=True,
    )

    # Char — not hardcoded Selection.
    # Set automatically by the button/context that opened this wizard.
    source = fields.Char(
        string='Source',
        default='manual',
        readonly=True,
    )

    task_id = fields.Many2one(
        comodel_name='project.task',
        string='Related Task',
        readonly=True,
    )

    # Record reference — routes through xp.mixin if available
    task_model = fields.Char(readonly=True)
    task_record_id = fields.Integer(readonly=True)

    def action_award_xp(self):
        self.ensure_one()

        if self.task_model and self.task_record_id:
            # Route through xp.mixin — preferred path
            record = self.env[self.task_model].browse(self.task_record_id)
            if record.exists():
                record.award_xp_now(self.xp_amount, self.reason, source=self.source)
                return {'type': 'ir.actions.act_window_close'}

        # Fallback — direct profile award (e.g. from profile form)
        # trusted=True because this is an intentional manager action
        self.profile_id.apply_xp(
            self.xp_amount,
            self.reason,
            source=self.source,
            task_id=self.task_id.id if self.task_id else None,
            trusted=True,
        )
        return {'type': 'ir.actions.act_window_close'}