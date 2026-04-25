{
    "name": "Restaurant Waitlist",
    "version": "19.0.1.0.0",
    "summary": "Waitlist management for Odoo Restaurant.",
    "description": "Adds a functional restaurant waitlist connected to PoS Restaurant tables.",
    "author": "Augusto",
    "license": "LGPL-3",
    "category": "Point of Sale",
    "depends": ["base", "contacts", "point_of_sale", "pos_restaurant"],
    "data": [
        "security/ir.model.access.csv",
        "data/admin_user.xml",
        "data/sequence.xml",
        "views/restaurant_waitlist_views.xml",
        "views/menus.xml",
    ],
    "installable": True,
    "application": True,
}
