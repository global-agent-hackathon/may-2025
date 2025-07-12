import { processHtmlFiles, createRobotsTxt, generateSitemap } from './publish-functions.js';
import { fileURLToPath } from 'url';
import path from 'path';

// Get the publish directory from command line args
const publishDir = process.argv[2];
const baseUrl = process.argv[3] || 'http://localhost';

if (!publishDir) {
  console.error('Error: No publish directory specified');
  process.exit(1);
}

console.log(`Post-processing website in: ${publishDir}`);

// Run all optimization tasks
processHtmlFiles(publishDir);
createRobotsTxt(publishDir, true);
generateSitemap(publishDir, baseUrl);

console.log('Post-processing complete!');
