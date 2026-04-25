from odoo import http
from odoo.http import request


class RestaurantDemoLogin(http.Controller):
    @http.route("/restaurant-demo/login", type="http", auth="none")
    def login(self, redirect="/odoo", **kwargs):
        request.session.authenticate(
            request.env,
            {
                "login": "reyessamayoa8@gmail.com",
                "password": "Buenas123$",
                "type": "password",
            },
        )
        return request.redirect(redirect)
