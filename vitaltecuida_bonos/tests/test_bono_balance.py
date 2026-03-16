from odoo.tests.common import TransactionCase


class TestVitaltecuidaBonoBalance(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "Cliente bono"})
        self.product_tmpl = self.env["product.template"].create({
            "name": "Bono prueba",
            "type": "service",
            "sale_ok": True,
            "available_in_pos": True,
            "is_bono": True,
            "n_uses": 5,
            "list_price": 50,
        })
        self.product = self.product_tmpl.product_variant_id
        self.balance_model = self.env["vitaltecuida.bono.balance"]

    def test_balance_accumulates_by_partner_and_product(self):
        balance = self.balance_model.get_or_create_balance(self.partner, self.product)
        balance.add_uses(5)
        same_balance = self.balance_model.get_or_create_balance(self.partner, self.product)
        same_balance.add_uses(5)

        self.assertEqual(balance.id, same_balance.id)
        self.assertEqual(balance.total_uses, 10)
        self.assertEqual(balance.remaining_uses, 10)

    def test_balance_consumption_and_restore(self):
        balance = self.balance_model.get_or_create_balance(self.partner, self.product)
        balance.add_uses(5)
        balance.consume_uses(2)
        self.assertEqual(balance.remaining_uses, 3)
        balance.restore_consumed_uses(1)
        self.assertEqual(balance.remaining_uses, 4)

    def test_get_pos_ui_data_includes_product_display_name(self):
        balance = self.balance_model.get_or_create_balance(self.partner, self.product)
        balance.add_uses(5)

        payload = self.balance_model.get_pos_ui_data([self.partner.id])

        self.assertEqual(payload["remove_ids"], [])
        self.assertEqual(len(payload["upsert"]), 1)
        self.assertEqual(payload["upsert"][0]["id"], balance.id)
        self.assertEqual(payload["upsert"][0]["product_id"], self.product.id)
        self.assertEqual(payload["upsert"][0]["product_display_name"], self.product.display_name)

    def test_redemption_line_recovers_missing_balance(self):
        balance = self.balance_model.get_or_create_balance(self.partner, self.product)
        balance.add_uses(5)

        order = self.env["pos.order"].new({})
        order.partner_id = self.partner
        order.company_id = self.env.company

        line = self.env["pos.order.line"].new({})
        line.order_id = order
        line.product_id = self.product
        line.qty = 1
        line.is_bono_redemption = True

        self.assertFalse(line.bono_balance_id)
        self.assertEqual(line._resolve_missing_bono_balance(), balance)
        self.assertEqual(line.bono_balance_id, balance)
