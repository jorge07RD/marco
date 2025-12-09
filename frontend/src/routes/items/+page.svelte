<script lang="ts">
  import { onMount } from 'svelte';
  import { getItems, createItem, deleteItem, type Item, type ItemCreate } from '$lib/api';

  let items: Item[] = $state([]);
  let loading = $state(true);
  let error: string | null = $state(null);

  let showForm = $state(false);
  let formData: ItemCreate = $state({
    name: '',
    description: '',
    value: 0,
    category: ''
  });

  async function loadItems() {
    try {
      loading = true;
      error = null;
      items = await getItems();
    } catch (e) {
      error = 'Error cargando items';
      console.error(e);
    } finally {
      loading = false;
    }
  }

  async function handleSubmit(e: Event) {
    e.preventDefault();
    try {
      await createItem(formData);
      formData = { name: '', description: '', value: 0, category: '' };
      showForm = false;
      await loadItems();
    } catch (e) {
      error = 'Error creando item';
      console.error(e);
    }
  }

  async function handleDelete(id: number) {
    if (!confirm('¿Estás seguro de eliminar este item?')) return;
    try {
      await deleteItem(id);
      await loadItems();
    } catch (e) {
      error = 'Error eliminando item';
      console.error(e);
    }
  }

  onMount(() => {
    loadItems();
  });
</script>

<div class="max-w-6xl mx-auto p-8">
  <div class="flex justify-between items-center mb-6">
    <h1 class="text-3xl font-bold">Items</h1>
    <button 
      class="bg-[#e94560] hover:bg-[#d63d56] text-white px-4 py-2 rounded-lg font-medium transition-colors"
      onclick={() => showForm = !showForm}
    >
      {showForm ? 'Cancelar' : '+ Nuevo Item'}
    </button>
  </div>

  {#if error}
    <div class="bg-[#e94560]/10 border border-[#e94560] text-[#e94560] p-4 rounded-lg mb-4">{error}</div>
  {/if}

  {#if showForm}
    <form class="bg-[#16213e] border border-[#533483] rounded-xl p-6 mb-6" onsubmit={handleSubmit}>
      <h3 class="text-lg font-semibold mb-4">Nuevo Item</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div class="flex flex-col gap-2">
          <label for="name" class="text-sm text-[#8d99ae]">Nombre *</label>
          <input
            type="text"
            id="name"
            bind:value={formData.name}
            required
            placeholder="Nombre del item"
            class="bg-[#0f0f23] border border-[#533483] rounded-lg px-4 py-2 text-[#edf2f4] focus:outline-none focus:border-[#e94560]"
          />
        </div>
        <div class="flex flex-col gap-2">
          <label for="category" class="text-sm text-[#8d99ae]">Categoría</label>
          <input
            type="text"
            id="category"
            bind:value={formData.category}
            placeholder="Categoría"
            class="bg-[#0f0f23] border border-[#533483] rounded-lg px-4 py-2 text-[#edf2f4] focus:outline-none focus:border-[#e94560]"
          />
        </div>
        <div class="flex flex-col gap-2">
          <label for="value" class="text-sm text-[#8d99ae]">Valor</label>
          <input
            type="number"
            id="value"
            bind:value={formData.value}
            step="0.01"
            class="bg-[#0f0f23] border border-[#533483] rounded-lg px-4 py-2 text-[#edf2f4] focus:outline-none focus:border-[#e94560]"
          />
        </div>
        <div class="flex flex-col gap-2 md:col-span-3">
          <label for="description" class="text-sm text-[#8d99ae]">Descripción</label>
          <input
            type="text"
            id="description"
            bind:value={formData.description}
            placeholder="Descripción del item"
            class="bg-[#0f0f23] border border-[#533483] rounded-lg px-4 py-2 text-[#edf2f4] focus:outline-none focus:border-[#e94560]"
          />
        </div>
      </div>
      <button type="submit" class="bg-[#e94560] hover:bg-[#d63d56] text-white px-4 py-2 rounded-lg font-medium transition-colors">
        Crear Item
      </button>
    </form>
  {/if}

  {#if loading}
    <div class="text-center py-12 text-[#8d99ae]">Cargando...</div>
  {:else if items.length === 0}
    <div class="text-center py-12 text-[#8d99ae]">
      <p>No hay items. ¡Crea el primero!</p>
    </div>
  {:else}
    <div class="bg-[#16213e] border border-[#533483] rounded-xl overflow-x-auto">
      <table class="w-full">
        <thead>
          <tr class="border-b border-[#533483]">
            <th class="px-4 py-3 text-left text-xs uppercase tracking-wider text-[#8d99ae] font-medium">ID</th>
            <th class="px-4 py-3 text-left text-xs uppercase tracking-wider text-[#8d99ae] font-medium">Nombre</th>
            <th class="px-4 py-3 text-left text-xs uppercase tracking-wider text-[#8d99ae] font-medium">Categoría</th>
            <th class="px-4 py-3 text-left text-xs uppercase tracking-wider text-[#8d99ae] font-medium">Valor</th>
            <th class="px-4 py-3 text-left text-xs uppercase tracking-wider text-[#8d99ae] font-medium">Creado</th>
            <th class="px-4 py-3 text-left text-xs uppercase tracking-wider text-[#8d99ae] font-medium">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {#each items as item}
            <tr class="border-b border-[#533483]/50 hover:bg-[#1a1a2e]/50">
              <td class="px-4 py-3">{item.id}</td>
              <td class="px-4 py-3">
                <div class="font-medium">{item.name}</div>
                {#if item.description}
                  <div class="text-xs text-[#8d99ae]">{item.description}</div>
                {/if}
              </td>
              <td class="px-4 py-3">
                {#if item.category}
                  <span class="bg-[#7b2cbf] text-white px-2 py-1 rounded text-xs">{item.category}</span>
                {:else}
                  <span class="text-[#8d99ae]">-</span>
                {/if}
              </td>
              <td class="px-4 py-3 font-mono text-[#00ff88]">${item.value.toFixed(2)}</td>
              <td class="px-4 py-3 text-sm text-[#8d99ae]">{new Date(item.created_at).toLocaleDateString()}</td>
              <td class="px-4 py-3">
                <button 
                  class="bg-[#e94560]/20 hover:bg-[#e94560]/30 text-[#e94560] px-3 py-1 rounded text-sm transition-colors"
                  onclick={() => handleDelete(item.id)}
                >
                  Eliminar
                </button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>
