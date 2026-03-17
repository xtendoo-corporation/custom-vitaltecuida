from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    is_bono = fields.Boolean(related="product_tmpl_id.is_bono", store=True, readonly=False)
    n_uses = fields.Integer(related="product_tmpl_id.n_uses", store=True, readonly=False)

    @api.onchange("is_bono")
    def _onchange_is_bono_force_service_type(self):
        for product in self:
            if product.is_bono:
                product.type = "service"

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = [dict(vals) for vals in vals_list]
        for vals in vals_list:
            if vals.get("is_bono"):
                vals["type"] = "service"
        return super().create(vals_list)

    def write(self, vals):
        vals = dict(vals)
        if vals.get("is_bono"):
            vals["type"] = "service"
        return super().write(vals)

    @api.model
    def _load_pos_data_fields(self, config_id):
        fields_list = super()._load_pos_data_fields(config_id)
        for field_name in ["is_bono", "n_uses"]:
            if field_name not in fields_list:
                fields_list.append(field_name)
        return fields_list
