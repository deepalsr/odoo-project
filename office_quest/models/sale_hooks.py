from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_user_profile(self):
        profile = self.env.user.profile_id
        if not profile:
            profile = self.env['game.profile'].search(
                [('name', '=', self.env.user.name)], limit=1
            )
        return profile

    def action_confirm(self):
        result = super().action_confirm()
        profile = self._get_user_profile()
        if profile:
            profile.apply_xp(
                150,
                f'Sale confirmed: {self.name}',
                source='sale_confirm',
            )
        return result

    def _action_cancel(self):
        result = super()._action_cancel()
        profile = self._get_user_profile()
        if profile:
            profile.apply_xp(
                -150,
                f'Sale cancelled: {self.name}',
                source='sale_cancel',
            )
        return result