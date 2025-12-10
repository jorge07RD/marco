<script lang="ts">
  import { goto } from '$app/navigation';
  import { registrar } from '$lib/api';
  import { authStore } from '$lib/stores/auth.svelte';

  let nombre = $state('');
  let email = $state('');
  let password = $state('');
  let confirmPassword = $state('');
  let loading = $state(false);
  let error = $state<string | null>(null);

  // Validaciones
  let passwordsMatch = $derived(password === confirmPassword);
  let passwordLength = $derived(password.length >= 8);
  let formValid = $derived(
    nombre.length > 0 &&
    email.length > 0 &&
    passwordLength &&
    passwordsMatch
  );

  async function handleRegister(e: Event) {
    e.preventDefault();

    if (!formValid) return;

    loading = true;
    error = null;

    try {
      const response = await registrar({
        nombre,
        email,
        password,
        ver_futuro: false
      });

      authStore.setUser(response.user);

      // Redirigir a la página principal
      goto('/');
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error desconocido al registrar';
      console.error('Error en registro:', err);
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>Registrarse - Marco</title>
</svelte:head>

<div class="min-h-screen bg-[#0E0D0D] flex items-center justify-center p-4">
  <div class="bg-[#1a1a1a] border border-[#533483] rounded-lg p-8 max-w-md w-full shadow-xl">
    <!-- Header -->
    <div class="text-center mb-8">
      <h1 class="text-3xl font-bold text-white mb-2">
        Crear Cuenta
      </h1>
      <p class="text-[#A0A0A0]">
        Comienza a trackear tus hábitos hoy
      </p>
    </div>

    <!-- Error Message -->
    {#if error}
      <div class="bg-red-500/10 border border-red-500 text-red-500 p-3 rounded-md mb-6 text-sm">
        <strong>Error:</strong> {error}
      </div>
    {/if}

    <!-- Register Form -->
    <form onsubmit={handleRegister} class="space-y-5">
      <!-- Nombre -->
      <div>
        <label for="nombre" class="block text-sm font-medium text-white mb-2">
          Nombre
        </label>
        <input
          id="nombre"
          type="text"
          bind:value={nombre}
          required
          disabled={loading}
          placeholder="Tu nombre"
          class="w-full bg-[#0E0D0D] border border-[#533483] text-white px-4 py-3
                 rounded-md focus:outline-none focus:ring-2 focus:ring-[#e94560]
                 transition-all disabled:opacity-50 disabled:cursor-not-allowed
                 placeholder:text-[#A0A0A0]"
        />
      </div>

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
          minlength="8"
          disabled={loading}
          placeholder="Mínimo 8 caracteres"
          class="w-full bg-[#0E0D0D] border border-[#533483] text-white px-4 py-3
                 rounded-md focus:outline-none focus:ring-2 focus:ring-[#e94560]
                 transition-all disabled:opacity-50 disabled:cursor-not-allowed
                 placeholder:text-[#A0A0A0]
                 {password && !passwordLength ? 'border-red-500' : ''}"
        />
        {#if password && !passwordLength}
          <p class="text-red-500 text-xs mt-1">
            La contraseña debe tener al menos 8 caracteres
          </p>
        {/if}
      </div>

      <!-- Confirm Password -->
      <div>
        <label for="confirmPassword" class="block text-sm font-medium text-white mb-2">
          Confirmar Contraseña
        </label>
        <input
          id="confirmPassword"
          type="password"
          bind:value={confirmPassword}
          required
          disabled={loading}
          placeholder="Repite tu contraseña"
          class="w-full bg-[#0E0D0D] border border-[#533483] text-white px-4 py-3
                 rounded-md focus:outline-none focus:ring-2 focus:ring-[#e94560]
                 transition-all disabled:opacity-50 disabled:cursor-not-allowed
                 placeholder:text-[#A0A0A0]
                 {confirmPassword && !passwordsMatch ? 'border-red-500' : ''}"
        />
        {#if confirmPassword && !passwordsMatch}
          <p class="text-red-500 text-xs mt-1">
            Las contraseñas no coinciden
          </p>
        {/if}
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
            Creando cuenta...
          </span>
        {:else}
          Crear Cuenta
        {/if}
      </button>
    </form>

    <!-- Login Link -->
    <div class="mt-6 text-center">
      <p class="text-[#A0A0A0]">
        ¿Ya tienes cuenta?
        <a
          href="/login"
          class="text-[#e94560] hover:text-[#d13851] font-medium transition-colors"
        >
          Inicia sesión aquí
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
