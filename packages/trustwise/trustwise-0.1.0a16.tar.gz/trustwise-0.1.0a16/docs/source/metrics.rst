.. _metrics:

Metrics
=======
The SDK provides access to all metrics through the unified ``metrics`` namespace. Each metric provides an ``evaluate()`` function. Example usage:

.. code-block:: python

    result = trustwise.metrics.faithfulness.evaluate(query="...", response="...", context=[...])
    clarity = trustwise.metrics.clarity.evaluate(query="...", response="...")
    cost = trustwise.metrics.cost.evaluate(model_name="...", model_type="LLM", ...)

Refer to the API reference for details on each metric's parameters.

.. note::
   Custom types such as ``Context`` are defined in :mod:`trustwise.sdk.types`.

Faithfulness
~~~~~~~~~~~~
.. function:: metrics.faithfulness.evaluate(query: str, response: str, context: list[ContextNode]) -> FaithfulnessResponse

   Evaluate the faithfulness of a response against its context.

   Parameters:

   - query (:class:`str`): The input query
   - response (:class:`str`): The response to evaluate
   - context (:class:`~trustwise.sdk.types.Context`): Context information (list of :class:`~trustwise.sdk.types.ContextNode`)

   Returns:

    - :class:`~trustwise.sdk.types.FaithfulnessResponse`
   
   Example response:

     .. code-block:: json

        {
            "score": 99.971924,
            "facts": [
                    {
                    "statement": "The capital of France is Paris.",
                    "label": "Safe",
                    "prob": 0.9997192,
                    "sentence_span": [
                        0,
                        30
                    ]
                }
            ]
        }

Answer Relevancy
~~~~~~~~~~~~~~~~
.. function:: metrics.answer_relevancy.evaluate(query: str, response: str, context: list[ContextNode]) -> AnswerRelevancyResponse

   Evaluate the relevancy of a response to the query.

   Parameters:

   - query (:class:`str`): The input query
   - response (:class:`str`): The response to evaluate
   - context (:class:`~trustwise.sdk.types.Context`): Context information (list of :class:`~trustwise.sdk.types.ContextNode`)

   Returns:

    - :class:`~trustwise.sdk.types.AnswerRelevancyResponse`
   
   Example response:

     .. code-block:: json

        {
            "score": 92.0,
            "generated_question": "What is the capital city of France?"
        }

Context Relevancy
~~~~~~~~~~~~~~~~~
.. function:: metrics.context_relevancy.evaluate(query: str, context: list[ContextNode], response: str) -> ContextRelevancyResponse

   Evaluate the relevancy of the context to the query.

   Parameters:

   - query (:class:`str`): The input query
   - context (:class:`~trustwise.sdk.types.Context`): Context information (list of :class:`~trustwise.sdk.types.ContextNode`)
   - response (:class:`str`): The response to evaluate

   Returns:

    - :class:`~trustwise.sdk.types.ContextRelevancyResponse`
   
   Example response:

     .. code-block:: json

        {
            "score": 88.5,
            "topics": ["geography", "capitals", "France"],
            "scores": [0.92, 0.85, 0.88]
        }

Summarization
~~~~~~~~~~~~~
.. function:: metrics.summarization.evaluate(query: str, response: str, context: list[ContextNode]) -> SummarizationResponse

   Evaluate the quality of a summary.

   Parameters:

   - query (:class:`str`): The input query
   - response (:class:`str`): The response to evaluate
   - context (:class:`~trustwise.sdk.types.Context`): Context information (list of :class:`~trustwise.sdk.types.ContextNode`)

   Returns:

   - :class:`~trustwise.sdk.types.SummarizationResponse`
   
   Example response:

     .. code-block:: json

        {
            "score": 90.0
        }

PII
~~~
.. function:: metrics.pii.evaluate(text: str, allowlist: list[str], blocklist: list[str]) -> PIIResponse

   Detect personally identifiable information in text.

   Parameters:

   - text (:class:`str`): The text to analyze
   - allowlist (:class:`list`\[:class:`str`\]): List of allowed PII patterns
   - blocklist (:class:`list`\[:class:`str`\]): List of blocked PII patterns

   Returns:

   - :class:`~trustwise.sdk.types.PIIResponse`
   
   Example response:

     .. code-block:: json

        {
            "identified_pii": [
                {
                    "interval": [0, 5],
                    "string": "Hello",
                    "category": "blocklist"
                },
                {
                    "interval": [94, 111],
                    "string": "www.wikipedia.org",
                    "category": "organization"
                }
            ]
        }

Prompt Injection
~~~~~~~~~~~~~~~~
.. function:: metrics.prompt_injection.evaluate(query: str, response: str, context: list[ContextNode]) -> PromptInjectionResponse

   Detect potential prompt injection attempts.

   Parameters:

   - query (:class:`str`): The input query
   - response (:class:`str`): The response to evaluate
   - context (:class:`list`\[:class:`~trustwise.sdk.types.ContextNode`\]): Context information (list of :class:`~trustwise.sdk.types.ContextNode`)

   Returns:

   - :class:`~trustwise.sdk.types.PromptInjectionResponse`
   
   Example response:

     .. code-block:: json

        {
            "score": 98.0
        }

Clarity
~~~~~~~
.. function:: metrics.clarity.evaluate(response: str) -> ClarityResponse

   Evaluate the clarity of a response.

   Parameters:
   
   - response (:class:`str`): The response to evaluate

   Returns:

   - :class:`~trustwise.sdk.types.ClarityResponse`
   
   Example response:

     .. code-block:: json

        {
            "score": 92.5
        }

