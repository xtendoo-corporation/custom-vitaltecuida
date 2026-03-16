from odoo import Command, _, api, fields, models
from odoo.exceptions import ValidationError


class VitaltecuidaBonoCreateWizard(models.TransientModel):
    _name = "vitaltecuida.bono.create.wizard"
    _description = "Wizard para crear bonos"

    source_product_tmpl_id = fields.Many2one("product.template", string="Producto origen")
    company_id = fields.Many2one(
        "res.company",
        string="Compañía",
        default=lambda self: self.env.company,
        required=True,
    )
    currency_id = fields.Many2one(related="company_id.currency_id")
    name = fields.Char(string="Nombre del bono", required=True)
    list_price = fields.Monetary(string="Precio del bono", required=True)
    n_uses = fields.Integer(string="Número de usos", required=True, default=1)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        source = self.env["product.template"].browse(self.env.context.get("default_source_product_tmpl_id"))
        if source:
            res.setdefault("source_product_tmpl_id", source.id)
            res.setdefault("name", _("%s - Bono") % source.name)
            res.setdefault("list_price", source.list_price)
        return res

    @api.constrains("n_uses", "list_price")
    def _check_values(self):
        for wizard in self:
            if wizard.n_uses <= 0:
                raise ValidationError(_("El número de usos debe ser mayor que 0."))
            if wizard.list_price < 0:
                raise ValidationError(_("El precio del bono no puede ser negativo."))

    def action_create_bono(self):
        self.ensure_one()
        source = self.source_product_tmpl_id
        product_vals = {
            "name": self.name,
            "type": "service",
            "sale_ok": True,
            "purchase_ok": False,
            "available_in_pos": True,
            "list_price": self.list_price,
            "is_bono": True,
            "n_uses": self.n_uses,
            "company_id": source.company_id.id if source and source.company_id else False,
            "categ_id": source.categ_id.id if source else False,
            "taxes_id": [Command.set(source.taxes_id.ids)] if source else False,
            "pos_categ_ids": [Command.set(source.pos_categ_ids.ids)] if source else False,
            "description_sale": source.description_sale if source else False,
        }
        bono = self.env["product.template"].create(product_vals)
        return {
            "type": "ir.actions.act_window",
            "name": _("Bono creado"),
            "res_model": "product.template",
            "res_id": bono.id,
            "view_mode": "form",
            "target": "current",
        }

