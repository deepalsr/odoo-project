from odoo import http
from odoo.http import request


class QuestWebsite(http.Controller):

    @http.route('/quest', auth='public', website=True)
    def leaderboard(self, **kwargs):
        profiles = request.env['game.profile'].sudo().search(
            [], order='xp desc'
        )
        return request.render('office_quest.quest_leaderboard', {
            'profiles': profiles,
        })

    @http.route('/quest/my', auth='user', website=True)
    def my_profile(self, **kwargs):
        user = request.env.user
        profile = user.profile_id
        if not profile:
            return request.redirect('/quest')
        logs = request.env['game.xp.log'].sudo().search(
            [('profile_id', '=', profile.id)],
            order='create_date desc',
            limit=20,
        )
        return request.render('office_quest.quest_my_profile', {
            'profile': profile,
            'logs': logs,
        })

    @http.route('/quest/manage', auth='user', website=True)
    def manage(self, **kwargs):
        if not request.env.user.has_group(
            'office_quest.group_office_quest_manager'
        ):
            return request.redirect('/quest')
        profiles = request.env['game.profile'].sudo().search(
            [], order='xp desc'
        )
        logs = request.env['game.xp.log'].sudo().search(
            [], order='create_date desc', limit=50
        )
        return request.render('office_quest.quest_manage', {
            'profiles': profiles,
            'logs': logs,
        })