import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Standard Vite + React config. Nothing fancy — keeps the build simple.
export default defineConfig({
  plugins: [react()],
});
