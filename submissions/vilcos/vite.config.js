import { defineConfig } from 'vite';
import tailwindcss from 'tailwindcss';
import autoprefixer from 'autoprefixer';
import { resolve } from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  css: {
    postcss: {
      plugins: [tailwindcss(), autoprefixer()],
    },
  },
  build: {
    // Output directory (relative to this config file)
    outDir: 'dist',
    // Simply use templates/ as the root when building
    root: 'templates'
  },
  // Use templates/ as the root for the dev server
  root: 'templates',
  server: {
    // Enhanced file watching for better live reloading
    watch: {
      usePolling: true,
      interval: 100
    },
    open: true
  },
  preview: {
    port: 3000
  }
}); 