Helpfulness
~~~~~~~~~~~
.. function:: metrics.helpfulness.evaluate(response: str) -> HelpfulnessResponse

   Evaluate the helpfulness of a response.

   Parameters:

   - response (:class:`str`): The response to evaluate

   Returns:

   - :class:`~trustwise.sdk.types.HelpfulnessResponse`
   
   Example response:

     .. code-block:: json

        {
            "score": 88.0
        }

Formality
~~~~~~~~~
.. function:: metrics.formality.evaluate(response: str) -> FormalityResponse

   Evaluate the formality level of a response.

   Parameters:

   - response (:class:`str`): The response to evaluate

   Returns:

   - :class:`~trustwise.sdk.types.FormalityResponse`
   
   Example response:

     .. code-block:: json

        {
            "score": 75.0,
            "sentences": [
                "The capital of France is Paris."
            ],
            "scores": [0.75]
        }

Simplicity
~~~~~~~~~~
.. function:: metrics.simplicity.evaluate(response: str) -> SimplicityResponse

   Evaluate the simplicity of a response.

   Parameters:

   - response (:class:`str`): The response to evaluate

   Returns:

   - :class:`~trustwise.sdk.types.SimplicityResponse`
   
   Example response:

     .. code-block:: json

        {
            "score": 82.0
        }

Sensitivity
~~~~~~~~~~~
.. function:: metrics.sensitivity.evaluate(response: str, topics: list[str]) -> SensitivityResponse

   Evaluate the sensitivity of a response regarding specific topics.

   Parameters:

   - response (:class:`str`): The response to evaluate
   - topics (:class:`list`\[:class:`str`\]): List of topics to evaluate sensitivity for

   Returns:

   - :class:`~trustwise.sdk.types.SensitivityResponse`
   
   Example response:

     .. code-block:: json

        {
            "scores": {
                "politics": 0.70,
                "religion": 0.60
            }
        }

Tone
~~~~
.. function:: metrics.tone.evaluate(response: str) -> ToneResponse

   Evaluate the tone of a response.

   Parameters:

   - response (:class:`str`): The response to evaluate

   Returns:

   - :class:`~trustwise.sdk.types.ToneResponse`
   
   Example response:

     .. code-block:: json

        {
            "labels": [
                "neutral",
                "happiness",
                "realization"
            ],
            "scores": [
                89.704185,
                6.6798472,
                2.9873204
            ]
        }

Cost
~~~~
.. function:: metrics.cost.evaluate(model_name: str, model_type: str, model_provider: str, number_of_queries: int, total_prompt_tokens: Optional[int] = None, total_completion_tokens: Optional[int] = None, total_tokens: Optional[int] = None, instance_type: Optional[str] = None, average_latency: Optional[float] = None) -> CostResponse

   Evaluates the cost of API usage based on token counts, model information, and infrastructure details.

   Parameters:

   - model_name (:class:`str`): Name of the model
   - model_type (:class:`str`): Type of model (LLM or Reranker)
   - model_provider (:class:`str`): Provider of the model
   - number_of_queries (:class:`int`): Number of queries to evaluate
   - total_prompt_tokens (:class:`Optional`\[:class:`int`\]): Total prompt tokens
   - total_completion_tokens (:class:`Optional`\[:class:`int`\]): Total completion tokens
   - total_tokens (:class:`Optional`\[:class:`int`\]): Total tokens (for Together Reranker)
   - instance_type (:class:`Optional`\[:class:`str`\]): Instance type (for Hugging Face)
   - average_latency (:class:`Optional`\[:class:`float`\]): Average latency in milliseconds

   Returns:

   - :class:`~trustwise.sdk.types.CostResponse`
   
   Example response:

     .. code-block:: json

        {
            "cost_estimate_per_run": 0.0025,
            "total_project_cost_estimate": 0.0125
        }

Carbon
~~~~~~
.. function:: metrics.carbon.evaluate(processor_name: str, provider_name: str, provider_region: str, instance_type: str, average_latency: int) -> CarbonResponse

   Evaluates the carbon emissions based on hardware specifications and infrastructure details.

   Parameters:

   - processor_name (:class:`str`): Name of the processor
   - provider_name (:class:`str`): Name of the cloud provider
   - provider_region (:class:`str`): Region of the cloud provider
   - instance_type (:class:`str`): Type of instance
   - average_latency (:class:`int`): Average latency in milliseconds

   Returns:

   - :class:`~trustwise.sdk.types.CarbonResponse`
   
   Example response:

     .. code-block:: json

        {
            "carbon_emitted": 0.00015,
            "sci_per_api_call": 0.00003,
            "sci_per_10k_calls": 0.3
        }

.. note::
   For more details on SDK usage and advanced features, see the :doc:`api` reference. 

Toxicity
~~~~~~~~
.. function:: metrics.toxicity.evaluate(response: str) -> ToxicityResponse

   Evaluate the toxicity of a response.

   Parameters:

   - response (:class:`str`): The response to evaluate

   Returns:

    - :class:`~trustwise.sdk.types.ToxicityResponse`
   
   Example response:

     .. code-block:: json

        {
            "labels": [
                "identity_hate",
                "insult",
                "threat",
                "obscene",
                "toxic"
            ],
            "scores": [
                0.036089644,
                0.06207772,
                0.027964465,
                0.105483316,
                0.3622106
            ]
        } 