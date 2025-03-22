import { defineConfig, UserConfig, ConfigEnv } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default ({ command }: ConfigEnv): UserConfig => {
  const isBuild = command === 'build';

  return defineConfig({
    plugins: [react()],
    define: {
      global: {}
    },
    build: {
      target: 'esnext',
      commonjsOptions: {
        transformMixedEsModules: true
      }
    },
    server: {
      port: 4000,
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:5000/',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
        },
      },
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        // Keep these aliases if they're still needed for your React project
        '@airgap/beacon-types': path.resolve(
          path.resolve(),
          `./node_modules/@airgap/beacon-types/dist/${
            isBuild ? 'esm' : 'cjs'
          }/index.js`
        ),
        // polyfills
        'readable-stream': 'vite-compatible-readable-stream',
        stream: 'vite-compatible-readable-stream'
      }
    }
  });
};