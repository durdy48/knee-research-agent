"""Application layer — use cases that orchestrate the domain and the ports.

Use cases depend on core (models, ports, knowledge_engine) only. They never import
infrastructure directly; concrete adapters are injected.
"""
