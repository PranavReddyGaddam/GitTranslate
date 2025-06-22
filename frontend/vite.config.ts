import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Proxy any browser request to /api/generate
      '/api/generate': {
        // Forward it to your HTTP backend
        target: 'http://3.95.215.8:8000',
        // Rewrite the Host header to match the target
        changeOrigin: true,
        // Allow self-signed or invalid certs (not needed for plain HTTP)
        secure: false,
        // Keep the path unchanged
        rewrite: (path) => path.replace(/^\/api\/generate/, '/api/generate'),
      },
    },
  },
})
