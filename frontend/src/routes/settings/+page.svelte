<script lang="ts">
  import { onMount } from 'svelte';
  import { obtenerUsuarioActual, updateUsuario } from '$lib/api';
  import { authStore } from '$lib/stores/auth.svelte';

  // Configuración del usuario
  let nombreUsuario = $state("");
  let email = $state("");
  let verFuturo = $state(false);
  let notificaciones = $state(true);
  let recordatorios = $state(true);
  let horaRecordatorio = $state("08:00");
  let temaOscuro = $state(true);
  let saving = $state(false);
  let saved = $state(false);
  let loading = $state(true);

  onMount(async () => {
    try {
      const usuario = authStore.user || await obtenerUsuarioActual();
      nombreUsuario = usuario.nombre;
      email = usuario.email;
      verFuturo = usuario.ver_futuro;
      console.log('Usuario cargado, ver_futuro:', usuario.ver_futuro);
    } catch (error) {
      console.error('Error cargando usuario:', error);
    } finally {
      loading = false;
    }
  });

  async function toggleVerFuturo() {
    verFuturo = !verFuturo;
    try {
      const updatedUser = await updateUsuario({ ver_futuro: verFuturo });
      // Actualizar el authStore con el usuario actualizado
      authStore.setUser(updatedUser);
      console.log('ver_futuro guardado:', verFuturo);
    } catch (error) {
      console.error('Error guardando ver_futuro:', error);
      // Revertir si falla
      verFuturo = !verFuturo;
    }
  }

  async function handleSave() {
    saving = true;
    try {
      const updatedUser = await updateUsuario({
        nombre: nombreUsuario,
        email: email,
        ver_futuro: verFuturo
      });
      // Actualizar el authStore con el usuario actualizado
      authStore.setUser(updatedUser);
      saved = true;
      setTimeout(() => saved = false, 2000);
    } catch (error) {
      console.error('Error guardando:', error);
    } finally {
      saving = false;
    }
  }
</script>

<svelte:head>
  <title>Ajustes | Hábitos</title>
</svelte:head>

