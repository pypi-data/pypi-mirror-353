from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.types import ToxicityRequest, ToxicityResponse


class ToxicityMetric:
    """Toxicity metric for evaluating response toxicity."""
    def __init__(self, client: TrustwiseClient) -> None:
        self.client = client
        self.base_url = client.config.get_alignment_url("v1")

    def evaluate(
        self,
        *,
        response: str | None = None,
        **kwargs
    ) -> ToxicityResponse:
        """
        Evaluate the toxicity of a response.

        Args:
            response: The response string (required)

        Returns:
            ToxicityResponse containing the evaluation results
        """
        req = ToxicityRequest(response=response, **kwargs)
        result = self.client._post(
            endpoint=f"{self.base_url}/toxicity",
            data=req.to_dict()
        )
        return ToxicityResponse(**result)

    def batch_evaluate(
        self,
        inputs: list[ToxicityRequest]
    ) -> list[ToxicityResponse]:
        """Evaluate multiple inputs for toxicity."""
        raise NotImplementedError("Batch evaluation not yet supported")

    def explain(
        self,
        *,
        response: str,
        **kwargs
    ) -> dict:
        """Get detailed explanation of the toxicity evaluation."""
        # req = ToxicityRequest(response=response)
        raise NotImplementedError("Explanation not yet supported") 