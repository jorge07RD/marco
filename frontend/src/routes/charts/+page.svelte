<script lang="ts">
  import { onMount } from 'svelte';
  import { Chart } from '$lib';
  import {
    getChartData,
    createBulkChartData,
    deleteSeries,
    type ChartData,
    type ChartSeries
  } from '$lib/api';
  import type { Options } from 'highcharts';

  let series: string[] = $state([]);
  let selectedSeries: string | null = $state(null);
  let seriesData: ChartSeries | null = $state(null);
  let loading = $state(true);
  let error: string | null = $state(null);

  let chartOptions: Options = $state({
    chart: { type: 'line' },
    title: { text: 'Selecciona una serie' },
    series: []
  });

  // Form for generating sample data
  let showGenerateForm = $state(false);
  let generateForm = $state({
    seriesName: '',
    pointCount: 10
  });

  async function loadSeries() {
    try {
      loading = true;
      series = await getSeries();
    } catch (e) {
      error = 'Error cargando series';
    } finally {
      loading = false;
    }
  }

  async function selectSeries(name: string) {
    try {
      selectedSeries = name;
      seriesData = await getSeriesData(name);
      
      chartOptions = {
        chart: { type: 'line' },
        title: { text: `Serie: ${name}` },
        xAxis: {
          categories: seriesData.categories
        },
        yAxis: {
          title: { text: 'Valor' }
        },
        series: [
          {
            name: name,
            type: 'line',
            data: seriesData.data
          }
        ]
      };
    } catch (e) {
      error = 'Error cargando datos de la serie';
    }
  }

  async function handleGenerate(e: Event) {
    e.preventDefault();
    try {
      const points = Array.from({ length: generateForm.pointCount }, (_, i) => ({
        label: `Punto ${i + 1}`,
        value: Math.random() * 100,
        series: generateForm.seriesName
      }));
      
      await createBulkChartData(points);
      generateForm = { seriesName: '', pointCount: 10 };
      showGenerateForm = false;
      await loadSeries();
      
      // Select the new series
      await selectSeries(generateForm.seriesName || points[0].series);
    } catch (e) {
      error = 'Error generando datos';
    }
  }

  async function handleDeleteSeries(name: string) {
    if (!confirm(`¿Eliminar la serie "${name}"?`)) return;
    try {
      await deleteSeries(name);
      if (selectedSeries === name) {
        selectedSeries = null;
        seriesData = null;
        chartOptions = {
          chart: { type: 'line' },
          title: { text: 'Selecciona una serie' },
          series: []
        };
      }
      await loadSeries();
    } catch (e) {
      error = 'Error eliminando serie';
    }
  }

  onMount(() => {
    loadSeries();
  });
</script>

<div class="max-w-6xl mx-auto p-8">
  <div class="flex justify-between items-center mb-6">
    <h1 class="text-3xl font-bold">Gráficos</h1>
    <button 
      class="bg-[#e94560] hover:bg-[#d63d56] text-white px-4 py-2 rounded-lg font-medium transition-colors"
      onclick={() => showGenerateForm = !showGenerateForm}
    >
      {showGenerateForm ? 'Cancelar' : '+ Generar Datos'}
    </button>
  </div>

  {#if error}
    <div class="bg-[#e94560]/10 border border-[#e94560] text-[#e94560] p-4 rounded-lg mb-4">{error}</div>
  {/if}

  {#if showGenerateForm}
    <form class="bg-[#16213e] border border-[#533483] rounded-xl p-6 mb-6" onsubmit={handleGenerate}>
      <h3 class="text-lg font-semibold mb-4">Generar Datos de Ejemplo</h3>
      <div class="flex flex-col md:flex-row gap-4 items-end">
        <div class="flex flex-col gap-2 flex-1">
          <label for="seriesName" class="text-sm text-[#8d99ae]">Nombre de la Serie *</label>
          <input
            type="text"
            id="seriesName"
            bind:value={generateForm.seriesName}
            required
            placeholder="ej: ventas-2024"
            class="bg-[#0f0f23] border border-[#533483] rounded-lg px-4 py-2 text-[#edf2f4] focus:outline-none focus:border-[#e94560]"
          />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="pointCount" class="text-sm text-[#8d99ae]">Cantidad de Puntos</label>
          <input
            type="number"
            id="pointCount"
            bind:value={generateForm.pointCount}
            min="1"
            max="100"
            class="bg-[#0f0f23] border border-[#533483] rounded-lg px-4 py-2 text-[#edf2f4] focus:outline-none focus:border-[#e94560]"
          />
        </div>
        <button type="submit" class="bg-[#e94560] hover:bg-[#d63d56] text-white px-4 py-2 rounded-lg font-medium transition-colors">
          Generar
        </button>
      </div>
    </form>
  {/if}

  <div class="grid grid-cols-1 md:grid-cols-[250px_1fr] gap-6">
    <aside class="bg-[#16213e] border border-[#533483] rounded-xl p-6 h-fit">
      <h3 class="font-semibold mb-4">Series Disponibles</h3>
      {#if loading}
        <p class="text-[#8d99ae]">Cargando...</p>
      {:else if series.length === 0}
        <p class="text-[#8d99ae]">No hay series. ¡Genera una!</p>
      {:else}
        <ul class="space-y-1">
          {#each series as s}
            <li class="flex justify-between items-center p-2 rounded-lg transition-colors hover:bg-[#7b2cbf]/20 group {selectedSeries === s ? 'bg-[#7b2cbf]/30' : ''}">
              <button 
                class="bg-transparent border-none text-[#edf2f4] text-left p-0 flex-1 cursor-pointer"
                onclick={() => selectSeries(s)}
              >
                {s}
              </button>
              <button 
                class="bg-transparent border-none text-[#8d99ae] text-xl px-1 opacity-0 group-hover:opacity-100 transition-opacity hover:text-[#e94560] cursor-pointer"
                onclick={() => handleDeleteSeries(s)}
              >
                ×
              </button>
            </li>
          {/each}
        </ul>
      {/if}
    </aside>

    <div class="flex flex-col gap-6">
      <div class="bg-[#16213e] border border-[#533483] rounded-xl p-6 min-h-[400px]">
        <Chart options={chartOptions} />
      </div>

      {#if seriesData}
        <div class="bg-[#16213e] border border-[#533483] rounded-xl p-6">
          <h3 class="font-semibold mb-4">Datos de la Serie</h3>
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead>
                <tr class="border-b border-[#533483]">
                  <th class="px-4 py-2 text-left text-xs uppercase tracking-wider text-[#8d99ae] font-medium">Etiqueta</th>
                  <th class="px-4 py-2 text-left text-xs uppercase tracking-wider text-[#8d99ae] font-medium">Valor</th>
                </tr>
              </thead>
              <tbody>
                {#each seriesData.categories as cat, i}
                  <tr class="border-b border-[#533483]/50">
                    <td class="px-4 py-2">{cat}</td>
                    <td class="px-4 py-2 font-mono text-[#e94560]">{seriesData.data[i].toFixed(2)}</td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        </div>
      {/if}
    </div>
  </div>
</div>
