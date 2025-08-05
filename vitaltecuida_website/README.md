# Vitaltecuida Website - Sistema de Reseñas

## Descripción

Este módulo añade un sistema completo de reseñas al sitio web de Vitaltecuida con moderación avanzada y diseño profesional.

## Funcionalidades

### 🌐 Página Pública de Reseñas
- **URL**: `/reviews` - Aparece en el menú principal al lado de "Inicio"
- **Formulario público**: Los visitantes pueden enviar reseñas sin registro
- **Estadísticas en tiempo real**: Muestra calificación promedio y total de reseñas
- **Diseño responsive**: Optimizado para móviles y escritorio

### ⭐ Sistema de Calificación
- **Escala de 1 a 5 estrellas** con iconos visuales
- **Cálculo automático** de promedio de calificaciones
- **Visualización atractiva** con emojis de estrellas

### 🛡️ Sistema de Moderación
- **Estados de reseña**:
  - **Pendiente**: Recién enviada, esperando revisión
  - **Aprobada**: Visible en el sitio web público
  - **Rechazada**: No se muestra, con razón del rechazo
- **Solo reseñas aprobadas** se muestran al público
- **Panel de administración** completo en el backend

### 📊 Panel de Administración
- **Ubicación**: Sitio Web > Configuración > Reseñas Web
- **Funciones disponibles**:
  - Ver todas las reseñas (pendientes, aprobadas, rechazadas)
  - Aprobar/rechazar con un clic
  - Agregar razones de rechazo
  - Filtros y búsquedas avanzadas
  - Estadísticas y agrupaciones

### 🎨 Diseño Moderno
- **Tarjetas de reseña** con efectos hover
- **Colores de Vitaltecuida** (verde/azul)
- **Animaciones suaves** y transiciones
- **CSS personalizado** incluido

## Instalación

1. El módulo se encuentra en: `custom-vitaltecuida/vitaltecuida_website/`
2. Dependencias: `website`, `mail`, `portal` (módulos core de Odoo)
3. Instalar desde Aplicaciones > Buscar "Vitaltecuida Website"

## Configuración

### Menú del Sitio Web
- Se crea automáticamente el menú "Reseñas" al lado de "Inicio"
- Secuencia: 20 (aparece después del menú principal)

### Permisos de Seguridad
- **Público**: Puede leer reseñas aprobadas y crear nuevas
- **Portal**: Puede leer y crear reseñas
- **Usuarios**: Pueden gestionar reseñas (aprobar/rechazar)
- **Administradores**: Control total

## Uso

### Para Visitantes del Sitio Web
1. Ir a `/reviews` o hacer clic en "Reseñas" en el menú
2. Llenar el formulario:
   - Nombre (requerido)
   - Email (opcional)
   - Calificación 1-5 estrellas (requerido)
   - Título de la experiencia (requerido)
   - Comentario detallado (requerido)
3. Enviar y esperar aprobación

### Para Administradores
1. Ir a **Sitio Web > Configuración > Reseñas Web**
2. Ver reseñas pendientes (filtro automático)
3. Abrir reseña y usar botones:
   - **Aprobar**: Hace visible la reseña al público
   - **Rechazar**: Oculta la reseña (agregar razón)
   - **Volver a Pendiente**: Resetea el estado

## Estructura de Archivos

```
vitaltecuida_website/
├── models/
│   └── website_review.py          # Modelo de reseñas
├── controllers/
│   └── main.py                    # Controlador web (rutas)
├── views/
│   └── review_views.xml           # Vistas de administración
├── templates/
│   └── review_templates.xml       # Plantillas del sitio web
├── data/
│   └── website_menu_data.xml      # Menú del sitio web
├── security/
│   └── ir.model.access.csv        # Permisos de acceso
├── static/src/css/
│   └── review_style.css           # Estilos personalizados
└── README.md                      # Documentación
```

## API y Endpoints

### Páginas Web
- **`/reviews`**: Página principal de reseñas
- **`/reviews/submit`**: Procesar envío de reseña (POST)

### API JSON
- **`/reviews/api/list`**: Obtener reseñas aprobadas (JSON)

## Campos del Modelo

### Información del Cliente
- `customer_name`: Nombre (requerido)
- `email`: Email (opcional)

### Contenido de la Reseña
- `rating`: Calificación 1-5 estrellas
- `title`: Título de la experiencia
- `review_text`: Comentario detallado

### Estado y Moderación
- `state`: pending/approved/rejected
- `website_published`: Boolean (auto-gestionado)
- `moderated_by`: Usuario que moderó
- `moderation_date`: Fecha de moderación
- `rejection_reason`: Motivo del rechazo

### Información Técnica
- `ip_address`: IP del visitante
- `user_agent`: Navegador usado

## Características Técnicas

### Seguridad
- **Protección CSRF** en formularios
- **Validación de datos** en backend
- **Registro de IP** para auditoría
- **Estados controlados** para moderación

### Performance
- **Consultas optimizadas** para reseñas públicas
- **Límites configurable** de reseñas mostradas
- **Caché-friendly** para estadísticas

### UX/UI
- **Notificaciones claras** después del envío
- **Páginas de error** personalizadas
- **Diseño responsive** para todos los dispositivos
- **Animaciones suaves** y efectos visuales

## Compatibilidad

- Odoo 18.0
- Módulos core: `website`, `mail`, `portal`
- Browsers: Chrome, Firefox, Safari, Edge
- Móviles: iOS, Android

## Futuras Mejoras

- Sistema de respuestas a reseñas
- Notificaciones por email para nuevas reseñas
- Integración con Google Reviews
- Sistema de puntos/gamificación
- Filtros avanzados por servicios

## Autor

Vitaltecuida
