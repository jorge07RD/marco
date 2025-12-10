<script lang="ts">
  import { register } from '$lib/api';
  import { authStore } from '$lib/stores/auth.svelte';
  import { goto } from '$app/navigation';

  let nombre = $state('');
  let email = $state('');
  let contrasena = $state('');
  let confirmarContrasena = $state('');
  let loading = $state(false);
  let error = $state<string | null>(null);
  let success = $state(false);

  async function handleSubmit(e: Event) {
    e.preventDefault();
    error = null;

    // Validaciones
    if (!nombre || !email || !contrasena || !confirmarContrasena) {
      error = 'Todos los campos son obligatorios';
      return;
    }

    if (contrasena.length < 6) {
      error = 'La contraseña debe tener al menos 6 caracteres';
      return;
    }

    if (contrasena !== confirmarContrasena) {
      error = 'Las contraseñas no coinciden';
      return;
    }

    try {
      loading = true;
      const response = await register({ nombre, email, contrasena });

      // Guardar token y usuario en el store
      authStore.login(response.access_token, response.usuario);

      success = true;

      // Redirigir a la página principal después de 1 segundo
      setTimeout(() => {
        goto('/');
      }, 1000);
    } catch (e) {
      error = e instanceof Error ? e.message : 'Error al registrarse';
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>Registro | Hábitos</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center bg-[#0E0D0D] px-4 py-12">
  <div class="w-full max-w-md">
    <!-- Logo / Título -->
    <div class="text-center mb-8">
      <h1 class="text-4xl font-bold text-accent mb-2">🎯 HÁBITOS</h1>
      <p class="text-text_secondary">Crea tu cuenta para comenzar</p>
    </div>

    <!-- Formulario de registro -->
    <fieldset class="border border-border bg-[#1B1B2F] rounded-lg p-6 slide-in-blurred-bottom">
      <legend class="text-accent text-xs font-bold px-2">REGISTRO</legend>

      {#if success}
        <div class="bg-success/20 border border-success text-success px-4 py-3 rounded-lg mb-4 animate-slide-in-down">
          ✓ Cuenta creada exitosamente. Redirigiendo...
        </div>
      {/if}

      {#if error}
        <div class="bg-accent/20 border border-accent text-accent px-4 py-3 rounded-lg mb-4">
          {error}
        </div>
      {/if}

      <form onsubmit={handleSubmit} class="space-y-4">
        <!-- Campo Nombre -->
        <div>
          <label for="nombre" class="block text-text_secondary text-sm mb-2">
            <span class="text-warning">●</span> NOMBRE DE USUARIO
          </label>
          <input
            type="text"
            id="nombre"
            bind:value={nombre}
            disabled={loading}
            class="w-full bg-bg_input border border-border text-text_primary px-4 py-3 rounded-lg focus:border-accent focus:outline-none transition-colors disabled:opacity-50"
            placeholder="Tu nombre de usuario"
            autocomplete="username"
          />
        </div>

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
            autocomplete="new-password"
          />
          <p class="text-text_secondary text-xs mt-1">Mínimo 6 caracteres</p>
        </div>

        <!-- Campo Confirmar Contraseña -->
        <div>
          <label for="confirmar" class="block text-text_secondary text-sm mb-2">
            <span class="text-warning">●</span> CONFIRMAR CONTRASEÑA
          </label>
          <input
            type="password"
            id="confirmar"
            bind:value={confirmarContrasena}
            disabled={loading}
            class="w-full bg-bg_input border border-border text-text_primary px-4 py-3 rounded-lg focus:border-accent focus:outline-none transition-colors disabled:opacity-50"
            placeholder="••••••••"
            autocomplete="new-password"
          />
        </div>

        <!-- Botón Submit -->
        <button
          type="submit"
          disabled={loading}
          class="w-full bg-accent hover:bg-accent/90 text-white font-bold py-3 px-6 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed {loading ? 'animate-pulse' : ''}"
        >
          {loading ? 'CREANDO CUENTA...' : 'CREAR CUENTA'}
        </button>
      </form>

      <!-- Link a Login -->
      <div class="mt-6 text-center">
        <p class="text-text_secondary text-sm">
          ¿Ya tienes cuenta?
          <a href="/login" class="text-accent hover:underline font-semibold ml-1">
            Inicia sesión aquí
          </a>
        </p>
      </div>
    </fieldset>
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
