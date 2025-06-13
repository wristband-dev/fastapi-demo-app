const { spawn } = require('child_process');

const port = 3001;

console.log(`Attempting to start Next.js dev server on port: ${port}`);

const child = spawn('next', ['dev', '-p', port.toString()], {
  stdio: 'inherit', // Inherit stdio to see Next.js output directly
  shell: true // Useful for cross-platform compatibility with 'next' command
});

// Display a clear message with the frontend URL
console.log('\n======================================');
console.log(`🚀 FRONTEND IS RUNNING AT: http://localhost:${port}`);
console.log('======================================\n');

child.on('close', (code) => {
  if (code !== 0) {
    console.log(`Next.js dev server process exited with code ${code}`);
  }
});

child.on('error', (err) => {
  console.error('Failed to start Next.js dev server:', err);
}); 
