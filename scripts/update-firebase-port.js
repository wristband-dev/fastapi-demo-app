const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

// Resolve paths from the project root, assuming this script is in <project_root>/scripts/
const projectRoot = path.resolve(__dirname, '..');
const configYmlPath = path.join(projectRoot, 'config.yml');
const firebaseJsonPath = path.join(projectRoot, 'database', 'firebase.json');
const firebaseDir = path.dirname(firebaseJsonPath);

function main() {
    let config;
    try {
        const configFileContents = fs.readFileSync(configYmlPath, 'utf8');
        config = yaml.load(configFileContents);
    } catch (err) {
        console.error(`Error reading or parsing ${configYmlPath}: ${err.message}`);
        console.error("Please ensure 'config.yml' exists at the project root and is a valid YAML file.");
        process.exit(1);
    }

    const firestorePort = config && config.database && config.database.port;

    if (typeof firestorePort !== 'number') {
        console.error('Error: database.port not found or is not a number in config.yml.');
        console.error(`Found port value: ${firestorePort} (type: ${typeof firestorePort})`);
        console.error("Please ensure 'config.yml' has 'database:' section with a numeric 'port:' key.");
        process.exit(1);
    }

    let firebaseConfig = {
        emulators: {
            firestore: {},
            ui: { enabled: true } // Default UI settings
        }
    };

    if (fs.existsSync(firebaseJsonPath)) {
        try {
            const firebaseFileContents = fs.readFileSync(firebaseJsonPath, 'utf8');
            // Allow empty file to be overwritten
            if (firebaseFileContents.trim() === '') {
                console.log(`${firebaseJsonPath} is empty. Initializing with default structure.`);
            } else {
                const existingConfig = JSON.parse(firebaseFileContents);
                // Merge carefully, prioritizing existing structure if valid
                firebaseConfig = {
                    ...firebaseConfig, // Start with defaults
                    ...existingConfig, // Overlay existing config
                    emulators: { // Ensure emulators section is well-defined
                        ...firebaseConfig.emulators,
                        ...(existingConfig.emulators || {}),
                        firestore: { // Ensure firestore section is well-defined
                            ...(firebaseConfig.emulators ? firebaseConfig.emulators.firestore : {}),
                            ...((existingConfig.emulators && existingConfig.emulators.firestore) ? existingConfig.emulators.firestore : {}),
                        },
                        ui: { // Ensure ui section is well-defined
                             ...(firebaseConfig.emulators ? firebaseConfig.emulators.ui : { enabled: true }),
                             ...((existingConfig.emulators && existingConfig.emulators.ui) ? existingConfig.emulators.ui : { enabled: true }),
                        }
                    }
                };
            }
        } catch (err) {
            console.warn(`Warning: Could not read or parse existing ${firebaseJsonPath}. It will be overwritten. Error: ${err.message}`);
            // Reset to default structure if parsing fails
            firebaseConfig = {
                emulators: {
                    firestore: {},
                    ui: { enabled: true }
                }
            };
        }
    } else {
        console.log(`${firebaseJsonPath} not found. Creating a new file.`);
    }

    // Set the firestore port
    if (!firebaseConfig.emulators.firestore) firebaseConfig.emulators.firestore = {};
    firebaseConfig.emulators.firestore.port = firestorePort;

    // Ensure UI enabled is present if UI object exists
    if (firebaseConfig.emulators.ui && typeof firebaseConfig.emulators.ui.enabled === 'undefined') {
        firebaseConfig.emulators.ui.enabled = true;
    }


    try {
        if (!fs.existsSync(firebaseDir)) {
            fs.mkdirSync(firebaseDir, { recursive: true });
            console.log(`Created directory ${firebaseDir}`);
        }
        fs.writeFileSync(firebaseJsonPath, JSON.stringify(firebaseConfig, null, 2) + '\n', 'utf8');
        console.log(`Successfully updated/created ${firebaseJsonPath} with Firestore port ${firestorePort}.`);
    } catch (err) {
        console.error(`Error writing ${firebaseJsonPath}: ${err.message}`);
        process.exit(1);
    }
}

main(); 