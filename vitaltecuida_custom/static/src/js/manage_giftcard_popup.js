/** @odoo-module */

import { Component, onMounted, useRef, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { useService } from "@web/core/utils/hooks";
import { DateTimeInput } from "@web/core/datetime/datetime_input";
import { serializeDate } from "@web/core/l10n/dates";

export class VitaltecuidaManageGiftCardPopup extends Component {
    static template = "vitaltecuida_custom.ManageGiftCardPopup";
    static components = { Dialog, DateTimeInput };
    static props = {
        title: String,
        placeholder: { type: String, optional: true },
        rows: { type: Number, optional: true },
        getPayload: Function,
        close: Function,
        defaultPrice: { type: Number, optional: true },
        defaultCode: { type: String, optional: true },
    };
    static defaultProps = {
        startingValue: "",
        placeholder: "",
        rows: 1,
        defaultPrice: 0,
        defaultCode: "",
    };

    setup() {
        this.ui = useState(useService("ui"));

        this.state = useState({
            // Usar el código proporcionado por props o vacío
            inputValue: this.props.defaultCode || "",
            amountValue: this.props.defaultPrice > 0 ? String(this.props.defaultPrice) : "",
            error: false,
            amountError: false,
            // Fecha de expiración: 1 año desde hoy
            expirationDate: luxon.DateTime.now().plus({ year: 1 }),
        });
        this.inputRef = useRef("input");
        this.amountInputRef = useRef("amountInput");
        onMounted(this.onMounted);
    }

    onMounted() {
        // Removing the main "DateTimeInput" component's class "o_input" and
        // adding the CSS classes "form-control" and "form-control-lg" for styling the form input with Bootstrap.
        const expirationDateInput = document.querySelector(".o_exp_date_container");
        if (expirationDateInput && expirationDateInput.children[1]) {
            expirationDateInput.children[1].classList.remove("o_input");
            expirationDateInput.children[1].classList.add("form-control", "form-control-lg");
        }
        // Focus en el campo de cantidad si ya tenemos código pre-llenado
        if (this.state.inputValue && this.amountInputRef.el) {
            this.amountInputRef.el.focus();
        } else if (this.inputRef.el) {
            this.inputRef.el.focus();
        }
    }

    addBalance() {
        if (!this.validateCode()) {
            return;
        }

        this.props.getPayload(
            this.state.inputValue,
            parseFloat(this.state.amountValue),
            this.state.expirationDate ? serializeDate(this.state.expirationDate) : false
        );
        this.props.close();
    }

    close() {
        this.props.close();
    }

    validateCode() {
        const { inputValue, amountValue } = this.state;
        if (inputValue.trim() === "") {
            this.state.error = true;
            return false;
        }
        if (amountValue.trim() === "") {
            this.state.amountError = true;
            return false;
        }
        return true;
    }

    onExpDateChange(date) {
        this.state.expirationDate = date;
    }
}


