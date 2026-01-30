<script lang="ts">
  import { onMount } from "svelte";
  import {
    getHabitos,
    deleteHabito,
    getRegistroPorFecha,
    verificarRegistroExiste,
    deleteRegistro,
    type Habito,
  } from "$lib/api";
  import { authStore } from "$lib/stores/auth.svelte";
  import HabitoForm from "$lib/components/HabitoForm.svelte";
  import ConfirmModal from "$lib/components/ConfirmModal.svelte";

  let habitos = $state<Habito[]>([]);
  let loading = $state(true);
  let error = $state<string | null>(null);
  let creandoRegistro = $state(false);
  let registroExiste = $state(true);
  let totalProgresosRegistro = $state(0);
  let mensajeRegistro = $state<string | null>(null);

  // Modal states
  let showForm = $state(false);
  let editingHabito = $state<Habito | null>(null);
  let showDeleteConfirm = $state(false);
  let habitoToDelete = $state<Habito | null>(null);

  onMount(async () => {
    await loadHabitos();
    await verificarRegistroHoy();
  });

  // Verificar si ya existe un registro para hoy
  async function verificarRegistroHoy() {
    try {
      const fecha = getFechaISO();
      const resultado = await verificarRegistroExiste(fecha);
      
      if (resultado.existe) {
        totalProgresosRegistro = resultado.total_progresos;
        // Verificar si todos los hábitos del día están en el registro
        const habitosHoy = getHabitosHoy();
        registroExiste = resultado.total_progresos >= habitosHoy.length;
      } else {
        registroExiste = false;
        totalProgresosRegistro = 0;
      }
    } catch {
      registroExiste = false;
      totalProgresosRegistro = 0;
    }
  }

    // Obtiene los hábitos que faltan por agregar al registro de hoy
    function getHabitosFaltantesHoy(): Habito[] {
      const habitosHoy = getHabitosHoy();
      // Si no hay registro, todos los hábitos de hoy faltan
      if (!registroExiste || totalProgresosRegistro === 0) {
        return habitosHoy;
      }
      // Si el registro tiene menos progresos que hábitos de hoy, hay faltantes
      if (totalProgresosRegistro < habitosHoy.length) {
        return habitosHoy; // Mostramos todos porque no sabemos cuáles faltan sin crear el registro
      }
      return [];
    }
    

  async function loadHabitos() {
    try {
      loading = true;
      error = null;
      habitos = await getHabitos();
    } catch (e) {
      error = e instanceof Error ? e.message : "Error cargando hábitos";
    } finally {
      loading = false;
    }
  }

  function openCreateForm() {
    editingHabito = null;
    showForm = true;
  }

  function openEditForm(habito: Habito) {
    editingHabito = habito;
    showForm = true;
  }

  function closeForm() {
    showForm = false;
    editingHabito = null;
  }

  function handleSave(savedHabito: Habito) {
    if (editingHabito) {
      habitos = habitos.map((h) => (h.id === savedHabito.id ? savedHabito : h));
    } else {
      habitos = [...habitos, savedHabito];
    }
    closeForm();
  }

  function confirmDelete(habito: Habito) {
    habitoToDelete = habito;
    showDeleteConfirm = true;
  }

  async function handleDelete() {
    if (!habitoToDelete) return;
    
    // Animar la tarjeta antes de eliminar
    const card = document.getElementById(`card-${habitoToDelete.id}`);
    if (card) {
      card.classList.add('slide-out-blurred-top');
      // Esperar a que termine la animación
      await new Promise(resolve => setTimeout(resolve, 450));
    }
    
    try {
      await deleteHabito(habitoToDelete.id);
      habitos = habitos.filter((h) => h.id !== habitoToDelete!.id);
    } catch (e) {
      error = e instanceof Error ? e.message : "Error eliminando hábito";
    }
    showDeleteConfirm = false;
    habitoToDelete = null;
  }

  function cancelDelete() {
    showDeleteConfirm = false;
    habitoToDelete = null;
  }

  function parseDias(diasJson: string): string[] {
    try {
      return JSON.parse(diasJson);
    } catch {
      return [];
    }
  }

  let diassemana: string[] = ["L", "M", "X", "J", "V", "S", "D"];

  // Obtener la fecha actual en formato ISO
  function getFechaISO(): string {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  // Obtener la letra del día actual
  function getDiaActual(): string {
    const dias = ['D', 'L', 'M', 'X', 'J', 'V', 'S'];
    return dias[new Date().getDay()];
  }

  // Contar hábitos activos para hoy
  function getHabitosHoy(): Habito[] {
    const diaActual = getDiaActual();
    return habitos.filter(h => {
      if (!h.activo) return false;
      try {
        const dias = JSON.parse(h.dias);
        return dias.includes(diaActual);
      } catch {
        return false;
      }
    });
  }

  // Crear/Recrear registro del día (elimina el existente y crea uno nuevo)
  async function crearRegistroHoy() {
    creandoRegistro = true;
    mensajeRegistro = null;
    try {
      const fecha = getFechaISO();
      
      // Verificar si existe un registro y eliminarlo
      const verificacion = await verificarRegistroExiste(fecha);
      if (verificacion.existe && verificacion.registro_id) {
        await deleteRegistro(verificacion.registro_id);
      }
      
      // Crear nuevo registro con todos los hábitos actuales
      const registro = await getRegistroPorFecha(fecha);
      registroExiste = true;
      totalProgresosRegistro = registro.progresos.length;
      mensajeRegistro = `✅ Registro ${verificacion.existe ? 'actualizado' : 'creado'} con ${registro.progresos.length} hábitos para hoy`;
      // Ocultar mensaje después de 3 segundos
      setTimeout(() => {
        mensajeRegistro = null;
      }, 3000);
    } catch (e) {
      mensajeRegistro = `❌ ${e instanceof Error ? e.message : 'Error al crear registro'}`;
    } finally {
      creandoRegistro = false;
    }
  }

  function handleDeleteMouseEnter(habitoId: number) {
    const card = document.getElementById(`card-${habitoId}`);
    if (card) {
      card.classList.remove('slide-in-blurred-right');
      card.classList.add("vibrate");
    }
  }

  function handleDeleteMouseLeave(habitoId: number) {
    const card = document.getElementById(`card-${habitoId}`);
    if (card) card.classList.remove("vibrate");
  }
</script>

<svelte:head>
  <title>Hábitos | Gestionar</title>
</svelte:head>

<div class="max-w-4xl mx-auto px-4 py-8 pb-24 md:pb-8">
  <div class="flex justify-between items-center mb-4">
    <h1 class="text-3xl font-bold text-text_primary">🎯 Mis Hábitos</h1>
    <button
      onclick={openCreateForm}
      class="hidden md:flex items-center gap-2 bg-accent hover:bg-accent/80 text-white font-bold py-2 px-4 rounded-lg transition-colors"
    >
      <span class="text-xl">+</span> Nuevo Hábito
    </button>
  </div>

  <!-- Botón para crear/actualizar registro del día -->
  {#if !loading && habitos.length > 0}
    {@const habitosHoy = getHabitosHoy()}
    {#if habitosHoy.length > 0}
      {@const necesitaActualizar = !registroExiste || totalProgresosRegistro < habitosHoy.length}
      <div class="mb-6 p-4 bg-[#1B1B2F] border border-border rounded-lg">
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div>
            <p class="text-text_primary font-medium">
              📅 Hoy tienes <span class="text-accent font-bold">{habitosHoy.length}</span> hábitos programados
              {#if registroExiste && totalProgresosRegistro < habitosHoy.length}
                <span class="text-warning text-sm">({habitosHoy.length - totalProgresosRegistro} nuevos)</span>
              {/if}
            </p>
            <p class="text-text_secondary text-sm">
              {habitosHoy.map(h => h.nombre).join(', ')}
            </p>
          </div>
          <button
            onclick={crearRegistroHoy}
            disabled={creandoRegistro}
            class="flex items-center gap-2 {necesitaActualizar ? 'bg-success hover:bg-success/80' : 'bg-accent hover:bg-accent/80'} disabled:opacity-50 disabled:cursor-not-allowed text-bg_primary font-bold py-2 px-4 rounded-lg transition-colors whitespace-nowrap"
          >
            {#if creandoRegistro}
              <span class="animate-spin">⏳</span> Procesando...
            {:else if registroExiste}
              <span>🔄</span> Actualizar registro
            {:else}
              <span>📝</span> Crear registro de hoy
            {/if}
          </button>
        </div>
        {#if mensajeRegistro}
          <p class="mt-3 text-sm {mensajeRegistro.startsWith('✅') ? 'text-success' : 'text-accent'}">
            {mensajeRegistro}
          </p>
        {/if}
      </div>
    {/if}
  {/if}

  {#if loading}
    <div class="flex justify-center items-center py-20">
      <div class="radar-spinner">
        <div class="circle">
          <div class="circle-inner-container">
            <div class="circle-inner"></div>
          </div>
        </div>

        <div class="circle">
          <div class="circle-inner-container">
            <div class="circle-inner"></div>
          </div>
        </div>

        <div class="circle">
          <div class="circle-inner-container">
            <div class="circle-inner"></div>
          </div>
        </div>

        <div class="circle">
          <div class="circle-inner-container">
            <div class="circle-inner"></div>
          </div>
        </div>
      </div>
    </div>
  {:else if error}
    <div class="bg-accent/20 border border-accent text-accent px-4 py-3 rounded-lg mb-4">
      {error}
    </div>
  {:else if habitos.length === 0}
    <div class="text-center py-20 text-text_secondary">
      <p class="text-6xl mb-4">🌱</p>
      <p class="text-xl mb-2">No tienes hábitos aún</p>
      <p>Crea tu primer hábito para comenzar</p>
    </div>
  {:else}
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      {#each habitos as habito, i (habito.id)}
        <div
          id="card-{habito.id}"
          class="bg-[#1B1B2F] border border-border rounded-lg p-3 flex items-center flex-col  justify-start gap-1 slide-in-blurred-right"
          style="animation-delay: {i * 0.1}s;"
        >
          <div class="flex flex-row w-full items-center gap-1">
            <!-- indicador de color del hábito -->
            <div
              class="w-2 rounded-xs mx-1 min-h-full self-stretch"
              style="background-color: {habito.color}"
            ></div>
            <!-- nombre del hábito -->
            <span class="text-[#ffff] justify-center text-sm truncate font-bold"
              >{habito.nombre}</span
            >
            <!-- estado del hábito -->
            {#if habito.activo}
              <div
                class="ml-auto grid w-auto text-[#00ff88] border border-[#00ff88] text-nowrap justify-center text-xs items-center p-2 rounded-xs bg-[#121127]"
              >
                ● ON
              </div>
            {:else}
              <div
                class="ml-auto grid w-auto text-[#ff4d4d] border border-[#ff4d4d] text-nowrap justify-center text-xs items-center p-2 rounded-xs bg-[#121127]"
              >
                ● OFF
              </div>
            {/if}
          </div>
          <div
            class="mr-auto grid w-auto text-border border border-border justify-center text-xs p-2 rounded-sm bg-[#121127]"
          >
            Categoría {habito.categoria_id}
          </div>
          <!-- meta diaria -->
          <div
            class="w-full text-[#533483] border border-[#533483] flex flex-col justify-center text-xs p-2 mt-2 rounded-sm bg-[#121127]"
          >
            <span class="font-bold">meta diaria</span>
            <span class="float-right text-green-500"
              >{habito.meta_diaria}
              <span class="text-border">{habito.unidad_medida}</span>
            </span>
          </div>
          <span class="text-border text-xs mr-auto">dias:</span>
          <div class="w-full flex justify-start items-center flex-wrap gap-1">
            {#each diassemana as dia}
              {#if parseDias(habito.dias).includes(dia)}
              <div
              class="w-6 h-6 flex justify-center items-center rounded-md bg-[#D54059] border border-[#D54059] text-[#ffff] text-xs"
              >
              {dia}
            </div>
            {:else}
            <div
              class="w-6 h-6 flex justify-center items-center rounded-md bg-[#121127] border border-border text-border text-xs"
            >
              {dia}
            </div>
              {/if}
            {/each}
          </div>
          <div class="ml-auto flex gap-2 mt-3">
            <button
              class="w-6 h-6 flex justify-center items-center rounded-xs bg-[#121127] border border-border text-border text-xs hover:border-accent hover:text-accent transition-colors"
              onclick={() => openEditForm(habito)}
            >
              <svg width="50" height="50" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M8.32955 18.8728L3 21L5.1272 15.6704M8.32955 18.8728L7.90348 16.0959L5.1272 15.6704M8.32955 18.8728L13.7476 13.4547M5.1272 15.6704L16.2021 4.59552M19.4045 7.79787L16.2021 4.59552M19.4045 7.79787L20.3988 6.80353C21.2831 5.91922 21.2831 4.48548 20.3988 3.60118V3.60118C19.5145 2.71687 18.0808 2.71687 17.1965 3.60118L16.2021 4.59552M19.4045 7.79787L16.576 10.6263" stroke="#f5c211" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path>
              </svg>
            </button>
            <button
              class="w-6 h-6 flex justify-center items-center rounded-xs bg-[#c70000] border border-border text-[#ffff] text-xs"
              onclick={() => confirmDelete(habito)}
              onmouseenter={() => handleDeleteMouseEnter(habito.id)}
              onmouseleave={() => handleDeleteMouseLeave(habito.id)}
            >
              X
            </button>
          </div>
        </div>
      {/each}
    </div>
  {/if}

  <!-- Floating Action Button (móvil) -->
  <button
    onclick={openCreateForm}
    class="md:hidden fixed bottom-20 right-6 w-14 h-14 bg-accent hover:bg-accent/80 text-white text-3xl rounded-full shadow-lg shadow-accent/30 flex items-center justify-center transition-all hover:scale-110 z-40"
  >
    +
  </button>
</div>

<!-- Modals -->
{#if showForm}
  <HabitoForm
    habito={editingHabito}
    usuarioId={1}
    onClose={closeForm}
    onSave={handleSave}
  />
{/if}

{#if showDeleteConfirm && habitoToDelete}
  <ConfirmModal
    title="Eliminar hábito"
    message="¿Estás seguro de que quieres eliminar '{habitoToDelete.nombre}'? Esta acción no se puede deshacer."
    confirmText="Eliminar"
    cancelText="Cancelar"
    onConfirm={handleDelete}
    onCancel={cancelDelete}
  />
{/if}

<style>
  /* Radar Spinner Animation */
  .radar-spinner,
  .radar-spinner * {
    box-sizing: border-box;
  }

  .radar-spinner {
    height: 60px;
    width: 60px;
    position: relative;
  }

  .radar-spinner .circle {
    position: absolute;
    height: 100%;
    width: 100%;
    top: 0;
    left: 0;
    animation: radar-spinner-animation 2s infinite;
  }

  .radar-spinner .circle:nth-child(1) {
    padding: calc(60px * 5 * 2 * 0 / 110);
    animation-delay: 300ms;
  }

  .radar-spinner .circle:nth-child(2) {
    padding: calc(60px * 5 * 2 * 1 / 110);
    animation-delay: 300ms;
  }

  .radar-spinner .circle:nth-child(3) {
    padding: calc(60px * 5 * 2 * 2 / 110);
    animation-delay: 300ms;
  }

  .radar-spinner .circle:nth-child(4) {
    padding: calc(60px * 5 * 2 * 3 / 110);
    animation-delay: 0ms;
  }

  .radar-spinner .circle-inner,
  .radar-spinner .circle-inner-container {
    height: 100%;
    width: 100%;
    border-radius: 50%;
    border: calc(60px * 5 / 110) solid transparent;
  }

  .radar-spinner .circle-inner {
    border-left-color: #ff1d5e;
    border-right-color: #ff1d5e;
  }

  @keyframes radar-spinner-animation {
    50% {
      transform: rotate(180deg);
    }
    100% {
      transform: rotate(0deg);
    }
  }
</style>
