/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  /**
   * The NextJS server starts on port 3001, and the FastAPI server starts on port 6001.
   * NextJS is configured with rewrites to forward all /api/* requests to the FastAPI backend at
   * http://localhost:6001/api/*. This allows the frontend to make clean API calls using relative
   * URLs like /api/nickname while keeping the backend services separate and maintainable. The
   * FastAPI server includes CORS middleware to allow cross-origin requests from the NextJS frontend.
   */
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `http://localhost:6001/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig; 
