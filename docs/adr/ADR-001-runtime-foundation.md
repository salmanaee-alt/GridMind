# ADR-001 — Runtime Foundation and Unified Engine Contract

## Status

ACCEPTED

## Context

GridMind has an approved Reasoning Framework containing multiple future
reasoning engines, including confidence propagation, evidence aggregation,
hypothesis competition, constraint evaluation, and decision scoring.

The Master Architecture requires these engines to be deterministic,
explainable, auditable, observable, and non-authoritative by default.

The architecture currently leaves engine discovery, registration,
execution contracts, and composition as an open architectural item.

Implementing additional reasoning engines before defining a shared runtime
contract would create inconsistent APIs and increase coupling.

## Decision

Introduce a small domain-agnostic Runtime Foundation containing:

- ExecutionContext
- EngineMetadata
- EngineResult
- EngineDiagnostics
- Engine protocol
- EngineRegistry
- Context validation
- Shared execution status types
- Foundation exceptions

The Foundation layer SHALL contain no transformer, relay, protection,
knowledge, physics, or other engineering-domain logic.

Reasoning engines SHALL interact with runtime state through ExecutionContext
rather than defining engine-specific runtime contexts.

New reasoning engines SHALL return EngineResult.

New reasoning engines SHALL be registered through EngineRegistry.

## Alternatives Considered

### Kernel

Rejected for now.

A Kernel would introduce orchestration and lifecycle responsibilities before
the system has demonstrated the need for a kernel abstraction.

### Engine-specific contracts

Rejected.

This would make reasoning engines difficult to compose and would create
duplicated runtime infrastructure.

### Direct EngineeringSession dependencies

Rejected for new reasoning engines.

This would couple reasoning engines to Brain/session implementation details.

## Consequences

### Positive

- Stable engine API.
- Lower coupling.
- Easier engine composition.
- Consistent diagnostics.
- Easier testing.
- Future capability/runtime integration.

### Trade-offs

- Adds a small abstraction layer.
- Existing components are not immediately migrated.
- Migration will occur incrementally.

## Safety

The Runtime Foundation does not grant execution authority.

Runtime engines remain non-authoritative unless explicitly promoted through
a separate architecture decision.

## Architectural Constraints

The Foundation layer MUST remain domain-agnostic.

It MUST NOT contain:

- transformer logic
- protection logic
- physics equations
- asset-specific logic
- control-system execution logic

## Decision Owner

Chief Architect

AI reviewers may provide recommendations but do not own architectural authority.