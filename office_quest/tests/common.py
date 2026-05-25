from odoo.tests.common import TransactionCase


class OfficeQuestCommon(TransactionCase):
    """
    Shared setup for all Office Quest tests.

    TransactionCase rolls back the entire database after
    each test method — tests are fully isolated.

    What we create here is available in every test as:
        self.manager_user   — user with manager group
        self.regular_user   — user with basic user group only
        self.profile        — game.profile linked to manager_user
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.manager_group = cls.env.ref(
            'office_quest.group_office_quest_manager'
        )
        cls.user_group = cls.env.ref(
            'office_quest.group_office_quest_user'
        )

        # Manager user — can manually award XP
        cls.manager_user = cls.env['res.users'].create({
            'name': 'Test Manager',
            'login': 'test_manager_oq@test.com',
            'group_ids': [(6, 0, [cls.manager_group.id])],  # ← groups_id → group_ids
        })

        # Regular user — cannot manually award XP
        cls.regular_user = cls.env['res.users'].create({
            'name': 'Test Player',
            'login': 'test_player_oq@test.com',
            'group_ids': [(6, 0, [cls.user_group.id])],     # ← groups_id → group_ids
        })

        # A profile to run XP operations against
        cls.profile = cls.env['game.profile'].create({
            'name': 'Test Hero',
            'hero_class': 'warrior',
            'xp': 0,
        })

        # Link profile to manager so _get_xp_player() works
        cls.manager_user.profile_id = cls.profile