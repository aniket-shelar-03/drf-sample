# drfsample/test_generator/generate_all_tests.py

import os
import yaml
from drfsample.test_generator.generate_tests import load_openapi, generate_tests_for_endpoint

OPENAPI_PATH = "http://localhost:8000/api/schema/"  # Update this path
TESTS_DIR = os.path.join(os.path.dirname(__file__), "tests")
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "sample_values.yaml")

def extract_sample_values(details):
    """Extract sample values from parameters and requestBody."""
    samples = {}
    # Parameters
    for param in details.get("parameters", []):
        name = param.get("name")
        example = param.get("example") or param.get("schema", {}).get("example")
        if name and example is not None:
            samples[name] = example
    # Request body (for POST)
    if "requestBody" in details:
        content = details["requestBody"].get("content", {})
        for media_type, media_details in content.items():
            example = media_details.get("example")
            if not example:
                schema = media_details.get("schema", {})
                example = schema.get("example")
            if example:
                samples["body"] = example
    return samples

def main():
    spec = load_openapi(OPENAPI_PATH)
    paths = spec.get("paths", {})
    os.makedirs(TESTS_DIR, exist_ok=True)
    config = {}

    for path, methods in paths.items():
        for method, details in methods.items():
            if method.lower() in ("get", "post"):
                # Generate a valid Python filename for the endpoint
                endpoint_name = path.strip("/").replace("/", "_").replace("{", "").replace("}", "")
                if not endpoint_name:
                    endpoint_name = "root"
                filename = f"test_{method.lower()}_{endpoint_name}.py"
                filepath = os.path.join(TESTS_DIR, filename)

                # Generate test code for this endpoint
                test_code = generate_tests_for_endpoint(path, method, details, spec)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(test_code)
                print(f"Generated {filepath}")

                # Collect sample values for config
                config_key = f"{method.upper()} {path}"
                config[config_key] = extract_sample_values(details)

    # Write config file
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False)
    print(f"Generated config file: {CONFIG_PATH}")

if __name__ == "__main__":
    main()