// eslint-disable-next-line @typescript-eslint/no-var-requires
const { spawn } = require('child_process');

const port = 6001;

console.log(`Attempting to start Vite dev server on port: ${port}`);

const child = spawn('vite', ['--host', '--port', port.toString()], {
  stdio: 'inherit', // Inherit stdio to see Vite output directly
  shell: true, // Useful for cross-platform compatibility with 'vite' command
});

// Display a clear message with the frontend URL
console.log('\n======================================');
console.log(`🚀 FRONTEND IS RUNNING AT: http://localhost:${port}`);
console.log('======================================\n');

child.on('close', (code) => {
  if (code !== 0) {
    console.log(`Vite dev server process exited with code ${code}`);
  }
});

child.on('error', (err) => {
  console.error('Failed to start Vite dev server:', err);
});
