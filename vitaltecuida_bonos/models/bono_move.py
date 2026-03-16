from odoo import fields, models


class VitaltecuidaBonoMove(models.Model):
    _name = "vitaltecuida.bono.move"
    _description = "Movimiento de bono"
    _order = "create_date desc, id desc"

    balance_id = fields.Many2one("vitaltecuida.bono.balance", string="Saldo", required=True, ondelete="cascade")
    partner_id = fields.Many2one(related="balance_id.partner_id", store=True, readonly=True)
    product_id = fields.Many2one(related="balance_id.product_id", store=True, readonly=True)
    company_id = fields.Many2one("res.company", string="Compañía", required=True, ondelete="restrict")
    order_id = fields.Many2one("pos.order", string="Pedido TPV", ondelete="set null")
    order_line_id = fields.Many2one("pos.order.line", string="Línea TPV", ondelete="set null")
    move_type = fields.Selection(
        [
            ("purchase", "Compra"),
            ("consume", "Consumo"),
            ("refund_purchase", "Devolución de compra"),
            ("refund_consume", "Devolución de consumo"),
            ("adjust", "Ajuste"),
        ],
        string="Tipo",
        required=True,
    )
    quantity = fields.Integer(string="Cantidad", required=True)
    remaining_after = fields.Integer(string="Restantes después", required=True)
    description = fields.Char(string="Descripción")

