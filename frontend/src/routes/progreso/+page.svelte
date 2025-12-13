<script lang="ts">
  import { onMount } from 'svelte';
  import { getHabitosByUsuario, type Habito } from '$lib/api';

  let habitos = $state<Habito[]>([]);
  let loading = $state(true);
  let error = $state<string | null>(null);
  let fechaSeleccionada = $state(new Date().toISOString().split('T')[0]);

  // Progreso simulado por hábito (en producción vendría de la API)
  let progresoHoy = $state<Record<number, number>>({});

  const diasSemana = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];

  onMount(async () => {
    try {
      habitos = await getHabitosByUsuario(1);
      // Inicializar progreso en 0
      habitos.forEach(h => {
        progresoHoy[h.id] = 0;
      });
    } catch (e) {
      error = e instanceof Error ? e.message : 'Error cargando hábitos';
    } finally {
      loading = false;
    }
  });

  function incrementar(habitoId: number, meta: number) {
    const actual = progresoHoy[habitoId] || 0;
    if (actual < meta) {
      progresoHoy[habitoId] = actual + 1;
    }
  }

  function decrementar(habitoId: number) {
    const actual = progresoHoy[habitoId] || 0;
    if (actual > 0) {
      progresoHoy[habitoId] = actual - 1;
    }
  }

  function getProgresoPorcentaje(habitoId: number, meta: number): number {
    return Math.min(100, ((progresoHoy[habitoId] || 0) / meta) * 100);
  }

  function estaCompletado(habitoId: number, meta: number): boolean {
    return (progresoHoy[habitoId] || 0) >= meta;
  }

  function getDiaActual(): string {
    const dias = ['D', 'L', 'M', 'X', 'J', 'V', 'S'];
    return dias[new Date().getDay()];
  }

  function habitoActivoHoy(habito: Habito): boolean {
    try {
      const dias = JSON.parse(habito.dias);
      return dias.includes(getDiaActual());
    } catch {
      return true;
    }
  }

  $effect(() => {
    // Contar completados
    const completados = habitos.filter(h => habitoActivoHoy(h) && estaCompletado(h.id, h.meta_diaria)).length;
    const activos = habitos.filter(h => habitoActivoHoy(h)).length;
  });
</script>

<svelte:head>
  <title>Progreso | Hábitos</title>
</svelte:head>

<div class="max-w-2xl mx-auto px-4 py-6 pb-24 md:pb-8">
  <!-- Header con fecha -->
  <div class="flex items-center  justify-between mb-6">
    <div>
      <h1 class="text-2xl font-bold text-text_primary">📊 Hoy</h1>
      <p class="text-text_secondary text-sm">
        {new Date().toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long' })}
      </p>
    </div>
    <input
      type="date"
      bind:value={fechaSeleccionada}
      class="bg-bg_input border border-border rounded px-3 py-2 text-text_primary focus:border-accent focus:outline-none"
    />
  </div>

  <!-- Resumen del día -->
  {#if !loading && habitos.length > 0}
    {@const habitosHoy = habitos.filter(h => habitoActivoHoy(h))}
    {@const completados = habitosHoy.filter(h => estaCompletado(h.id, h.meta_diaria)).length}

    <div class="bg-bg_secondary border border-border rounded-lg p-4 mb-6 slide-in-blurred-top">
      <div class="flex items-center justify-between mb-3">
        <span class="text-text_secondary">Progreso del día</span>
        <span class="text-text_primary font-bold">{completados}/{habitosHoy.length}</span>
      </div>
      <div class="w-full bg-bg_input rounded-full h-3">
        <div
          class="bg-gradient-to-r from-accent to-success h-3 rounded-full transition-all duration-500"
          style="width: {habitosHoy.length > 0 ? (completados / habitosHoy.length) * 100 : 0}%"
        ></div>
      </div>
      {#if completados === habitosHoy.length && habitosHoy.length > 0}
        <p class="text-success text-center mt-3 font-bold">🎉 ¡Completaste todos los hábitos!</p>
      {/if}
    </div>
  {/if}

  <!-- Loading -->
  {#if loading}
    <div class="flex justify-center items-center py-20">
      <div class="breeding-rhombus-spinner">
        <div class="rhombus child-1"></div>
        <div class="rhombus child-2"></div>
        <div class="rhombus child-3"></div>
        <div class="rhombus child-4"></div>
        <div class="rhombus child-5"></div>
        <div class="rhombus child-6"></div>
        <div class="rhombus child-7"></div>
        <div class="rhombus child-8"></div>
        <div class="rhombus big"></div>
      </div>
    </div>
  {:else if error}
    <div class="bg-accent/20 border border-accent text-accent px-4 py-3 rounded-lg">
      {error}
    </div>
  {:else}
    <!-- Lista de hábitos para hoy -->
    <div class="space-y-4">
      {#each habitos.filter(h => habitoActivoHoy(h)) as habito, i (habito.id)}
        {@const progreso = progresoHoy[habito.id] || 0}
        {@const porcentaje = getProgresoPorcentaje(habito.id, habito.meta_diaria)}
        {@const completado = estaCompletado(habito.id, habito.meta_diaria)}

        <div
          class="bg-bg_secondary border rounded-lg p-4 transition-all slide-in-blurred-right {completado ? 'border-success/50 bg-success/5' : 'border-border'}"
          style="animation-delay: {0.2 + i * 0.1}s;"
        >
          <div class="flex items-center   gap-4">
            <!-- Indicador de color -->
            <div 
              class="w-12 h-12 rounded-full flex items-center   justify-center text-white font-bold shrink-0 transition-all {completado ? 'scale-110' : ''}"
              style="background-color: {habito.color}"
            >
              {#if completado}
                ✓
              {:else}
                {progreso}
              {/if}
            </div>

            <!-- Info del hábito -->
            <div class="flex-1 min-w-0">
              <h3 class="font-semibold text-text_primary truncate {completado ? 'line-through opacity-70' : ''}">
                {habito.nombre}
              </h3>
              <p class="text-text_secondary text-sm">
                {progreso} / {habito.meta_diaria} {habito.unidad_medida}
              </p>
              <!-- Barra de progreso -->
              <div class="w-full bg-bg_input rounded-full h-2 mt-2">
                <div 
                  class="h-2 rounded-full transition-all duration-300"
                  style="width: {porcentaje}%; background-color: {habito.color}"
                ></div>
              </div>
            </div>

            <!-- Controles -->
            <div class="flex items-center gap-2 shrink-0">
              <button
                onclick={() => decrementar(habito.id)}
                disabled={progreso === 0}
                class="w-10 h-10 rounded-full bg-bg_input border border-border text-text_secondary hover:border-accent hover:text-accent transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
              >
                −
              </button>
              <button
                onclick={() => incrementar(habito.id, habito.meta_diaria)}
                disabled={completado}
                class="w-10 h-10 rounded-full bg-accent text-white font-bold hover:bg-accent/80 transition-colors disabled:bg-success disabled:cursor-default"
              >
                +
              </button>
            </div>
          </div>
        </div>
      {/each}

      {#if habitos.filter(h => habitoActivoHoy(h)).length === 0}
        <div class="text-center py-12 text-text_secondary">
          <p class="text-4xl mb-4">😴</p>
          <p>No tienes hábitos programados para hoy</p>
          <a href="/habitos" class="text-accent hover:underline mt-2 inline-block">
            Gestionar hábitos →
          </a>
        </div>
      {/if}
    </div>
  {/if}
</div>
