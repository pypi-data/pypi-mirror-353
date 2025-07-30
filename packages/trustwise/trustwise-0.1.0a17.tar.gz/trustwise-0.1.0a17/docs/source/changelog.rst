Changelog
=========

All notable changes to the Trustwise SDK will be documented in this file.

v1.0.0 (06-11-2025)
-------------------

Features
~~~~~~~~

- Initial release of Trustwise Python SDK
- Unified interface for evaluating AI-generated content across 14+ metrics:
  - Faithfulness
  - Answer Relevancy
  - Context Relevancy
  - Summarization
  - Prompt Injection Detection
  - PII Detection
  - Clarity
  - Helpfulness
  - Toxicity
  - Tone
  - Formality
  - Simplicity
  - Sensitivity
  - Cost Estimation
  - Carbon Emissions
- Experimental guardrails system for multi-metric validation, threshold configuration, and block-on-failure functionality
- Cost and carbon emissions estimation for model runs
- Flexible configuration via environment variables or direct instantiation (API key, base URL, etc.)
- Strong type definitions for all request and response objects
- Serialization support: all responses can be converted to JSON and Python dicts for easy integration
- Explicit and default API versioning with version switching and fallback
- Designed for extensibility to support future metrics and features
- Comprehensive documentation, including quickstart, usage, and API reference

Metrics
-------

- Added support for context-based faithfulness, answer relevancy, and other metrics
- Implemented query-response alignment scoring
- Added cost and carbon evaluation for model runs

Guardrails System (Experimental)
^^^^^^^^^^^^^^^^^

- Added multi-metric guardrail system with configurable thresholds
- Implemented block-on-failure functionality
- Added support for comprehensive evaluation result aggregation
- Introduced flexible threshold configuration per metric

Version Management
^^^^^^^^^^^^^^^^^^

- Added explicit version support for all API endpoints
- Implemented default version fallback system
- Added version switching capabilities
- Introduced version-aware evaluation methods

Configuration
^^^^^^^^^^^^^

- Added environment variable based configuration
- Implemented direct configuration through TrustwiseConfig
- Added support for API key and base URL configuration
- Introduced flexible configuration options for all features 