<div class="max-w-2xl mx-auto px-4 py-8 pb-24 md:pb-8">
  <h1 class="text-3xl font-bold text-text_primary mb-8">⚙️ Ajustes</h1>

  <div class="space-y-6">
    <!-- Perfil -->
    <section class="bg-bg_secondary border border-border rounded-lg p-6">
      <h2 class="text-xl font-semibold text-text_primary mb-4">👤 Perfil</h2>
      
      <div class="space-y-4">
        <div>
          <label for="nombre" class="block text-text_secondary text-sm mb-1">Nombre</label>
          <input
            id="nombre"
            type="text"
            bind:value={nombreUsuario}
            class="w-full bg-bg_input border border-border rounded px-3 py-2 text-text_primary focus:border-accent focus:outline-none"
          />
        </div>
        <div>
          <label for="email" class="block text-text_secondary text-sm mb-1">Email</label>
          <input
            id="email"
            type="email"
            bind:value={email}
            class="w-full bg-bg_input border border-border rounded px-3 py-2 text-text_primary focus:border-accent focus:outline-none"
          />
        </div>
      </div>
    </section>

    <!-- Progreso -->
    <section class="bg-bg_secondary border border-border rounded-lg p-6">
      <h2 class="text-xl font-semibold text-text_primary mb-4">📅 Progreso</h2>
      
      <div class="flex items-center justify-between">
        <div>
          <p class="text-text_primary">Puedo ver el futuro 🔮</p>
          <p class="text-text_secondary text-sm">Ver y editar registros de días futuros</p>
        </div>
        <button
          type="button"
          aria-label="Activar ver futuro"
          onclick={toggleVerFuturo}
          class="w-12 h-6 rounded-full transition-all cursor-pointer {verFuturo ? 'bg-accent' : 'bg-bg_input border border-border'}"
        >
          <div class="w-5 h-5 rounded-full bg-white shadow transition-transform {verFuturo ? 'translate-x-6' : 'translate-x-0.5'}"></div>
        </button>
      </div>
    </section>

    <!-- Notificaciones -->
    <section class="bg-bg_secondary border border-border rounded-lg p-6">
      <h2 class="text-xl font-semibold text-text_primary mb-4">🔔 Notificaciones</h2>
      
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-text_primary">Notificaciones push</p>
            <p class="text-text_secondary text-sm">Recibe alertas de tus hábitos</p>
          </div>
          <button
            type="button"
            aria-label="Activar notificaciones push"
            onclick={() => notificaciones = !notificaciones}
            class="w-12 h-6 rounded-full transition-all {notificaciones ? 'bg-success' : 'bg-bg_input border border-border'}"
          >
            <div class="w-5 h-5 rounded-full bg-white shadow transition-transform {notificaciones ? 'translate-x-6' : 'translate-x-0.5'}"></div>
          </button>
        </div>

        <div class="flex items-center justify-between">
          <div>
            <p class="text-text_primary">Recordatorios diarios</p>
            <p class="text-text_secondary text-sm">Te recordamos completar tus hábitos</p>
          </div>
          <button
            type="button"
            aria-label="Activar recordatorios diarios"
            onclick={() => recordatorios = !recordatorios}
            class="w-12 h-6 rounded-full transition-all {recordatorios ? 'bg-success' : 'bg-bg_input border border-border'}"
          >
            <div class="w-5 h-5 rounded-full bg-white shadow transition-transform {recordatorios ? 'translate-x-6' : 'translate-x-0.5'}"></div>
          </button>
        </div>

        {#if recordatorios}
          <div>
            <label for="hora" class="block text-text_secondary text-sm mb-1">Hora del recordatorio</label>
            <input
              id="hora"
              type="time"
              bind:value={horaRecordatorio}
              class="bg-bg_input border border-border rounded px-3 py-2 text-text_primary focus:border-accent focus:outline-none"
            />
          </div>
        {/if}
      </div>
    </section>

    <!-- Apariencia -->
    <section class="bg-bg_secondary border border-border rounded-lg p-6">
      <h2 class="text-xl font-semibold text-text_primary mb-4">🎨 Apariencia</h2>
      
      <div class="flex items-center justify-between">
        <div>
          <p class="text-text_primary">Tema oscuro</p>
          <p class="text-text_secondary text-sm">Usar colores oscuros</p>
        </div>
        <button
          type="button"
          aria-label="Activar tema oscuro"
          onclick={() => temaOscuro = !temaOscuro}
          class="w-12 h-6 rounded-full transition-all {temaOscuro ? 'bg-success' : 'bg-bg_input border border-border'}"
        >
          <div class="w-5 h-5 rounded-full bg-white shadow transition-transform {temaOscuro ? 'translate-x-6' : 'translate-x-0.5'}"></div>
        </button>
      </div>
    </section>

    <!-- Datos -->
    <section class="bg-bg_secondary border border-border rounded-lg p-6">
      <h2 class="text-xl font-semibold text-text_primary mb-4">💾 Datos</h2>
      
      <div class="space-y-3">
        <button class="w-full py-2 px-4 rounded border border-border text-text_secondary hover:border-accent hover:text-accent transition-colors text-left">
          📤 Exportar datos
        </button>
        <button class="w-full py-2 px-4 rounded border border-border text-text_secondary hover:border-accent hover:text-accent transition-colors text-left">
          📥 Importar datos
        </button>
        <button class="w-full py-2 px-4 rounded border border-accent/50 text-accent hover:bg-accent/10 transition-colors text-left">
          🗑️ Eliminar todos los datos
        </button>
      </div>
    </section>

    <!-- Guardar -->
    <button
      onclick={handleSave}
      disabled={saving}
      class="w-full py-3 px-4 rounded bg-accent text-white font-bold hover:bg-accent/80 transition-colors disabled:opacity-50"
    >
      {#if saving}
        Guardando...
      {:else if saved}
        ✓ Guardado
      {:else}
        Guardar cambios
      {/if}
    </button>
  </div>
</div>
