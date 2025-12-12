# VitalTeCuida Citas - Wizard de Creación de Citas

## Descripción

Este módulo ha sido mejorado para incluir un wizard personalizado para la creación de citas desde la vista de calendario de recursos.

## Características Implementadas

### 1. Wizard de Creación de Citas (`calendar.event.wizard`)

El wizard permite crear citas de manera estructurada con los siguientes campos:

- **Cliente** (partner_id): Campo obligatorio para seleccionar el cliente de la cita
- **Tipo de Cita** (appointment_type_id): Selección del tipo de cita (opcional)
- **Nombre de la Cita**: Descripción breve de la cita (obligatorio)
- **Fecha y Hora Inicio**: Fecha y hora de inicio de la cita (obligatorio)
- **Duración**: Duración en horas (por defecto 1 hora)
- **Fecha y Hora Fin**: Calculada automáticamente según duración
- **Recursos Asignados**: Uno o más recursos a asignar (obligatorio)
- **Descripción**: Campo HTML para notas adicionales

### 2. Funcionalidades Automáticas

- **Cálculo automático de fecha fin**: Se calcula automáticamente basándose en la fecha de inicio y la duración
- **Integración con tipos de cita**: Si el tipo de cita tiene duración configurada, se aplica automáticamente
- **Asignación de colores**: Los eventos creados heredan el color del primer recurso asignado
- **Contexto desde calendario**: Si se crea desde el calendario, la fecha seleccionada se pasa al wizard

### 3. Integración con Vista Calendario

- Al hacer clic en el calendario en la vista "Resource Calendar", se abre el wizard personalizado
- El wizard captura la fecha/hora del slot seleccionado
- Después de crear, se muestra el evento creado en formulario estándar

### 4. Accesos

- Menú "Nueva Cita (Wizard)" disponible en el módulo de Citas
- Accesible desde "Appointment > Resource Calendar > Nueva Cita (Wizard)"

## Archivos Creados

1. **wizards/calendar_event_wizard.py**: Modelo del wizard
2. **wizards/__init__.py**: Inicialización del módulo wizards
3. **views/calendar_event_wizard_views.xml**: Vista formulario del wizard
4. **security/ir.model.access.csv**: Permisos de acceso
5. **static/src/js/calendar_controller.js**: JavaScript para interceptar creación desde calendario

## Archivos Modificados

1. **__init__.py**: Añadida importación de wizards
2. **__manifest__.py**: Añadidos archivos de datos y assets JavaScript
3. **models/calendar_event.py**: Campo appointment_type_id ya existía
4. **views/appointment_resource_calendar.xml**:
   - Mejorada vista calendario con más información
   - Añadida vista heredada del formulario de eventos
   - Añadido menú para acceso al wizard
   - Añadido contexto para JavaScript

## Uso

### Desde el Calendario:
1. Ir a "Appointment > Resource Calendar"
2. Hacer clic en un slot del calendario
3. Se abrirá el wizard automáticamente con la fecha pre-seleccionada
4. Rellenar los campos y hacer clic en "Crear"

### Desde el Menú:
1. Ir a "Appointment > Nueva Cita (Wizard)"
2. Rellenar todos los campos necesarios
3. Hacer clic en "Crear"

## Actualización del Módulo

Para aplicar los cambios:

```bash
# Actualizar el módulo
odoo-bin -u vitaltecuida_citas -d nombre_base_datos

# O desde la interfaz de Odoo:
# Apps > VitalTeCuida Citas > Actualizar
```

## Notas Técnicas

- El wizard es un modelo transitorio (`TransientModel`)
- La creación del evento se hace mediante el método `action_create_event`
- Los recursos se asignan mediante relación many2many
- El color del evento se calcula automáticamente según el primer recurso asignado

