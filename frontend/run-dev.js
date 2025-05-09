const fs = require('fs');
const path = require('path');
const yaml = require('yaml');
const { spawn } = require('child_process');

// Path to config.yml, assuming it's in the parent directory of 'frontend'
const configPath = path.join(__dirname, '../config.yml');
const DEFAULT_PORT = 3000; // Default port if not found in config or config is missing
let port = DEFAULT_PORT;

try {
  if (fs.existsSync(configPath)) {
    const fileContents = fs.readFileSync(configPath, 'utf8');
    const appConfig = yaml.parse(fileContents);
    if (appConfig && appConfig.frontend && typeof appConfig.frontend.port === 'number') {
      port = appConfig.frontend.port;
    } else {
      console.warn(`WARN: 'frontend.port' not found or invalid in ${configPath}. Using default port ${DEFAULT_PORT}.`);
    }
  } else {
    console.warn(`WARN: ${configPath} not found. Using default port ${DEFAULT_PORT}.`);
  }
} catch (error) {
  console.error(`ERROR: Could not read or parse ${configPath}. Using default port ${DEFAULT_PORT}.`, error);
}

console.log(`Attempting to start Next.js dev server on port: ${port}`);

const child = spawn('next', ['dev', '-p', port.toString()], {
  stdio: 'inherit', // Inherit stdio to see Next.js output directly
  shell: true // Useful for cross-platform compatibility with 'next' command
});

child.on('close', (code) => {
  if (code !== 0) {
    console.log(`Next.js dev server process exited with code ${code}`);
  }
});

child.on('error', (err) => {
  console.error('Failed to start Next.js dev server:', err);
}); 