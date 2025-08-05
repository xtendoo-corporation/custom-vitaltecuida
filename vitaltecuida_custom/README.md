# Vitaltecuida Custom - Monedero Electrónico

## Descripción

Este módulo automáticamente establece la fecha de expiración de los monederos electrónicos (loyalty cards) a 1 año después de su creación y envía notificaciones por WhatsApp 15 días antes de la expiración usando el sistema nativo de WhatsApp de Odoo. Además, envía felicitaciones de cumpleaños automáticas con tarjetas regalo de 10€.

## Funcionalidades

### 🔧 Gestión Automática de Expiración
- **Fecha de expiración automática**: Cuando se crea un nuevo monedero electrónico, automáticamente se establece la fecha de expiración a 365 días (1 año) desde la fecha de creación.
- **Valores por defecto**: Establece la fecha de expiración como valor por defecto en formularios.
- **No sobrescribe**: Si ya se proporciona una fecha de expiración manualmente, respeta ese valor.

### 📱 Notificaciones por WhatsApp
- **Alertas automáticas**: Envía notificaciones por WhatsApp 15 días antes de la expiración del monedero.
- **Integración nativa**: Usa el sistema de WhatsApp existente en Odoo sin crear modelos personalizados.
- **Plantilla predefinida**: Mensaje profesional con formato optimizado para WhatsApp.
- **Ejecución diaria**: Cron job que verifica diariamente los monederos próximos a expirar.
- **Respaldo de actividades**: Crea actividades en Odoo como respaldo de las notificaciones enviadas.

### 🎉 Sistema de Cumpleaños con Tarjetas Regalo
- **Felicitaciones automáticas**: Envía mensajes de WhatsApp de felicitación el día del cumpleaños.
- **Tarjetas regalo automáticas**: Crea automáticamente tarjetas regalo de 10€ en el cumpleaños.
- **Programa de lealtad dedicado**: Crea automáticamente un programa específico para tarjetas regalo de cumpleaños.
- **Validez de 1 año**: Las tarjetas regalo de cumpleaños expiran en 1 año.
- **Registro completo**: Crea actividades de seguimiento para cada tarjeta regalo creada.

## Plantillas de WhatsApp Incluidas

### 1. Notificación de Expiración de Monedero
```
🔔 *Vitaltecuida - Aviso Importante*

Hola {nombre_cliente},

Tu monedero electrónico está próximo a vencer.

⏰ *Días restantes:* 15 días
📅 *Fecha de expiración:* {fecha_expiracion}

💡 *¿Qué puedes hacer?*
• Usa tu saldo antes de la fecha de vencimiento
• Contacta con nosotros para renovar tu monedero
• Visita nuestros centros Vitaltecuida

📞 *¿Necesitas ayuda?*
Contáctanos al WhatsApp o visita www.vitaltecuida.com

¡Gracias por confiar en Vitaltecuida! 💚
```

### 2. Felicitación de Cumpleaños con Tarjeta Regalo
```
🎉 *¡Feliz Cumpleaños {nombre_cliente}!* 🎂

Desde Vitaltecuida queremos acompañarte en este día tan especial.

🎁 *¡Tenemos una sorpresa para ti!*
Como regalo de cumpleaños, hemos añadido a tu monedero electrónico una
*tarjeta regalo de 10€* para que disfrutes de nuestros servicios.

💳 *Tu regalo ya está disponible en tu cuenta*
Puedes usar tu tarjeta regalo de inmediato en cualquiera de nuestros
centros o servicios online.

🌟 *Celebra tu día especial con nosotros:*
• Tratamientos de bienestar
• Productos de belleza y salud
• Servicios personalizados
• Y mucho más...

📍 *Visítanos o agenda tu cita:*
🌐 www.vitaltecuida.com
📞 Contáctanos por WhatsApp

¡Que tengas un cumpleaños increíble! 💚✨

_*Vitaltecuida - Cuidamos de ti*_
```

## Instalación

1. El módulo se encuentra en la ruta: `custom-vitaltecuida/vitaltecuida_custom/`
2. Asegúrate de que los módulos `loyalty` y `mail` estén instalados (dependencias)
3. Para usar WhatsApp, asegúrate de tener configurado el módulo de WhatsApp de Odoo
4. Actualiza la lista de aplicaciones en Odoo
5. Instala el módulo "Vitaltecuida Custom - Monedero Electrónico"

## Configuración

### Sistema de WhatsApp
El módulo se integra automáticamente con el sistema de WhatsApp existente en Odoo. Crea dos plantillas:
- **Plantilla de expiración**: Tipo "utility" para notificaciones importantes
- **Plantilla de cumpleaños**: Tipo "marketing" para felicitaciones promocionales

### Fechas de Cumpleaños
Para que funcione el sistema de cumpleaños:
1. Asegúrate de que los contactos tengan el campo `birthdate` completado
2. Verifica que tengan número de móvil en el campo `mobile`
3. Solo funcionará con contactos marcados como personas (no empresas)

## Uso

Una vez instalado, el módulo funcionará automáticamente:

### Monederos Electrónicos
- **Monederos nuevos**: Se creará automáticamente con fecha de expiración a 1 año
- **Notificaciones**: El sistema verificará diariamente y enviará WhatsApp 15 días antes de la expiración

### Cumpleaños
- **Verificación diaria**: El sistema verifica cada día si hay cumpleaños
- **Creación automática**: Crea tarjetas regalo de 10€ automáticamente
- **Felicitación WhatsApp**: Envía mensaje personalizado de felicitación
- **Programa dedicado**: Crea el programa "Tarjetas Regalo Cumpleaños Vitaltecuida" si no existe

## Estructura de Archivos

```
vitaltecuida_custom/
├── models/
│   └── loyalty_card.py                 # Lógica principal del módulo
├── data/
│   ├── whatsapp_template_data.xml      # Plantillas de WhatsApp
│   └── cron_data.xml                   # Configuración de cron jobs
└── README.md                           # Documentación
```

## Cron Jobs Configurados

1. **Notificaciones de Expiración**: Ejecuta diariamente a las 00:00
2. **Felicitaciones de Cumpleaños**: Ejecuta diariamente a las 00:00

## Compatibilidad

- Odoo 18.0
- Módulos `loyalty` y `mail` (core de Odoo)
- Compatible con el módulo de WhatsApp nativo de Odoo

## Ventajas de esta Implementación

✅ **Automatización completa**: Todo funciona sin intervención manual

✅ **Doble funcionalidad**: Gestiona tanto expiración como cumpleaños

✅ **Integración nativa**: Usa modelos estándar de Odoo sin conflictos

✅ **Registro completo**: Todas las acciones se registran como actividades

✅ **Escalable**: Fácil de extender con nuevas funcionalidades

## Autor

Vitaltecuida
