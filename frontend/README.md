# Frontend SvelteKit + Highcharts

Dashboard con SvelteKit y Highcharts para visualización de datos.

## Requisitos

- Node.js 18+
- npm o pnpm

## Instalación

```bash
npm install
```

## Ejecutar

```bash
# Modo desarrollo
npm run dev

# Producción
npm run build
npm run preview
```

## Estructura

```
src/
├── lib/
│   ├── api.ts              # Cliente API para el backend
│   ├── components/
│   │   └── Chart.svelte    # Componente Highcharts reutilizable
│   └── index.ts
├── routes/
│   ├── +layout.svelte      # Layout principal
│   ├── +page.svelte        # Dashboard principal
│   ├── items/
│   │   └── +page.svelte    # Gestión de items
│   └── charts/
│       └── +page.svelte    # Visualización de gráficos
└── app.css                 # Estilos globales
```

## Características

- 📊 Gráficos interactivos con Highcharts
- 🌙 Tema oscuro
- 📱 Diseño responsive
- 🔌 Integración con API REST
