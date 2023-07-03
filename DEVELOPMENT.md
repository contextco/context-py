# Development Instructions

## Building a new version

1. Generate new code from the OpenAPI Spec:

   ```
   autorest README.md --input-file=/Users/alex/scratch/context/web/swagger/v1/swagger.yaml
   ```

2. Test changes by running the examples with a Context API key:

   ```
   GETCONTEXT_TOKEN=*** poetry run python examples/log_conversation.py
   ```

3. Bump the version in `pyproject.toml`

## Publishing

1. Build a new version:

   ```
   poetry build
   ```

2. Publish the new version:
   
   ```
   poetry publish
   ```
