#!/usr/bin/env node

/**
 * Custom server to serve Next.js static export with proper CSP headers
 * This fixes the CSP issues that prevent API calls to localhost:8000
 */

const http = require('http');
const path = require('path');
const fs = require('fs');
const url = require('url');

const PORT = process.env.PORT || 9000;
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

// CSP policy that allows localhost connections
const CSP_POLICY = [
  "default-src 'self'",
  "script-src 'self' 'unsafe-eval' 'unsafe-inline'",
  "style-src 'self' 'unsafe-inline'", 
  "img-src 'self' data: https:",
  `connect-src 'self' ${BACKEND_URL} https://api.openai.com https://api.anthropic.com https://*.supabase.co wss://*.supabase.co`,
  "font-src 'self' data:",
  "object-src 'none'",
  "base-uri 'self'",
  "form-action 'self'",
  "frame-ancestors 'none'"
].join('; ');

// Serve static files from the out directory
const staticPath = path.join(__dirname, 'out');

// Check if out directory exists
if (!fs.existsSync(staticPath)) {
  console.error('❌ Error: out directory not found. Please run "npm run build" first.');
  process.exit(1);
}

// MIME types
const mimeTypes = {
  '.html': 'text/html',
  '.js': 'text/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.wav': 'audio/wav',
  '.mp4': 'video/mp4',
  '.woff': 'application/font-woff',
  '.ttf': 'application/font-ttf',
  '.eot': 'application/vnd.ms-fontobject',
  '.otf': 'application/font-otf',
  '.wasm': 'application/wasm'
};

// Create HTTP server
const server = http.createServer((req, res) => {
  // Add security headers
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
  res.setHeader('Content-Security-Policy', CSP_POLICY);

  // CORS headers for development
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  const parsedUrl = url.parse(req.url);
  let pathname = parsedUrl.pathname;

  // Handle root path
  if (pathname === '/') {
    pathname = '/index.html';
  }

  let filePath = path.join(staticPath, pathname);

  // Check if file exists
  if (!fs.existsSync(filePath)) {
    // For client-side routing, serve index.html
    filePath = path.join(staticPath, 'index.html');
  }

  // Get file extension for MIME type
  const ext = path.parse(filePath).ext;
  const mimeType = mimeTypes[ext] || 'text/plain';

  // Read and serve file
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404);
      res.end('Page not found');
      return;
    }

    res.writeHead(200, { 'Content-Type': mimeType });
    res.end(data);
  });
});

// Start server
server.listen(PORT, () => {
  console.log('🌐 PlaybookWiz Frontend Server Started');
  console.log('========================================');
  console.log(`📍 Frontend URL: http://localhost:${PORT}`);
  console.log(`🔗 Backend URL: ${BACKEND_URL}`);
  console.log(`🔒 CSP Policy: ${CSP_POLICY.substring(0, 100)}...`);
  console.log('');
  console.log('✅ CSP configured to allow localhost API calls');
  console.log('✅ Security headers properly set');
  console.log('✅ Client-side routing supported');
  console.log('');
  console.log('🎯 Ready to test API key saving!');
});

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log('\n👋 Shutting down frontend server...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n👋 Shutting down frontend server...');
  process.exit(0);
});
