import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src/pixocr'),
    },
  },
  define: {
    'process.env.NEXT_PUBLIC_API': 'import.meta.env.VITE_API_BASE',
  },
});
