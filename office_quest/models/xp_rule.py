from odoo import models, fields, api


class XpRule(models.Model):
    """
    game.xp.rule — UI-configured XP rules.

    Admins create rules in Office Quest → Configuration → XP Rules.
    No Python needed. Rules fire automatically via xp.mixin.write().

    Priority: Python hooks (_xp_award_rules / _xp_deduct_rules)
    override DB rules for the same field+value combination.
    DB rules only fire when Python hooks have nothing for that trigger.
    """

    _name = 'game.xp.rule'
    _description = 'Office Quest — XP Rule'
    _order = 'model_id, sequence'

    name = fields.Char(
        string='Rule Name',
        required=True,
    )
    sequence = fields.Integer(
        default=10,
        help='Lower sequence fires first when multiple rules match.',
    )
    active = fields.Boolean(
        default=True,
        help='Uncheck to disable this rule without deleting it.',
    )

    # ── WHAT model does this rule watch? ──────────────────
    model_id = fields.Many2one(
        comodel_name='ir.model',
        string='Model',
        required=True,
        ondelete='cascade',
        help='The Odoo model this rule watches. e.g. Sale Order',
    )
    # technical name e.g. 'sale.order' — used in write() lookup
    model_name = fields.Char(
        related='model_id.model',
        store=True,
        readonly=True,
    )

    # ── WHAT field on that model? ─────────────────────────
    field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Field',
        required=True,
        ondelete='cascade',
        domain="[('model_id', '=', model_id), "
               " ('ttype', 'in', ['selection', 'boolean', 'integer'])]",
        help='Only Selection, Boolean, and Integer fields are supported.',
    )
    field_name = fields.Char(
        related='field_id.name',
        store=True,
        readonly=True,
    )
    # Computed from the field — drives which trigger widget shows
    field_type = fields.Selection(
        related='field_id.ttype',
        string='Field Type',
        readonly=True,
        store=True,
    )

    # ── TRIGGER VALUE — one per field type ────────────────
    # Only one is used at a time depending on field_type.
    # We use separate fields so each has the right widget in UI.

    trigger_value_selection = fields.Char(
        string='When value becomes',
        help='For Selection fields. Enter the technical value e.g. "sale", "done"',
    )
    trigger_value_boolean = fields.Boolean(
        string='When value is',
        help='For Boolean fields. True = checked, False = unchecked.',
    )
    trigger_operator = fields.Selection([
        ('=',  'Equal to'),
        ('>',  'Greater than'),
        ('>=', 'Greater than or equal to'),
        ('<',  'Less than'),
        ('<=', 'Less than or equal to'),
    ], string='Operator', default='=')
    trigger_value_integer = fields.Integer(
        string='Value',
        help='For Integer fields.',
    )

    # ── WHAT happens when triggered? ──────────────────────
    action = fields.Selection([
        ('award',  'Award XP'),
        ('deduct', 'Deduct XP'),
    ], string='Action', required=True, default='award')

    xp_amount = fields.Integer(
        string='XP Amount',
        required=True,
        default=100,
        help='Always positive. Action determines whether it is added or subtracted.',
    )
    reason = fields.Char(
        string='Reason',
        required=True,
        help='Shown in the chatter and XP log. e.g. "Sale order confirmed"',
    )

    # ── VALIDATION ────────────────────────────────────────
    @api.constrains('xp_amount')
    def _check_xp_amount(self):
        for rule in self:
            if rule.xp_amount <= 0:
                raise models