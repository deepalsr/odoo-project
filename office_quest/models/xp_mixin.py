from odoo import models
import logging

_logger = logging.getLogger(__name__)


class XpMixin(models.AbstractModel):
    """
    Office Quest — XP Mixin
    ═══════════════════════
    A reusable engine that any Odoo model can inherit to get
    automatic XP award/deduction behaviour.

    HOW TO USE IN YOUR MODULE
    ─────────────────────────
    Step 1 — inherit this mixin alongside your model:

        class SaleOrder(models.Model):
            _inherit = ['sale.order', 'xp.mixin']

    Step 2 — tell the mixin WHO gets the XP:

        def _get_xp_player(self):
            return self.user_id.profile_id

    Step 3 — define WHEN XP fires on field changes (optional):

        def _xp_award_rules(self):
            return {
                'state': {
                    'sale': (100, 'Order confirmed'),
                    'done': (50,  'Order delivered'),
                }
            }

        def _xp_deduct_rules(self):
            return {
                'state': {
                    'cancel': (75, 'Order cancelled'),
                }
            }

    Step 4 — OR trigger XP manually from any button (optional):

        def action_my_button(self):
            self.award_xp_now(200, 'Did something great!')
    """

    _name = 'xp.mixin'
    _description = 'Office Quest — XP Mixin'

    # ══════════════════════════════════════════════════════
    # HOOK 1 — WHO gets the XP?
    # Override this in your model.
    # Must return a single game.profile recordset.
    # ══════════════════════════════════════════════════════
    def _get_xp_player(self):
        self.ensure_one()
        if hasattr(self, 'user_id') and self.user_id:
            return self.user_id.profile_id
        return self.env['game.profile']

    # ══════════════════════════════════════════════════════
    # HOOK 2 — WHEN to award XP on field changes?
    # Format: { 'field_name': { 'new_value': (amount, reason) } }
    # ══════════════════════════════════════════════════════
    def _xp_award_rules(self):
        return {}

    # ══════════════════════════════════════════════════════
    # HOOK 3 — WHEN to deduct XP on field changes?
    # Amounts are POSITIVE — mixin negates them automatically.
    # ══════════════════════════════════════════════════════
    def _xp_deduct_rules(self):
        return {}

    # ══════════════════════════════════════════════════════
    # ENGINE — intercepts all field changes via write()
    #
    # 1. Snapshot old values BEFORE write
    # 2. Call super().write()
    # 3. Compare old vs new — fire XP where values changed
    # ══════════════════════════════════════════════════════
    def write(self, vals):
        award_rules = self._xp_award_rules()
        deduct_rules = self._xp_deduct_rules()

        # Only watch fields that are in our rules AND being written
        tracked_fields = set(award_rules.keys()) | set(deduct_rules.keys())
        fields_to_watch = tracked_fields & set(vals.keys())

        # Step 1 — snapshot old values BEFORE write
        old_values = {}
        if fields_to_watch:
            for record in self:
                old_values[record.id] = {
                    field: getattr(record, field)
                    for field in fields_to_watch
                }

        # Step 2 — perform the actual write
        result = super().write(vals)

        # Step 3 — compare and fire XP
        if fields_to_watch:
            for record in self:
                old = old_values.get(record.id, {})
                for field in fields_to_watch:
                    old_val = old.get(field)
                    new_val = getattr(record, field)

                    # Value didn't change — skip
                    if old_val == new_val:
                        continue

                    # Check award rules
                    if field in award_rules:
                        rule = award_rules[field].get(new_val)
                        if rule:
                            xp_amount, reason = rule
                            record._trigger_xp(xp_amount, reason, 'python_hook')

                    # Check deduct rules
                    if field in deduct_rules:
                        rule = deduct_rules[field].get(new_val)
                        if rule:
                            xp_amount, reason = rule
                            record._trigger_xp(-xp_amount, reason, 'python_hook')

        return result

    # ══════════════════════════════════════════════════════
    # PUBLIC — manual trigger from any button or method
    #
    # Usage:
    #   def action_approve(self):
    #       super().action_approve()
    #       self.award_xp_now(300, 'Request approved!')
    # ══════════════════════════════════════════════════════
    def award_xp_now(self, amount, reason, source='mixin_manual'):
        self.ensure_one()
        self._trigger_xp(amount, reason, source)

    # ══════════════════════════════════════════════════════
    # INTERNAL — safe dispatcher
    # Never call this directly. Use award_xp_now() instead.
    # try/except ensures XP bugs never crash the main transaction.
    # ══════════════════════════════════════════════════════
    def _trigger_xp(self, amount, reason, source):
        self.ensure_one()
        try:
            player = self._get_xp_player()
            if player and player.exists():
                player.apply_xp(amount, reason, source=source, trusted=True)
            else:
                _logger.warning(
                    "XP Mixin [%s id=%s]: No game.profile found. "
                    "Override _get_xp_player() in your model.",
                    self._name, self.id,
                )
        except Exception as exc:
            _logger.error(
                "XP Mixin [%s id=%s]: Failed to apply XP — %s",
                self._name, self.id, exc,
            )