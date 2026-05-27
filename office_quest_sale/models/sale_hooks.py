from odoo import models


class SaleOrder(models.Model):
    """
    Office Quest — Sale Order XP integration.

    This is the reference implementation shipped with Office Quest.
    Install this sub-module to automatically award/deduct XP
    on sale order state changes.

    Customising XP amounts:
        Create your own module that depends on office_quest_sale
        and override these three methods.
    """

    _inherit = ['sale.order', 'xp.mixin']

    # WHO gets the XP — the salesperson on the order
    def _get_xp_player(self):
        self.ensure_one()
        return self.user_id.profile_id if self.user_id else self.env['game.profile']

    # WHEN to award — order confirmed or completed
    def _xp_award_rules(self):
        return {
            'state': {
                'sale': (150, 'Sale order confirmed'),
                'done': (50,  'Sale order completed'),
            }
        }

    # WHEN to deduct — order cancelled
    def _xp_deduct_rules(self):
        return {
            'state': {
                'cancel': (150, 'Sale order cancelled'),
            }
        }