<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { getProgresoMes, getRegistroPorFecha } from '$lib/api';
  import type { ProgresoDiaCalendario } from '$lib/api';

  // Estado del calendario
  let currentDate = $state(new Date());
  let progresoMes = $state<ProgresoDiaCalendario[]>([]);
  let loading = $state(true);
  let error = $state<string | null>(null);

  // Estados para secciones colapsables
  let mostrarLeyenda = $state(false);
  let mostrarInstrucciones = $state(false);

  // Información derivada
  let year = $derived(currentDate.getFullYear());
  let month = $derived(currentDate.getMonth()); // 0-11
  let monthName = $derived(
    new Date(year, month, 1).toLocaleDateString('es-ES', { month: 'long', year: 'numeric' })
  );

  // Cargar datos del mes al montar o cambiar fecha
  onMount(() => {
    cargarProgresoMes();
  });

  $effect(() => {
    // Recargar cuando cambie el mes
    cargarProgresoMes();
  });

  async function cargarProgresoMes() {
    try {
      loading = true;
      error = null;
      // month es 0-11, el backend espera 1-12
      progresoMes = await getProgresoMes(year, month + 1);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error al cargar progreso del mes';
    } finally {
      loading = false;
    }
  }

  // Navegación entre meses
  function mesAnterior() {
    currentDate = new Date(year, month - 1, 1);
  }

  function mesSiguiente() {
    currentDate = new Date(year, month + 1, 1);
  }

  function irMesActual() {
    currentDate = new Date();
  }

  // Construir el calendario (grid con días)
  function construirCalendario() {
    const primerDia = new Date(year, month, 1);
    const ultimoDia = new Date(year, month + 1, 0);

    // Día de la semana del primer día (0 = domingo, 1 = lunes, ...)
    // Ajustamos para que lunes sea 0
    let diaSemanaInicio = primerDia.getDay() - 1;
    if (diaSemanaInicio === -1) diaSemanaInicio = 6; // domingo

    const totalDias = ultimoDia.getDate();

    // Crear array de días del calendario (con vacíos al inicio)
    const dias: (ProgresoDiaCalendario | null)[] = [];

    // Llenar días vacíos al inicio
    for (let i = 0; i < diaSemanaInicio; i++) {
      dias.push(null);
    }

    // Llenar días del mes
    for (let dia = 1; dia <= totalDias; dia++) {
      const fechaStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(dia).padStart(2, '0')}`;
      const progreso = progresoMes.find((p) => p.fecha === fechaStr);

      if (progreso) {
        dias.push(progreso);
      } else {
        // Día sin datos
        dias.push({
          fecha: fechaStr,
          total_habitos: 0,
          habitos_completados: 0,
          porcentaje: 0,
          tiene_registro: false
        });
      }
    }

    return dias;
  }

  let diasCalendario = $derived(construirCalendario());

  // Helper para parsear fecha YYYY-MM-DD como fecha local (no UTC)
  function parsearFechaLocal(fechaStr: string): Date {
    const [year, month, day] = fechaStr.split('-').map(Number);
    return new Date(year, month - 1, day, 12, 0, 0, 0);
  }

  // Verificar si es hoy
  function esHoy(fecha: string): boolean {
    const hoy = new Date();
    hoy.setHours(12, 0, 0, 0);
    const fechaComparar = parsearFechaLocal(fecha);
    return fechaComparar.toDateString() === hoy.toDateString();
  }

  // Obtener color según porcentaje
  function getColorPorcentaje(porcentaje: number): string {
    if (porcentaje === 0) return 'bg-[#1a1a1a]'; // Sin progreso
    if (porcentaje < 25) return 'bg-red-900/40';
    if (porcentaje < 50) return 'bg-orange-900/40';
    if (porcentaje < 75) return 'bg-yellow-900/40';
    if (porcentaje < 100) return 'bg-blue-900/40';
    return 'bg-green-900/50'; // 100%
  }

  // Navegar al día específico
  function irADia(fecha: string) {
    goto(`/?fecha=${fecha}`);
  }
</script>

<div class="container mx-auto p-3 sm:p-4 md:p-6 max-w-6xl pb-24 md:pb-8">
  <!-- Header del Calendario -->
  <div class="mb-4 md:mb-6">
    <h1 class="text-2xl sm:text-3xl font-bold text-white mb-1 sm:mb-2">Calendario de Progreso</h1>
    <p class="text-sm sm:text-base text-text_secondary">Visualiza tu progreso diario en cada hábito</p>
  </div>

  <!-- Navegación de Meses -->
  <div class="bg-bg_secondary border border-border rounded-lg p-3 sm:p-4 mb-4 md:mb-6">
    <div class="flex items-center justify-between gap-2">
      <button
        onclick={mesAnterior}
        class="flex items-center justify-center gap-1 sm:gap-2 px-3 sm:px-4 py-2 sm:py-2.5
               bg-[#1a1a1a] border border-[#533483] text-white rounded-md
               hover:bg-[#533483]/20 transition-colors min-w-[44px] touch-manipulation"
        aria-label="Mes anterior"
      >
        <span class="text-lg sm:text-xl">←</span>
        <span class="hidden sm:inline text-sm">Anterior</span>
      </button>

      <div class="flex flex-col items-center gap-1 sm:gap-2 flex-1 min-w-0">
        <h2 class="text-lg sm:text-xl md:text-2xl font-bold text-white capitalize truncate w-full text-center">
          {monthName}
        </h2>
        <button
          onclick={irMesActual}
          class="text-xs sm:text-sm text-[#e94560] hover:text-[#d13851] transition-colors
                 py-1 px-2 touch-manipulation"
        >
          Ir a hoy
        </button>
      </div>

      <button
        onclick={mesSiguiente}
        class="flex items-center justify-center gap-1 sm:gap-2 px-3 sm:px-4 py-2 sm:py-2.5
               bg-[#1a1a1a] border border-[#533483] text-white rounded-md
               hover:bg-[#533483]/20 transition-colors min-w-[44px] touch-manipulation"
        aria-label="Mes siguiente"
      >
        <span class="hidden sm:inline text-sm">Siguiente</span>
        <span class="text-lg sm:text-xl">→</span>
      </button>
    </div>
  </div>

  <!-- Error -->
  {#if error}
    <div class="bg-red-500/10 border border-red-500 text-red-500 p-4 rounded-md mb-6">
      {error}
    </div>
  {/if}

  <!-- Loading -->
  {#if loading}
    <div class="flex justify-center items-center py-20">
      <div class="flex flex-col items-center gap-4">
        <svg
          class="animate-spin h-12 w-12 text-accent"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            class="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            stroke-width="4"
          ></circle>
          <path
            class="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          ></path>
        </svg>
        <p class="text-text_secondary">Cargando calendario...</p>
      </div>
    </div>
  {:else}
    <!-- Calendario -->
    <div class="bg-bg_secondary border border-border rounded-lg p-2 sm:p-4 md:p-6">
      <!-- Días de la semana -->
      <div class="grid grid-cols-7 gap-1 sm:gap-2 mb-2 sm:mb-4">
        {#each [
          { completo: 'Lun', corto: 'L' },
          { completo: 'Mar', corto: 'M' },
          { completo: 'Mié', corto: 'X' },
          { completo: 'Jue', corto: 'J' },
          { completo: 'Vie', corto: 'V' },
          { completo: 'Sáb', corto: 'S' },
          { completo: 'Dom', corto: 'D' }
        ] as dia}
          <div class="text-center text-xs sm:text-sm font-semibold text-text_secondary py-1 sm:py-2">
            <span class="hidden sm:inline">{dia.completo}</span>
            <span class="sm:hidden">{dia.corto}</span>
          </div>
        {/each}
      </div>

      <!-- Días del mes -->
      <div class="grid grid-cols-7 gap-1 sm:gap-2">
        {#each diasCalendario as dia}
          {#if dia === null}
            <!-- Día vacío (de otro mes) -->
            <div class="aspect-square"></div>
          {:else}
            <!-- Día del mes -->
            <button
              onclick={() => irADia(dia.fecha)}
              class="aspect-square border border-[#533483] rounded-md p-1 sm:p-2
                     hover:border-[#e94560] active:scale-95 sm:hover:scale-105
                     transition-all min-h-[44px] touch-manipulation
                     {getColorPorcentaje(dia.porcentaje)}
                     {esHoy(dia.fecha) ? 'ring-1 sm:ring-2 ring-[#e94560]' : ''}"
              title="Ver progreso del día"
            >
              <div class="h-full flex flex-col justify-between text-[10px] sm:text-xs">
                <!-- Número del día -->
                <div class="flex justify-between items-start gap-0.5">
                  <span
                    class="font-semibold leading-none {esHoy(dia.fecha)
                      ? 'text-[#e94560] text-sm sm:text-base'
                      : 'text-white text-xs sm:text-sm'}"
                  >
                    {parsearFechaLocal(dia.fecha).getDate()}
                  </span>
                  {#if dia.tiene_registro && dia.total_habitos > 0}
                    <span class="text-[8px] sm:text-[10px] text-text_secondary leading-none">
                      {dia.habitos_completados}/{dia.total_habitos}
                    </span>
                  {/if}
                </div>

                <!-- Indicador de progreso -->
                {#if dia.total_habitos > 0}
                  <div class="mt-auto">
                    <div class="w-full bg-[#0E0D0D] rounded-full h-1 sm:h-1.5">
                      <div
                        class="h-1 sm:h-1.5 rounded-full transition-all duration-300 {dia.porcentaje ===
                        100
                          ? 'bg-[#00ff88]'
                          : 'bg-[#e94560]'}"
                        style="width: {dia.porcentaje}%"
                      ></div>
                    </div>
                    <p class="text-center mt-0.5 sm:mt-1 text-[8px] sm:text-[10px] text-text_secondary leading-none">
                      {Math.round(dia.porcentaje)}%
                    </p>
                  </div>
                {:else}
                  <div class="mt-auto text-center text-[8px] sm:text-[10px] text-text_secondary leading-none hidden sm:block">
                    Sin hábitos
                  </div>
                {/if}
              </div>
            </button>
          {/if}
        {/each}
      </div>

      <!-- Leyenda (Colapsable) -->
      <div class="mt-4 sm:mt-6 pt-3 sm:pt-4 border-t border-border">
        <button
          onclick={() => (mostrarLeyenda = !mostrarLeyenda)}
          class="flex items-center justify-between w-full text-left group hover:text-white transition-colors touch-manipulation"
        >
          <p class="text-xs sm:text-sm text-text_secondary group-hover:text-white">
            Leyenda de progreso
          </p>
          <span class="text-text_secondary group-hover:text-white transition-transform duration-200 {mostrarLeyenda ? 'rotate-180' : ''}">
            ▼
          </span>
        </button>

        {#if mostrarLeyenda}
          <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 sm:gap-3 text-[10px] sm:text-xs mt-2 sm:mt-3 animate-slide-down">
            <div class="flex items-center gap-1.5 sm:gap-2">
              <div class="w-3 h-3 sm:w-4 sm:h-4 bg-[#1a1a1a] border border-[#533483] rounded flex-shrink-0"></div>
              <span class="text-text_secondary truncate">Sin progreso</span>
            </div>
            <div class="flex items-center gap-1.5 sm:gap-2">
              <div class="w-3 h-3 sm:w-4 sm:h-4 bg-red-900/40 border border-[#533483] rounded flex-shrink-0"></div>
              <span class="text-text_secondary truncate">{'< 25%'}</span>
            </div>
            <div class="flex items-center gap-1.5 sm:gap-2">
              <div class="w-3 h-3 sm:w-4 sm:h-4 bg-orange-900/40 border border-[#533483] rounded flex-shrink-0"></div>
              <span class="text-text_secondary truncate">25-49%</span>
            </div>
            <div class="flex items-center gap-1.5 sm:gap-2">
              <div class="w-3 h-3 sm:w-4 sm:h-4 bg-yellow-900/40 border border-[#533483] rounded flex-shrink-0"></div>
              <span class="text-text_secondary truncate">50-74%</span>
            </div>
            <div class="flex items-center gap-1.5 sm:gap-2">
              <div class="w-3 h-3 sm:w-4 sm:h-4 bg-blue-900/40 border border-[#533483] rounded flex-shrink-0"></div>
              <span class="text-text_secondary truncate">75-99%</span>
            </div>
            <div class="flex items-center gap-1.5 sm:gap-2">
              <div class="w-3 h-3 sm:w-4 sm:h-4 bg-green-900/50 border border-[#533483] rounded flex-shrink-0"></div>
              <span class="text-text_secondary truncate">100%</span>
            </div>
          </div>
        {/if}
      </div>
    </div>
  {/if}

  <!-- Instrucciones (Colapsable) -->
  <div class="mt-4 sm:mt-6 bg-[#1a1a1a] border border-[#533483] rounded-lg p-3 sm:p-4">
    <button
      onclick={() => (mostrarInstrucciones = !mostrarInstrucciones)}
      class="flex items-center justify-between w-full text-left group touch-manipulation"
    >
      <h3 class="text-white font-semibold text-sm sm:text-base">💡 Cómo usar el calendario</h3>
      <span class="text-text_secondary group-hover:text-white transition-transform duration-200 {mostrarInstrucciones ? 'rotate-180' : ''}">
        ▼
      </span>
    </button>

    {#if mostrarInstrucciones}
      <ul class="text-text_secondary text-xs sm:text-sm space-y-1 list-disc list-inside mt-3 animate-slide-down">
        <li>Toca cualquier día para ver tu progreso</li>
        <li class="hidden sm:list-item">Los colores indican el porcentaje de hábitos completados</li>
        <li>El borde rojo indica el día actual</li>
        <li class="hidden sm:list-item">Usa las flechas para navegar entre meses</li>
      </ul>
    {/if}
  </div>
</div>

<style>
  @keyframes slide-down {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  :global(.animate-slide-down) {
    animation: slide-down 0.3s ease-out;
  }
</style>
