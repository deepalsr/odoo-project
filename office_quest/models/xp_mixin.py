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

    PRIORITY RULE
    ─────────────
    If both a Python hook AND a UI rule (game.xp.rule) exist
    for the same model + field + value, the Python hook wins
    and the UI rule is skipped for that trigger.
    """

    _name = 'xp.mixin'
    _description = 'Office Quest — XP Mixin'

    # ══════════════════════════════════════════════════════
    # HOOK 1 — WHO gets the XP?
    #
    # Override this in your model.
    # Must return a single game.profile recordset.
    # ══════════════════════════════════════════════════════
    def _get_xp_player(self):
        self.ensure_one()
        # Default — works for any model that has user_id
        # e.g. sale.order, purchase.order, helpdesk.ticket
        if hasattr(self, 'user_id') and self.user_id:
            return self.user_id.profile_id
        # No user_id found — return empty recordset, no XP fires
        return self.env['game.profile']

    # ══════════════════════════════════════════════════════
    # HOOK 2 — WHEN to award XP on field changes?
    #
    # Return format:
    #   { 'field_name': { 'new_value': (xp_amount, reason) } }
    #
    # Returning {} means: rely on UI rules only.
    # ══════════════════════════════════════════════════════
    def _xp_award_rules(self):
        return {}

    # ══════════════════════════════════════════════════════
    # HOOK 3 — WHEN to deduct XP on field changes?
    #
    # Same format as award rules.
    # xp_amount is POSITIVE — mixin negates it automatically.
    # ══════════════════════════════════════════════════════
    def _xp_deduct_rules(self):
        return {}

    # ══════════════════════════════════════════════════════
    # ENGINE — intercepts all field changes
    #
    # Flow:
    #   1. Snapshot old values BEFORE write
    #   2. Call super().write() to save data
    #   3. Compare old vs new
    #   4. Check Python hooks first (higher priority)
    #   5. Fall through to UI rules if Python had nothing
    # ══════════════════════════════════════════════════════
    def write(self, vals):
        award_rules = self._xp_award_rules()
        deduct_rules = self._xp_deduct_rules()

        # Fields tracked by Python hooks
        python_fields = set(award_rules.keys()) | set(deduct_rules.keys())

        # DB rules for this specific model — loaded once per write() call
        db_rules = self.env['game.xp.rule'].search([
            ('model_name', '=', self._name),
            ('active', '=', True),
        ])
        db_fields = set(db_rules.mapped('field_name'))

        # Union of both sources — only watch fields being written right now
        all_tracked = python_fields | db_fields
        fields_to_watch = all_tracked & set(vals.keys())

        # Step 1 — snapshot old values per record BEFORE the write
        # Only read fields we actually care about — no wasted DB reads
        old_values = {}
        if fields_to_watch:
            for record in self:
                old_values[record.id] = {
                    field: getattr(record, field)
                    for field in fields_to_watch
                }

        # Step 2 — perform the actual write
        result = super().write(vals)

        # Step 3 — compare old vs new and fire XP
        if fields_to_watch:
            for record in self:
                old = old_values.get(record.id, {})
                for field in fields_to_watch:
                    old_val = old.get(field)
                    new_val = getattr(record, field)

                    # Nothing changed on this field — skip
                    if old_val == new_val:
                        continue

                    # ── SOURCE 1: Python hooks (higher priority) ──────
                    # If Python defines a rule for this field+value,
                    # fire it and mark python_fired = True so DB rules
                    # are skipped for this particular trigger.
                    python_fired = False

                    if field in award_rules:
                        rule = award_rules[field].get(new_val)
                        if rule:
                            xp_amount, reason = rule
                            record._trigger_xp(xp_amount, reason, 'python_hook')
                            python_fired = True

                    if field in deduct_rules:
                        rule = deduct_rules[field].get(new_val)
                        if rule:
                            xp_amount, reason = rule
                            record._trigger_xp(-xp_amount, reason, 'python_hook')
                            python_fired = True

                    # ── SOURCE 2: UI rules (fallback) ─────────────────
                    # Only runs if Python had nothing for this trigger.
                    # Admin-configured rules from game.xp.rule table.
                    if not python_fired:
                        matching = db_rules.filtered(
                            lambda r: r.field_name == field
                            and r._matches(new_val)
                        )
                        for db_rule in matching:
                            amount = db_rule.xp_amount
                            if db_rule.action == 'deduct':
                                amount = -amount
                            record._trigger_xp(amount, db_rule.reason, 'ui_rule')

        return result

    # ══════════════════════════════════════════════════════
    # PUBLIC — manual button trigger
    #
    # Call from any method or button in your model:
    #   def action_approve(self):
    #       super().action_approve()
    #       self.award_xp_now(300, 'Request approved!')
    # ══════════════════════════════════════════════════════
    def award_xp_now(self, amount, reason, source='mixin_manual'):
        self.ensure_one()
        self._trigger_xp(amount, reason, source)

    # ══════════════════════════════════════════════════════
    # INTERNAL — safe dispatcher
    #
    # Finds the player and calls apply_xp().
    # try/except ensures an XP bug never crashes the real
    # business transaction (e.g. confirming a sale order).
    # ══════════════════════════════════════════════════════
    def _trigger_xp(self, amount, reason, source):
        self.ensure_one()
        try:
            player = self._get_xp_player()
            if player and player.exists():
                # trusted=True — bypasses the manager-only check
                # in apply_xp() for all automated/mixin flows
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