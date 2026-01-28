<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { getProgresoMes, getRegistroPorFecha, getHabitos, getProgresoMesHabito } from '$lib/api';
  import type { ProgresoDiaCalendario, Habito, ProgresoHabitoDiaCalendario } from '$lib/api';

  // Estado del calendario
  let currentDate = $state(new Date());
  let progresoMes = $state<ProgresoDiaCalendario[]>([]);
  let progresoHabitosMes = $state<Map<number, ProgresoHabitoDiaCalendario[]>>(new Map());
  let loading = $state(true);
  let error = $state<string | null>(null);

  // Estado para filtro de hábitos (ahora es un array para múltiple selección)
  let habitos = $state<Habito[]>([]);
  let habitosSeleccionados = $state<number[]>([]);
  let loadingHabitos = $state(false);

  // Estado para menú desplegable en móvil
  let mostrarFiltros = $state(false);

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
    cargarHabitos();
    cargarProgresoMes();
  });

  $effect(() => {
    // Recargar cuando cambie el mes
    cargarProgresoMes();
  });

  $effect(() => {
    // Recargar cuando cambien los hábitos seleccionados
    if (habitosSeleccionados.length > 0) {
      cargarProgresoHabitos();
    }
  });

  async function cargarHabitos() {
    try {
      loadingHabitos = true;
      habitos = await getHabitos();
    } catch (err) {
      console.error('Error al cargar hábitos:', err);
    } finally {
      loadingHabitos = false;
    }
  }

  async function cargarProgresoMes() {
    try {
      loading = true;
      error = null;
      // month es 0-11, el backend espera 1-12
      progresoMes = await getProgresoMes(year, month + 1);
      
      // Si hay hábitos seleccionados, cargar su progreso también
      if (habitosSeleccionados.length > 0) {
        await cargarProgresoHabitos();
      }
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error al cargar progreso del mes';
    } finally {
      loading = false;
    }
  }

  async function cargarProgresoHabitos() {
    if (habitosSeleccionados.length === 0) return;
    
    try {
      const nuevoMapa = new Map<number, ProgresoHabitoDiaCalendario[]>();
      
      // Cargar progreso de cada hábito seleccionado en paralelo
      const promesas = habitosSeleccionados.map(async (habitoId) => {
        const progreso = await getProgresoMesHabito(year, month + 1, habitoId);
        return { habitoId, progreso };
      });
      
      const resultados = await Promise.all(promesas);
      
      for (const { habitoId, progreso } of resultados) {
        nuevoMapa.set(habitoId, progreso);
      }
      
      progresoHabitosMes = nuevoMapa;
    } catch (err) {
      console.error('Error al cargar progreso de los hábitos:', err);
    }
  }

  function toggleHabito(habitoId: number) {
    if (habitosSeleccionados.includes(habitoId)) {
      habitosSeleccionados = habitosSeleccionados.filter(id => id !== habitoId);
    } else {
      habitosSeleccionados = [...habitosSeleccionados, habitoId];
    }
    
    if (habitosSeleccionados.length === 0) {
      progresoHabitosMes = new Map();
    }
  }

  function limpiarSeleccion() {
    habitosSeleccionados = [];
    progresoHabitosMes = new Map();
  }

  function seleccionarTodosHabitos() {
    const activos = habitos.filter(h => h.activo === 1).map(h => h.id);
    habitosSeleccionados = activos;
  }

  // Obtener los hábitos seleccionados actuales
  let habitosActuales = $derived(habitos.filter(h => habitosSeleccionados.includes(h.id)));
  
  // Verificar si hay filtro activo
  let hayFiltroActivo = $derived(habitosSeleccionados.length > 0);

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

  // Obtener el progreso de todos los hábitos seleccionados para una fecha específica
  function getProgresoHabitosPorFecha(fecha: string): { habito: Habito; progreso: ProgresoHabitoDiaCalendario | undefined }[] {
    return habitosActuales.map(habito => {
      const progresoArray = progresoHabitosMes.get(habito.id);
      const progreso = progresoArray?.find(p => p.fecha === fecha);
      return { habito, progreso };
    });
  }

  // Calcular estado combinado de múltiples hábitos para una fecha
  function getEstadoCombinado(fecha: string): { 
    todosProgramados: number;
    completados: number;
    hayProgramado: boolean;
  } {
    const progresos = getProgresoHabitosPorFecha(fecha);
    const programados = progresos.filter(p => p.progreso?.programado);
    const completados = programados.filter(p => p.progreso?.completado);
    
    return {
      todosProgramados: programados.length,
      completados: completados.length,
      hayProgramado: programados.length > 0
    };
  }

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

  <!-- Filtro de Hábitos -->
  <div class="bg-bg_secondary border border-border rounded-lg mb-4 md:mb-6 overflow-hidden">
    <!-- Header del filtro (siempre visible) -->
    <button
      onclick={() => (mostrarFiltros = !mostrarFiltros)}
      class="w-full p-3 sm:p-4 flex items-center justify-between touch-manipulation sm:cursor-default"
    >
      <div class="flex items-center gap-2">
        <span class="text-sm text-text_secondary">🔍 Filtrar por hábito</span>
        {#if habitosSeleccionados.length > 0}
          <span class="bg-[#e94560] text-white text-xs px-2 py-0.5 rounded-full">
            {habitosSeleccionados.length}
          </span>
        {/if}
      </div>
      <span class="text-text_secondary sm:hidden transition-transform duration-200 {mostrarFiltros ? 'rotate-180' : ''}">
        ▼
      </span>
    </button>

    <!-- Contenido del filtro (desplegable en móvil, siempre visible en desktop) -->
    <div class="{mostrarFiltros ? 'block' : 'hidden'} sm:block px-3 sm:px-4 pb-3 sm:pb-4 border-t border-border sm:border-t-0">
      <!-- Botones de acción rápida -->
      <div class="flex flex-wrap gap-2 mb-3 pt-3 sm:pt-0">
        <button
          onclick={limpiarSeleccion}
          class="px-3 py-2 rounded-md text-sm font-medium transition-all touch-manipulation
                 {habitosSeleccionados.length === 0 
                   ? 'bg-[#e94560] text-white ring-2 ring-[#e94560]/50' 
                   : 'bg-[#1a1a1a] border border-[#533483] text-text_secondary hover:text-white hover:border-[#e94560]'}"
        >
          📊 Vista general
        </button>
        <button
          onclick={seleccionarTodosHabitos}
          class="px-3 py-2 rounded-md text-sm font-medium transition-all touch-manipulation
                 bg-[#1a1a1a] border border-[#533483] text-text_secondary hover:text-white hover:border-[#e94560]"
        >
          ✓ Todos
        </button>
      </div>

      <!-- Grid de hábitos con checkboxes para fácil selección múltiple -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
        {#each habitos.filter(h => h.activo === 1) as habito (habito.id)}
          {@const isSelected = habitosSeleccionados.includes(habito.id)}
          <button
            onclick={() => toggleHabito(habito.id)}
            class="p-3 rounded-lg text-sm font-medium transition-all touch-manipulation flex items-center gap-3
                   {isSelected 
                     ? 'ring-2 ring-offset-2 ring-offset-bg_secondary' 
                     : 'bg-[#1a1a1a] border border-[#533483] hover:border-white/30'}"
            style={isSelected 
              ? `background-color: ${habito.color}; ring-color: ${habito.color}` 
              : ''}
          >
            <!-- Checkbox visual -->
            <div 
              class="w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 transition-colors
                     {isSelected ? 'border-white bg-white/20' : 'border-[#533483]'}"
            >
              {#if isSelected}
                <span class="text-white text-xs">✓</span>
              {/if}
            </div>
            
            <!-- Color del hábito -->
            <span 
              class="w-4 h-4 rounded flex-shrink-0" 
              style="background-color: {habito.color}"
            ></span>
            
            <!-- Nombre del hábito -->
            <span class="truncate {isSelected ? 'text-white' : 'text-text_secondary'}">{habito.nombre}</span>
          </button>
        {/each}
      </div>
    </div>
    
    <!-- Resumen de selección -->
    {#if habitosSeleccionados.length > 0}
      <div class="px-3 sm:px-4 pb-3 sm:pb-4 pt-3 border-t border-border">
        <div class="flex flex-wrap items-center gap-2 text-sm">
          <span class="text-white font-medium">Viendo:</span>
          <div class="flex flex-wrap gap-1">
            {#each habitosActuales as habito (habito.id)}
              <span 
                class="inline-flex items-center gap-1 px-2 py-1 rounded text-xs text-white"
                style="background-color: {habito.color}"
              >
                {habito.nombre}
                <button 
                  onclick={(e) => { e.stopPropagation(); toggleHabito(habito.id); }}
                  class="ml-1 hover:bg-white/20 rounded-full w-4 h-4 flex items-center justify-center"
                >
                  ×
                </button>
              </span>
            {/each}
          </div>
        </div>
      </div>
    {/if}
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
        <div class="orbit-spinner">
          <div class="orbit"></div>
          <div class="orbit"></div>
          <div class="orbit"></div>
        </div>
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
        {#each diasCalendario as dia, i (dia ? `${year}-${month}-${dia.fecha}` : `empty-${i}`)}
          {#if dia === null}
            <!-- Día vacío (de otro mes) -->
            <div class="aspect-square"></div>
          {:else if hayFiltroActivo}
            <!-- Vista filtrada por hábitos: muestra cuadrados de colores -->
            {@const progresos = getProgresoHabitosPorFecha(dia.fecha)}
            {@const estado = getEstadoCombinado(dia.fecha)}
            <button
              onclick={() => irADia(dia.fecha)}
              class="aspect-square border border-[#533483] rounded-md p-1
                     hover:scale-105 active:scale-95
                     transition-all min-h-[44px] touch-manipulation flip-in-hor-bottom
                     {esHoy(dia.fecha) ? 'ring-2 ring-[#e94560]' : ''}
                     {estado.hayProgramado 
                       ? (estado.completados === estado.todosProgramados ? 'bg-green-900/30' : 'bg-[#1a1a1a]')
                       : 'bg-[#1a1a1a]'}"
              style="animation-delay: {i * 0.02}s;"
              title={estado.hayProgramado 
                ? `${estado.completados}/${estado.todosProgramados} completados` 
                : 'No programado'}
            >
              <div class="h-full flex flex-col justify-between">
                <!-- Número del día -->
                <span
                  class="font-semibold leading-none {esHoy(dia.fecha)
                    ? 'text-[#e94560] text-xs sm:text-sm'
                    : 'text-white text-[10px] sm:text-xs'}"
                >
                  {parsearFechaLocal(dia.fecha).getDate()}
                </span>

                <!-- Grid de cuadrados de colores de hábitos -->
                {#if estado.hayProgramado}
                  <div class="mt-auto flex flex-wrap justify-center gap-0.5">
                    {#each progresos.filter(p => p.progreso?.programado) as { habito, progreso } (habito.id)}
                      <div 
                        class="w-2 h-2 sm:w-2.5 sm:h-2.5 rounded-sm transition-all"
                        style="background-color: {progreso?.completado ? habito.color : `${habito.color}40`};
                               border: 1px solid {habito.color};"
                        title="{habito.nombre}: {progreso?.completado ? '✓' : '○'}"
                      ></div>
                    {/each}
                  </div>
                {:else}
                  <div class="mt-auto text-center text-[8px] text-text_secondary opacity-50">
                    —
                  </div>
                {/if}
              </div>
            </button>
          {:else}
            <!-- Vista general: todos los hábitos -->
            <button
              onclick={() => irADia(dia.fecha)}
              class="aspect-square border border-[#533483] rounded-md p-1 sm:p-2
                     hover:border-[#e94560] active:scale-95 sm:hover:scale-105
                     transition-all min-h-[44px] touch-manipulation flip-in-hor-bottom
                     {getColorPorcentaje(dia.porcentaje)}
                     {esHoy(dia.fecha) ? 'ring-1 sm:ring-2 ring-[#e94560]' : ''}"
              style="animation-delay: {i * 0.02}s;"
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
          {#if hayFiltroActivo}
            <!-- Leyenda para vista filtrada por hábitos -->
            <div class="mt-2 sm:mt-3 animate-slide-down">
              <p class="text-[10px] sm:text-xs text-text_secondary mb-2">Cada cuadrado representa un hábito:</p>
              <div class="flex flex-wrap gap-2 mb-3">
                {#each habitosActuales as habito (habito.id)}
                  <div class="flex items-center gap-1.5">
                    <div 
                      class="w-3 h-3 sm:w-4 sm:h-4 rounded-sm"
                      style="background-color: {habito.color}"
                    ></div>
                    <span class="text-[10px] sm:text-xs text-text_secondary">{habito.nombre}</span>
                  </div>
                {/each}
              </div>
              <div class="grid grid-cols-2 sm:grid-cols-3 gap-2 text-[10px] sm:text-xs border-t border-border pt-2">
                <div class="flex items-center gap-1.5">
                  <div class="w-3 h-3 sm:w-4 sm:h-4 rounded-sm bg-green-500 border border-green-500"></div>
                  <span class="text-text_secondary">Completado</span>
                </div>
                <div class="flex items-center gap-1.5">
                  <div class="w-3 h-3 sm:w-4 sm:h-4 rounded-sm bg-green-500/30 border border-green-500"></div>
                  <span class="text-text_secondary">Pendiente</span>
                </div>
                <div class="flex items-center gap-1.5">
                  <div class="w-3 h-3 sm:w-4 sm:h-4 rounded-sm bg-[#1a1a1a] border border-[#533483]"></div>
                  <span class="text-text_secondary">No programado</span>
                </div>
              </div>
            </div>
          {:else}
            <!-- Leyenda para vista general -->
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
        <li>Filtra por hábito para ver su progreso individual</li>
      </ul>
    {/if}
  </div>
</div>

<style>
  /* Orbit Spinner Animation */
  .orbit-spinner,
  .orbit-spinner * {
    box-sizing: border-box;
  }

  .orbit-spinner {
    height: 55px;
    width: 55px;
    border-radius: 50%;
    perspective: 800px;
  }

  .orbit-spinner .orbit {
    position: absolute;
    box-sizing: border-box;
    width: 100%;
    height: 100%;
    border-radius: 50%;
  }

  .orbit-spinner .orbit:nth-child(1) {
    left: 0%;
    top: 0%;
    animation: orbit-spinner-orbit-one-animation 1200ms linear infinite;
    border-bottom: 3px solid #ff1d5e;
  }

  .orbit-spinner .orbit:nth-child(2) {
    right: 0%;
    top: 0%;
    animation: orbit-spinner-orbit-two-animation 1200ms linear infinite;
    border-right: 3px solid #ff1d5e;
  }

  .orbit-spinner .orbit:nth-child(3) {
    right: 0%;
    bottom: 0%;
    animation: orbit-spinner-orbit-three-animation 1200ms linear infinite;
    border-top: 3px solid #ff1d5e;
  }

  @keyframes orbit-spinner-orbit-one-animation {
    0% {
      transform: rotateX(35deg) rotateY(-45deg) rotateZ(0deg);
    }
    100% {
      transform: rotateX(35deg) rotateY(-45deg) rotateZ(360deg);
    }
  }

  @keyframes orbit-spinner-orbit-two-animation {
    0% {
      transform: rotateX(50deg) rotateY(10deg) rotateZ(0deg);
    }
    100% {
      transform: rotateX(50deg) rotateY(10deg) rotateZ(360deg);
    }
  }

  @keyframes orbit-spinner-orbit-three-animation {
    0% {
      transform: rotateX(35deg) rotateY(55deg) rotateZ(0deg);
    }
    100% {
      transform: rotateX(35deg) rotateY(55deg) rotateZ(360deg);
    }
  }

  /* Slide Down Animation */
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

  /* Flip In Animation */
  @keyframes flip-in-hor-bottom {
    0% {
      transform: rotateX(80deg);
      opacity: 0;
    }
    100% {
      transform: rotateX(0);
      opacity: 1;
    }
  }

  :global(.flip-in-hor-bottom) {
    animation: flip-in-hor-bottom 0.5s cubic-bezier(0.250, 0.460, 0.450, 0.940) both;
    transform-origin: bottom;
  }
</style>
