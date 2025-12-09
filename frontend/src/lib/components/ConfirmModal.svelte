<script lang="ts">
  interface Props {
    title: string;
    message: string;
    confirmText?: string;
    cancelText?: string;
    onConfirm: () => void;
    onCancel: () => void;
  }

  let { 
    title, 
    message, 
    confirmText = "Eliminar", 
    cancelText = "Cancelar",
    onConfirm, 
    onCancel 
  }: Props = $props();

  let isClosing = $state(false);

  function handleClose() {
    isClosing = true;
    // Esperar a que termine la animación slide-out-blurred-top (0.45s)
    setTimeout(() => {
      onCancel();
    }, 450);
  }

  function handleConfirm() {
    isClosing = true;
    setTimeout(() => {
      onConfirm();
    }, 500);
  }
</script>

<!-- Overlay -->
<div 
  class="fixed inset-0 backdrop-blur-md z-50 flex items-center justify-center p-4 {isClosing ? 'backdrop-blur-0' : ''} transition-all duration-500"
  onclick={handleClose}
  onkeydown={(e) => e.key === 'Escape' && handleClose()}
  role="button"
  tabindex="0"
>
  <!-- Modal -->
  <div 
    class="bg-bg_secondary border border-border rounded-lg w-full max-w-sm p-6 {isClosing ? 'slide-out-blurred-top' : 'bounce-in-top'}"
    onclick={(e) => e.stopPropagation()}
    onkeydown={(e) => e.stopPropagation()}
    role="dialog"
    tabindex="-1"
  >
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-bold text-text_primary">
        {title}
      </h2>
      <button 
        onclick={handleClose}
        class="text-text_secondary hover:text-accent transition-colors text-2xl"
      >
        ×
      </button>
    </div>

    <p class="text-text_secondary mb-6">
      {message}
    </p>

    <!-- Botones -->
    <div class="flex gap-3">
      <button
        type="button"
        onclick={handleClose}
        class="flex-1 py-2 px-4 rounded border border-border text-text_secondary hover:border-text_secondary transition-colors"
      >
        {cancelText}
      </button>
      <button
        type="button"
        onclick={handleConfirm}
        class="flex-1 py-2 px-4 rounded bg-accent text-white font-bold hover:bg-accent/80 transition-colors"
      >
        {confirmText}
      </button>
    </div>
  </div>
</div>
