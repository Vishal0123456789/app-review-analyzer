#!/usr/bin/env node

/**
 * Build script to inject environment variables into index.html
 * This runs after Vite builds, injecting VITE_API_URL into the meta tag
 */

const fs = require('fs');
const path = require('path');

const distDir = path.join(__dirname, 'dist');
const indexPath = path.join(distDir, 'index.html');

// Get API URL from environment variable
const apiUrl = process.env.VITE_API_URL || 'http://localhost:8000';

console.log(`[Build] Injecting API URL: ${apiUrl}`);

// Read the built index.html
let html = fs.readFileSync(indexPath, 'utf-8');

// Replace the meta tag content
html = html.replace(
  /<meta name="api-url" content="" \/>/,
  `<meta name="api-url" content="${apiUrl}" />`
);

// Write back to file
fs.writeFileSync(indexPath, html, 'utf-8');

console.log('[Build] API URL injected successfully');
