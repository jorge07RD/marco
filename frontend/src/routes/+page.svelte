<script lang="ts">
  import { onMount } from 'svelte';
  import {
    getMyHabitos,
    getCurrentUser,
    getRegistroPorFecha,
    toggleProgreso,
    type Habito,
    type Usuario,
    type RegistroConProgresos,
    type ProgresoHabito
  } from '$lib/api';
  import { authStore } from '$lib/stores/auth.svelte';
  import { goto } from '$app/navigation';

  let habitos = $state<Habito[]>([]);
  let usuario = $state<Usuario | null>(null);
  let registro = $state<RegistroConProgresos | null>(null);
  let loading = $state(true);
  let error = $state<string | null>(null);

  // Fecha seleccionada - iniciar con hoy
  let fechaActual = $state(new Date());

  // Estado para animaciones y notificaciones
  let sacudir = $state(false);
  let notificacion = $state<string | null>(null);

  const diasSemanaCorto = ['DOM', 'LUN', 'MAR', 'MIÉ', 'JUE', 'VIE', 'SÁB'];
  const diasSemanaLetra = ['D', 'L', 'M', 'X', 'J', 'V', 'S'];

  function mostrarNotificacion(mensaje: string) {
    notificacion = mensaje;
    sacudir = true;
    setTimeout(() => sacudir = false, 500);
    setTimeout(() => notificacion = null, 3000);
  }

  onMount(async () => {
    await cargarDatos();
  });

  async function cargarDatos() {
    try {
      loading = true;
      error = null;

      // Verificar que el usuario esté autenticado
      if (!authStore.isAuthenticated) {
        goto('/login');
        return;
      }

      // Cargar usuario actual y hábitos
      [usuario, habitos] = await Promise.all([
        getCurrentUser(),
        getMyHabitos()
      ]);

      // Actualizar el store con los datos más recientes del usuario
      if (usuario) {
        authStore.updateUsuario(usuario);
      }

      // Cargar registro del día
      await cargarRegistro();
    } catch (e) {
      error = e instanceof Error ? e.message : 'Error cargando datos';
      // Si hay error 401, redirigir al login
      if (e instanceof Error && e.message.includes('401')) {
        authStore.logout();
        goto('/login');
      }
    } finally {
      loading = false;
    }
  }

  async function cargarRegistro() {
    if (!usuario) return;

    try {
      const fechaStr = getFechaISO();
      registro = await getRegistroPorFecha(usuario.id, fechaStr);
      error = null;
    } catch (e) {
      if (e instanceof Error && e.message.includes('futuro')) {
        // Para errores de futuro, usar notificación en lugar de error permanente
        mostrarNotificacion("🔮 No puedes ver el futuro. Actívalo en Ajustes.");
        registro = null;
      } else {
        throw e;
      }
    }
  }

  async function cambiarDia(delta: number) {
    const nueva = new Date(fechaActual);
    nueva.setDate(nueva.getDate() + delta);
    
    // Verificar si es futuro y el usuario no puede ver futuro
    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);
    nueva.setHours(0, 0, 0, 0);
    
    if (nueva > hoy && !usuario?.ver_futuro) {
      mostrarNotificacion("🔮 No puedes ver el futuro. Actívalo en Ajustes.");
      return;
    }
    
    error = null;
    fechaActual = nueva;
    loading = true;
    await cargarRegistro();
    loading = false;
  }

  function esHoy(): boolean {
    const hoy = new Date();
    return fechaActual.toDateString() === hoy.toDateString();
  }

  function esFuturo(): boolean {
    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);
    const fecha = new Date(fechaActual);
    fecha.setHours(0, 0, 0, 0);
    return fecha > hoy;
  }

  function getDiaSemana(): string {
    return diasSemanaCorto[fechaActual.getDay()];
  }

  function getDiaLetra(): string {
    return diasSemanaLetra[fechaActual.getDay()];
  }

  function getFechaFormateada(): string {
    return fechaActual.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' });
  }

  function getFechaISO(): string {
    // Usar fecha local, no UTC para evitar problemas de zona horaria
    const year = fechaActual.getFullYear();
    const month = String(fechaActual.getMonth() + 1).padStart(2, '0');
    const day = String(fechaActual.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  function getHabitoById(id: number): Habito | undefined {
    return habitos.find(h => h.id === id);
  }

  async function handleToggleProgreso(progreso: ProgresoHabito) {
    try {
      const updated = await toggleProgreso(progreso.id);
      // Actualizar el progreso en el registro local
      if (registro) {
        registro = {
          ...registro,
          progresos: registro.progresos.map(p => 
            p.id === updated.id ? updated : p
          )
        };
      }
    } catch (e) {
      error = e instanceof Error ? e.message : 'Error al actualizar progreso';
    }
  }

  function getCompletados(): number {
    return registro?.progresos.filter(p => p.completado).length || 0;
  }

  function getTotalHabitos(): number {
    return registro?.progresos.length || 0;
  }

  function getPorcentaje(): number {
    const total = getTotalHabitos();
    return total > 0 ? Math.round((getCompletados() / total) * 100) : 0;
  }
</script>

<svelte:head>
  <title>Progreso | Hábitos</title>
</svelte:head>

<div class="max-w-xl mx-auto px-4 py-6 pb-24 md:pb-8">
  
  <!-- Notificación flotante -->
  {#if notificacion}
    <div class="fixed top-4 left-1/2 -translate-x-1/2 z-50 animate-slide-in-down">
      <div class="bg-accent text-white px-6 py-3 rounded-lg shadow-lg font-medium">
        {notificacion}
      </div>
    </div>
  {/if}
  
  <!-- PROGRESO DIARIO - Navegación de fecha -->
  <fieldset class="border border-border bg-[#1B1B2F] rounded-lg p-4 mb-6 {sacudir ? 'animate-shake' : ''}">
    <legend class="text-accent text-xs font-bold px-2">PROGRESO DIARIO</legend>
    
    <div class="flex items-center justify-between">
      <button 
        onclick={() => cambiarDia(-1)}
        class="w-10 h-10 flex items-center justify-center text-text_secondary bg-[#121127] hover:text-accent transition-colors border border-border rounded"
      >
        ◀
      </button>
      
      <div class="text-center">
        <div class="flex items-center justify-center gap-2">
          <span class="text-text_secondary">📅</span>
          <span class="text-2xl font-bold text-text_primary">{getDiaSemana()}</span>
          {#if esHoy()}
            <span class="bg-success text-black text-xs font-bold px-2 py-0.5 rounded">HOY</span>
          {/if}
        </div>
        <p class="text-text_secondary text-sm mt-1">{getFechaFormateada()}</p>
      </div>
      
      <button 
        onclick={() => cambiarDia(1)}
        class="w-10 h-10 flex items-center justify-center text-text_secondary hover:text-accent transition-colors border bg-[#121127] border-border rounded"
      >
        ▶
      </button>
    </div>
  </fieldset>

  <!-- PROGRESO - Resumen -->
  <div class="flex items-center justify-center  gap-4 mb-6">
    <span class="text-text_secondary text-sm">📊 PROGRESO:</span>
    <span class="bg-bg_secondary border border-border text-text_primary text-sm px-3 py-1 rounded">
      {getCompletados()}/{getTotalHabitos()}
    </span>
    <span class="bg-accent text-white text-sm font-bold px-3 py-1 rounded">
      {getPorcentaje()}%
    </span>
  </div>
  
  <!-- Barra de progreso general -->
  <div class="w-full bg-bg_input rounded-full h-3 mb-6 overflow-hidden {getCompletados() === getTotalHabitos() && getTotalHabitos() > 0 ? 'neon-glow' : ''}">
    <div 
      class="h-3 rounded-full transition-all duration-500 {getCompletados() === getTotalHabitos() && getTotalHabitos() > 0 ? 'neon-gradient animate-neon-on' : 'bg-accent'}"
      style="width: {getPorcentaje()}%"
    ></div>
  </div>

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
  {:else if registro}
    <!-- HÁBITOS - Lista -->
    <fieldset class="border border-border bg-[#1B1B2F]  rounded-lg p-4">
      <legend class="text-accent text-xs font-bold px-2">HÁBITOS</legend>
      
      <div class="space-y-2">
        {#each registro.progresos as progreso, i (progreso.id)}
          {@const habito = getHabitoById(progreso.habito_id)}
          {#if habito}
            <button
              onclick={() => handleToggleProgreso(progreso)}
              class="w-full bg-bg_secondary border border-border bg-[#121127] slide-in-blurred-bottom rounded-lg p-3 flex items-center gap-3 hover:border-accent/50 transition-all text-left"
              style="animation-delay: {i * 0.1}s;"
            >
              <!-- Indicador de color -->
              <div 
                class="w-1.5 h-10 rounded-full shrink-0"
                style="background-color: {habito.color}"
              ></div>
              
              <!-- Info del hábito -->
              <div class="flex-1 min-w-0">
                <h3 class="font-semibold text-text_primary truncate text-sm">
                  {habito.nombre}
                </h3>
                <p class="text-xs flex items-center gap-1">
                  <span class="text-text_secondary">━━</span>
                  <span class="text-warning">●</span>
                  <span class="text-text_secondary">{habito.meta_diaria} {habito.unidad_medida}</span>
                </p>
              </div>
              
              <!-- Radio button de completado -->
              <div class="shrink-0">
                {#if progreso.completado}
                  <div class="w-5 h-5 rounded-full bg-success flex items-center justify-center">
                    <span class="text-black text-xs">✓</span>
                  </div>
                {:else}
                  <div class="w-5 h-5 rounded-full border-2 border-text_secondary"></div>
                {/if}
              </div>
            </button>
          {/if}
        {/each}

        {#if registro.progresos.length === 0}
          <div class="text-center py-8 text-text_secondary">
            <p class="text-3xl mb-2">😴</p>
            <p class="text-sm">No hay hábitos para este día</p>
            <a href="/habitos" class="text-accent hover:underline text-sm mt-2 inline-block">
              Gestionar hábitos →
            </a>
          </div>
        {/if}
      </div>
    </fieldset>
  {:else}
    <div class="text-center py-8 text-text_secondary">
      <p class="text-3xl mb-2">📅</p>
      <p class="text-sm">No hay registro para esta fecha</p>
    </div>
  {/if}
</div>

<style>
  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
    20%, 40%, 60%, 80% { transform: translateX(5px); }
  }
  
  @keyframes slide-in-down {
    0% { 
      opacity: 0;
      transform: translateX(-50%) translateY(-20px);
    }
    100% { 
      opacity: 1;
      transform: translateX(-50%) translateY(0);
    }
  }
  
  :global(.animate-shake) {
    animation: shake 0.5s ease-in-out;
  }
  
  :global(.animate-slide-in-down) {
    animation: slide-in-down 0.3s ease-out;
  }
  
  /* Neon Gradient Effect */
  :global(.neon-gradient) {
    background: linear-gradient(90deg, #8b5cf6, #e94560, #ff6b35, #e94560, #8b5cf6);
    background-size: 200% 100%;
    animation: neon-flow 3s linear infinite;
  }
  
  :global(.neon-glow) {
    box-shadow: 
      0 0 5px rgba(233, 69, 96, 0.5),
      0 0 10px rgba(139, 92, 246, 0.4),
      0 0 15px rgba(255, 107, 53, 0.3);
    animation: neon-pulse 1.5s ease-in-out infinite alternate;
  }
  
  :global(.animate-neon-on) {
    animation: neon-flicker 0.8s ease-out forwards, neon-flow 3s linear infinite 0.8s;
  }
  
  @keyframes neon-flow {
    0% { background-position: 0% 50%; }
    100% { background-position: 200% 50%; }
  }
  
  @keyframes neon-pulse {
    0% {
      box-shadow: 
        0 0 5px rgba(233, 69, 96, 0.5),
        0 0 10px rgba(139, 92, 246, 0.4);
    }
    100% {
      box-shadow: 
        0 0 10px rgba(233, 69, 96, 0.8),
        0 0 20px rgba(139, 92, 246, 0.6),
        0 0 30px rgba(255, 107, 53, 0.5);
    }
  }
  
  @keyframes neon-flicker {
    0% {
      opacity: 0.2;
      filter: brightness(0.3);
    }
    10% {
      opacity: 0.2;
      filter: brightness(0.3);
    }
    15% {
      opacity: 0.4;
      filter: brightness(0.5);
    }
    20% {
      opacity: 0.2;
      filter: brightness(0.3);
    }
    30% {
      opacity: 0.3;
      filter: brightness(0.4);
    }
    40% {
      opacity: 0.2;
      filter: brightness(0.3);
    }
    50% {
      opacity: 0.5;
      filter: brightness(0.6);
    }
    55% {
      opacity: 0.3;
      filter: brightness(0.4);
    }
    70% {
      opacity: 1;
      filter: brightness(1.5);
    }
    100% {
      opacity: 1;
      filter: brightness(1);
    }
  }
</style>
