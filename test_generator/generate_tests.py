import os
import requests
import json
import openai
import yaml


# openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = "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"


def load_openapi(swagger_url):
    print(f"Fetching Swagger/OpenAPI spec from: {swagger_url}")
    response = requests.get(swagger_url)

    if response.status_code != 200:
        raise Exception(f"Unable to download swagger file: {response.status_code}")

    try:
        return response.json()
    except ValueError:
        return yaml.safe_load(response.text)


def generate_tests_for_endpoint(path, method, schemas, details):

    cleaned_path = path.strip("/").replace("/", "_").replace("{", "").replace("}", "")
    prompt = f"""
Generate a pytest test case for this API endpoint based on the Swagger/OpenAPI schema.

Endpoint:
  {method.upper()} {path}

OpenAPI Schema:
{json.dumps(details, indent=2)}

Requirements:
- Use `requests` library
- Create a test function name like: test_{method}_{cleaned_path}
- Use schema definitions from {json.dumps(schemas, indent=2)}
- Add assertions for status code, schema fields, required params
- Use example values from the schema if present
- Format as valid Python code only and strip any explanations
- Consider the base url as `http://localhost:8000`
"""
    print("Prompt for AI:\n", prompt)
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    # print(response.choices[0].message.content)

    return response.choices[0].message.content


def save_test_file(path, method, content):
    safe_path = path.strip("/").replace("/", "_").replace("{", "").replace("}", "")
    filename = f"tests/test_{method}_{safe_path}.py"

    os.makedirs("tests", exist_ok=True)

    with open(filename, "w") as f:
        f.write(content)

    print(f"Saved: {filename}")


def main():
    # swagger_url = input("Enter Swagger/OpenAPI URL: ").strip()
    swagger_url = "http://localhost:8000/api/schema/"
    spec = load_openapi(swagger_url)

    paths = spec.get("paths", {})

    schemas = spec.get("components", {}).get("schemas", {})

    print(f"Found {len(paths)} endpoints. Generating tests...\n")

    for path, methods in paths.items():
        for method, details in methods.items():
            if method.lower() in ["get", "post"] and "/docappauthors/" in path :
                print(f"Generating test: {method.upper()} {path}")
                ai_test = generate_tests_for_endpoint(path, method, schemas, details)
                save_test_file(path, method, ai_test)

    print("\n Done! Test cases generated in /tests folder.")


if __name__ == "__main__":
    main()
