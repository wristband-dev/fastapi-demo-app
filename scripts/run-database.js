const fs = require('node:fs');
const yaml = require('js-yaml');
const { spawn } = require('node:child_process');

try {
    // Read and parse config.yml (path relative to project root, as npm scripts run from project root)
    const configFile = fs.readFileSync('config.yml', 'utf8');
    const config = yaml.load(configFile);

    const dbPort = config.database.port;
    const projectId = config.database.project_id;
    
    // Construct FIRESTORE_EMULATOR_HOST using "127.0.0.1" and the dynamic port from config.yml
    const firestoreEmulatorHost = `127.0.0.1:${dbPort}`;

    console.log(`Preparing to start database emulator with dynamic configuration:`);
    console.log(`  FIRESTORE_EMULATOR_HOST=${firestoreEmulatorHost}`);
    console.log(`  GOOGLE_CLOUD_PROJECT=${projectId}`);
    console.log(`  Using project ID for Firebase CLI: ${projectId}`);

    const firebaseCommand = 'firebase';
    const args = [
        'emulators:start',
        '--only',
        'firestore',
        '--project',
        projectId // Use dynamic project ID from config
    ];

    // Execute the command.
    // The 'cwd' option is set to 'database' because Firebase CLI typically expects to be run
    // from the directory containing firebase.json and other Firebase project files.
    const dbProcess = spawn(firebaseCommand, args, {
        env: {
            ...process.env, // Inherit current environment variables
            FIRESTORE_EMULATOR_HOST: firestoreEmulatorHost,
            GOOGLE_CLOUD_PROJECT: projectId,
        },
        cwd: 'database', 
        stdio: 'inherit' // Pipe output (stdout, stderr) to the current terminal
    });

    dbProcess.on('error', (err) => {
        console.error('Failed to start database process. Make sure Firebase CLI is installed and in your PATH.', err);
        process.exit(1); // Exit if spawn itself fails (e.g., command not found)
    });

    // Handle process exit to provide feedback, especially on errors.
    dbProcess.on('exit', (code, signal) => {
        if (signal) {
            console.log(`Database process was killed with signal ${signal}`);
        } else if (code !== null && code !== 0) {
            // Non-zero exit code indicates an error from the firebase command itself.
            console.log(`Database process exited with error code ${code}. Check Firebase emulator logs above for details.`);
        } else if (code === 0) {
            console.log('Database process exited successfully.');
        } else {
            // This case should ideally not be reached if code or signal is always present on exit.
            console.log('Database process exited.'); 
        }
    });

} catch (e) {
    console.error('Error setting up or running database emulator:', e.message);
    if (e.code === 'ENOENT' && e.path === 'config.yml') {
        console.error('Ensure config.yml exists at the project root.');
    }
    process.exit(1); // Exit the script with an error code
} 