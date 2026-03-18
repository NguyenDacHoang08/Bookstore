import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

type ProxyTarget = {
  target: string
  changeOrigin: boolean
}

const proxyTarget = (target: string): ProxyTarget => ({
  target,
  changeOrigin: true,
})

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': proxyTarget('http://localhost:8000'),
    },
  },
})
