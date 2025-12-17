<script lang="ts">
  import { createHabito, updateHabito, getCategorias, crearCategoria, type Habito, type HabitoCreate, type Categoria } from "$lib/api";
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";

  interface Props {
    habito?: Habito | null;
    usuarioId: number;
    onClose: () => void;
    onSave: (habito: Habito) => void;
  }

  let { habito = null, usuarioId, onClose, onSave }: Props = $props();

  // Form state
  let nombre = $state(habito?.nombre ?? "");
  let descripcion = $state(habito?.descripcion ?? "");
  let categoria_id = $state(habito?.categoria_id ?? 1);
  let unidad_medida = $state(habito?.unidad_medida ?? "");
  let meta_diaria = $state(habito?.meta_diaria ?? 1);
  let diasSeleccionados = $state<string[]>(habito ? JSON.parse(habito.dias) : []);
  let color = $state(habito?.color ?? "#e94560");
  let activo = $state(habito?.activo ?? 1);

  let categorias = $state<Categoria[]>([]);
  let saving = $state(false);
  let errorMsg = $state<string | null>(null);
  let isClosing = $state(false);
  let loadingCategorias = $state(true);
  let mostrarCrearCategoria = $state(false);
  let nombreNuevaCategoria = $state("");

  const diassemana = ["L", "M", "X", "J", "V", "S", "D"];
  const colores = ["#e94560", "#00ff88", "#7b2cbf", "#0b61b8", "#ffd60a", "#ff6b35", "#4ecdc4", "#533483"];

  const isEditing = habito !== null;

  onMount(async () => {
    await cargarCategorias();
  });

  async function cargarCategorias() {
    try {
      loadingCategorias = true;
      categorias = await getCategorias();

      // Si no hay categorías y no está editando, mostrar formulario para crear categoría
      if (categorias.length === 0 && !isEditing) {
        mostrarCrearCategoria = true;
      } else if (categorias.length > 0) {
        // Si ya hay categorías, asegurarse de que categoria_id tenga valor válido
        if (!categoria_id || !categorias.find(c => c.id === categoria_id)) {
          categoria_id = categorias[0].id;
        }
      }
    } catch (e) {
      console.error("Error cargando categorías:", e);
      errorMsg = "Error al cargar categorías";
    } finally {
      loadingCategorias = false;
    }
  }

  async function handleCrearCategoriaInline() {
    if (!nombreNuevaCategoria.trim()) {
      errorMsg = "El nombre de la categoría es requerido";
      return;
    }

    try {
      const nuevaCat = await crearCategoria(nombreNuevaCategoria.trim());
      await cargarCategorias();
      categoria_id = nuevaCat.id;
      nombreNuevaCategoria = "";
      mostrarCrearCategoria = false;
      errorMsg = null;
    } catch (e) {
      errorMsg = e instanceof Error ? e.message : "Error al crear categoría";
    }
  }

  function handleClose() {
    isClosing = true;
    // Esperar a que termine la animación slide-out-blurred-top (0.45s)
    setTimeout(() => {
      onClose();
    }, 450);
  }

  function toggleDia(dia: string) {
    if (diasSeleccionados.includes(dia)) {
      diasSeleccionados = diasSeleccionados.filter(d => d !== dia);
    } else {
      diasSeleccionados = [...diasSeleccionados, dia];
    }
  }

  async function handleSubmit() {
    if (!nombre.trim()) {
      errorMsg = "El nombre es requerido";
      return;
    }
    if (!unidad_medida.trim()) {
      errorMsg = "La unidad de medida es requerida";
      return;
    }
    if (diasSeleccionados.length === 0) {
      errorMsg = "Selecciona al menos un día";
      return;
    }

    saving = true;
    errorMsg = null;

    try {
      const habitoData: HabitoCreate = {
        nombre: nombre.trim(),
        descripcion: descripcion.trim() || undefined,
        categoria_id,
        usuario_id: usuarioId,
        unidad_medida: unidad_medida.trim(),
        meta_diaria,
        dias: JSON.stringify(diasSeleccionados),
        color,
        activo
      };

      let savedHabito: Habito;
      if (isEditing && habito) {
        savedHabito = await updateHabito(habito.id, habitoData);
      } else {
        savedHabito = await createHabito(habitoData);
      }

      onSave(savedHabito);
    } catch (e) {
      errorMsg = e instanceof Error ? e.message : "Error al guardar";
    } finally {
      saving = false;
    }
  }
