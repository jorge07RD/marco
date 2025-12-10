<script lang="ts">
  import { login } from '$lib/api';
  import { authStore } from '$lib/stores/auth.svelte';
  import { goto } from '$app/navigation';

  let email = $state('');
  let contrasena = $state('');
  let loading = $state(false);
  let error = $state<string | null>(null);
  let success = $state(false);

  async function handleSubmit(e: Event) {
    e.preventDefault();
    error = null;

    // Validaciones
    if (!email || !contrasena) {
      error = 'Email y contraseña son obligatorios';
      return;
    }

    try {
      loading = true;
      const response = await login({ email, contrasena });

      // Guardar token y usuario en el store
      authStore.login(response.access_token, response.usuario);

      success = true;

      // Redirigir a la página principal después de 1 segundo
      setTimeout(() => {
        goto('/');
      }, 1000);
    } catch (e) {
      error = e instanceof Error ? e.message : 'Error al iniciar sesión';
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>Login | Hábitos</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center bg-[#0E0D0D] px-4 py-12">
  <div class="w-full max-w-md">
    <!-- Logo / Título -->
    <div class="text-center mb-8">
      <h1 class="text-4xl font-bold text-accent mb-2">🎯 HÁBITOS</h1>
      <p class="text-text_secondary">Inicia sesión para continuar</p>
    </div>

    <!-- Formulario de login -->
    <fieldset class="border border-border bg-[#1B1B2F] rounded-lg p-6 slide-in-blurred-bottom">
      <legend class="text-accent text-xs font-bold px-2">INICIAR SESIÓN</legend>

      {#if success}
        <div class="bg-success/20 border border-success text-success px-4 py-3 rounded-lg mb-4 animate-slide-in-down">
          ✓ Sesión iniciada exitosamente. Redirigiendo...
        </div>
      {/if}

      {#if error}
        <div class="bg-accent/20 border border-accent text-accent px-4 py-3 rounded-lg mb-4">
          {error}
        </div>
      {/if}

      <form onsubmit={handleSubmit} class="space-y-4">
        <!-- Campo Email -->
        <div>
          <label for="email" class="block text-text_secondary text-sm mb-2">
            <span class="text-warning">●</span> EMAIL
          </label>
          <input
            type="email"
            id="email"
            bind:value={email}
            disabled={loading}
            class="w-full bg-bg_input border border-border text-text_primary px-4 py-3 rounded-lg focus:border-accent focus:outline-none transition-colors disabled:opacity-50"
            placeholder="tu@email.com"
            autocomplete="email"
          />
        </div>

        <!-- Campo Contraseña -->
        <div>
          <label for="contrasena" class="block text-text_secondary text-sm mb-2">
            <span class="text-warning">●</span> CONTRASEÑA
          </label>
          <input
            type="password"
            id="contrasena"
            bind:value={contrasena}
            disabled={loading}
            class="w-full bg-bg_input border border-border text-text_primary px-4 py-3 rounded-lg focus:border-accent focus:outline-none transition-colors disabled:opacity-50"
            placeholder="••••••••"
            autocomplete="current-password"
          />
        </div>

        <!-- Botón Submit -->
        <button
          type="submit"
          disabled={loading}
          class="w-full bg-accent hover:bg-accent/90 text-white font-bold py-3 px-6 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed {loading ? 'animate-pulse' : ''}"
        >
          {loading ? 'INICIANDO SESIÓN...' : 'INICIAR SESIÓN'}
        </button>
      </form>

      <!-- Link a Registro -->
      <div class="mt-6 text-center">
        <p class="text-text_secondary text-sm">
          ¿No tienes cuenta?
          <a href="/register" class="text-accent hover:underline font-semibold ml-1">
            Regístrate aquí
          </a>
        </p>
      </div>
    </fieldset>

    <!-- Información adicional -->
    <div class="mt-6 text-center">
      <p class="text-text_secondary text-xs">
        Al iniciar sesión, aceptas nuestros términos y condiciones
      </p>
    </div>
  </div>
</div>

<style>
  @keyframes slide-in-down {
    0% {
      opacity: 0;
      transform: translateY(-20px);
    }
    100% {
      opacity: 1;
      transform: translateY(0);
    }
  }

  :global(.animate-slide-in-down) {
    animation: slide-in-down 0.3s ease-out;
  }
</style>
