<script lang="ts">
  import { onMount } from 'svelte';
  import {
    getRendimientoPorDia,
    getCumplimientoHabitos,
    type RendimientoDia,
    type CumplimientoHabito
  } from '$lib/api';

  // Tipos de datos transformados
  interface ProgresoDia {
    fecha: string;
    habitos: number;
    habitos_completados: number;
    porcentaje: number;
  }

  interface HabitoData {
    completados: number;
    total: number;
    porcentaje: number;
    nombre: string;
    color: string;
  }

  // Estados reactivos (elimina $state, usa variables normales)
  let loading = true;
  let error: string | null = null;
  let showDateFilter = false;
  let isClosing = false;
  let fullscreenChart: string | null = null;
  let isClosingFullscreen = false;

  // Datos
  let rendimientoDatos: RendimientoDia[] = [];
  let cumplimientoDatos: CumplimientoHabito[] = [];

  // Datos transformados
  let progresoDias: ProgresoDia[] = [];
  let habitosData: HabitoData[] = [];
  let categorias: string[] = [];

  // Fechas por defecto: mes actual
  const hoy = new Date();
  const primerDiaMes = new Date(hoy.getFullYear(), hoy.getMonth(), 1);
  const ultimoDiaMes = new Date(hoy.getFullYear(), hoy.getMonth() + 1, 0);

  let fechaInicio = formatoFecha(primerDiaMes);
  let fechaFin = formatoFecha(ultimoDiaMes);

  // Función auxiliar para formatear fechas
  function formatoFecha(fecha: Date): string {
    return fecha.toISOString().split('T')[0];
  }

  // Funciones de transformación de datos
  function getProgresoPorDia(datos: RendimientoDia[]): ProgresoDia[] {
    return datos.map(dato => {
      const porcentaje = dato.habitos > 0
        ? Math.round((dato.habitos_completados / dato.habitos) * 100)
        : 0;

      return {
        fecha: dato.fecha,
        habitos: dato.habitos,
        habitos_completados: dato.habitos_completados,
        porcentaje
      };
    });
  }

  function getHabitosCompletados(datos: CumplimientoHabito[]): HabitoData[] {
    return datos.map(dato => {
      const total = dato.total_habitos > 0 ? dato.total_habitos : 1;
      const completado = dato.habitos_completados;
      const porcentaje = Math.round((completado / total) * 100);

      return {
        completados: completado,
        total: total,
        porcentaje: porcentaje,
        nombre: dato.nombre_habito,
        color: dato.color
      };
    });
  }

  function getCategoriasHabitos(datos: CumplimientoHabito[]): string[] {
    return [...new Set(datos.map(d => d.nombre_habito))];
  }

  // Shortcuts de fecha
  function setEsteMes() {
    const hoy = new Date();
    fechaInicio = formatoFecha(new Date(hoy.getFullYear(), hoy.getMonth(), 1));
    fechaFin = formatoFecha(new Date(hoy.getFullYear(), hoy.getMonth() + 1, 0));
  }

  function setUltimaSemana() {
    const hoy = new Date();
    const hace7Dias = new Date(hoy);
    hace7Dias.setDate(hoy.getDate() - 7);
    fechaInicio = formatoFecha(hace7Dias);
    fechaFin = formatoFecha(hoy);
  }

  function setUltimoMes() {
    const hoy = new Date();
    const hace30Dias = new Date(hoy);
    hace30Dias.setDate(hoy.getDate() - 30);
    fechaInicio = formatoFecha(hace30Dias);
    fechaFin = formatoFecha(hoy);
  }

  function setEsteAnio() {
    const hoy = new Date();
    fechaInicio = formatoFecha(new Date(hoy.getFullYear(), 0, 1));
    fechaFin = formatoFecha(hoy);
  }

  // Cargar datos
  async function cargarDatos() {
    try {
      loading = true;
      error = null;

      const [rendimiento, cumplimiento] = await Promise.all([
        getRendimientoPorDia(fechaInicio, fechaFin),
        getCumplimientoHabitos(fechaInicio, fechaFin)
      ]);

      rendimientoDatos = rendimiento;
      cumplimientoDatos = cumplimiento;

      progresoDias = getProgresoPorDia(rendimiento);
      habitosData = getHabitosCompletados(cumplimiento);
      categorias = getCategoriasHabitos(cumplimiento);

      // Renderizar gráficos después de cargar datos y asegurar que el DOM esté actualizado
      setTimeout(() => renderizarGraficos(), 0);

    } catch (err) {
      error = err instanceof Error ? err.message : 'Error al cargar datos';
    } finally {
      loading = false;
    }
  }

  function handleCloseModal() {
    isClosing = true;
    // Esperar a que termine la animación slide-out-blurred-top (0.45s)
    setTimeout(() => {
      showDateFilter = false;
      isClosing = false;
    }, 450);
  }

  async function aplicarFiltro() {
    isClosing = true;
    setTimeout(async () => {
      showDateFilter = false;
      isClosing = false;
      await cargarDatos();

      // Si hay un gráfico en fullscreen, re-renderizarlo con los nuevos datos
      if (fullscreenChart) {
        setTimeout(() => renderizarGraficoFullscreen(fullscreenChart), 100);
      }
    }, 450);
  }

  function openFullscreen(chartId: string) {
    fullscreenChart = chartId;
    // Renderizar el gráfico en fullscreen después de que el modal esté visible
    setTimeout(() => renderizarGraficoFullscreen(chartId), 100);
  }

  function closeFullscreen() {
    isClosingFullscreen = true;
    setTimeout(() => {
      fullscreenChart = null;
      isClosingFullscreen = false;
    }, 450);
  }

  // Renderizar gráficos con Highcharts
  async function renderizarGraficos() {
    if (typeof window === 'undefined') return;

    // Importar Highcharts dinámicamente solo en el cliente
    const Highcharts = (await import('highcharts')).default;

    // Para Highcharts v12+, HighchartsMore se exporta como default
    const HighchartsMore = (await import('highcharts/highcharts-more')).default;

    // Inicializar HighchartsMore
    if (typeof HighchartsMore === 'function') {
      HighchartsMore(Highcharts);
    }

    // Limpia los contenedores antes de renderizar para evitar superposición
    [
      'chart-rendimiento-area',
      'chart-polar',
      'chart-pie',
      'chart-spline',
      'chart-column',
      'chart-gauge',
      'chart-radar',
      'chart-bar'
    ].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.innerHTML = '';
    });

    const COLORS = {
      bg_primary: '#0E0D0D',
      bg_secondary: '#1a1a1a',
      bg_input: '#1a1a1a',
      border: '#533483',
      accent: '#e94560',
      success: '#00ff88',
      warning: '#ffc107',
      text_primary: '#FFFFFF',
      text_secondary: '#A0A0A0'
    };

    // Gráfico 1: Rendimiento de Hábitos por Día (Area)
    const chart1El = document.getElementById('chart-rendimiento-area');
    if (chart1El && progresoDias.length > 0) {
      Highcharts.chart('chart-rendimiento-area', {
        title: { text: 'Rendimiento de Hábitos por Día', style: { color: '#e0e0e0' } },
        chart: { type: 'area', backgroundColor: COLORS.bg_input },
        xAxis: {
          categories: progresoDias.map(d => d.fecha),
          labels: { style: { color: '#e0e0e0' } }
        },
        yAxis: {
          title: { text: 'Cantidad / Porcentaje', style: { color: '#e0e0e0' } },
          labels: { style: { color: '#e0e0e0' } }
        },
        plotOptions: {
          area: {
            stacking: 'normal' as const,
            lineColor: '#666666',
            lineWidth: 1,
            marker: { lineWidth: 1, lineColor: '#666666' }
          }
        },
        legend: { itemStyle: { color: '#e0e0e0' } },
        series: [
          { name: 'Hábitos Completados', type: 'area', data: progresoDias.map(d => d.habitos_completados) },
          { name: 'Total Hábitos', type: 'area', data: progresoDias.map(d => d.habitos) },
          { name: 'Porcentaje (%)', type: 'area', data: progresoDias.map(d => d.porcentaje) }
        ]
      });
    }

    // Gráfico 2: Análisis Polar de Hábitos
    const chart2El = document.getElementById('chart-polar');
    if (chart2El && habitosData.length > 0) {
      Highcharts.chart('chart-polar', {
        colors: [COLORS.accent, COLORS.success, COLORS.warning],
        chart: { type: 'column', inverted: true, polar: true, backgroundColor: COLORS.bg_input },
        title: { text: 'Análisis Polar de Hábitos', style: { color: '#e0e0e0' } },
        subtitle: { text: 'Completados vs Total por hábito' },
        tooltip: { outside: true },
        pane: { size: '85%', innerSize: '20%', endAngle: 270 },
        xAxis: {
          tickInterval: 1,
          labels: { align: 'right' as const, step: 1, y: 3, style: { fontSize: '13px', color: '#e0e0e0' } },
          lineWidth: 0,
          gridLineWidth: 0,
          categories: categorias
        },
        yAxis: {
          lineWidth: 0,
          tickInterval: 25,
          reversedStacks: false,
          endOnTick: true,
          showLastLabel: true,
          gridLineWidth: 0,
          labels: { style: { color: '#e0e0e0' } }
        },
        plotOptions: {
          column: {
            stacking: 'normal' as const,
            borderWidth: 0,
            pointPadding: 0,
            groupPadding: 0.15,
            borderRadius: 5
          }
        },
        legend: { itemStyle: { color: '#e0e0e0' } },
        series: [
          { name: 'Completados', type: 'column', data: habitosData.map(h => h.completados) },
          { name: 'Porcentaje', type: 'column', data: habitosData.map(h => h.porcentaje) }
        ]
      });
    }

    // Gráfico 3: Análisis de Hábitos (Pie)
    const chart3El = document.getElementById('chart-pie');
    if (chart3El && habitosData.length > 0) {
      Highcharts.chart('chart-pie', {
        title: { text: 'Análisis de Hábitos', style: { color: '#e0e0e0' } },
        chart: { type: 'pie', backgroundColor: COLORS.bg_input },
        tooltip: { pointFormat: '{series.name}: <b>{point.percentage:.0f}%</b>' },
        legend: { enabled: false },
        plotOptions: {
          pie: {
            allowPointSelect: true,
            cursor: 'pointer',
            borderRadius: 8,
            dataLabels: [
              { enabled: true, distance: 20, format: '{point.name}' },
              { enabled: true, distance: -15, format: '{point.percentage:.0f}%', style: { fontSize: '0.9em' } }
            ],
            showInLegend: true
          }
        },
        series: [{
          name: 'Hábitos',
          type: 'pie',
          colorByPoint: true,
          innerSize: '75%',
          data: habitosData.map(h => ({
            name: `${h.nombre} (${h.porcentaje}%)`,
            y: h.completados
          }))
        }]
      });
    }

    // Gráfico 4: Progreso de Hábitos por Día (Spline)
    const chart4El = document.getElementById('chart-spline');
    if (chart4El && progresoDias.length > 0) {
      Highcharts.chart('chart-spline', {
        chart: { type: 'spline', backgroundColor: COLORS.bg_input },
        title: { text: 'Progreso de Hábitos por Día', style: { color: '#e0e0e0' } },
        subtitle: { text: 'Rendimiento diario de hábitos' },
        xAxis: {
          categories: progresoDias.map(d => d.fecha),
          labels: { style: { color: '#e0e0e0' } }
        },
        yAxis: {
          title: { text: 'Cantidad / Porcentaje', style: { color: '#e0e0e0' } },
          labels: { style: { color: '#e0e0e0' } }
        },
        plotOptions: {
          spline: {
            dataLabels: { enabled: true },
            enableMouseTracking: true,
            marker: { enabled: true }
          }
        },
        legend: { itemStyle: { color: '#e0e0e0' } },
        series: [
          { name: 'Hábitos Completados', type: 'spline', data: progresoDias.map(d => d.habitos_completados) },
          { name: 'Total Hábitos', type: 'spline', data: progresoDias.map(d => d.habitos) },
          { name: 'Porcentaje (%)', type: 'spline', data: progresoDias.map(d => d.porcentaje) }
        ]
      });
    }

    // Gráfico 5: Comparación por Hábito (Column)
    const chart5El = document.getElementById('chart-column');
    if (chart5El && habitosData.length > 0) {
      Highcharts.chart('chart-column', {
        title: { text: 'Comparación por Hábito', style: { color: '#e0e0e0' } },
        chart: { type: 'column', backgroundColor: COLORS.bg_input },
        xAxis: { categories: categorias, labels: { style: { color: '#e0e0e0' } } },
        yAxis: {
          labels: { style: { color: '#e0e0e0' } },
          title: { text: 'Cantidad', style: { color: COLORS.accent } }
        },
        legend: { itemStyle: { color: '#e0e0e0' } },
        series: [
          { name: 'Total Hábitos', type: 'column', data: habitosData.map(h => h.total) },
          { name: 'Hábitos Completados', type: 'column', data: habitosData.map(h => h.completados) }
        ]
      });
    }

    // Gráfico 6: Promedio General (Gauge)
    const chart6El = document.getElementById('chart-gauge');
    if (chart6El && habitosData.length > 0) {
      const promedioGeneral = habitosData.length > 0
        ? Math.round(habitosData.reduce((sum, h) => sum + h.porcentaje, 0) / habitosData.length)
        : 0;

      Highcharts.chart('chart-gauge', {
        chart: { type: 'gauge', backgroundColor: COLORS.bg_input },
        title: { text: 'Promedio General de Cumplimiento', style: { color: '#e0e0e0' } },
        pane: {
          startAngle: -150,
          endAngle: 150,
          background: [{ backgroundColor: COLORS.bg_input, borderWidth: 0, outerRadius: '100%' }]
        },
        yAxis: {
          min: 0,
          max: 100,
          tickInterval: 10,
          labels: { style: { color: '#e0e0e0' } },
          title: { text: 'Porcentaje (%)', style: { color: '#e0e0e0' } },
          plotBands: [
            { from: 0, to: 60, color: COLORS.warning },
            { from: 60, to: 80, color: COLORS.accent },
            { from: 80, to: 100, color: COLORS.success }
          ]
        },
        series: [{
          name: 'Cumplimiento',
          type: 'gauge',
          data: [promedioGeneral],
          tooltip: { valueSuffix: '%' }
        }]
      });
    }

    // Gráfico 7: Radar/Spider
    const chart7El = document.getElementById('chart-radar');
    if (chart7El && habitosData.length > 0) {
      Highcharts.chart('chart-radar', {
        chart: { polar: true, type: 'line', backgroundColor: COLORS.bg_input },
        title: { text: 'Gráfico Radar de Cumplimiento', style: { color: '#e0e0e0' } },
        pane: { size: '80%' },
        xAxis: {
          categories: categorias,
          tickmarkPlacement: 'on' as const,
          lineWidth: 0,
          labels: { style: { color: '#e0e0e0' } }
        },
        yAxis: {
          gridLineInterpolation: 'polygon' as const,
          lineWidth: 0,
          min: 0,
          max: 100,
          labels: { style: { color: '#e0e0e0' } }
        },
        tooltip: {
          shared: true,
          pointFormat: '<span style="color:{series.color}">{series.name}: <b>{point.y:.1f}%</b><br/>'
        },
        legend: { align: 'center' as const, itemStyle: { color: '#e0e0e0' } },
        series: [{
          name: 'Porcentaje Cumplimiento',
          type: 'line',
          data: habitosData.map(h => h.porcentaje),
          pointPlacement: 'on' as const,
          color: COLORS.accent,
          fillOpacity: 0.3
        }],
        plotOptions: {
          line: { lineWidth: 2, marker: { enabled: true, radius: 4 } }
        }
      });
    }

    // Gráfico 8: Top Hábitos por Cumplimiento (Bar)
    const chart8El = document.getElementById('chart-bar');
    if (chart8El && habitosData.length > 0) {
      const habitosOrdenados = [...habitosData].sort((a, b) => b.porcentaje - a.porcentaje);

      Highcharts.chart('chart-bar', {
        chart: { type: 'bar', backgroundColor: COLORS.bg_input },
        title: { text: 'Top Hábitos por Cumplimiento', style: { color: '#e0e0e0' } },
        xAxis: {
          categories: habitosOrdenados.map(h => h.nombre),
          labels: { style: { color: '#e0e0e0' } }
        },
        yAxis: {
          min: 0,
          max: 100,
          title: { text: 'Porcentaje (%)', style: { color: '#e0e0e0' } },
          labels: { style: { color: '#e0e0e0' } }
        },
        legend: { enabled: false },
        plotOptions: {
          bar: {
            borderRadius: 5,
            dataLabels: { enabled: true, format: '{y}%', style: { color: '#e0e0e0' } },
            colorByPoint: true
          }
        },
        series: [{
          name: 'Cumplimiento',
          type: 'bar',
          data: habitosOrdenados.map(h => h.porcentaje)
        }]
      });
    }
  }

  // Renderizar un gráfico en modo fullscreen
  async function renderizarGraficoFullscreen(chartId: string) {
    if (typeof window === 'undefined') return;

    const Highcharts = (await import('highcharts')).default;
    const HighchartsMore = (await import('highcharts/highcharts-more')).default;

    if (typeof HighchartsMore === 'function') {
      HighchartsMore(Highcharts);
    }

    const fullscreenId = `${chartId}-fullscreen`;
    const el = document.getElementById(fullscreenId);
    if (!el) return;

    el.innerHTML = '';

    const COLORS = {
      bg_primary: '#0E0D0D',
      bg_secondary: '#1a1a1a',
      bg_input: '#1a1a1a',
      border: '#533483',
      accent: '#e94560',
      success: '#00ff88',
      warning: '#ffc107',
      text_primary: '#FFFFFF',
      text_secondary: '#A0A0A0'
    };

    // Renderizar el gráfico específico
    switch (chartId) {
      case 'chart-rendimiento-area':
        if (progresoDias.length > 0) {
          Highcharts.chart(fullscreenId, {
            title: { text: 'Rendimiento de Hábitos por Día', style: { color: '#e0e0e0' } },
            chart: { type: 'area', backgroundColor: COLORS.bg_input },
            xAxis: { categories: progresoDias.map(d => d.fecha), labels: { style: { color: '#e0e0e0' } } },
            yAxis: { title: { text: 'Cantidad / Porcentaje', style: { color: '#e0e0e0' } }, labels: { style: { color: '#e0e0e0' } } },
            plotOptions: { area: { stacking: 'normal' as const, lineColor: '#666666', lineWidth: 1, marker: { lineWidth: 1, lineColor: '#666666' } } },
            legend: { itemStyle: { color: '#e0e0e0' } },
            series: [
              { name: 'Hábitos Completados', type: 'area', data: progresoDias.map(d => d.habitos_completados) },
              { name: 'Total Hábitos', type: 'area', data: progresoDias.map(d => d.habitos) },
              { name: 'Porcentaje (%)', type: 'area', data: progresoDias.map(d => d.porcentaje) }
            ]
          });
        }
        break;

      case 'chart-polar':
        if (habitosData.length > 0) {
          Highcharts.chart(fullscreenId, {
            colors: [COLORS.accent, COLORS.success, COLORS.warning],
            chart: { type: 'column', inverted: true, polar: true, backgroundColor: COLORS.bg_input },
            title: { text: 'Análisis Polar de Hábitos', style: { color: '#e0e0e0' } },
            subtitle: { text: 'Completados vs Total por hábito' },
            tooltip: { outside: true },
            pane: { size: '85%', innerSize: '20%', endAngle: 270 },
            xAxis: { tickInterval: 1, labels: { align: 'right' as const, step: 1, y: 3, style: { fontSize: '13px', color: '#e0e0e0' } }, lineWidth: 0, gridLineWidth: 0, categories: categorias },
            yAxis: { lineWidth: 0, tickInterval: 25, reversedStacks: false, endOnTick: true, showLastLabel: true, gridLineWidth: 0, labels: { style: { color: '#e0e0e0' } } },
            plotOptions: { column: { stacking: 'normal' as const, borderWidth: 0, pointPadding: 0, groupPadding: 0.15, borderRadius: 5 } },
            legend: { itemStyle: { color: '#e0e0e0' } },
            series: [
              { name: 'Completados', type: 'column', data: habitosData.map(h => h.completados) },
              { name: 'Porcentaje', type: 'column', data: habitosData.map(h => h.porcentaje) }
            ]
          });
        }
        break;

      case 'chart-pie':
        if (habitosData.length > 0) {
          Highcharts.chart(fullscreenId, {
            title: { text: 'Análisis de Hábitos', style: { color: '#e0e0e0' } },
            chart: { type: 'pie', backgroundColor: COLORS.bg_input },
            tooltip: { pointFormat: '{series.name}: <b>{point.percentage:.0f}%</b>' },
            legend: { enabled: false },
            plotOptions: { pie: { allowPointSelect: true, cursor: 'pointer', borderRadius: 8, dataLabels: [{ enabled: true, distance: 20, format: '{point.name}' }, { enabled: true, distance: -15, format: '{point.percentage:.0f}%', style: { fontSize: '0.9em' } }], showInLegend: true } },
            series: [{ name: 'Hábitos', type: 'pie', colorByPoint: true, innerSize: '75%', data: habitosData.map(h => ({ name: `${h.nombre} (${h.porcentaje}%)`, y: h.completados })) }]
          });
        }
        break;

      case 'chart-spline':
        if (progresoDias.length > 0) {
          Highcharts.chart(fullscreenId, {
            chart: { type: 'spline', backgroundColor: COLORS.bg_input },
            title: { text: 'Progreso de Hábitos por Día', style: { color: '#e0e0e0' } },
            subtitle: { text: 'Rendimiento diario de hábitos' },
            xAxis: { categories: progresoDias.map(d => d.fecha), labels: { style: { color: '#e0e0e0' } } },
            yAxis: { title: { text: 'Cantidad / Porcentaje', style: { color: '#e0e0e0' } }, labels: { style: { color: '#e0e0e0' } } },
            plotOptions: { spline: { dataLabels: { enabled: true }, enableMouseTracking: true, marker: { enabled: true } } },
            legend: { itemStyle: { color: '#e0e0e0' } },
            series: [
              { name: 'Hábitos Completados', type: 'spline', data: progresoDias.map(d => d.habitos_completados) },
              { name: 'Total Hábitos', type: 'spline', data: progresoDias.map(d => d.habitos) },
              { name: 'Porcentaje (%)', type: 'spline', data: progresoDias.map(d => d.porcentaje) }
            ]
          });
        }
        break;

      case 'chart-column':
        if (habitosData.length > 0) {
          Highcharts.chart(fullscreenId, {
            title: { text: 'Comparación por Hábito', style: { color: '#e0e0e0' } },
            chart: { type: 'column', backgroundColor: COLORS.bg_input },
            xAxis: { categories: categorias, labels: { style: { color: '#e0e0e0' } } },
            yAxis: { labels: { style: { color: '#e0e0e0' } }, title: { text: 'Cantidad', style: { color: COLORS.accent } } },
            legend: { itemStyle: { color: '#e0e0e0' } },
            series: [
              { name: 'Total Hábitos', type: 'column', data: habitosData.map(h => h.total) },
              { name: 'Hábitos Completados', type: 'column', data: habitosData.map(h => h.completados) }
            ]
          });
        }
        break;

      case 'chart-gauge':
        if (habitosData.length > 0) {
          const promedioGeneral = Math.round(habitosData.reduce((sum, h) => sum + h.porcentaje, 0) / habitosData.length);
          Highcharts.chart(fullscreenId, {
            chart: { type: 'gauge', backgroundColor: COLORS.bg_input },
            title: { text: 'Promedio General de Cumplimiento', style: { color: '#e0e0e0' } },
            pane: { startAngle: -150, endAngle: 150, background: [{ backgroundColor: COLORS.bg_input, borderWidth: 0, outerRadius: '100%' }] },
            yAxis: { min: 0, max: 100, tickInterval: 10, labels: { style: { color: '#e0e0e0' } }, title: { text: 'Porcentaje (%)', style: { color: '#e0e0e0' } }, plotBands: [{ from: 0, to: 60, color: COLORS.warning }, { from: 60, to: 80, color: COLORS.accent }, { from: 80, to: 100, color: COLORS.success }] },
            series: [{ name: 'Cumplimiento', type: 'gauge', data: [promedioGeneral], tooltip: { valueSuffix: '%' } }]
          });
        }
        break;

      case 'chart-radar':
        if (habitosData.length > 0) {
          Highcharts.chart(fullscreenId, {
            chart: { polar: true, type: 'line', backgroundColor: COLORS.bg_input },
            title: { text: 'Gráfico Radar de Cumplimiento', style: { color: '#e0e0e0' } },
            pane: { size: '80%' },
            xAxis: { categories: categorias, tickmarkPlacement: 'on' as const, lineWidth: 0, labels: { style: { color: '#e0e0e0' } } },
            yAxis: { gridLineInterpolation: 'polygon' as const, lineWidth: 0, min: 0, max: 100, labels: { style: { color: '#e0e0e0' } } },
            tooltip: { shared: true, pointFormat: '<span style="color:{series.color}">{series.name}: <b>{point.y:.1f}%</b><br/>' },
            legend: { align: 'center' as const, itemStyle: { color: '#e0e0e0' } },
            series: [{ name: 'Porcentaje Cumplimiento', type: 'line', data: habitosData.map(h => h.porcentaje), pointPlacement: 'on' as const, color: COLORS.accent, fillOpacity: 0.3 }],
            plotOptions: { line: { lineWidth: 2, marker: { enabled: true, radius: 4 } } }
          });
        }
        break;

      case 'chart-bar':
        if (habitosData.length > 0) {
          const habitosOrdenados = [...habitosData].sort((a, b) => b.porcentaje - a.porcentaje);
          Highcharts.chart(fullscreenId, {
            chart: { type: 'bar', backgroundColor: COLORS.bg_input },
            title: { text: 'Top Hábitos por Cumplimiento', style: { color: '#e0e0e0' } },
            xAxis: { categories: habitosOrdenados.map(h => h.nombre), labels: { style: { color: '#e0e0e0' } } },
            yAxis: { min: 0, max: 100, title: { text: 'Porcentaje (%)', style: { color: '#e0e0e0' } }, labels: { style: { color: '#e0e0e0' } } },
            legend: { enabled: false },
            plotOptions: { bar: { borderRadius: 5, dataLabels: { enabled: true, format: '{y}%', style: { color: '#e0e0e0' } }, colorByPoint: true } },
            series: [{ name: 'Cumplimiento', type: 'bar', data: habitosOrdenados.map(h => h.porcentaje) }]
          });
        }
        break;
    }
  }

  // Vuelve a renderizar los gráficos cada vez que los datos cambian
  $: if (!loading && habitosData.length > 0) {
    setTimeout(() => renderizarGraficos(), 0);
  }

  onMount(() => {
    cargarDatos();
  });
