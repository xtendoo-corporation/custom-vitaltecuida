/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { OrderSummary } from "@point_of_sale/app/screens/product_screen/order_summary/order_summary";
import { patch } from "@web/core/utils/patch";
import { VitaltecuidaManageGiftCardPopup } from "@vitaltecuida_custom/js/manage_giftcard_popup";

patch(OrderSummary.prototype, {
    /**
     * Busca el siguiente código de tarjeta regalo disponible
     * Formato: 000000001, 000000002, etc.
     * Verifica en la base de datos cuáles ya existen
     */
    async _getNextAvailableGiftCardCode() {
        let nextCode = 1;
        let found = false;

        while (!found) {
            const codeStr = String(nextCode).padStart(9, '0');

            // Buscar si existe una tarjeta con este código en la base de datos
            const existingCards = await this.pos.data.searchRead(
                "loyalty.card",
                [["code", "=", codeStr]],
                ["id"]
            );

            // También verificar en los cambios pendientes del pedido actual
            const pendingInOrder = this.currentOrder.duplicateCouponChanges
                ? this.currentOrder.duplicateCouponChanges(codeStr)
                : false;

            if (existingCards.length === 0 && !pendingInOrder) {
                found = true;
            } else {
                nextCode++;
            }

            // Límite de seguridad para evitar bucle infinito
            if (nextCode > 999999999) {
                console.error("Se alcanzó el límite máximo de códigos de tarjeta regalo");
                break;
            }
        }

        return String(nextCode).padStart(9, '0');
    },

    /**
     * Override manageGiftCard para usar el popup personalizado de Vitaltecuida
     * que incluye el precio del producto seleccionado (tarjeta regalo)
     */
    async manageGiftCard() {
        const selectedLine = this.currentOrder.get_selected_orderline();
        let defaultPrice = 0;

        // Obtener el precio del producto seleccionado (la tarjeta regalo)
        // Primero intentamos con el precio unitario de la línea (price_unit)
        // Si no está disponible, usamos el precio de lista del producto (lst_price)
        if (selectedLine) {
            if (selectedLine.price_unit && selectedLine.price_unit > 0) {
                defaultPrice = selectedLine.price_unit;
            } else if (selectedLine.get_unit_price && typeof selectedLine.get_unit_price === 'function') {
                defaultPrice = selectedLine.get_unit_price();
            } else if (selectedLine.product_id && selectedLine.product_id.lst_price) {
                defaultPrice = selectedLine.product_id.lst_price;
            }
        }

        // Obtener el siguiente código disponible de la base de datos
        const nextCode = await this._getNextAvailableGiftCardCode();

        this.dialog.add(VitaltecuidaManageGiftCardPopup, {
            title: _t("Vender/Gestionar tarjeta regalo física"),
            placeholder: _t("Introducir Número de Tarjeta Regalo"),
            defaultPrice: defaultPrice,
            defaultCode: nextCode,
            getPayload: async (code, points, expirationDate) => {
                points = parseFloat(points);
                if (isNaN(points)) {
                    console.error("Valor de importe inválido:", points);
                    return;
                }
                code = code.trim();
                const res = await this.pos.data.searchRead(
                    "loyalty.card",
                    ["&", ["program_type", "=", "gift_card"], ["code", "=", code]],
                    []
                );
                if (res.length > 0) {
                    this.notification.add(_t("Esta tarjeta regalo ya ha sido vendida."), {
                        type: "danger",
                    });
                    return;
                }

                // check for duplicate code
                if (this.currentOrder.duplicateCouponChanges(code)) {
                    const { ConfirmationDialog } = await import("@web/core/confirmation_dialog/confirmation_dialog");
                    this.dialog.add(ConfirmationDialog, {
                        title: _t("Error de Validación"),
                        body: _t("Un cupón/tarjeta de fidelidad debe tener un código único."),
                    });
                    return;
                }

                await this._updateGiftCardOrderline(code, points);
                this.currentOrder.processGiftCard(code, points, expirationDate);

                // update indexedDB
                this.pos.data.syncDataWithIndexedDB(this.pos.data.records);
            },
        });
    },
});

