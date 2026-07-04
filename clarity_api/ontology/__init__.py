"""Clarity ontology contribution (CONCEPT:AU-KG.ontology.federation-provider-leg).

Data-only subpackage: it carries ``clarity.ttl`` (the ``owl:Ontology``
``http://knuckles.team/kg/clarity`` module — Clarity projects, aggregate
session-analytics snapshots, named metric insights, and their dimension
breakdowns) which the agent-utilities hub federates in via the
``agent_utilities.ontology_providers`` entry-point. It holds no business logic
and no heavy imports so the hub can resolve it cheaply.
"""