</script>

<div class="min-h-screen bg-[#0E0D0D] text-white p-4 md:p-6 pb-24 md:pb-8">
  <!-- Header -->
  <div class="max-w-[95vw] mx-auto mb-6">
    <div class="flex flex-col gap-2">
      <h1 class="text-3xl font-bold text-[#e94560]">Análisis de Hábitos</h1>
      <!-- Rango de fechas seleccionado -->
      <p class="text-[#A0A0A0]">
        Periodo: {fechaInicio} al {fechaFin}
      </p>
    </div>
  </div>

  <!-- Modal de filtros de fecha -->
  {#if showDateFilter}
    <!-- Overlay -->
    <div
      class="fixed inset-0 backdrop-blur-md z-[70] flex items-center justify-center p-4 {isClosing ? 'backdrop-blur-0' : ''} transition-all duration-500"
      onclick={handleCloseModal}
      onkeydown={(e) => e.key === 'Escape' && handleCloseModal()}
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
          <h3 class="text-xl font-bold text-text_primary">📅 Filtrar por Fecha</h3>
          <button
            onclick={handleCloseModal}
            class="text-text_secondary hover:text-accent transition-colors text-2xl"
          >
            ×
          </button>
        </div>

        <div class="space-y-4">
          <!-- Fecha Inicio -->
          <div>
            <label class="block text-text_secondary text-sm mb-1">Fecha Inicio</label>
            <input
              type="date"
              bind:value={fechaInicio}
              class="w-full bg-bg_input border border-border rounded px-3 py-2 text-text_primary focus:border-accent focus:outline-none"
            />
          </div>

          <!-- Fecha Fin -->
          <div>
            <label class="block text-text_secondary text-sm mb-1">Fecha Fin</label>
            <input
              type="date"
              bind:value={fechaFin}
              class="w-full bg-bg_input border border-border rounded px-3 py-2 text-text_primary focus:border-accent focus:outline-none"
            />
          </div>

          <div class="border-t border-border pt-4">
            <p class="text-text_secondary text-sm mb-2">Acceso Rápido</p>
            <div class="grid grid-cols-2 gap-2">
              <button
                type="button"
                onclick={setEsteMes}
                class="bg-bg_input border border-border text-text_primary px-3 py-2 rounded hover:border-accent transition-colors text-sm"
              >
                Este mes
              </button>
              <button
                type="button"
                onclick={setUltimaSemana}
                class="bg-bg_input border border-border text-text_primary px-3 py-2 rounded hover:border-accent transition-colors text-sm"
              >
                Última semana
              </button>
              <button
                type="button"
                onclick={setUltimoMes}
                class="bg-bg_input border border-border text-text_primary px-3 py-2 rounded hover:border-accent transition-colors text-sm"
              >
                Último mes
              </button>
              <button
                type="button"
                onclick={setEsteAnio}
                class="bg-bg_input border border-border text-text_primary px-3 py-2 rounded hover:border-accent transition-colors text-sm"
              >
                Este año
              </button>
            </div>
          </div>

          <!-- Botones -->
          <div class="flex gap-3 pt-4">
            <button
              type="button"
              onclick={handleCloseModal}
              class="flex-1 py-2 px-4 rounded border border-border text-text_secondary hover:border-text_secondary transition-colors"
            >
              Cancelar
            </button>
            <button
              type="button"
              onclick={aplicarFiltro}
              class="flex-1 py-2 px-4 rounded bg-success text-bg_primary font-bold hover:bg-success/80 transition-colors"
            >
              ✓ Aplicar
            </button>
          </div>
        </div>
      </div>
    </div>
  {/if}

  <!-- Error -->
  {#if error}
    <div class="max-w-[95vw] mx-auto mb-6">
      <div class="bg-red-500/10 border border-red-500 text-red-500 p-4 rounded-md">
        {error}
      </div>
    </div>
  {/if}

  <!-- Loading -->
  {#if loading}
    <div class="flex justify-center items-center py-20">
      <div class="w-12 h-12 border-2 border-[#533483] border-t-[#e94560] rounded-full animate-spin"></div>
    </div>
  {:else if habitosData.length === 0}
    <!-- Estado vacío -->
    <div class="max-w-[95vw] mx-auto">
      <div class="bg-[#1a1a1a] border-2 border-dashed border-[#533483] rounded-lg p-8 text-center">
        <p class="text-xl text-[#A0A0A0] mb-2">📭 No hay hábitos</p>
        <p class="text-[#A0A0A0] text-sm">Presiona + para agregar uno</p>
      </div>
    </div>
  {:else}
    <!-- Contenido principal -->
    <div class="max-w-[95vw] mx-auto space-y-6">
      <!-- Tarjetas resumen -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {#each habitosData as habito, i}
          <div
            class="bg-[#1a1a1a] border border-[#533483] rounded-lg p-4 slide-in-blurred-right"
            style="animation-delay: {i * 0.1}s;"
          >
            <h3 class="font-bold text-[#e94560] mb-2 truncate">{habito.nombre}</h3>
            <div class="h-1 rounded-full mb-2" style="background-color: {habito.color};"></div>
            <p class="text-sm text-[#A0A0A0]">Completados: {habito.completados} / {habito.total}</p>
            <p class="text-sm text-[#A0A0A0]">Porcentaje: {habito.porcentaje}%</p>
          </div>
        {/each}
      </div>

      <!-- Separador -->
      <div class="border-t border-[#533483]"></div>

      <!-- Gráficos -->
      <div class="space-y-6">
        <!-- Fila 1: Rendimiento Area + Polar -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div
            class="lg:col-span-2 bg-[#1a1a1a] border border-[#533483] rounded-lg p-4 h-96 md:h-[500px] lg:h-[600px] slide-in-blurred-bottom relative"
            style="animation-delay: 0.3s;"
          >
            <!-- Botón expandir -->
            <button
              onclick={() => openFullscreen('chart-rendimiento-area')}
              class="absolute top-2 right-2 z-10 bg-[#533483] hover:bg-[#7047a8] text-white p-2 rounded-md transition-colors"
              title="Ver en pantalla completa"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
            </button>
            <div id="chart-rendimiento-area" class="w-full h-full"></div>
          </div>
          <div
            class="bg-[#1a1a1a] border border-[#533483] rounded-lg p-4 h-96 md:h-[500px] lg:h-[600px] slide-in-blurred-bottom relative"
            style="animation-delay: 0.4s;"
          >
            <!-- Botón expandir -->
            <button
              onclick={() => openFullscreen('chart-polar')}
              class="absolute top-2 right-2 z-10 bg-[#533483] hover:bg-[#7047a8] text-white p-2 rounded-md transition-colors"
              title="Ver en pantalla completa"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
            </button>
            <div id="chart-polar" class="w-full h-full"></div>
          </div>
        </div>

        <!-- Fila 2: Pie + Spline -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div
            class="bg-[#1a1a1a] border border-[#533483] rounded-lg p-4 h-96 md:h-[500px] lg:h-[600px] slide-in-blurred-bottom relative"
            style="animation-delay: 0.5s;"
          >
            <button
              onclick={() => openFullscreen('chart-pie')}
              class="absolute top-2 right-2 z-10 bg-[#533483] hover:bg-[#7047a8] text-white p-2 rounded-md transition-colors"
              title="Ver en pantalla completa"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
            </button>
            <div id="chart-pie" class="w-full h-full"></div>
          </div>
          <div
            class="lg:col-span-2 bg-[#1a1a1a] border border-[#533483] rounded-lg p-4 h-96 md:h-[500px] lg:h-[600px] slide-in-blurred-bottom relative"
            style="animation-delay: 0.6s;"
          >
            <button
              onclick={() => openFullscreen('chart-spline')}
              class="absolute top-2 right-2 z-10 bg-[#533483] hover:bg-[#7047a8] text-white p-2 rounded-md transition-colors"
              title="Ver en pantalla completa"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
            </button>
            <div id="chart-spline" class="w-full h-full"></div>
          </div>
        </div>

        <!-- Fila 3: Column + Gauge -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div
            class="lg:col-span-2 bg-[#1a1a1a] border border-[#533483] rounded-lg p-4 h-96 md:h-[500px] lg:h-[600px] slide-in-blurred-bottom relative"
            style="animation-delay: 0.7s;"
          >
            <button
              onclick={() => openFullscreen('chart-column')}
              class="absolute top-2 right-2 z-10 bg-[#533483] hover:bg-[#7047a8] text-white p-2 rounded-md transition-colors"
              title="Ver en pantalla completa"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
            </button>
            <div id="chart-column" class="w-full h-full"></div>
          </div>
          <div
            class="bg-[#1a1a1a] border border-[#533483] rounded-lg p-4 h-96 md:h-[500px] lg:h-[600px] slide-in-blurred-bottom relative"
            style="animation-delay: 0.8s;"
          >
            <button
              onclick={() => openFullscreen('chart-gauge')}
              class="absolute top-2 right-2 z-10 bg-[#533483] hover:bg-[#7047a8] text-white p-2 rounded-md transition-colors"
              title="Ver en pantalla completa"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
            </button>
            <div id="chart-gauge" class="w-full h-full"></div>
          </div>
        </div>

        <!-- Fila 4: Radar + Bar -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div
            class="bg-[#1a1a1a] border border-[#533483] rounded-lg p-4 h-96 md:h-[500px] lg:h-[600px] slide-in-blurred-bottom relative"
            style="animation-delay: 0.9s;"
          >
            <button
              onclick={() => openFullscreen('chart-radar')}
              class="absolute top-2 right-2 z-10 bg-[#533483] hover:bg-[#7047a8] text-white p-2 rounded-md transition-colors"
              title="Ver en pantalla completa"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
            </button>
            <div id="chart-radar" class="w-full h-full"></div>
          </div>
          <div
            class="lg:col-span-2 bg-[#1a1a1a] border border-[#533483] rounded-lg p-4 h-96 md:h-[500px] lg:h-[600px] slide-in-blurred-bottom relative"
            style="animation-delay: 1.0s;"
          >
            <button
              onclick={() => openFullscreen('chart-bar')}
              class="absolute top-2 right-2 z-10 bg-[#533483] hover:bg-[#7047a8] text-white p-2 rounded-md transition-colors"
              title="Ver en pantalla completa"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
            </button>
            <div id="chart-bar" class="w-full h-full"></div>
          </div>
        </div>
      </div>
    </div>
  {/if}

  <!-- Floating Action Button (visible en todas las vistas) -->
  <button
    onclick={() => showDateFilter = !showDateFilter}
    class="fixed bottom-20 md:bottom-6 right-6 w-14 h-14 bg-[#533483] hover:bg-[#7047a8] text-white text-2xl rounded-full shadow-lg shadow-[#533483]/30 flex items-center justify-center transition-all hover:scale-110 z-[60]"
    title="Filtrar fechas"
  >
    📅
  </button>

  <!-- Modal Fullscreen para Gráficos -->
  {#if fullscreenChart}
    <div
      class="fixed inset-0 bg-black/95 z-50 flex items-center justify-center p-4 {isClosingFullscreen ? 'opacity-0' : 'opacity-100'} transition-opacity duration-500"
      onclick={closeFullscreen}
      onkeydown={(e) => e.key === 'Escape' && closeFullscreen()}
      role="button"
      tabindex="0"
    >
      <!-- Modal -->
      <div
        class="w-full h-full max-w-[98vw] max-h-[95vh] bg-[#1a1a1a] border-2 border-[#533483] rounded-lg p-4 {isClosingFullscreen ? 'slide-out-blurred-top' : 'bounce-in-top'}"
        onclick={(e) => e.stopPropagation()}
        onkeydown={(e) => e.stopPropagation()}
        role="dialog"
        tabindex="-1"
      >
        <!-- Header con botón cerrar -->
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-xl font-bold text-[#e94560]">Gráfico Ampliado</h3>
          <button
            onclick={closeFullscreen}
            class="text-text_secondary hover:text-accent transition-colors text-3xl font-bold"
            title="Cerrar (ESC)"
          >
            ×
          </button>
        </div>

        <!-- Contenedor del gráfico -->
        <div class="w-full h-[calc(100%-4rem)]">
          <div id="{fullscreenChart}-fullscreen" class="w-full h-full"></div>
        </div>
      </div>
    </div>
  {/if}
</div>
