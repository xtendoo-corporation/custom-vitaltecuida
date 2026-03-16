from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class VitaltecuidaBonoBalance(models.Model):
    _name = "vitaltecuida.bono.balance"
    _description = "Saldo de bono por cliente"
    _inherit = ["pos.load.mixin"]
    _order = "partner_id, product_id, id desc"

    partner_id = fields.Many2one("res.partner", string="Cliente", required=True, ondelete="cascade")
    product_id = fields.Many2one(
        "product.product",
        string="Bono",
        required=True,
        ondelete="restrict",
        domain=[("is_bono", "=", True)],
    )
    product_display_name = fields.Char(string="Nombre del bono", related="product_id.display_name")
    company_id = fields.Many2one(
        "res.company",
        string="Compañía",
        required=True,
        default=lambda self: self.env.company,
        ondelete="restrict",
    )
    total_uses = fields.Integer(string="Usos totales", default=0)
    remaining_uses = fields.Integer(string="Usos restantes", default=0)
    move_ids = fields.One2many("vitaltecuida.bono.move", "balance_id", string="Movimientos")
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "partner_product_company_unique",
            "unique(partner_id, product_id, company_id)",
            "Ya existe un saldo para este cliente y este bono en la misma compañía.",
        )
    ]

    @api.constrains("total_uses", "remaining_uses")
    def _check_uses(self):
        for balance in self:
            if balance.total_uses < 0 or balance.remaining_uses < 0:
                raise ValidationError(_("Los usos del bono no pueden ser negativos."))
            if balance.remaining_uses > balance.total_uses:
                raise ValidationError(_("Los usos restantes no pueden superar a los usos totales."))

    @api.model
    def _load_pos_data_domain(self, data):
        partner_ids = [partner["id"] for partner in data.get("res.partner", {}).get("data", [])]
        product_ids = [product["id"] for product in data.get("product.product", {}).get("data", [])]
        return [
            ("partner_id", "in", partner_ids),
            ("product_id", "in", product_ids),
            ("company_id", "=", self.env.company.id),
            ("remaining_uses", ">", 0),
        ]

    @api.model
    def _load_pos_data_fields(self, config_id):
        return [
            "id",
            "partner_id",
            "product_id",
            "product_display_name",
            "total_uses",
            "remaining_uses",
            "write_date",
        ]

    @api.model
    def get_or_create_balance(self, partner, product, company=None):
        company = company or self.env.company
        balance = self.search([
            ("partner_id", "=", partner.id),
            ("product_id", "=", product.id),
            ("company_id", "=", company.id),
        ], limit=1)
        if not balance:
            balance = self.create({
                "partner_id": partner.id,
                "product_id": product.id,
                "company_id": company.id,
            })
        return balance

    @api.model
    def get_pos_ui_data(self, partner_ids=None):
        domain = [("company_id", "=", self.env.company.id)]
        if partner_ids:
            domain.append(("partner_id", "in", partner_ids))
        balances = self.search(domain)
        positive_balances = balances.filtered(lambda balance: balance.remaining_uses > 0)
        return {
            "upsert": positive_balances.read(self._load_pos_data_fields(False), load=False),
            "remove_ids": (balances - positive_balances).ids,
        }

    def _create_move(self, move_type, quantity, description=False, order=False, order_line=False):
        self.ensure_one()
        return self.env["vitaltecuida.bono.move"].create({
            "balance_id": self.id,
            "move_type": move_type,
            "quantity": quantity,
            "remaining_after": self.remaining_uses,
            "description": description or False,
            "order_id": getattr(order, "id", False),
            "order_line_id": getattr(order_line, "id", False),
            "company_id": self.company_id.id,
        })

    def add_uses(self, quantity, move_type="purchase", description=False, order=False, order_line=False):
        self.ensure_one()
        quantity = int(quantity)
        if quantity <= 0:
            raise ValidationError(_("La cantidad de usos a sumar debe ser positiva."))
        self.write({
            "total_uses": self.total_uses + quantity,
            "remaining_uses": self.remaining_uses + quantity,
        })
        return self._create_move(move_type, quantity, description, order, order_line)

    def consume_uses(self, quantity, description=False, order=False, order_line=False):
        self.ensure_one()
        quantity = int(quantity)
        if quantity <= 0:
            raise ValidationError(_("La cantidad de usos a consumir debe ser positiva."))
        if self.remaining_uses < quantity:
            raise ValidationError(
                _("El cliente %(partner)s no tiene usos suficientes para el bono %(product)s.")
                % {"partner": self.partner_id.display_name, "product": self.product_id.display_name}
            )
        self.write({"remaining_uses": self.remaining_uses - quantity})
        return self._create_move("consume", -quantity, description, order, order_line)

    def restore_consumed_uses(self, quantity, description=False, order=False, order_line=False):
        self.ensure_one()
        quantity = int(quantity)
        if quantity <= 0:
            raise ValidationError(_("La cantidad de usos a restaurar debe ser positiva."))
        self.write({"remaining_uses": self.remaining_uses + quantity})
        return self._create_move("refund_consume", quantity, description, order, order_line)

    def remove_purchased_uses(self, quantity, description=False, order=False, order_line=False):
        self.ensure_one()
        quantity = int(quantity)
        if quantity <= 0:
            raise ValidationError(_("La cantidad de usos a descontar debe ser positiva."))
        if self.remaining_uses < quantity:
            raise ValidationError(
                _(
                    "No se puede devolver la compra del bono %(product)s para %(partner)s porque ya se han consumido usos."
                )
                % {"partner": self.partner_id.display_name, "product": self.product_id.display_name}
            )
        self.write({
            "total_uses": self.total_uses - quantity,
            "remaining_uses": self.remaining_uses - quantity,
        })
        return self._create_move("refund_purchase", -quantity, description, order, order_line)
