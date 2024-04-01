import { defineConfig } from 'vite';
import preact from '@preact/preset-vite';

// https://vitejs.dev/config/
export default defineConfig({
	plugins: [preact()],
	base: "/app",
	// server: {
	// 	hmr: {
	// 		protocol: 'wss',
	// 		host: "kotaz.ddnsfree.com",
	// 		port: 24555,
	// 	}
	// }
	server: {
		hmr: false
	}
});
