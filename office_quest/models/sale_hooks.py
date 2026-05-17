from odoo import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        result = super().action_confirm()

        
        profile = self.env.user.profile_id
        if profile:
            profile.xp += 150

        return result