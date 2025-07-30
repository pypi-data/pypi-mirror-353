# llm-templates-fsspec
Load LLM templates from local paths and cloud storage (S3, GCS, Azure) using any
supported fsspec URL scheme.

Lear more about Filesystem Spec (fsspec) and it's features in https://filesystem-spec.readthedocs.io/

## Installation
Install this plugin in the same environment as [LLM](https://llm.datasette.io/).

```bash
llm install llm-templates-fsspec
```

or add it along your project if using a environment manager like `poetry` or `uv`

```bash
# with Poetry
poetry add llm llm-templates-fsspec
# with UV
uv add llm llm-templates-fsspec
```

## Usage

### Load templates from local filesystem
```bash
llm -t fsspec:file:///home/user/templates/summary.yaml
```

### Load templates from AWS S3
```bash
# Configure AWS credentials first
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret

llm -t fsspec:s3://my-bucket/templates/analyze.yaml
```

### Load templates from Google Cloud Storage
```bash
# Configure GCP credentials
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

llm -t fsspec:gs://my-bucket/templates/review.yaml
```

### Load templates from Azure Blob Storage
```bash
# Configure Azure credentials
export AZURE_STORAGE_ACCOUNT_NAME=myaccount
export AZURE_STORAGE_ACCOUNT_KEY=mykey

llm -t fsspec:az://my-container/templates/report.yaml
```

### Load templates from HTTP/HTTPS
```bash
llm -t fsspec:https://example.com/templates/chatbot.yaml
```

### Load templates from FTP
```bash
llm -t fsspec:ftp://ftp.example.com/templates/assistant.yaml
```

## Why fsspec?

The `llm-templates-fsspec` plugin leverages the robust `fsspec` library to provide:

- **Universal Access**: Single interface for templates stored anywhere - local files, S3, GCS, Azure, FTP, HTTP, and [more built-in implementations](https://filesystem-spec.readthedocs.io/en/latest/api.html#implementations)
- **Production Ready**: Battle-tested library used by pandas, dask, and other major data tools
- **Credential Management**: Integrates with standard credential chains (AWS CLI, gcloud, environment variables)
- **Caching**: Built-in caching support for remote templates to improve performance
- **Extensibility**: Support for new storage backends

## Examples
### Using templates from local

```bash
# Assuming your on this repository cloned in your computer.
cat README.md | llm -t "fsspec:file://$(pwd)/demo/template-demo.yaml"
```

### Using templates from a private S3 bucket
```bash
# Template in private bucket with AWS CLI credentials configured
curl https://example.com/data.json | \
  llm -t fsspec:s3://private-bucket/templates/analyze-json.yaml
```

### Caching remote templates locally
```bash
# Set cache directory for better performance with remote templates
export LLM_TEMPLATES_FSSPEC_CACHE_DIR=/tmp/llm-template-cache

# First run downloads and caches the template
llm -t fsspec:https://raw.githubusercontent.com/org/repo/main/template.yaml "Analyze this"

# Subsequent runs use the cached versio
llm -t fsspec:https://raw.githubusercontent.com/org/repo/main/template.yaml "Analyze that"
```

### Using templates from a corporate GCS bucket
```bash
# With service account key file
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
llm -t fsspec:gs://company-ai-assets/templates/legal-review.yaml < contract.txt
```

### Loading templates with custom storage options
```bash
# Pass additional storage options via environment variable
export LLM_TEMPLATES_FSSPEC_STORAGE_OPTIONS='{"client_kwargs": {"region_name": "eu-west-1"}}'
llm -t fsspec:s3://eu-bucket/templates/gdpr-check.yaml
```

## Configuration

### Environment Variables

- `LLM_TEMPLATES_FSSPEC_CACHE_DIR`: Directory for caching remote templates (optional)
- `LLM_TEMPLATES_FSSPEC_STORAGE_OPTIONS`: JSON string of additional fsspec storage options (optional)

### Credential Configuration

This plugin uses standard credential chains for each cloud provider:

- **AWS S3**: AWS CLI configuration, environment variables, or IAM roles
- **Google Cloud Storage**: Application default credentials or service account key file
- **Azure Blob Storage**: Environment variables or Azure CLI credentials

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment using [UV](https://docs.astral.sh/uv/)

```bash
cd llm-templates-fsspec
uv venv
uv sync
source venv/bin/activate
```

Now install the dependencies and test dependencies:
```bash
llm install -e '.[test]'
```

To run the tests:
```bash
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

Apache 2.0