from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.metrics.base import BaseMetric
from trustwise.sdk.types import (
    PromptInjectionRequest,
    PromptInjectionResponse,
)


class PromptInjectionMetric:
    """Prompt injection detection metric."""
    
    def __init__(self, client: TrustwiseClient) -> None:
        self.client = client
        self.base_url = client.config.get_safety_url("v3")
    
    def evaluate(
        self,
        *,
        query: str | None = None,
        **kwargs
    ) -> PromptInjectionResponse:
        """
        Evaluate the prompt injection risk of a query.

        Args:
            query: The query string (required)

        Returns:
            PromptInjectionResponse containing the evaluation results
        """
        req = BaseMetric.validate_request_model(PromptInjectionRequest, query=query, **kwargs)

        request_dict = req.to_dict()
        request_dict["context"] = [{"node_id": "0", "node_score": 0, "node_text": "placeholder"}] # TODO: Remove this once the API is updated
        request_dict["response"] = "placeholder" # TODO: Remove this once the API is updated

        result = self.client._post(
            endpoint=f"{self.base_url}/prompt_injection",
            data=request_dict
        )
        return PromptInjectionResponse(**result)
    
    def batch_evaluate(
        self,
        inputs: list[PromptInjectionRequest]
    ) -> list[PromptInjectionResponse]:
        """Evaluate multiple inputs for prompt injection attempts."""
        raise NotImplementedError("Batch evaluation not yet supported")
    
    def explain(
        self,
        *,
        query: str,
        **kwargs
    ) -> dict:
        """Get detailed explanation of the prompt injection detection."""
        # req = PromptInjectionRequest(query=query)
        raise NotImplementedError("Explanation not yet supported") 