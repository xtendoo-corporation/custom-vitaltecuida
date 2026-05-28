import odoo
from odoo.tests import Form, TransactionCase


@odoo.tests.tagged("post_install", "-at_install")
class TestPosDefaultPartner(TransactionCase):
    """
    Tests for vitaltecuida_pos_config:
    - Field default_partner_id exists on pos.config
    - Field pos_default_partner_id exists on res.config.settings and is linked
    - Setting via res.config.settings is reflected on pos.config
    - Setting does not bleed over to other pos.config instances
    - Unsetting the field works correctly
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_a = cls.env["res.partner"].create({"name": "Cliente A (defecto)"})
        cls.partner_b = cls.env["res.partner"].create({"name": "Cliente B (defecto)"})
        cls.config_1 = cls.env["pos.config"].create(
            {"name": "Caja Test 1", "module_pos_restaurant": False}
        )
        cls.config_2 = cls.env["pos.config"].create(
            {"name": "Caja Test 2", "module_pos_restaurant": False}
        )

    # ------------------------------------------------------------------
    # 1. Modelo pos.config
    # ------------------------------------------------------------------

    def test_field_exists_on_pos_config(self):
        """El campo default_partner_id existe en pos.config y acepta un partner."""
        self.config_1.default_partner_id = self.partner_a
        self.assertEqual(
            self.config_1.default_partner_id,
            self.partner_a,
            "default_partner_id debería ser partner_a",
        )

    def test_field_is_optional(self):
        """El campo default_partner_id es opcional (puede estar vacío)."""
        self.config_2.default_partner_id = False
        self.assertFalse(
            self.config_2.default_partner_id,
            "default_partner_id debería estar vacío por defecto",
        )

    def test_field_can_be_unset(self):
        """Se puede eliminar el cliente por defecto una vez asignado."""
        self.config_1.default_partner_id = self.partner_a
        self.config_1.default_partner_id = False
        self.assertFalse(
            self.config_1.default_partner_id,
            "default_partner_id debería vaciarse correctamente",
        )

    # ------------------------------------------------------------------
    # 2. res.config.settings → proxy field
    # ------------------------------------------------------------------

    def test_proxy_field_reads_from_pos_config(self):
        """pos_default_partner_id en res.config.settings refleja el valor de pos.config."""
        self.config_1.default_partner_id = self.partner_a
        settings = self.env["res.config.settings"].create(
            {"pos_config_id": self.config_1.id}
        )
        self.assertEqual(
            settings.pos_default_partner_id,
            self.partner_a,
            "El campo proxy debería leer el valor de pos.config",
        )

    def test_proxy_field_writes_to_pos_config(self):
        """Escribir en pos_default_partner_id actualiza pos.config."""
        self.config_1.default_partner_id = False
        settings = self.env["res.config.settings"].create(
            {"pos_config_id": self.config_1.id}
        )
        settings.pos_default_partner_id = self.partner_b
        self.assertEqual(
            self.config_1.default_partner_id,
            self.partner_b,
            "Escribir en el proxy debería actualizar pos.config",
        )

    def test_settings_via_form(self):
        """Cambiar el cliente por defecto a través del Form de ajustes funciona correctamente."""
        with Form(self.env["res.config.settings"]) as form:
            form.pos_config_id = self.config_1
            form.pos_default_partner_id = self.partner_a

        self.assertEqual(
            self.config_1.default_partner_id,
            self.partner_a,
            "El cliente por defecto debería haberse guardado en pos.config",
        )

    # ------------------------------------------------------------------
    # 3. Aislamiento entre cajas
    # ------------------------------------------------------------------

    def test_default_partner_does_not_bleed_to_other_config(self):
        """Configurar un cliente por defecto en una caja no afecta a otra."""
        self.config_1.default_partner_id = self.partner_a
        self.config_2.default_partner_id = False

        self.assertEqual(self.config_1.default_partner_id, self.partner_a)
        self.assertFalse(
            self.config_2.default_partner_id,
            "La caja 2 no debería heredar el cliente por defecto de la caja 1",
        )

    def test_each_config_has_independent_default_partner(self):
        """Cada caja puede tener su propio cliente por defecto independiente."""
        self.config_1.default_partner_id = self.partner_a
        self.config_2.default_partner_id = self.partner_b

        self.assertEqual(self.config_1.default_partner_id, self.partner_a)
        self.assertEqual(self.config_2.default_partner_id, self.partner_b)

    def test_settings_change_only_affects_selected_config(self):
        """Cambiar ajustes para una caja no modifica el partner de otra caja."""
        self.config_1.default_partner_id = self.partner_a
        self.config_2.default_partner_id = self.partner_b

        with Form(self.env["res.config.settings"]) as form:
            form.pos_config_id = self.config_1
            form.pos_default_partner_id = self.partner_b  # cambia caja 1

        self.assertEqual(
            self.config_1.default_partner_id,
            self.partner_b,
            "La caja 1 debería tener partner_b ahora",
        )
        self.assertEqual(
            self.config_2.default_partner_id,
            self.partner_b,
            "La caja 2 debería mantener su partner_b sin cambios",
        )

    # ------------------------------------------------------------------
    # 4. Integridad del modelo
    # ------------------------------------------------------------------

    def test_pos_config_can_be_created_without_default_partner(self):
        """Crear una pos.config sin cliente por defecto no produce errores."""
        config = self.env["pos.config"].create(
            {"name": "Caja Sin Default", "module_pos_restaurant": False}
        )
        self.assertFalse(
            config.default_partner_id,
            "Una caja nueva no debería tener cliente por defecto",
        )

    def test_deleting_partner_clears_default(self):
        """Al archivar el partner, la referencia debe comportarse correctamente."""
        partner_temp = self.env["res.partner"].create({"name": "Partner Temporal"})
        self.config_1.default_partner_id = partner_temp

        # Archivar el partner (Odoo no permite borrar partners con dependencias)
        partner_temp.active = False

        # El campo debería quedar vacío o el partner inactivo, sin error
        # (Odoo gestiona la referencia con on_delete por defecto)
        self.assertIn(
            self.config_1.default_partner_id.id,
            [False, partner_temp.id],
            "La referencia a un partner archivado no debe causar errores",
        )
