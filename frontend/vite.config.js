import { defineConfig } from 'vite';
import { resolve } from 'path';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
    base: '/',
    plugins: [
        tailwindcss(),
    ],
    server: {
        host: '0.0.0.0',
    },
    build: {
        rollupOptions: {
            input: {
                main: resolve(__dirname, 'index.html'),
                detail: resolve(__dirname, 'detail.html'),
                info: resolve(__dirname, 'info.html'),
                evaluation: resolve(__dirname, 'evaluation.html'),
                line: resolve(__dirname, 'line.html')
            },
        },
    },
});
