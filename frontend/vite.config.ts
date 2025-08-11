import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import viteTsconfigPaths from 'vite-tsconfig-paths';
import svgr from 'vite-plugin-svgr';

export default defineConfig({
  build: {
    chunkSizeWarningLimit: 1600,
    outDir: 'dist',
  },
  plugins: [
    react({
      jsxRuntime: 'automatic',
    }),
    svgr(),
    viteTsconfigPaths()
  ],
  server: {
    allowedHosts: ['.business.invotastic.com', 'localhost'],
    cors: true,
    port: 6001,
    proxy: {
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: false,
        secure: false,
        headers: { Connection: 'keep-alive' },
      },
    },
  },
});
