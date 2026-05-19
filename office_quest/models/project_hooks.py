from odoo import models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    def action_award_task_xp(self):
        self.ensure_one()
        # Get the first assigned user's hero profile
        assigned_user = self.user_ids[:1] if self.user_ids else self.env['res.users']
        profile = assigned_user.profile_id if assigned_user else self.env['game.profile']
        return {
            'type': 'ir.actions.act_window',
            'name': 'Award XP',
            'res_model': 'game.award.xp.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_profile_id': profile.id if profile else False,
                'default_xp_amount': 100,
                'default_reason': f'Task completed: {self.name}',
                'default_source': 'task_done',
                'default_task_id': self.id,
            },
        }

    def action_deduct_task_xp(self):
        self.ensure_one()
        assigned_user = self.user_ids[:1] if self.user_ids else self.env['res.users']
        profile = assigned_user.profile_id if assigned_user else self.env['game.profile']
        return {
            'type': 'ir.actions.act_window',
            'name': 'Deduct XP',
            'res_model': 'game.award.xp.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_profile_id': profile.id if profile else False,
                'default_xp_amount': -50,
                'default_reason': f'Missed deadline: {self.name}',
                'default_source': 'task_deadline',
                'default_task_id': self.id,
            },
        }