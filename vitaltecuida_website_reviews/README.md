# Vital Tecuida Website Reviews

## Descripción

Módulo para Odoo 18 Enterprise que permite añadir reseñas de clientes al sitio web mediante un bloque configurable arrastrando y soltando en el constructor de sitios web.

## Características

- 📝 **Gestión de Reseñas**: Interfaz backend completa para crear y gestionar reseñas de clientes
- ⭐ **Valoraciones de 1 a 5 estrellas**: Sistema de puntuación visual con estrellas
- 🎨 **Bloque Arrastrar y Soltar**: Snippet totalmente integrado con el constructor de sitios web
- ⚙️ **Fácil Configuración**: Opciones simples para mostrar 5, 6, 9 o 10 reseñas
- 📱 **Diseño Responsive**: Adaptado automáticamente a todos los dispositivos
- 🎯 **Ordenamiento**: Control de secuencia para ordenar las reseñas
- 👁️ **Activar/Desactivar**: Ocultar reseñas sin eliminarlas

## Instalación

1. Copiar el módulo en la carpeta de addons personalizado
2. Actualizar la lista de aplicaciones
3. Instalar el módulo "Vital Tecuida Website Reviews"

## Uso

### Backend - Gestión de Reseñas

1. Ir a **Sitio Web > Configuración > Reviews**
2. Crear nuevas reseñas con:
   - Nombre del cliente
   - Valoración (1-5 estrellas)
   - Descripción/comentario
   - Fecha
   - Secuencia (orden de aparición)
3. Activar/desactivar reseñas según necesidad

### Frontend - Añadir Bloque en Website

1. Ir al constructor de sitios web (modo edición)
2. En el panel de snippets, buscar la sección **Vital Tecuida**
3. Arrastrar el bloque **Customer Reviews** a la página
4. Configurar opciones:
   - Número de reseñas a mostrar (5, 6, 9 o 10)
   - Título del bloque
   - Subtítulo
5. Click en "Configure Reviews" para ir a gestionar las reseñas

## Estructura del Módulo

```
vitaltecuida_website_reviews/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── main.py
├── models/
│   ├── __init__.py
│   └── website_review.py
├── security/
│   └── ir.model.access.csv
├── static/
│   └── src/
│       ├── img/
│       │   └── snippets_thumbs/
│       │       └── s_reviews.svg
│       ├── js/
│       │   ├── s_reviews.js
│       │   └── s_reviews_options.js
│       └── scss/
│           └── s_reviews.scss
└── views/
    ├── website_review_views.xml
    └── snippets/
        ├── s_reviews.xml
        └── snippets.xml
```

## Tecnologías

- Python 3.10+
- Odoo 18 Enterprise
- JavaScript (Odoo Module System)
- SCSS/CSS
- XML (QWeb)

## Autor

**Vital Tecuida**
- Website: https://vitaltecuida.com

## Licencia

LGPL-3.0

## Versión

18.0.1.0.0

