/**
 * Vilcos Publishing Functions
 * 
 * This module contains utilities for optimizing and publishing static site content
 */

// Import required modules
import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

/**
 * Optimize HTML files by removing comments and minimizing
 * @param {string} htmlContent - The HTML content to optimize
 * @returns {string} - Optimized HTML
 */
function optimizeHtml(htmlContent) {
  // Remove comments (except conditional comments)
  const withoutComments = htmlContent.replace(/<!--(?![\[\]>])[\s\S]*?-->/g, '');
  
  // Remove extra whitespace (simple minification)
  const minified = withoutComments
    .replace(/\s+/g, ' ')
    .replace(/>\s+</g, '><')
    .trim();
  
  return minified;
}

/**
 * Process all HTML files in a directory
 * @param {string} directory - Directory containing HTML files
 */
function processHtmlFiles(directory) {
  try {
    // Read all files in the directory
    const files = fs.readdirSync(directory);
    
    // Process each file
    files.forEach(file => {
      const filePath = path.join(directory, file);
      const stat = fs.statSync(filePath);
      
      if (stat.isDirectory()) {
        // Recursively process subdirectories
        processHtmlFiles(filePath);
      } else if (file.endsWith('.html')) {
        // Process HTML files
        console.log(`Optimizing: ${filePath}`);
        const content = fs.readFileSync(filePath, 'utf8');
        const optimized = optimizeHtml(content);
        fs.writeFileSync(filePath, optimized, 'utf8');
      }
    });
    
    console.log(`Processed HTML files in: ${directory}`);
  } catch (error) {
    console.error(`Error processing directory ${directory}:`, error);
  }
}

/**
 * Create a robots.txt file for the published site
 * @param {string} directory - Target directory
 * @param {boolean} allowIndexing - Whether to allow search engines to index the site
 */
function createRobotsTxt(directory, allowIndexing = true) {
  const content = allowIndexing 
    ? `User-agent: *\nAllow: /\nSitemap: /sitemap.xml`
    : `User-agent: *\nDisallow: /`;
  
  fs.writeFileSync(path.join(directory, 'robots.txt'), content, 'utf8');
  console.log(`Created robots.txt in: ${directory}`);
}

/**
 * Generate a basic sitemap for the site
 * @param {string} directory - Target directory
 * @param {string} baseUrl - Base URL for the site
 */
function generateSitemap(directory, baseUrl = 'http://localhost') {
  try {
    const pages = [];
    
    // Find all HTML files recursively
    function findHtmlFiles(dir, relativePath = '') {
      const files = fs.readdirSync(dir);
      
      files.forEach(file => {
        const filePath = path.join(dir, file);
        const stat = fs.statSync(filePath);
        
        if (stat.isDirectory()) {
          findHtmlFiles(filePath, path.join(relativePath, file));
        } else if (file.endsWith('.html')) {
          // Add to pages list with relative path
          const pageUrl = path.join(relativePath, file)
            .replace(/\\/g, '/'); // Convert backslashes to forward slashes
          pages.push(pageUrl);
        }
      });
    }
    
    findHtmlFiles(directory);
    
    // Generate sitemap XML
    let sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n';
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n';
    
    pages.forEach(page => {
      // Clean up the URL
      const cleanUrl = page.startsWith('/') ? page : `/${page}`;
      
      sitemap += '  <url>\n';
      sitemap += `    <loc>${baseUrl}${cleanUrl}</loc>\n`;
      sitemap += '    <changefreq>weekly</changefreq>\n';
      sitemap += '  </url>\n';
    });
    
    sitemap += '</urlset>';
    
    fs.writeFileSync(path.join(directory, 'sitemap.xml'), sitemap, 'utf8');
    console.log(`Generated sitemap.xml with ${pages.length} pages in: ${directory}`);
  } catch (error) {
    console.error('Error generating sitemap:', error);
  }
}

// Export the functions
export {
  optimizeHtml,
  processHtmlFiles,
  createRobotsTxt,
  generateSitemap
}; 