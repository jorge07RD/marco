<script lang="ts">
  import '../app.css';
  import type { Snippet } from 'svelte';
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { authStore } from '$lib/stores/auth.svelte';

  interface Props {
    children: Snippet;
  }

  let { children }: Props = $props();

  const navItems = [
    { href: '/', icon: '📊', label: 'Progreso' },
    { href: '/habitos', icon: '🎯', label: 'Hábitos' },
    { href: '/calendario', icon: '📅', label: 'Calendario' },
    { href: '/analisis', icon: '📈', label: 'Análisis' },
    { href: '/settings', icon: '⚙️', label: 'Ajustes' },
  ];

  // Rutas públicas que no requieren autenticación
  const publicRoutes = ['/login', '/register'];

  // Inicializar auth store
  onMount(async () => {
    await authStore.init();
  });

  // Protección de rutas reactiva
  $effect(() => {
    if (authStore.loading) return; // Esperar a que termine de cargar

    const currentPath = $page.url.pathname;
    const isPublicRoute = publicRoutes.includes(currentPath);
    const isAuthenticated = authStore.isAuthenticated;

    // Si está en ruta pública pero autenticado, redirigir a home
    if (isPublicRoute && isAuthenticated) {
      goto('/');
      return;
    }

    // Si está en ruta privada pero no autenticado, redirigir a login
    if (!isPublicRoute && !isAuthenticated) {
      goto('/login');
      return;
    }
  });

  function handleLogout() {
    authStore.logout();
  }
</script>

<div class="flex flex-col min-h-screen bg-[#0E0D0D] text-text-primary">
  <!-- Header Desktop -->
  <header class="hidden md:block bg-bg_secondary border-b border-border px-8 py-4 sticky top-0 z-50">
    <nav class="max-w-6xl mx-auto flex justify-between items-center">
      <a href="/" class="text-xl font-bold text-accent">🎯 HÁBITOS</a>

      {#if authStore.isAuthenticated}
        <ul class="flex gap-6 list-none items-center">
          {#each navItems as item}
            <li>
              <a
                href={item.href}
                class="transition-colors {$page.url.pathname === item.href ? 'text-accent font-semibold' : 'text-text_secondary hover:text-accent'}"
              >
                {item.label}
              </a>
            </li>
          {/each}

          <!-- User Info & Logout -->
          <li class="flex items-center gap-4 ml-4 pl-4 border-l border-border">
            <span class="text-text_secondary text-sm">
              Hola, <span class="text-white font-medium">{authStore.user?.nombre}</span>
            </span>
            <button
              onclick={handleLogout}
              class="px-4 py-2 bg-[#e94560] text-white rounded-md hover:bg-[#d13851]
                     transition-colors text-sm font-medium"
            >
              Cerrar Sesión
            </button>
          </li>
        </ul>
      {/if}
    </nav>
  </header>

  <!-- Header Móvil -->
  <header class="md:hidden bg-bg_secondary border-b border-border px-4 py-3 sticky top-0 z-50">
    <div class="flex justify-between items-center">
      <span class="text-lg font-bold text-accent">🎯 HÁBITOS</span>
      {#if authStore.isAuthenticated}
        <button
          onclick={handleLogout}
          class="px-3 py-1.5 bg-[#e94560] text-white rounded-md hover:bg-[#d13851]
                 transition-colors text-xs font-medium"
        >
          Salir
        </button>
      {/if}
    </div>
  </header>

  <main class="flex-1">
    {#if authStore.loading}
      <!-- Loading State mientras se verifica autenticación -->
      <div class="flex items-center justify-center min-h-[60vh]">
        <div class="flex flex-col items-center gap-4">
          <svg class="animate-spin h-12 w-12 text-accent" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p class="text-text_secondary">Cargando...</p>
        </div>
      </div>
    {:else}
      {@render children()}
    {/if}
  </main>

  <!-- Bottom Navigation Móvil -->
  {#if authStore.isAuthenticated}
    <nav class="md:hidden fixed bottom-0 left-0 right-0 bg-bg_secondary border-t border-border z-50">
      <ul class="flex justify-around items-center list-none py-2">
        {#each navItems as item}
          <li>
            <a
              href={item.href}
              class="flex flex-col items-center gap-1 px-4 py-2 transition-colors {$page.url.pathname === item.href ? 'text-accent' : 'text-text_secondary'}"
            >
              <span class="text-xl">{item.icon}</span>
              <span class="text-xs">{item.label}</span>
            </a>
          </li>
        {/each}
      </ul>
    </nav>
  {/if}

  <!-- Footer Desktop -->
  <footer class="hidden md:block bg-bg_secondary border-t border-border p-6 text-center text-text_secondary text-sm">
    <p>Dashboard &copy; 2024</p>
  </footer>
</div>
