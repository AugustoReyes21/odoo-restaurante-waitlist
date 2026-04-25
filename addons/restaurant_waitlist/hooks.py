from odoo import Command


def post_init_hook(env):
    """Prepare the restaurant demo after installing the addon."""
    ensure_restaurant_setup(env)


def ensure_restaurant_setup(env):
    """Make the restaurant ready to use without manual configuration."""
    company = env.ref("base.main_company")
    floors = _ensure_floors_and_tables(env)
    payments = _ensure_payment_methods(env, company)
    products = _ensure_menu_products(env)
    _ensure_pos_config(env, company, floors, payments)
    return {
        "floors": len(floors),
        "payments": len(payments),
        "products": len(products),
    }


def _ensure_payment_methods(env, company):
    journal_model = env["account.journal"]
    payment_model = env["pos.payment.method"]

    sale_journal = journal_model.search(
        [("name", "=", "Punto de Venta Restaurante"), ("company_id", "=", company.id)],
        limit=1,
    ) or journal_model.create(
        {
            "name": "Punto de Venta Restaurante",
            "code": "POSS",
            "type": "general",
            "company_id": company.id,
        }
    )
    cash_journal = journal_model.search(
        [("name", "=", "Efectivo Restaurante"), ("company_id", "=", company.id)],
        limit=1,
    ) or journal_model.create(
        {
            "name": "Efectivo Restaurante",
            "code": "CSHR",
            "type": "cash",
            "company_id": company.id,
        }
    )
    bank_journal = journal_model.search(
        [("name", "=", "Banco Restaurante"), ("company_id", "=", company.id)],
        limit=1,
    ) or journal_model.create(
        {
            "name": "Banco Restaurante",
            "code": "BNKR",
            "type": "bank",
            "company_id": company.id,
        }
    )

    payments = []
    for name, journal in (
        ("Efectivo", cash_journal),
        ("Tarjeta", bank_journal),
    ):
        payment = payment_model.search(
            [("name", "=", name), ("company_id", "=", company.id)],
            limit=1,
        )
        vals = {"name": name, "journal_id": journal.id, "company_id": company.id}
        if payment:
            payment.write(vals)
        else:
            payment = payment_model.create(vals)
        payments.append(payment)

    customer_account = payment_model.search(
        [("name", "=", "Cuenta de cliente"), ("company_id", "=", company.id)],
        limit=1,
    )
    vals = {
        "name": "Cuenta de cliente",
        "split_transactions": True,
        "company_id": company.id,
    }
    if customer_account:
        customer_account.write(vals)
    else:
        customer_account = payment_model.create(vals)
    payments.append(customer_account)

    return env["pos.payment.method"].browse([payment.id for payment in payments]), sale_journal


def _ensure_floors_and_tables(env):
    floor_model = env["restaurant.floor"]
    table_model = env["restaurant.table"]

    main_floor = floor_model.search([("name", "=", "Main Floor")], limit=1)
    if not main_floor:
        main_floor = floor_model.create(
            {
                "name": "Main Floor",
                "sequence": 1,
                "background_color": "rgb(237,230,219)",
                "active": True,
            }
        )

    patio = floor_model.search([("name", "=", "Patio")], limit=1)
    if not patio:
        patio = floor_model.create(
            {
                "name": "Patio",
                "sequence": 2,
                "background_color": "rgb(222,236,225)",
                "active": True,
            }
        )

    tables = [
        (main_floor, "1", 4, 220, 120, 90, 90, "square", "rgb(53,211,116)"),
        (main_floor, "2", 4, 390, 120, 90, 90, "square", "rgb(53,211,116)"),
        (main_floor, "3", 6, 570, 120, 130, 90, "square", "rgb(53,211,116)"),
        (main_floor, "4", 4, 220, 260, 90, 90, "square", "rgb(53,211,116)"),
        (main_floor, "5", 4, 390, 260, 90, 90, "square", "rgb(53,211,116)"),
        (main_floor, "6", 6, 570, 350, 130, 90, "square", "rgb(53,211,116)"),
        (main_floor, "7", 4, 220, 430, 90, 90, "square", "rgb(235,109,109)"),
        (main_floor, "8", 4, 390, 430, 90, 90, "square", "rgb(235,109,109)"),
        (main_floor, "9", 6, 120, 570, 130, 90, "square", "rgb(235,109,109)"),
        (main_floor, "10", 4, 250, 570, 90, 90, "square", "rgb(235,109,109)"),
        (main_floor, "11", 4, 390, 570, 90, 90, "square", "rgb(172,109,173)"),
        (main_floor, "12", 6, 570, 570, 130, 90, "square", "rgb(172,109,173)"),
        (patio, "21", 4, 150, 130, 90, 90, "round", "rgb(53,211,116)"),
        (patio, "22", 4, 320, 130, 90, 90, "round", "rgb(53,211,116)"),
        (patio, "23", 6, 490, 130, 120, 90, "square", "rgb(53,211,116)"),
        (patio, "24", 4, 150, 290, 90, 90, "round", "rgb(235,109,109)"),
        (patio, "25", 4, 320, 290, 90, 90, "round", "rgb(235,109,109)"),
        (patio, "26", 6, 490, 290, 120, 90, "square", "rgb(172,109,173)"),
    ]

    for floor, identifier, seats, x, y, width, height, shape, color in tables:
        table = table_model.search(
            [("floor_id", "=", floor.id), ("identifier", "=", identifier)],
            limit=1,
        )
        vals = {
            "floor_id": floor.id,
            "table_number": int(identifier),
            "identifier": identifier,
            "seats": seats,
            "position_h": x,
            "position_v": y,
            "width": width,
            "height": height,
            "shape": shape,
            "color": color,
        }
        if table:
            table.write(vals)
        else:
            table_model.create(vals)

    return env["restaurant.floor"].browse([main_floor.id, patio.id])


def _ensure_menu_products(env):
    categories = {
        "food": env.ref("pos_restaurant.food", raise_if_not_found=False),
        "drinks": env.ref("pos_restaurant.drinks", raise_if_not_found=False),
    }

    products = [
        ("Hamburguesa de la casa", 45.00, categories["food"]),
        ("Pizza margarita", 62.00, categories["food"]),
        ("Pasta Alfredo", 55.00, categories["food"]),
        ("Cafe americano", 18.00, categories["drinks"]),
        ("Gaseosa", 15.00, categories["drinks"]),
        ("Agua pura", 10.00, categories["drinks"]),
    ]

    ready_products = []
    for name, price, category in products:
        product = env["product.product"].search([("name", "=", name)], limit=1)
        vals = {
            "name": name,
            "type": "consu",
            "available_in_pos": True,
            "list_price": price,
        }
        if category:
            vals["pos_categ_ids"] = [Command.set([category.id])]
        if product:
            product.write(vals)
        else:
            env["product.product"].create(vals)
            product = env["product.product"].search([("name", "=", name)], limit=1)
        ready_products.append(product.id)
    return env["product.product"].browse(ready_products)


def _ensure_pos_config(env, company, floors, payments_and_journal):
    payments, sale_journal = payments_and_journal
    config = env["pos.config"].search([("name", "=", "Restaurante Augusto")], limit=1)
    vals = {
        "name": "Restaurante Augusto",
        "company_id": company.id,
        "journal_id": sale_journal.id,
        "payment_method_ids": [Command.set(payments.ids)],
        "module_pos_restaurant": True,
        "iface_splitbill": True,
        "floor_ids": [Command.set(floors.ids)],
    }
    if config:
        config.write(vals)
    else:
        config = env["pos.config"].create(vals)
    return config
