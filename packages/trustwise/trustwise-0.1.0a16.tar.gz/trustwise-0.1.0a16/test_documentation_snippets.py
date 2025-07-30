# test_documentation_snippets.py
# This script contains all Python code snippets from the Trustwise SDK Sphinx documentation.
# Each section is marked with comments for clarity.

# --- Load .env file ---
from dotenv import load_dotenv
load_dotenv()

# --- Quickstart (index.rst) ---
import os
from trustwise.sdk import TrustwiseSDK
from trustwise.sdk.config import TrustwiseConfig

# Initialize the SDK (using environment variable)
config = TrustwiseConfig(api_key=os.environ.get("TW_API_KEY", "your-api-key"))
trustwise = TrustwiseSDK(config)

# Evaluate faithfulness
result = trustwise.metrics.faithfulness.evaluate(
    query="What is the capital of France?",
    response="The capital of France is Paris.",
    context=[{"node_id": "doc:idx:1", "node_score": 0.95, "node_text": "Paris is the capital of France."}]
)
print(f"Faithfulness score: {result.score}")
print(f"Faithfulness score: {result.score}")
for fact in result.facts:
    print(f"Fact: {fact.statement}, Label: {fact.label}, Probability: {fact.prob}, Span: {fact.sentence_span}")

# --- Basic Setup (usage.rst) ---
# Configure using environment variables
os.environ["TW_API_KEY"] = os.environ.get("TW_API_KEY", "your-api-key")
os.environ["TW_BASE_URL"] = "https://api.trustwise.ai"
config = TrustwiseConfig()

# Or configure directly
# config = TrustwiseConfig(
#     api_key="your-api-key",
#     base_url="https://api.trustwise.ai"
# )

# Initialize the SDK
trustwise = TrustwiseSDK(config)

# --- Evaluating Metrics (usage.rst) ---
# Faithfulness Metric
result = trustwise.metrics.faithfulness.evaluate(
        query="What is the capital of France?",
        response="The capital of France is Paris.",
        context=[
            {"node_id": "1", "node_score": 1.0, "node_text": "Paris is the capital of France."}
        ]
    )
print(result)
print(result.to_json(indent=2))
dict_output = result.to_dict()
print(dict_output)
print('---')

# Cost Metric
cost_result = trustwise.metrics.cost.evaluate(
        model_name="gpt-3.5-turbo",
        model_type="LLM",
        model_provider="OpenAI",
        number_of_queries=5,
        total_prompt_tokens=950,
        total_completion_tokens=50
    )

print(cost_result)
print(cost_result.to_json(indent=2))

# Carbon Metric
carbon_result = trustwise.metrics.carbon.evaluate(
    processor_name="AMD A10-9700",
    provider_name="aws",
    provider_region="us-east-1",
    instance_type="p4d.24xlarge",
    average_latency=100
)

print(carbon_result)
print(carbon_result.to_json(indent=2))

# --- Guardrails (usage.rst & api.rst) ---
# Create a multi-metric guardrail
context = [{"node_id": "1", "node_score": 1.0, "node_text": "Paris is the capital of France."}]
guardrail = trustwise.guardrails(
    thresholds={
        "faithfulness": 0.8,
        "answer_relevancy": 0.7,
        "clarity": 0.7
    },
    block_on_failure=True
)
# Evaluate with multiple metrics
evaluation = guardrail.evaluate(
    query="What is the capital of France?",
    response="The capital of France is Paris.",
    context=context
)
# Pythonic access
print(evaluation.passed)
print(evaluation.results['faithfulness']['result'].score)
# Serialization
print(evaluation.to_dict())
print(evaluation.to_json(indent=2))

# --- Versioning (versioning.rst) ---
# Get available versions
versions = trustwise.get_versions()

# Get current version
print(trustwise.metrics.version)

# Using explicit version path
result = trustwise.metrics.v3.faithfulness.evaluate(
    query="What is the capital of France?",
    response="The capital of France is Paris.",
    context=[{"node_id": "doc:idx:1", "node_score": 0.95, "node_text": "Paris is the capital of France."}]
)

# Using default version
result = trustwise.metrics.faithfulness.evaluate(
    query="What is the capital of France?",
    response="The capital of France is Paris.",
    context=[{"node_id": "doc:idx:1", "node_score": 0.95, "node_text": "Paris is the capital of France."}]
)

# --- Metrics API (metrics.rst) ---
# Example calls for all metrics (with placeholder values)

# # Faithfulness
# trustwise.metrics.faithfulness.evaluate(query="...", response="...", context=[...])
# # Clarity
# trustwise.metrics.clarity.evaluate(query="...", response="...")
# # Cost
# trustwise.metrics.cost.evaluate(model_name="...", model_type="LLM", model_provider="...", number_of_queries=1)
# # Answer Relevancy
# trustwise.metrics.answer_relevancy.evaluate(query="...", response="...", context=[...])
# # Context Relevancy
# trustwise.metrics.context_relevancy.evaluate(query="...", context=[...], response="...")
# # Summarization
# trustwise.metrics.summarization.evaluate(query="...", response="...", context=[...])
# # PII
# trustwise.metrics.pii.evaluate(text="...", allowlist=["..."], blocklist=["..."])
# # Prompt Injection
# trustwise.metrics.prompt_injection.evaluate(query="...", response="...", context=[...])
# # Helpfulness
# trustwise.metrics.helpfulness.evaluate(query="...", response="...")
# # Formality
# trustwise.metrics.formality.evaluate(response="...")
# # Simplicity
# trustwise.metrics.simplicity.evaluate(response="...")
# # Sensitivity
# trustwise.metrics.sensitivity.evaluate(response="...", topics=["politics", "religion"], query=None)
# # Toxicity
# trustwise.metrics.toxicity.evaluate(query=None, response=None, user_id=None)
# # Tone
# trustwise.metrics.tone.evaluate(response="...", query=None)
# # Carbon
# trustwise.metrics.carbon.evaluate(processor_name="...", provider_name="...", provider_region="...", instance_type="...", average_latency=1000)

# --- End of documentation snippets --- 


guardrail = trustwise.guardrails(
    thresholds={
        "faithfulness": 0.8,
        "answer_relevancy": 0.7,
        "clarity": 0.7
    },
    block_on_failure=True
)

# Evaluate with multiple metrics
evaluation = guardrail.evaluate(
    query="What is the capital of France?",
    response="The capital of France is Paris.",
    context=[
        {"node_id": "1", "node_score": 1.0, "node_text": "Paris is the capital of France."}
    ]
)

print(evaluation)
json_output = evaluation.to_json(indent=2)
print(json_output)


from trustwise.sdk import TrustwiseSDK
from trustwise.sdk.config import TrustwiseConfig

# Get available versions
versions = trustwise.get_versions()
print(versions)


print(trustwise.metrics.version)