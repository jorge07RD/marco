<script lang="ts">
  import { onMount } from 'svelte';
  import { obtenerUsuarioActual, updateUsuario, getCategorias, crearCategoria, updateCategoria, deleteCategoria, verificarContrasena, eliminarTodosLosDatos, eliminarCuenta, logout, type Categoria } from '$lib/api';
  import { authStore } from '$lib/stores/auth.svelte';
  import ConfirmModal from '$lib/components/ConfirmModal.svelte';
  import {
    isPushSupported,
    getNotificationPermission,
    subscribeToPush,
    unsubscribeFromPush,
    hasActivePushSubscription,
    getNotificationPreferences,
    updateNotificationPreferences,
    sendTestNotification,
    TIMEZONES
  } from '$lib/pushNotifications';

  // Configuración del usuario
  let nombreUsuario = $state("");
  let email = $state("");
  let verFuturo = $state(false);
  let notificaciones = $state(false);
  let horaRecordatorio = $state("08:00");
  let timezone = $state("America/Santo_Domingo");
  let temaOscuro = $state(true);
  let saving = $state(false);
  let saved = $state(false);

  // Estados de notificaciones push
  let pushSupported = $state(false);
  let pushPermission = $state<NotificationPermission>('default');
  let pushSubscribed = $state(false);
  let pushLoading = $state(false);
  let pushError = $state<string | null>(null);
  let testingNotification = $state(false);
  let testResult = $state<{success: boolean; message: string} | null>(null);

  // Gestión de categorías
  let categorias = $state<Categoria[]>([]);
  let nuevaCategoria = $state("");
  let editandoCategoria = $state<Categoria | null>(null);
  let nombreCategoriaEdit = $state("");
  let categoriasLoading = $state(true);
  let showDeleteConfirm = $state(false);
  let categoriaToDelete = $state<Categoria | null>(null);

  // Estados para eliminar datos
  let showPasswordModal = $state(false);
  let passwordInput = $state("");
  let passwordError = $state("");
  let passwordVerified = $state(false);
  let showDeleteOptions = $state(false);
  let deletingData = $state(false);
  let deleteMessage = $state<string | null>(null);

  onMount(async () => {
    try {
      const usuario = authStore.user || await obtenerUsuarioActual();
      nombreUsuario = usuario.nombre;
      email = usuario.email;
      verFuturo = usuario.ver_futuro;
      console.log('Usuario cargado, ver_futuro:', usuario.ver_futuro);
    } catch (error) {
      console.error('Error cargando usuario:', error);
    }

    // Cargar categorías
    await cargarCategorias();

    // Inicializar estado de notificaciones push
    await initPushNotifications();
  });

  async function initPushNotifications() {
    pushSupported = isPushSupported();
    if (!pushSupported) return;

    pushPermission = getNotificationPermission();
    pushSubscribed = await hasActivePushSubscription();

    // Cargar preferencias del servidor
    const prefs = await getNotificationPreferences();
    if (prefs) {
      notificaciones = prefs.notificaciones_activas;
      horaRecordatorio = prefs.hora_recordatorio;
      timezone = prefs.zona_horaria;
    }
  }

  async function toggleNotificaciones() {
    if (pushLoading) return;
    pushLoading = true;
    pushError = null;
    testResult = null;

    try {
      if (!notificaciones) {
        // Activar notificaciones
        const success = await subscribeToPush();
        if (success) {
          notificaciones = true;
          pushSubscribed = true;
          await updateNotificationPreferences({ notificaciones_activas: true });
        } else {
          pushError = 'No se pudieron activar las notificaciones. Verifica los permisos del navegador.';
        }
      } else {
        // Desactivar notificaciones
        await unsubscribeFromPush();
        notificaciones = false;
        pushSubscribed = false;
        await updateNotificationPreferences({ notificaciones_activas: false });
      }
    } catch (error) {
      pushError = 'Error al cambiar el estado de las notificaciones';
      console.error(error);
    } finally {
      pushLoading = false;
    }
  }

  async function handleHoraChange(e: Event) {
    const target = e.target as HTMLInputElement;
    horaRecordatorio = target.value;
    await updateNotificationPreferences({ hora_recordatorio: horaRecordatorio });
  }

  async function handleZonaChange(e: Event) {
    const target = e.target as HTMLSelectElement;
    timezone = target.value;
    await updateNotificationPreferences({ zona_horaria: timezone });
  }

  async function handleTestNotification() {
    if (testingNotification) return;
    testingNotification = true;
    testResult = null;

    const result = await sendTestNotification();
    testResult = result;
    testingNotification = false;

    // Limpiar mensaje después de 5 segundos
    setTimeout(() => {
      testResult = null;
    }, 5000);
  }

  async function cargarCategorias() {
    try {
      categoriasLoading = true;
      categorias = await getCategorias();
    } catch (error) {
      console.error('Error cargando categorías:', error);
    } finally {
      categoriasLoading = false;
    }
  }

  async function handleCrearCategoria() {
    if (!nuevaCategoria.trim()) return;

    try {
      await crearCategoria(nuevaCategoria.trim());
      nuevaCategoria = "";
      await cargarCategorias();
    } catch (error) {
      console.error('Error creando categoría:', error);
    }
  }

  function iniciarEdicion(categoria: Categoria) {
    editandoCategoria = categoria;
    nombreCategoriaEdit = categoria.nombre;
  }

  function cancelarEdicion() {
    editandoCategoria = null;
    nombreCategoriaEdit = "";
  }

  async function handleActualizarCategoria(id: number) {
    if (!nombreCategoriaEdit.trim()) return;

    try {
      await updateCategoria(id, nombreCategoriaEdit.trim());
      editandoCategoria = null;
      nombreCategoriaEdit = "";
      await cargarCategorias();
    } catch (error) {
      console.error('Error actualizando categoría:', error);
    }
  }

  function confirmarEliminar(categoria: Categoria) {
    categoriaToDelete = categoria;
    showDeleteConfirm = true;
  }

  async function handleEliminarCategoria() {
    if (!categoriaToDelete) return;

    try {
      await deleteCategoria(categoriaToDelete.id);
      showDeleteConfirm = false;
      categoriaToDelete = null;
      await cargarCategorias();
    } catch (error) {
      console.error('Error eliminando categoría:', error);
      showDeleteConfirm = false;
      categoriaToDelete = null;
    }
  }

  function cancelarEliminar() {
    showDeleteConfirm = false;
    categoriaToDelete = null;
  }

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

  // Funciones para eliminar datos
  function iniciarEliminacionDatos() {
    showPasswordModal = true;
    passwordInput = "";
    passwordError = "";
    passwordVerified = false;
  }

  async function verificarPassword() {
    passwordError = "";
    try {
      const esValida = await verificarContrasena(passwordInput);
      if (esValida) {
        passwordVerified = true;
        showPasswordModal = false;
        showDeleteOptions = true;
        passwordInput = "";
      } else {
        passwordError = "Contraseña incorrecta";
      }
    } catch (error) {
      passwordError = "Error al verificar contraseña";
    }
  }

  function cancelarPassword() {
    showPasswordModal = false;
    passwordInput = "";
    passwordError = "";
  }

  function cancelarDeleteOptions() {
    showDeleteOptions = false;
    passwordVerified = false;
  }

  async function handleEliminarSoloRegistros() {
    deletingData = true;
    deleteMessage = null;
    try {
      await eliminarTodosLosDatos();
      deleteMessage = "✅ Todos los registros han sido eliminados";
      setTimeout(() => {
        deleteMessage = null;
        showDeleteOptions = false;
        passwordVerified = false;
      }, 3000);
    } catch (error) {
      deleteMessage = `❌ ${error instanceof Error ? error.message : 'Error al eliminar datos'}`;
    } finally {
      deletingData = false;
    }
  }

  async function handleEliminarCuenta() {
    deletingData = true;
    deleteMessage = null;
    try {
      await eliminarCuenta();
      // Cerrar sesión automáticamente
      logout();
    } catch (error) {
      deleteMessage = `❌ ${error instanceof Error ? error.message : 'Error al eliminar cuenta'}`;
      deletingData = false;
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

    <!-- Categorías -->
    <section class="bg-bg_secondary border border-border rounded-lg p-6">
      <h2 class="text-xl font-semibold text-text_primary mb-4">📁 Categorías</h2>

      <!-- Formulario para crear categoría -->
      <form onsubmit={(e) => { e.preventDefault(); handleCrearCategoria(); }} class="mb-4">
        <div class="flex gap-2">
          <input
            type="text"
            bind:value={nuevaCategoria}
            placeholder="Nueva categoría..."
            class="flex-1 bg-bg_input border border-border rounded px-3 py-2 text-text_primary placeholder-text_secondary/50 focus:border-accent focus:outline-none"
          />
          <button
            type="submit"
            class="bg-accent text-white px-4 py-2 rounded hover:bg-accent/80 transition-colors font-medium"
          >
            Añadir
          </button>
        </div>
      </form>

      <!-- Lista de categorías -->
      {#if categoriasLoading}
        <p class="text-text_secondary text-sm">Cargando categorías...</p>
      {:else if categorias.length === 0}
        <p class="text-text_secondary text-sm">No hay categorías. Crea una para empezar.</p>
      {:else}
        <div class="space-y-2">
          {#each categorias as categoria (categoria.id)}
            <div class="bg-bg_input border border-border rounded p-3 flex items-center justify-between">
              {#if editandoCategoria?.id === categoria.id}
                <!-- Modo edición -->
                <input
                  type="text"
                  bind:value={nombreCategoriaEdit}
                  class="flex-1 bg-bg_secondary border border-accent rounded px-2 py-1 text-text_primary focus:outline-none mr-2"
                  autofocus
                />
                <div class="flex gap-2">
                  <button
                    onclick={() => handleActualizarCategoria(categoria.id)}
                    class="text-success hover:text-success/80 text-sm font-medium"
                  >
                    Guardar
                  </button>
                  <button
                    onclick={cancelarEdicion}
                    class="text-text_secondary hover:text-white text-sm font-medium"
                  >
                    Cancelar
                  </button>
                </div>
              {:else}
                <!-- Modo vista -->
                <span class="text-text_primary">{categoria.nombre}</span>
                <div class="flex gap-2">
                  <button
                    onclick={() => iniciarEdicion(categoria)}
                    class="text-warning hover:text-warning/80 text-sm font-medium"
                  >
                    Editar
                  </button>
                  <button
                    onclick={() => confirmarEliminar(categoria)}
                    class="text-accent hover:text-accent/80 text-sm font-medium"
                  >
                    Eliminar
                  </button>
                </div>
              {/if}
            </div>
          {/each}
        </div>
      {/if}
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

      {#if !pushSupported}
        <p class="text-text_secondary text-sm">
          Tu navegador no soporta notificaciones push.
        </p>
      {:else}
        <div class="space-y-4">
          <!-- Toggle de notificaciones -->
          <div class="flex items-center justify-between">
            <div>
              <p class="text-text_primary">Notificaciones push</p>
              <p class="text-text_secondary text-sm">
                {#if pushPermission === 'denied'}
                  Bloqueadas por el navegador
                {:else}
                  Recibe recordatorios de tus hábitos
                {/if}
              </p>
            </div>
            <button
              type="button"
              aria-label="Activar notificaciones push"
              onclick={toggleNotificaciones}
              disabled={pushLoading || pushPermission === 'denied'}
              class="w-12 h-6 rounded-full transition-all disabled:opacity-50 disabled:cursor-not-allowed {notificaciones ? 'bg-success' : 'bg-bg_input border border-border'}"
            >
              <div class="w-5 h-5 rounded-full bg-white shadow transition-transform {notificaciones ? 'translate-x-6' : 'translate-x-0.5'}"></div>
            </button>
          </div>

          {#if pushError}
            <p class="text-accent text-sm">{pushError}</p>
          {/if}

          {#if notificaciones}
            <!-- Hora del recordatorio -->
            <div>
              <label for="hora" class="block text-text_secondary text-sm mb-1">Hora del recordatorio</label>
              <input
                id="hora"
                type="time"
                value={horaRecordatorio}
                onchange={handleHoraChange}
                class="bg-bg_input border border-border rounded px-3 py-2 text-text_primary focus:border-accent focus:outline-none"
              />
            </div>

            <!-- Zona horaria -->
            <div>
              <label for="zona" class="block text-text_secondary text-sm mb-1">Zona horaria</label>
              <select
                id="zona"
                value={timezone}
                onchange={handleZonaChange}
                class="w-full bg-bg_input border border-border rounded px-3 py-2 text-text_primary focus:border-accent focus:outline-none"
              >
                {#each TIMEZONES as tz}
                  <option value={tz.value}>{tz.label}</option>
                {/each}
              </select>
            </div>

            <!-- Botón de prueba -->
            <div class="pt-2">
              <button
                type="button"
                onclick={handleTestNotification}
                disabled={testingNotification || !pushSubscribed}
                class="w-full py-2 px-4 rounded border border-border text-text_secondary hover:border-success hover:text-success transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {#if testingNotification}
                  Enviando...
                {:else}
                  🔔 Enviar notificación de prueba
                {/if}
              </button>
              {#if testResult}
                <p class="text-sm mt-2 {testResult.success ? 'text-success' : 'text-accent'}">
                  {testResult.message}
                </p>
              {/if}
            </div>
          {/if}
        </div>
      {/if}
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
        <button 
          onclick={iniciarEliminacionDatos}
          class="w-full py-2 px-4 rounded border border-accent/50 text-accent hover:bg-accent/10 transition-colors text-left"
        >
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

<!-- Modal de confirmación para eliminar categoría -->
{#if showDeleteConfirm && categoriaToDelete}
  <ConfirmModal
    title="Eliminar categoría"
    message="¿Estás seguro de que quieres eliminar '{categoriaToDelete.nombre}'? Los hábitos que usen esta categoría podrían verse afectados."
    confirmText="Eliminar"
    cancelText="Cancelar"
    onConfirm={handleEliminarCategoria}
    onCancel={cancelarEliminar}
  />
{/if}

<!-- Modal para verificar contraseña -->
{#if showPasswordModal}
  <div class="fixed inset-0 bg-[#0E0D0D] flex items-center justify-center z-50 p-4">
    <div class="bg-bg_secondary border border-border rounded-lg p-6 max-w-md w-full">
      <h3 class="text-xl font-semibold text-text_primary mb-4">🔐 Verificar identidad</h3>
      <p class="text-text_secondary mb-4">Por seguridad, ingresa tu contraseña para continuar.</p>
      
      <input
        type="password"
        bind:value={passwordInput}
        placeholder="Contraseña"
        class="w-full px-4 py-2 rounded border border-border bg-bg_input text-text_primary placeholder-text_secondary mb-2 focus:outline-none focus:border-accent"
        onkeydown={(e) => e.key === 'Enter' && verificarPassword()}
      />
      
      {#if passwordError}
        <p class="text-accent text-sm mb-4">{passwordError}</p>
      {/if}
      
      <div class="flex gap-3 mt-4">
        <button
          onclick={cancelarPassword}
          class="flex-1 py-2 px-4 rounded border border-border text-text_secondary hover:border-accent hover:text-accent transition-colors"
        >
          Cancelar
        </button>
        <button
          onclick={verificarPassword}
          disabled={!passwordInput}
          class="flex-1 py-2 px-4 rounded bg-accent text-white font-bold hover:bg-accent/80 transition-colors disabled:opacity-50"
        >
          Verificar
        </button>
      </div>
    </div>
  </div>
{/if}

<!-- Modal para opciones de eliminación -->
{#if showDeleteOptions}
  <div class="fixed inset-0 bg-[#0E0D0D] flex items-center justify-center z-50 p-4">
    <div class="bg-bg_secondary border border-border rounded-lg p-6 max-w-md w-full">
      {#if deletingData}
        <!-- Indicador de carga -->
        <div class="flex flex-col items-center justify-center py-8">
          <div class="w-12 h-12 border-4 border-accent border-t-transparent rounded-full animate-spin mb-4"></div>
          <p class="text-text_primary font-medium">Eliminando datos...</p>
          <p class="text-text_secondary text-sm mt-2">Por favor espera</p>
        </div>
      {:else}
        <h3 class="text-xl font-semibold text-text_primary mb-4">⚠️ Eliminar datos</h3>
        <p class="text-text_secondary mb-6">¿Qué deseas eliminar?</p>
        
        {#if deleteMessage}
          <p class="text-sm mb-4 {deleteMessage.startsWith('✅') ? 'text-success' : 'text-accent'}">
            {deleteMessage}
          </p>
        {/if}
        
        <div class="space-y-3">
          <button
            onclick={handleEliminarSoloRegistros}
            disabled={deletingData}
            class="w-full py-3 px-4 rounded border border-warning text-warning hover:bg-warning/10 transition-colors disabled:opacity-50"
          >
            📊 Solo registros y progresos
          </button>
          <p class="text-text_secondary text-xs px-2">Elimina todo el historial de registros pero mantiene tu cuenta y hábitos.</p>
          
          <button
            onclick={handleEliminarCuenta}
            disabled={deletingData}
            class="w-full py-3 px-4 rounded border border-accent text-accent hover:bg-accent/10 transition-colors disabled:opacity-50"
          >
            👤 Eliminar cuenta completa
          </button>
          <p class="text-text_secondary text-xs px-2">Elimina tu cuenta y todos los datos asociados. Esta acción es irreversible.</p>
        </div>
        
        <button
          onclick={cancelarDeleteOptions}
          disabled={deletingData}
          class="w-full mt-6 py-2 px-4 rounded border border-border text-text_secondary hover:border-accent hover:text-accent transition-colors disabled:opacity-50"
        >
          Cancelar
        </button>
      {/if}
    </div>
  </div>
{/if}
