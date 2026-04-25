from odoo import _, api, fields, models
from odoo.exceptions import UserError


class RestaurantWaitlist(models.Model):
    _name = "restaurant.waitlist"
    _description = "Restaurant Waitlist Entry"
    _order = "priority desc, check_in_datetime asc, id asc"

    name = fields.Char(
        string="Reference",
        required=True,
        readonly=True,
        copy=False,
        default=lambda self: _("New"),
    )
    customer_id = fields.Many2one("res.partner", string="Customer")
    customer_name = fields.Char(string="Customer Name", required=True)
    phone = fields.Char(string="Phone")
    party_size = fields.Integer(string="Party Size", required=True, default=2)
    check_in_datetime = fields.Datetime(
        string="Check-in Time",
        required=True,
        default=fields.Datetime.now,
    )
    estimated_wait_minutes = fields.Integer(string="Estimated Wait (minutes)", default=15)
    priority = fields.Selection(
        [
            ("normal", "Normal"),
            ("high", "High"),
        ],
        string="Priority",
        default="normal",
        required=True,
    )
    pos_config_id = fields.Many2one("pos.config", string="Restaurant")
    table_id = fields.Many2one("restaurant.table", string="Assigned Table")
    notes = fields.Text(string="Notes")
    state = fields.Selection(
        [
            ("waiting", "Waiting"),
            ("notified", "Notified"),
            ("seated", "Seated"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="waiting",
        required=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code("restaurant.waitlist") or _("New")
            if vals.get("customer_id") and not vals.get("customer_name"):
                vals["customer_name"] = self.env["res.partner"].browse(vals["customer_id"]).name
        return super().create(vals_list)

    @api.onchange("customer_id")
    def _onchange_customer_id(self):
        for entry in self:
            if entry.customer_id:
                entry.customer_name = entry.customer_id.name
                entry.phone = entry.customer_id.phone or entry.customer_id.mobile

    def action_notify(self):
        self.write({"state": "notified"})

    def action_seat(self):
        for entry in self:
            if not entry.table_id:
                raise UserError(_("Assign a restaurant table before seating the customer."))
        self.write({"state": "seated"})

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def action_reset_waiting(self):
        self.write({"state": "waiting"})
