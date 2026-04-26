import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('@tremor/react')) {
            return 'tremor'
          }
          if (id.includes('node_modules') && (id.includes('react') || id.includes('axios'))) {
            return 'vendor'
          }
        },
      },
    },
  },
})
