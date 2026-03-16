from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    is_bono = fields.Boolean(related="product_tmpl_id.is_bono", store=True, readonly=True)
    n_uses = fields.Integer(related="product_tmpl_id.n_uses", store=True, readonly=True)

    @api.model
    def _load_pos_data_fields(self, config_id):
        fields_list = super()._load_pos_data_fields(config_id)
        for field_name in ["is_bono", "n_uses"]:
            if field_name not in fields_list:
                fields_list.append(field_name)
        return fields_list

