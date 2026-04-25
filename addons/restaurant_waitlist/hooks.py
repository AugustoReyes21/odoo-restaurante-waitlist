import base64
from io import BytesIO

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
        if not payment:
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
    if not customer_account:
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
    main_floor.write(
        {
            "background_color": "rgb(237,230,219)",
            "floor_background_image": _build_main_floor_background(),
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
    patio.write(
        {
            "background_color": "rgb(222,236,225)",
            "floor_background_image": _build_patio_background(),
        }
    )

    tables = [
        (main_floor, "1", 4, 340, 55, 75, 75, "square", "rgb(53,211,116)"),
        (main_floor, "2", 4, 485, 55, 75, 75, "square", "rgb(53,211,116)"),
        (main_floor, "3", 6, 635, 55, 135, 80, "square", "rgb(53,211,116)"),
        (main_floor, "4", 4, 340, 190, 75, 75, "square", "rgb(53,211,116)"),
        (main_floor, "5", 4, 485, 190, 75, 75, "square", "rgb(53,211,116)"),
        (main_floor, "6", 6, 635, 305, 135, 80, "square", "rgb(53,211,116)"),
        (main_floor, "7", 4, 340, 395, 75, 75, "square", "rgb(235,109,109)"),
        (main_floor, "8", 4, 485, 395, 75, 75, "square", "rgb(235,109,109)"),
        (main_floor, "9", 6, 100, 520, 135, 80, "square", "rgb(235,109,109)"),
        (main_floor, "10", 4, 340, 525, 75, 75, "square", "rgb(235,109,109)"),
        (main_floor, "11", 4, 485, 525, 75, 75, "square", "rgb(172,109,173)"),
        (main_floor, "12", 6, 635, 525, 135, 80, "square", "rgb(172,109,173)"),
        (patio, "21", 4, 115, 95, 82, 82, "round", "rgb(53,211,116)"),
        (patio, "22", 4, 300, 95, 82, 82, "round", "rgb(53,211,116)"),
        (patio, "23", 6, 490, 95, 135, 82, "square", "rgb(53,211,116)"),
        (patio, "24", 4, 115, 300, 82, 82, "round", "rgb(235,109,109)"),
        (patio, "25", 4, 300, 300, 82, 82, "round", "rgb(235,109,109)"),
        (patio, "26", 6, 490, 300, 135, 82, "square", "rgb(172,109,173)"),
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


def _build_main_floor_background():
    from PIL import Image, ImageDraw

    width, height = 855, 650
    image = Image.new("RGB", (width, height), "#b39b82")
    draw = ImageDraw.Draw(image)

    for x in range(width):
        shade = 150 + (x % 26)
        draw.line((x, 0, x, height), fill=(shade, 132 + (x % 14), 108))
    for x in range(280, width, 52):
        draw.line((x, 0, x, height), fill=(132, 113, 92), width=1)

    draw.rectangle((0, 0, 278, 280), fill="#aeb8bd", outline="#233746", width=8)
    draw.rectangle((70, 42, 225, 170), fill="#90999d", outline="#2d3a43", width=2)
    draw.ellipse((148, 57, 168, 77), fill="#ffffff", outline="#808080")
    draw.ellipse((165, 112, 185, 132), fill="#ffffff", outline="#808080")
    for row in range(4):
        for col in range(3):
            cx = 28 + col * 36
            cy = 55 + row * 36
            draw.ellipse((cx, cy, cx + 16, cy + 16), fill="#b7c0c5", outline="#6d777d")
    draw.rectangle((18, 0, 70, 35), fill="#c6d0d5", outline="#6d777d")
    draw.text((38, 8), "#", fill="#44515a")
    draw.rectangle((75, 220, 120, 255), fill="#cfd2d2", outline="#6d777d", width=2)
    draw.rectangle((125, 220, 170, 255), fill="#cfd2d2", outline="#6d777d", width=2)
    draw.ellipse((95, 230, 115, 250), fill="#ffffff", outline="#808080")
    draw.ellipse((137, 230, 157, 250), fill="#ffffff", outline="#808080")
    draw.rectangle((118, 300, 160, 380), fill="#d9c0a8", outline="#75655b", width=2)
    draw.rectangle((176, 300, 214, 370), fill="#f1b29b", outline="#75655b", width=2)
    draw.line((278, 0, 278, 650), fill="#233746", width=10)

    table_specs = [
        (340, 55, 75, 75, 4),
        (485, 55, 75, 75, 4),
        (635, 55, 135, 80, 6),
        (340, 190, 75, 75, 4),
        (485, 190, 75, 75, 4),
        (635, 305, 135, 80, 6),
        (340, 395, 75, 75, 4),
        (485, 395, 75, 75, 4),
        (100, 520, 135, 80, 6),
        (340, 525, 75, 75, 4),
        (485, 525, 75, 75, 4),
        (635, 525, 135, 80, 6),
    ]
    for x, y, table_width, table_height, seats in table_specs:
        _draw_chairs(draw, x, y, table_width, table_height, seats)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue())


def _build_patio_background():
    from PIL import Image, ImageDraw

    width, height = 720, 500
    image = Image.new("RGB", (width, height), "#d9e8d4")
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, width, height), fill="#d9e8d4")
    for x in range(0, width, 42):
        draw.line((x, 0, x + 110, height), fill="#c9dcc1", width=6)
    for y in range(0, height, 54):
        draw.line((0, y, width, y + 22), fill="#e7d4ad", width=3)

    draw.rectangle((0, 0, 720, 55), fill="#7d9d77")
    draw.rectangle((0, 445, 720, 500), fill="#7d9d77")
    for x in range(25, 700, 70):
        draw.ellipse((x, 12, x + 35, 47), fill="#5d8f54", outline="#3f6c38")
        draw.ellipse((x + 15, 455, x + 50, 490), fill="#5d8f54", outline="#3f6c38")

    draw.rectangle((35, 80, 660, 420), outline="#9a8363", width=5)
    draw.rectangle((45, 90, 650, 410), outline="#f2ead8", width=2)
    draw.rectangle((625, 200, 690, 295), fill="#c3b08f", outline="#8a7559", width=3)
    draw.text((640, 235), "BAR", fill="#5b4633")

    table_specs = [
        (115, 95, 82, 82, 4),
        (300, 95, 82, 82, 4),
        (490, 95, 135, 82, 6),
        (115, 300, 82, 82, 4),
        (300, 300, 82, 82, 4),
        (490, 300, 135, 82, 6),
    ]
    for x, y, table_width, table_height, seats in table_specs:
        _draw_chairs(draw, x, y, table_width, table_height, seats)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue())


def _draw_chairs(draw, x, y, width, height, seats):
    chair_fill = "#687fc8"
    chair_outline = "#435a9a"
    if seats >= 6:
        chair_positions = [
            (x + 22, y - 18, x + 58, y + 6),
            (x + width - 58, y - 18, x + width - 22, y + 6),
            (x + 22, y + height - 6, x + 58, y + height + 18),
            (x + width - 58, y + height - 6, x + width - 22, y + height + 18),
            (x - 18, y + 22, x + 6, y + height - 22),
            (x + width - 6, y + 22, x + width + 18, y + height - 22),
        ]
    else:
        chair_positions = [
            (x + 18, y - 18, x + width - 18, y + 6),
            (x + 18, y + height - 6, x + width - 18, y + height + 18),
            (x - 18, y + 18, x + 6, y + height - 18),
            (x + width - 6, y + 18, x + width + 18, y + height - 18),
        ]
    for box in chair_positions:
        draw.rounded_rectangle(box, radius=7, fill=chair_fill, outline=chair_outline, width=2)


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
