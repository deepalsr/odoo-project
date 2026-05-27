from odoo import models


class ProjectTask(models.Model):
    """
    Office Quest — Project Task XP integration.

    project.task uses the manual button pattern — a manager
    clicks Award/Deduct XP on a task and a wizard opens.

    It also supports auto tracking via _xp_award_rules() —
    override that method to fire XP automatically on stage changes.
    """

    _inherit = ['project.task', 'xp.mixin']

    # WHO gets the XP — first assignee on the task
    def _get_xp_player(self):
        self.ensure_one()
        user = self.user_ids[:1] if self.user_ids else self.env['res.users']
        return user.profile_id if user else self.env['game.profile']

    # No automatic rules — project uses manual buttons by default.
    # Override in your own module to add stage-based auto rules.
    def _xp_award_rules(self):
        return {}

    def _xp_deduct_rules(self):
        return {}

    # MANUAL BUTTON — opens wizard to award XP
    def action_award_task_xp(self):
        self.ensure_one()
        player = self._get_xp_player()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Award XP',
            'res_model': 'game.award.xp.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_profile_id': player.id if player else False,
                'default_xp_amount': 100,
                'default_reason': f'Task completed: {self.name}',
                'default_source': 'task_done',
                'default_task_id': self.id,
                'default_action': 'award',
                'default_task_model': self._name,
                'default_task_record_id': self.id,
            },
        }

    # MANUAL BUTTON — opens wizard to deduct XP
    def action_deduct_task_xp(self):
        self.ensure_one()
        player = self._get_xp_player()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Deduct XP',
            'res_model': 'game.award.xp.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_profile_id': player.id if player else False,
                'default_xp_amount': 50,
                'default_reason': f'Missed deadline: {self.name}',
                'default_source': 'task_deadline',
                'default_task_id': self.id,
                'default_action': 'deduct',
                'default_task_model': self._name,
                'default_task_record_id': self.id,
            },
        }