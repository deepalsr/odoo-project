from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        result = super().action_confirm()
        # Iterate per order — handles multi-recordset confirm
        for order in self:
            # Use salesperson profile, not session user
            profile = order.user_id.profile_id if order.user_id else None
            if profile:
                profile.apply_xp(
                    150,
                    f'Sale confirmed: {order.name}',
                    source='sale_confirm',
                )
        return result

    def _action_cancel(self):
        result = super()._action_cancel()
        # Iterate per order — handles multi-recordset cancel
        for order in self:
            # Use salesperson profile, not session user
            profile = order.user_id.profile_id if order.user_id else None
            if profile:
                profile.apply_xp(
                    -150,
                    f'Sale cancelled: {order.name}',
                    source='sale_cancel',
                )
        return result