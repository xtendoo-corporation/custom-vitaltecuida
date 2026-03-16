from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    is_bono_redemption = fields.Boolean(string="Consumo de bono", default=False)
    bono_balance_id = fields.Many2one(
        "vitaltecuida.bono.balance",
        string="Saldo de bono",
        ondelete="restrict",
    )

    @api.constrains("is_bono_redemption", "qty")
    def _check_bono_redemption_qty(self):
        for line in self:
            if line.is_bono_redemption and not float(line.qty).is_integer():
                raise ValidationError(_("Los consumos de bono deben usar cantidades enteras."))

    @api.model
    def _load_pos_data_fields(self, config_id):
        fields_list = super()._load_pos_data_fields(config_id)
        for field_name in ["is_bono_redemption", "bono_balance_id"]:
            if field_name not in fields_list:
                fields_list.append(field_name)
        return fields_list

    def _get_bono_unit_count(self):
        self.ensure_one()
        return abs(int(self.qty or 0)) or 1

    def _get_bono_sale_use_count(self):
        self.ensure_one()
        return self._get_bono_unit_count() * self.product_id.n_uses

    def _get_or_create_balance_for_sale(self):
        self.ensure_one()
        return self.env["vitaltecuida.bono.balance"].get_or_create_balance(
            self.order_id.partner_id,
            self.product_id,
            self.order_id.company_id,
        )

    def _grant_bono_uses(self):
        self.ensure_one()
        balance = self._get_or_create_balance_for_sale()
        return balance.add_uses(
            self._get_bono_sale_use_count(),
            move_type="purchase",
            description=_("Compra de bono en TPV"),
            order=self.order_id,
            order_line=self,
        )

    def _remove_granted_bono_uses(self):
        self.ensure_one()
        balance = self._get_or_create_balance_for_sale()
        return balance.remove_purchased_uses(
            self._get_bono_sale_use_count(),
            description=_("Devolución de compra de bono en TPV"),
            order=self.order_id,
            order_line=self,
        )

    def _resolve_missing_bono_balance(self):
        self.ensure_one()
        if self.bono_balance_id or not self.is_bono_redemption or not self.product_id:
            return self.bono_balance_id

        partner = self.order_id.partner_id
        company = self.order_id.company_id or self.env.company
        if not partner:
            return self.bono_balance_id

        balance = self.env["vitaltecuida.bono.balance"].search(
            [
                ("partner_id", "=", partner.id),
                ("product_id", "=", self.product_id.id),
                ("company_id", "=", company.id),
            ],
            limit=1,
        )
        if balance:
            self.bono_balance_id = balance
        return self.bono_balance_id

    def _consume_bono_uses(self):
        self.ensure_one()
        self._resolve_missing_bono_balance()
        if not self.bono_balance_id:
            raise UserError(_("No se ha indicado el saldo del bono a consumir."))
        return self.bono_balance_id.consume_uses(
            self._get_bono_unit_count(),
            description=_("Consumo de bono en TPV"),
            order=self.order_id,
            order_line=self,
        )

    def _restore_bono_uses(self):
        self.ensure_one()
        self._resolve_missing_bono_balance()
        if not self.bono_balance_id:
            raise UserError(_("No se ha indicado el saldo del bono a restaurar."))
        return self.bono_balance_id.restore_consumed_uses(
            self._get_bono_unit_count(),
            description=_("Devolución de consumo de bono en TPV"),
            order=self.order_id,
            order_line=self,
        )

