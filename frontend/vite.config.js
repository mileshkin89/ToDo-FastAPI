import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig(function (_a) {
    var mode = _a.mode;
    var env = loadEnv(mode, process.cwd(), '');
    return {
        plugins: [react()],
        server: {
            proxy: {
                '/api': {
                    target: env.VITE_API_BASE_URL || 'http://localhost:8000',
                    changeOrigin: true,
                },
                '/protected': {
                    target: env.VITE_API_BASE_URL || 'http://localhost:8000',
                    changeOrigin: true,
                },
            },
        },
    };
});
