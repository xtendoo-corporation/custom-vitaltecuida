from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_bono = fields.Boolean(string="Bono", copy=False)
    n_uses = fields.Integer(string="Número de usos", default=1)
    bono_balance_count = fields.Integer(
        string="Clientes con bono",
        compute="_compute_bono_balance_count",
    )

    @staticmethod
    def _force_service_type_on_vals(vals):
        if vals.get("is_bono"):
            vals["type"] = "service"
        return vals

    @api.onchange("is_bono")
    def _onchange_is_bono_force_service_type(self):
        for product in self:
            if product.is_bono:
                product.type = "service"

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = [self._force_service_type_on_vals(dict(vals)) for vals in vals_list]
        return super().create(vals_list)

    def write(self, vals):
        vals = self._force_service_type_on_vals(dict(vals))
        return super().write(vals)

    @api.depends("product_variant_ids")
    def _compute_bono_balance_count(self):
        balance_model = self.env["vitaltecuida.bono.balance"]
        for product in self:
            product.bono_balance_count = balance_model.search_count([
                ("product_id", "in", product.product_variant_ids.ids),
                ("remaining_uses", ">", 0),
            ])

    @api.constrains("is_bono", "n_uses")
    def _check_bono_uses(self):
        for product in self:
            if product.is_bono and product.n_uses <= 0:
                raise ValidationError(_("El número de usos del bono debe ser mayor que 0."))

    def action_view_bono_balances(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "vitaltecuida_bonos.action_vitaltecuida_bono_balance"
        )
        action["domain"] = [("product_id", "in", self.product_variant_ids.ids)]
        action["context"] = {
            "default_product_id": self.product_variant_id.id,
            "search_default_available": 1,
        }
        return action
