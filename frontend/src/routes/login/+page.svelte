<script lang="ts">
  import { goto } from '$app/navigation';
  import { login } from '$lib/api';
  import { authStore } from '$lib/stores/auth.svelte';

  let email = $state('');
  let password = $state('');
  let loading = $state(false);
  let error = $state<string | null>(null);

  // Validación simple
  let formValid = $derived(
    email.length > 0 &&
    password.length >= 6
  );

  async function handleLogin(e: Event) {
    e.preventDefault();

    if (!formValid) return;

    loading = true;
    error = null;

    try {
      const response = await login({ email, password });
      authStore.setUser(response.user);

      // Redirigir a la página principal
      goto('/');
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error desconocido al iniciar sesión';
      console.error('Error en login:', err);
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>Iniciar Sesión - Marco</title>
</svelte:head>

<div class="min-h-screen bg-[#0E0D0D] flex items-center justify-center p-4">
  <div class="bg-[#1a1a1a] border border-[#533483] rounded-lg p-8 max-w-md w-full shadow-xl">
    <!-- Header -->
    <div class="text-center mb-8">
      <h1 class="text-3xl font-bold text-white mb-2">
        ¡Bienvenido de nuevo!
      </h1>
      <p class="text-[#A0A0A0]">
        Inicia sesión para continuar con tus hábitos
      </p>
    </div>

    <!-- Error Message -->
    {#if error}
      <div class="bg-red-500/10 border border-red-500 text-red-500 p-3 rounded-md mb-6 text-sm">
        <strong>Error:</strong> {error}
      </div>
    {/if}

    <!-- Login Form -->
    <form onsubmit={handleLogin} class="space-y-5">
      <!-- Email -->
      <div>
        <label for="email" class="block text-sm font-medium text-white mb-2">
          Correo Electrónico
        </label>
        <input
          id="email"
          type="email"
          bind:value={email}
          required
          disabled={loading}
          placeholder="tu@email.com"
          class="w-full bg-[#0E0D0D] border border-[#533483] text-white px-4 py-3
                 rounded-md focus:outline-none focus:ring-2 focus:ring-[#e94560]
                 transition-all disabled:opacity-50 disabled:cursor-not-allowed
                 placeholder:text-[#A0A0A0]"
        />
      </div>

      <!-- Password -->
      <div>
        <label for="password" class="block text-sm font-medium text-white mb-2">
          Contraseña
        </label>
        <input
          id="password"
          type="password"
          bind:value={password}
          required
          minlength="6"
          disabled={loading}
          placeholder="••••••••"
          class="w-full bg-[#0E0D0D] border border-[#533483] text-white px-4 py-3
                 rounded-md focus:outline-none focus:ring-2 focus:ring-[#e94560]
                 transition-all disabled:opacity-50 disabled:cursor-not-allowed
                 placeholder:text-[#A0A0A0]"
        />
      </div>

      <!-- Submit Button -->
      <button
        type="submit"
        disabled={!formValid || loading}
        class="w-full bg-[#e94560] text-white py-3 px-4 rounded-md font-medium text-lg
               hover:bg-[#d13851] transition-colors disabled:opacity-50
               disabled:cursor-not-allowed disabled:hover:bg-[#e94560]
               focus:outline-none focus:ring-2 focus:ring-[#e94560] focus:ring-offset-2
               focus:ring-offset-[#1a1a1a]"
      >
        {#if loading}
          <span class="flex items-center justify-center gap-2">
            <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Iniciando sesión...
          </span>
        {:else}
          Iniciar Sesión
        {/if}
      </button>
    </form>

    <!-- Register Link -->
    <div class="mt-6 text-center">
      <p class="text-[#A0A0A0]">
        ¿No tienes cuenta?
        <a
          href="/register"
          class="text-[#e94560] hover:text-[#d13851] font-medium transition-colors"
        >
          Regístrate aquí
        </a>
      </p>
    </div>
  </div>
</div>

<style>
  /* Animación sutil para el formulario */
  form {
    animation: fadeIn 0.3s ease-in;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
</style>
