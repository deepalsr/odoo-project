from odoo import models, fields


class AwardXpWizard(models.TransientModel):
    _name = 'game.award.xp.wizard'
    _description = 'Award Bonus XP Wizard'

    profile_id = fields.Many2one(
        comodel_name='game.profile',
        string='Hero',
        required=True,
    )
    xp_amount = fields.Integer(string='XP to Award', default=50)
    reason = fields.Char(string='Reason')

    def action_award_xp(self):
        self.ensure_one()
        if self.profile_id:
            self.profile_id.xp += self.xp_amount
        return {'type': 'ir.actions.act_window_close'}