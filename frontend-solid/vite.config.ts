import { defineConfig } from 'vite';
import solidPlugin from 'vite-plugin-solid';
import path from 'path';

export default defineConfig({
  plugins: [solidPlugin()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@solidjs/router': path.resolve(__dirname, 'node_modules/@solidjs/router/dist/index.js'), // Força o uso do .js compilado
    },
    conditions: ['default', 'module', 'import', 'browser'], 
  },
  server: {
    port: 3000,
    open: true, // Abrir navegador automaticamente
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  },
  build: {
    target: 'esnext',
  },
});