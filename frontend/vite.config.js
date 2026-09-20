import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const backend = 'http://127.0.0.1:8000'

function proxyApi() {
  return {
    target: backend,
    changeOrigin: true,
  }
}

function proxyApiComRotaFrontend() {
  return {
    target: backend,
    changeOrigin: true,

    bypass(req) {
      const accept = req.headers.accept || ''

      // Navegação do navegador:
      // deixa o Vite servir index.html para o React Router.
      if (
        req.method === 'GET' &&
        accept.includes('text/html')
      ) {
        return req.url
      }
    },
  }
}

export default defineConfig({
  plugins: [react()],

  server: {
    host: '0.0.0.0',
    port: 5173,

    // Ambiente temporário de desenvolvimento via Cloudflare Tunnel
    allowedHosts: true,

    proxy: {
      '/auth': proxyApi(),

      // Também são rotas do React.
      '/chat': proxyApiComRotaFrontend(),
      '/tarefas': proxyApiComRotaFrontend(),

      '/usuarios': proxyApi(),
      '/conversas': proxyApi(),
      '/mensagens': proxyApi(),
      '/memorias': proxyApi(),

      '/database': proxyApi(),
      '/health': proxyApi(),
    },
  },
})
