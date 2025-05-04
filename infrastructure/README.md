# GCP Infrastructure for FastAPI and Firebase

This directory contains Terraform configuration to:

1. Check or create the GCP project based on your project_config.yml
2. Set up Firebase and Firestore for your application
3. Configure Cloud Run to host your FastAPI backend
4. Create CI/CD pipelines for both backend and frontend

## Dynamic Configuration

**All configurations are dynamically generated from project_config.yml**:

- The project ID and name are read from project_config.yml
- GitHub owner and repository are automatically extracted from project_config.yml
- Firebase hosting sites are named based on your project ID
- The Cloud Run URL is dynamically detected during deployment
- No hardcoded IDs or URLs anywhere in the infrastructure

## Workflow

For the project creation:
- If the project exists and the user has access: Proceed successfully
- If the project exists but the user doesn't have access: Throw an error
- If the project doesn't exist: Create it (when `check_only = false`)

For the CI/CD pipeline:
- On push to the configured branch (e.g., `develop` for staging), automatically:
  - Build and deploy the FastAPI backend to Cloud Run
  - Build and deploy the frontend to Firebase Hosting
- Manual triggers are also available for both backend and frontend

## How It Works

The infrastructure automatically:
- Reads the project ID, name, and GitHub info from `project_config.yml` at the root of the repository
- Uses this project ID for provider authentication and all resource creation
- Gets the billing account ID from the `GCP_BILLING_ACCOUNT_ID` environment variable (if set)
- Creates separate environments (staging/production) using Terraform variables
- Dynamically configures Firebase hosting for both staging and production
- Detects the Cloud Run URL during deployment to configure the frontend

## Prerequisites

- [Terraform](https://www.terraform.io/downloads.html) installed (v1.0.0+)
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed and configured
- [Firebase CLI](https://firebase.google.com/docs/cli) installed
- Authenticated to Google Cloud (`gcloud auth login`)
- Authenticated to Firebase (`firebase login`)
- GitHub repository with your code
- GCP Billing Account (can be set up manually or via environment variable)

## Configuration

1. Make sure your project_config.yml is set up correctly:

```yaml
project:
    label: "Your Project Name"
    id: "your-project-id"
    description: "Your project description"
github:
    user: "your-github-username"
    repo: "your-github-repo"
```

2. **Set up GCP Billing - Option 1: Environment Variable**:

```bash
# Find your billing account ID using:
gcloud billing accounts list

# Set the environment variable:
export GCP_BILLING_ACCOUNT_ID=XXXXXX-XXXXXX-XXXXXX
```

3. Create a `terraform.tfvars` file based on the example:

```bash
cp terraform.tfvars.example terraform.tfvars
```

4. Edit `terraform.tfvars` to set your configuration:

```hcl
# The GCP region to use
gcp_region = "us-central1"

# Set to false to create the project if it doesn't exist
check_only = false

# The environment to deploy to
environment = "staging"

# The branch that triggers the deployment
trigger_branch = "develop"

# Valid Firestore locations: nam5 (us-central1), eur3 (europe-west)
firestore_location = "nam5"
```

## Billing Account Setup

There are two ways to set up billing for your GCP project:

### Option 1: Environment Variable (Recommended)

```bash
# Find your billing account ID using:
gcloud billing accounts list

# Set the environment variable before running Terraform:
export GCP_BILLING_ACCOUNT_ID=XXXXXX-XXXXXX-XXXXXX
```

### Option 2: Manual Setup

If you don't set the environment variable, Terraform will:
1. Create the project without a billing account
2. Display instructions on how to manually link a billing account
3. You'll need to link the billing account in the GCP Console
4. Run `terraform apply` again to continue with the setup

## Staging vs Production Setup

You can create separate environments by running Terraform with different variable sets:

1. For staging:
```hcl
environment = "staging"
trigger_branch = "develop"
```

2. For production:
```hcl
environment = "production"
trigger_branch = "main"
```

Each environment will create:
- A separate Cloud Run service
- Separate Firestore collection prefixes
- Separate Firebase Hosting sites

## Usage

Initialize Terraform:

```bash
terraform init
```

Validate the configuration:

```bash
terraform plan
```

Apply the configuration:

```bash
terraform apply
```

## Troubleshooting

### Missing Billing Account

If you see an error about missing billing account, you have two options:

1. Set the environment variable and run again:
   ```bash
   export GCP_BILLING_ACCOUNT_ID=XXXXXX-XXXXXX-XXXXXX
   terraform apply
   ```

2. Let Terraform create the project, then:
   - Follow the displayed instructions to manually link a billing account
   - Go to the GCP Console and link the billing account
   - Run `terraform apply` again

### Invalid Firestore Location

If you see an error about invalid Firestore location, make sure you're using a valid location code:
- `nam5`: US Central (Iowa)
- `eur3`: Europe West
- Other valid values: `asia-east1`, `asia-northeast1`, `asia-south1`, `australia-southeast1`, etc.

## Multiple Environments

To manage multiple environments, you can use Terraform workspaces:

```bash
# Create and select the staging workspace
terraform workspace new staging
terraform apply -var-file=staging.tfvars

# Create and select the production workspace
terraform workspace new production
terraform apply -var-file=production.tfvars
```

## Manual Deployments

After setting up the infrastructure, you can manually trigger deployments:

1. For backend (FastAPI):
   - Create a pull request to your configured branch
   - Comment `/gcbrun` on the pull request

2. For frontend:
   - Create a pull request to your configured branch
   - Comment `/gcbrun` on the pull request

## Outputs

- `config_project_id`: The project ID extracted from project_config.yml
- `project_exists`: Whether the project exists in GCP
- `project_name`: The name of the GCP project
- `fastapi_url`: The URL of the deployed FastAPI service
- `firebase_hosting_production`: The Firebase Hosting URL for production
- `firebase_hosting_staging`: The Firebase Hosting URL for staging
- `project_action`: The action performed on the project (exists/created)

## CI/CD Integration

This setup creates Cloud Build triggers that:

1. On push to the configured branch:
   - Build and deploy the FastAPI backend to Cloud Run
   - Build and deploy the frontend to Firebase Hosting

2. For manual triggers (via pull request comments):
   - Same steps as above, but triggered manually

The Firebase configuration includes separate hosting targets for staging and production. 