# Frontend - Aplicación de Seguimiento de Hábitos

Aplicación web construida con SvelteKit 5, Highcharts 12 y Tailwind CSS para el seguimiento y análisis de hábitos personales.

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

## Estructura del Proyecto

```
src/
├── lib/
│   ├── api.ts                    # Cliente API con autenticación JWT
│   ├── stores/
│   │   └── auth.svelte.ts        # Store de autenticación con Runes
│   └── components/
│       └── (componentes compartidos)
├── routes/
│   ├── +layout.svelte            # Layout principal con navegación
│   ├── +page.svelte              # Dashboard de progreso diario
│   ├── login/
│   │   └── +page.svelte          # Página de inicio de sesión
│   ├── register/
│   │   └── +page.svelte          # Página de registro
│   ├── habitos/
│   │   └── +page.svelte          # Gestión de hábitos
│   ├── analisis/
│   │   └── +page.svelte          # Análisis y reportes con gráficos
│   └── settings/
│       └── +page.svelte          # Configuración de usuario
└── app.css                       # Estilos globales con Tailwind
```

## Características Principales

### 🔐 Autenticación
- Sistema completo de registro y login
- Protección de rutas con JWT
- Store reactivo de autenticación usando Svelte 5 Runes

### 🎯 Gestión de Hábitos
- Crear, editar y eliminar hábitos
- Asignar categorías y colores
- Configurar metas diarias y días de la semana
- Vista de progreso en tiempo real

### 📊 Dashboard de Progreso
- Vista diaria de todos los hábitos
- Marcar hábitos como completados
- Navegación por fechas
- Indicadores visuales de progreso

### 📈 Análisis Avanzado (8 tipos de gráficos)
Visualización de datos con Highcharts 12:

1. **Área** - Tendencia de hábitos completados
2. **Polar** - Distribución de completados por día
3. **Pastel** - Cumplimiento de hábitos por categoría
4. **Spline** - Progreso suavizado en el tiempo
5. **Columnas** - Comparación de hábitos activos vs completados
6. **Gauge** - Porcentaje de cumplimiento total
7. **Radar** - Completados por día de la semana
8. **Barras** - Ranking de hábitos por cumplimiento

#### Filtros de Fecha
- Este mes
- Última semana
- Último mes
- Este año
- Rango personalizado

### 🎨 Diseño
- Tema oscuro moderno
- Diseño responsive (móvil, tablet, desktop)
- Animaciones suaves
- Paleta de colores personalizada (#e94560, #533483, #0E0D0D)

## Tecnologías Utilizadas

- **SvelteKit 5** - Framework con Runes ($state, $effect, $derived)
- **Highcharts 12** - Librería de gráficos interactivos
- **Tailwind CSS** - Framework de estilos utility-first
- **TypeScript** - Tipado estático
- **Vite** - Build tool ultrarrápido

## Integración con Backend

El frontend se comunica con el backend FastAPI mediante la API REST:

```typescript
// Ejemplo de uso de la API con autenticación
import { listarHabitos, crearHabito } from '$lib/api';

// Listar hábitos del usuario autenticado
const habitos = await listarHabitos();

// Crear nuevo hábito
const nuevoHabito = await crearHabito({
  nombre: 'Ejercicio',
  categoria_id: 1,
  meta_diaria: 30,
  unidad_medida: 'minutos',
  dias: '["L","M","X","J","V"]',
  color: '#e94560'
});
```

## Configuración de Entorno

El frontend está configurado para usar variables de entorno para la URL de la API:

```typescript
// src/lib/api.ts
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";
```

Puedes crear un archivo `.env` en la raíz del frontend:

```env
VITE_API_URL=http://localhost:8000/api
```

## Despliegue

```bash
# Compilar para producción
npm run build

# Vista previa de producción
npm run preview

# El build se genera en ./build/
```

## Notas de Desarrollo

### SSR y Highcharts
Los gráficos de Highcharts se cargan dinámicamente en el cliente para evitar errores de SSR:

```typescript
async function renderizarGraficos() {
  if (typeof window === 'undefined') return;

  const Highcharts = (await import('highcharts')).default;
  // ... configuración de gráficos
}
```

### Svelte 5 Runes
El proyecto usa la nueva sintaxis de Runes de Svelte 5:

```typescript
let habitos = $state<Habito[]>([]);
let habitosFiltrados = $derived(habitos.filter(h => h.activo));

$effect(() => {
  console.log('Hábitos actualizados:', habitos.length);
});
```
