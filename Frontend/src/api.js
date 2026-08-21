// Central place for the backend URL.
// Set VITE_API_URL in a .env file (Vite requires the VITE_ prefix).
// Locally: VITE_API_URL=http://127.0.0.1:8000
// In prod (Vercel/Netlify): VITE_API_URL=https://your-backend.onrender.com
export const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
