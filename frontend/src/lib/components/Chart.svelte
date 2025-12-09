<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import Highcharts from 'highcharts';
  import type { Options } from 'highcharts';

  interface Props {
    options: Options;
    class?: string;
  }

  let { options, class: className = '' }: Props = $props();
  
  let container: HTMLDivElement;
  let chart: Highcharts.Chart | null = null;

  // Set dark theme defaults
  const darkTheme: Partial<Options> = {
    chart: {
      backgroundColor: '#1e293b',
      style: {
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
      }
    },
    title: {
      style: {
        color: '#f1f5f9'
      }
    },
    subtitle: {
      style: {
        color: '#94a3b8'
      }
    },
    xAxis: {
      labels: {
        style: {
          color: '#94a3b8'
        }
      },
      lineColor: '#334155',
      tickColor: '#334155'
    },
    yAxis: {
      labels: {
        style: {
          color: '#94a3b8'
        }
      },
      gridLineColor: '#334155',
      title: {
        style: {
          color: '#94a3b8'
        }
      }
    },
    legend: {
      itemStyle: {
        color: '#f1f5f9'
      },
      itemHoverStyle: {
        color: '#3b82f6'
      }
    },
    tooltip: {
      backgroundColor: '#0f172a',
      borderColor: '#334155',
      style: {
        color: '#f1f5f9'
      }
    },
    credits: {
      enabled: false
    }
  };

  function mergeOptions(base: Partial<Options>, custom: Options): Options {
    return {
      ...base,
      ...custom,
      chart: { ...base.chart, ...custom.chart },
      title: { ...base.title, ...custom.title },
      xAxis: { ...base.xAxis, ...custom.xAxis },
      yAxis: { ...base.yAxis, ...custom.yAxis },
      legend: { ...base.legend, ...custom.legend },
      tooltip: { ...base.tooltip, ...custom.tooltip }
    };
  }

  onMount(() => {
    const mergedOptions = mergeOptions(darkTheme, options);
    chart = Highcharts.chart(container, mergedOptions);
  });

  onDestroy(() => {
    if (chart) {
      chart.destroy();
      chart = null;
    }
  });

  $effect(() => {
    if (chart && options) {
      const mergedOptions = mergeOptions(darkTheme, options);
      chart.update(mergedOptions, true, true);
    }
  });
</script>

<div bind:this={container} class="chart-container {className}"></div>

<style>
  .chart-container {
    width: 100%;
    min-height: 400px;
  }
</style>