</script>

<!-- Overlay -->
<div 
  class="fixed inset-0 backdrop-blur-md z-40 flex items-center justify-center p-4 {isClosing ? 'backdrop-blur-0' : ''} transition-all duration-500"
  onclick={handleClose}
  onkeydown={(e) => e.key === 'Escape' && handleClose()}
  role="button"
  tabindex="0"
>
  <!-- Modal -->
  <div 
    class="bg-bg_secondary border border-border rounded-lg w-full max-w-md max-h-[90vh] overflow-y-auto p-6 {isClosing ? 'slide-out-blurred-top' : 'bounce-in-top'}"
    onclick={(e) => e.stopPropagation()}
    onkeydown={(e) => e.stopPropagation()}
    role="dialog"
    tabindex="-1"
  >
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-xl font-bold text-text_primary">
        {isEditing ? "Editar Hábito" : "Nuevo Hábito"}
      </h2>
      <button 
        onclick={handleClose}
        class="text-text_secondary hover:text-accent transition-colors text-2xl"
      >
        ×
      </button>
    </div>

    {#if errorMsg}
      <div class="bg-accent/20 border border-accent text-accent px-4 py-2 rounded mb-4 text-sm">
        {errorMsg}
      </div>
    {/if}

    {#if loadingCategorias}
      <div class="text-center py-8">
        <p class="text-text_secondary">Cargando categorías...</p>
      </div>
    {:else if categorias.length === 0}
      <!-- No hay categorías - Mostrar opciones para crear -->
      <div class="bg-warning/10 border border-warning rounded-lg p-4 mb-4">
        <p class="text-warning font-semibold mb-2">⚠️ No hay categorías</p>
        <p class="text-text_secondary text-sm mb-3">
          Necesitas crear al menos una categoría antes de crear un hábito.
        </p>

        {#if mostrarCrearCategoria}
          <!-- Formulario inline para crear categoría -->
          <form onsubmit={(e) => { e.preventDefault(); handleCrearCategoriaInline(); }} class="space-y-3">
            <div>
              <label for="nueva-categoria" class="block text-text_secondary text-sm mb-1">
                Nombre de la categoría
              </label>
              <input
                id="nueva-categoria"
                type="text"
                bind:value={nombreNuevaCategoria}
                placeholder="Ej: Salud, Trabajo, Personal..."
                class="w-full bg-bg_input border border-border rounded px-3 py-2 text-text_primary placeholder-text_secondary/50 focus:border-accent focus:outline-none"
                autofocus
              />
            </div>
            <div class="flex gap-2">
              <button
                type="submit"
                class="flex-1 bg-success text-bg_primary font-bold py-2 px-4 rounded hover:bg-success/80 transition-colors"
              >
                Crear categoría
              </button>
              <button
                type="button"
                onclick={handleClose}
                class="flex-1 border border-border text-text_secondary py-2 px-4 rounded hover:border-text_secondary transition-colors"
              >
                Cancelar
              </button>
            </div>
          </form>
        {:else}
          <div class="flex gap-2">
            <button
              onclick={() => mostrarCrearCategoria = true}
              class="flex-1 bg-success text-bg_primary font-bold py-2 px-4 rounded hover:bg-success/80 transition-colors"
            >
              Crear categoría aquí
            </button>
            <button
              onclick={() => goto('/settings')}
              class="flex-1 border border-border text-text_secondary py-2 px-4 rounded hover:border-text_secondary transition-colors"
            >
              Ir a Ajustes
            </button>
          </div>
        {/if}
      </div>
    {:else}
      <!-- Formulario de hábito normal -->
      <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="space-y-4">
      <!-- Nombre -->
      <div>
        <label for="nombre" class="block text-text_secondary text-sm mb-1">Nombre</label>
        <input
          id="nombre"
          type="text"
          bind:value={nombre}
          placeholder="Ej: Beber agua 💧"
          class="w-full bg-bg_input border border-border rounded px-3 py-2 text-text_primary placeholder-text_secondary/50 focus:border-accent focus:outline-none"
        />
      </div>

      <!-- Descripción -->
      <div>
        <label for="descripcion" class="block text-text_secondary text-sm mb-1">Descripción (opcional)</label>
        <input
          id="descripcion"
          type="text"
          bind:value={descripcion}
          placeholder="Ej: Mantenerme hidratado"
          class="w-full bg-bg_input border border-border rounded px-3 py-2 text-text_primary placeholder-text_secondary/50 focus:border-accent focus:outline-none"
        />
      </div>

      <!-- Categoría -->
      <div>
        <label for="categoria" class="block text-text_secondary text-sm mb-1">Categoría</label>
        <select
          id="categoria"
          bind:value={categoria_id}
          class="w-full bg-bg_input border border-border rounded px-3 py-2 text-text_primary focus:border-accent focus:outline-none"
        >
          {#each categorias as cat}
            <option value={cat.id}>{cat.nombre}</option>
          {/each}
        </select>
      </div>

      <!-- Meta diaria y Unidad -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label for="meta" class="block text-text_secondary text-sm mb-1">Meta diaria</label>
          <input
            id="meta"
            type="number"
            step="0.1"
            min="0"
            bind:value={meta_diaria}
            class="w-full bg-bg_input border border-border rounded px-3 py-2 text-text_primary focus:border-accent focus:outline-none"
          />
        </div>
        <div>
          <label for="unidad" class="block text-text_secondary text-sm mb-1">Unidad</label>
          <input
            id="unidad"
            type="text"
            bind:value={unidad_medida}
            placeholder="Ej: litros"
            class="w-full bg-bg_input border border-border rounded px-3 py-2 text-text_primary placeholder-text_secondary/50 focus:border-accent focus:outline-none"
          />
        </div>
      </div>

      <!-- Días -->
      <div>
        <label class="block text-text_secondary text-sm mb-2">Días de la semana</label>
        <div class="flex gap-2 flex-wrap">
          {#each diassemana as dia}
            <button
              type="button"
              onclick={() => toggleDia(dia)}
              class="w-10 h-10 rounded flex items-center justify-center text-sm font-bold transition-all {diasSeleccionados.includes(dia) ? 'bg-accent text-white' : 'bg-bg_input border border-border text-text_secondary hover:border-accent'}"
            >
              {dia}
            </button>
          {/each}
        </div>
      </div>

      <!-- Color -->
      <div>
        <label class="block text-text_secondary text-sm mb-2">Color</label>
        <div class="flex gap-2 flex-wrap">
          {#each colores as c}
            <button
              type="button"
              onclick={() => color = c}
              class="w-8 h-8 rounded-full transition-all {color === c ? 'ring-2 ring-white ring-offset-2 ring-offset-bg_secondary' : ''}"
              style="background-color: {c}"
            ></button>
          {/each}
        </div>
      </div>

      <!-- Activo -->
      <div class="flex items-center gap-3">
        <label for="activo" class="text-text_secondary text-sm">Activo</label>
        <button
          type="button"
          onclick={() => activo = activo === 1 ? 0 : 1}
          class="w-12 h-6 rounded-full transition-all {activo === 1 ? 'bg-success' : 'bg-bg_input border border-border'}"
        >
          <div class="w-5 h-5 rounded-full bg-white shadow transition-transform {activo === 1 ? 'translate-x-6' : 'translate-x-0.5'}"></div>
        </button>
      </div>

      <!-- Botones -->
      <div class="flex gap-3 pt-4">
        <button
          type="button"
          onclick={handleClose}
          class="flex-1 py-2 px-4 rounded border border-border text-text_secondary hover:border-text_secondary transition-colors"
        >
          Cancelar
        </button>
        <button
          type="submit"
          disabled={saving}
          class="flex-1 py-2 px-4 rounded bg-accent text-white font-bold hover:bg-accent/80 transition-colors disabled:opacity-50"
        >
          {saving ? "Guardando..." : (isEditing ? "Actualizar" : "Crear")}
        </button>
      </div>
    </form>
    {/if}
  </div>
</div>
