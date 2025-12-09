<script lang="ts">
  import '../app.css';
  import type { Snippet } from 'svelte';
  import { page } from '$app/stores';

  interface Props {
    children: Snippet;
  }

  let { children }: Props = $props();

  const navItems = [
    { href: '/', icon: '📊', label: 'Progreso' },
    { href: '/habitos', icon: '🎯', label: 'Hábitos' },
    { href: '/charts', icon: '📈', label: 'Análisis' },
    { href: '/settings', icon: '⚙️', label: 'Ajustes' },
  ];
</script>

<div class="flex flex-col min-h-screen bg-[#0E0D0D] text-text-primary">
  <!-- Header Desktop -->
  <header class="hidden md:block bg-bg_secondary border-b border-border px-8 py-4 sticky top-0 z-50">
    <nav class="max-w-6xl mx-auto flex justify-between items-center">
      <a href="/" class="text-xl font-bold text-accent">🎯 HÁBITOS</a>
      <ul class="flex gap-6 list-none">
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
      </ul>
    </nav>
  </header>

  <!-- Header Móvil -->
  <header class="md:hidden bg-bg_secondary border-b border-border px-4 py-3 sticky top-0 z-50">
    <div class="flex justify-center items-center">
      <span class="text-lg font-bold text-accent">🎯 HÁBITOS</span>
    </div>
  </header>

  <main class="flex-1">
    {@render children()}
  </main>

  <!-- Bottom Navigation Móvil -->
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

  <!-- Footer Desktop -->
  <footer class="hidden md:block bg-bg_secondary border-t border-border p-6 text-center text-text_secondary text-sm">
    <p>Dashboard &copy; 2024</p>
  </footer>
</div>
