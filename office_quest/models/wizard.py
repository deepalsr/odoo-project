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
        help='Use a positive value. For deductions the button determines the sign.',
    )
    reason = fields.Char(
        string='Reason',
        required=True,
    )

    # Free text now — not a hardcoded Selection.
    # Any consumer module can pass its own source string
    # without needing to modify Office Quest core.
    source = fields.Char(
        string='Source',
        default='manual',
        readonly=True,
        help='Set automatically by the button that opened this wizard.',
    )

    task_id = fields.Many2one(
        comodel_name='project.task',
        string='Related Task',
        readonly=True,
    )

    # Which record triggered this wizard — used to route
    # through xp.mixin instead of calling apply_xp directly
    task_model = fields.Char(readonly=True)
    task_record_id = fields.Integer(readonly=True)

    # action = 'award' or 'deduct' — set by context from the button
    action = fields.Selection([
        ('award', 'Award'),
        ('deduct', 'Deduct'),
    ], default='award', readonly=True)

    def action_award_xp(self):
        """
        Confirm button on the wizard.

        If we have a record reference (task_model + task_record_id),
        we route through xp.mixin.award_xp_now() — this keeps the
        full mixin engine in the loop (logging, player lookup, etc).

        Fallback: call apply_xp() directly on the profile with
        trusted=True — for manual awards from the profile form itself.
        """
        self.ensure_one()

        # Determine final sign based on action
        amount = abs(self.xp_amount)
        if self.action == 'deduct':
            amount = -amount

        if self.task_model and self.task_record_id:
            # Route through xp.mixin — preferred path
            record = self.env[self.task_model].browse(self.task_record_id)
            if record.exists():
                record.award_xp_now(amount, self.reason, source=self.source)
                return {'type': 'ir.actions.act_window_close'}

        # Fallback — direct profile award (e.g. from profile form button)
        # trusted=True because this is an intentional manager action
        self.profile_id.apply_xp(
            amount,
            self.reason,
            source=self.source,
            task_id=self.task_id.id if self.task_id else None,
            trusted=True,
        )
        return {'type': 'ir.actions.act_window_close'}