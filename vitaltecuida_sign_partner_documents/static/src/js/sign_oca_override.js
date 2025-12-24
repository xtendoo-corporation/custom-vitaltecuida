odoo.define('vitaltecuida_sign_partner_documents.sign_oca_override', function (require) {
    "use strict";
    // Oculta mensajes de agradecimiento/email si la URL contiene el parámetro especial
    function hideThanksMessages(context) {
        let ocultados = 0;
        let $context = context ? $(context) : $("body");
        $context.find('*').filter(function() {
            if (/Thanks for signing|correo electrónico|bandeja de entrada|Debería haber recibido un correo|Please check your inbox|documento final/i.test($(this).text())) {
                ocultados++;
                return true;
            }
            return false;
        }).hide();
        let clases = $context.find(".o_sign_oca_thanks, .o_sign_oca_final_message, .o_sign_oca_final_email").length;
        $context.find(".o_sign_oca_thanks, .o_sign_oca_final_message, .o_sign_oca_final_email").hide();
        if (ocultados > 0 || clases > 0) {
            console.log('[sign_oca_override] Ocultados', ocultados, 'elementos por texto y', clases, 'por clase en', context ? 'iframe' : 'documento principal');
        }
    }
    function applyToIframes() {
        $("iframe").each(function() {
            try {
                let doc = this.contentDocument || this.contentWindow.document;
                if (doc && doc.readyState === "complete") {
                    hideThanksMessages(doc.body);
                    let observer = new MutationObserver(function() {
                        hideThanksMessages(doc.body);
                    });
                    observer.observe(doc.body, { childList: true, subtree: true });
                } else {
                    $(this).on('load', function() {
                        let doc = this.contentDocument || this.contentWindow.document;
                        hideThanksMessages(doc.body);
                        let observer = new MutationObserver(function() {
                            hideThanksMessages(doc.body);
                        });
                        observer.observe(doc.body, { childList: true, subtree: true });
                    });
                }
            } catch (e) {
                // Puede fallar por cross-origin, ignorar
            }
        });
    }
    $(document).ready(function () {
        var urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('no_email_thanks') === '1') {
            console.log('[sign_oca_override] Activado modo sin mensaje de email.');
            hideThanksMessages();
            var observer = new MutationObserver(function() {
                hideThanksMessages();
                applyToIframes();
            });
            observer.observe(document.body, { childList: true, subtree: true });
            applyToIframes();
        }
    });
});
