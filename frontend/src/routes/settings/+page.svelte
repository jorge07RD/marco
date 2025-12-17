<script lang="ts">
  import { onMount } from 'svelte';
  import { obtenerUsuarioActual, updateUsuario, getCategorias, crearCategoria, updateCategoria, deleteCategoria, type Categoria } from '$lib/api';
  import { authStore } from '$lib/stores/auth.svelte';
  import ConfirmModal from '$lib/components/ConfirmModal.svelte';

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

  // Gestión de categorías
  let categorias = $state<Categoria[]>([]);
  let nuevaCategoria = $state("");
  let editandoCategoria = $state<Categoria | null>(null);
  let nombreCategoriaEdit = $state("");
  let categoriasLoading = $state(true);
  let showDeleteConfirm = $state(false);
  let categoriaToDelete = $state<Categoria | null>(null);

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

    // Cargar categorías
    await cargarCategorias();
  });

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
