import fs from 'fs';
import yaml from 'yaml';
import path from 'path';

// Find the config.yml in the project root (one level up from the frontend directory)
const configPath = path.join(process.cwd(), '..', 'config.yml');
const fileContents = fs.readFileSync(configPath, 'utf8');
const config = yaml.parse(fileContents) as any;

export default config; 