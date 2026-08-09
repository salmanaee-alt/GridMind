# ADR-002 — Canonical Runtime Architecture

## 1. Status

ACCEPTED.

This ADR formalizes Option C (Layered Runtime) from `RUNTIME_ARCHITECTURE_ANALYSIS.md`, which the architecture owner has approved as the preferred direction. Per ADR-001's own precedent — "AI reviewers may provide recommendations but do not own architectural authority" — this document records that direction as a proposed, not yet accepted, architectural decision. Formal ACCEPTED status requires the same sign-off ADR-001 required: a named Decision Owner (§21), through the project's ADR process (Handbook Part V §3; docs/adr/).

This ADR documents a decision. It does not implement one. No code in the repository is changed by this document.

## 2. Context

ADR-001 introduced a small, domain-agnostic Runtime Foundation (`app/foundation/`) so future reasoning engines would share one contract instead of each inventing its own runtime plumbing. ADR-001 was accepted and implemented: `ExecutionContext`, `EngineMetadata`, `EngineResult`, `EngineDiagnostics`, the `Engine` protocol, and `EngineRegistry` all exist, are fully unit-tested, and are constrained to remain domain-agnostic by a dedicated architecture-boundary test.

A repository review conducted after ADR-001 (`GridMind_Repository_Review_PreSpec.md`) found that Foundation currently has **zero consumers**. It also found three other, independently-evolved runtime-like mechanisms already live in the codebase, none of them built on Foundation and none structurally compatible with it:

- **Capability Runtime** (`app/capabilities/`) — a mature registry/runtime/orchestrator system with ABI-versioned manifests, shadow-mode enforcement, optional process isolation, and dependency-ordered pipelines. Live-wired into the `/transformer/differential-trip` endpoint. Has no ADR.
- **Thinking Stage Processor** (`app/thinking/`) — a fixed, 11-stage, fully-immutable state-threading pipeline over `ThinkingState`. Live-wired into `EngineeringBrain`. Has no ADR.
- **Reasoning Contracts** (`app/reasoning/`) — the result/contribution contracts for Confidence Propagation, the engine ADR-001 was itself motivated by. The engine implementation is empty (0 bytes); the existing contract independently re-defines the same shadow-safety fields `EngineResult` already provides, rather than using it.

`RUNTIME_ARCHITECTURE_ANALYSIS.md` examined all four mechanisms against ADR-001 and the current repository only, produced three options (Minimal Migration, Unified Runtime, Layered Runtime), and recommended Layered Runtime. That recommendation is what this ADR formalizes.

## 3. Problem Statement

GridMind's repository contains four structurally different contracts for "a unit of runtime work," with no documented, canonical relationship between them. This has already produced duplicated runtime infrastructure inside the one module ADR-001 was written to prevent it in (`ConfidencePropagationResult` re-declares `shadow_only`/`affects_reasoning`/`affects_decision` instead of using `EngineResult`). It leaves the most mature and most exercised of the four mechanisms (Capability Runtime) with no architectural governance at all. And it leaves every future engine, capability, or processing stage without a settled answer to "which pattern do I follow," which is the exact condition ADR-001's Context section identified as the original problem, now recurring one layer up.

## 4. Decision Drivers

- Prevent further duplication of runtime infrastructure (already observed once; likely to recur without a decision).
- Preserve tested, safety-relevant behavior that already exceeds Foundation's minimal scope: Capability Runtime's process isolation and `Literal`-locked `affects_decision` fields; Thinking's `Literal`-locked shadow flags and immutable state-threading.
- Avoid unreviewed breaking changes to live, production-exercised call sites (`app/transformer/engineer.py`, `app/brain/engineering_brain.py`).
- Close the governance gap around Capability Runtime without pretending its scope is smaller than it is.
- Avoid re-deciding the Kernel/orchestration question ADR-001 already closed, without a dedicated ADR for that specific question.
- Make forward progress using decisions already accepted (Reasoning engines implementing `Engine` is ADR-001's existing mandate, not a new one) rather than only proposing new ones.

## 5. Decision

Adopt a **Layered Runtime Architecture**:

- Foundation (`app/foundation/`) remains the innermost, domain-agnostic layer, **unchanged in scope** from ADR-001.
- Reasoning engines **SHALL** implement the `Engine` protocol directly against Foundation. This reaffirms ADR-001 §"Decision" without modification; it does not newly decide anything.
- Capability Runtime and Thinking Runtime **SHALL each expose an `Engine`-compatible boundary adapter**, while retaining their own internal, specialized machinery (Capability's orchestration/process-isolation/manifest-validation; Thinking's fixed stage sequence and state-threading). Neither mechanism's internal contract is replaced.
- Foundation's own contracts **SHALL be tightened**, not expanded: `EngineResult.shadow_only`, `.affects_reasoning`, and `.affects_decision` are to move from plain `bool` defaults to `Literal`-constrained fields, matching the guarantee already present on `CapabilityMetadata`, `CapabilityResult`, `ConfidencePropagationResult`, and `ThinkingState`. This is a refinement of an existing contract, not a new feature.
- Diagnostics **SHALL** converge on `EngineDiagnostics`'s shape as the common vocabulary, additively, without requiring control-flow changes in the mechanisms adopting it.
- Validation **remains specialized per layer** (a context is not the same thing as a capability registration or a state, and is not validated the same way) but **SHALL** keep the shared stateless-validator / frozen-result pattern Foundation already established.
- Runtime orchestration beyond what Capability Runtime already does (i.e., a general-purpose Kernel) is **explicitly out of scope for this ADR** and is deferred to a future ADR (§20).

This is Option C from `RUNTIME_ARCHITECTURE_ANALYSIS.md`, unmodified.

## 6. Runtime Layer Model

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 2 — Orchestration (NOT decided by this ADR)            │
│ CapabilityOrchestrator's dependency-ordered pipeline execu-   │
│ tion is real and in production, but whether a general-purpose│
│ orchestration/Kernel layer is adopted platform-wide is        │
│ deferred to a future ADR (§20).                               │
├─────────────────────────────────────────────────────────────┤
│ Layer 1 — Runtime-specific layers (each owns its own extra    │
│ machinery beyond Foundation; each exposes an Engine-          │
│ compatible boundary)                                          │
│                                                                 │
│   Capability Runtime      Thinking Runtime      Reasoning      │
│   (registry, ABI/         (fixed 11-stage        Runtime       │
│   manifest validation,    pipeline, immutable    (engines      │
│   shadow enforcement,     state-threading over   implementing  │
│   process isolation,      ThinkingState)         Engine         │
│   dependency-ordered                             directly,      │
│   pipelines)                                     per ADR-001)   │
├─────────────────────────────────────────────────────────────┤
│ Layer 0 — Foundation (domain-agnostic, unchanged scope)        │
│ ExecutionContext · EngineMetadata · EngineResult ·             │
│ EngineDiagnostics · Engine protocol · EngineRegistry ·         │
│ ExecutionContextValidator · Foundation exceptions              │
└─────────────────────────────────────────────────────────────┘
```

Layer 0 has zero knowledge of, and zero dependency on, Layers 1 or 2. Layer 1 mechanisms depend downward on Layer 0 (once adapted) and never on each other. Layer 2 is not specified by this ADR.

## 7. Responsibilities of Each Runtime Layer (summary)

| Layer | Owns | Does not own |
|---|---|---|
| Foundation | The shared minimal contract: context, metadata, result, diagnostics, status, the `Engine` shape, and a name-keyed registry primitive. | Domain logic of any kind; orchestration/lifecycle; execution authority. |
| Capability Runtime | Capability registration with ABI/manifest validation; shadow-mode enforcement; optional process-isolated execution; dependency-ordered multi-capability pipelines. | Domain-agnostic contract definition (uses Foundation's, once adapted); general-purpose orchestration beyond capabilities (§20). |
| Thinking Runtime | The fixed, domain-agnostic 11-stage engineering-thinking sequence and its immutable state model. | Domain-specific physics/protection/knowledge logic (lives in capabilities and domain modules, not in Thinking); engine registration/discovery. |
| Reasoning Runtime | Reasoning-engine-specific domain logic (e.g., confidence contribution shapes) carried as `Engine` payloads. | Its own parallel result/shadow-flag contract — this is retired in favor of `EngineResult` (§11). |

Detail for each layer follows in §8–§11.

## 8. Foundation Responsibilities

Unchanged from ADR-001, reaffirmed:

- Define and own `ExecutionContext`, `EngineMetadata`, `EngineResult`, `EngineDiagnostics`, `ExecutionStatus`, the `Engine` protocol, `EngineRegistry`, and Foundation's exception hierarchy.
- Remain domain-agnostic: no transformer, protection, physics, asset-specific, or control-execution logic, enforced by the existing architecture-boundary test.
- Grant no execution authority; every `EngineResult` remains non-authoritative by default.
- Provide no orchestration or lifecycle management (unchanged position on the Kernel question, §20).

One refinement, newly introduced by this ADR and scoped narrowly: `EngineResult`'s three safety flags **SHALL** become `Literal`-typed rather than plain `bool`, so Foundation's own type-level guarantee is at least as strong as every mechanism now expected to adapt to it. This is documented here as a requirement of the decision; it is not performed by this ADR.

## 9. Capability Runtime Responsibilities

- Continues to own: `CapabilityRegistry` (ABI-version and manifest cross-validation at registration), `CapabilityRuntime` (validate → execute → audit invocation, shadow-mode enforcement, optional timeout and process isolation, structured retryable error classification), and `CapabilityOrchestrator` (declarative, dependency-ordered multi-capability execution).
- **SHALL** gain an `Engine`-compatible boundary: a capability's identity and result **SHALL** be expressible as `EngineMetadata` and `EngineResult` at the point where Capability Runtime needs to interoperate with the rest of the layered runtime, without changing `EngineeringCapability`'s existing `validate`/`execute`/`audit` internal contract.
- This ADR is the first architectural decision to formally recognize Capability Runtime's existence and place it in the runtime layer model. It does not, by itself, produce the dedicated Capability Runtime ADR that documents its internal design in ADR-001-level detail — that remains a future ADR (§20) if the architecture owner wants that level of governance.

## 10. Thinking Runtime Responsibilities

- Continues to own: `ThinkingStage`, `ThinkingState`, `ThinkingStageRecord`, the `ThinkingStageProcessor` protocol, and the fixed 11-stage sequence in `EngineeringThinkingEngine`. This vocabulary is domain-specific to engineering investigations (observe, hypothesize, safety-gate, etc.) and **MUST NOT** move into Foundation, per Foundation's own domain-agnosticism constraint.
- The 11 internal stage processors **remain individually outside** the `Engine` protocol — their shared, per-investigation state-threading design is a different pattern from Foundation's stateless, per-call `execute(context)`, and this ADR does not change that.
- Only the **outer boundary** of `EngineeringThinkingEngine` as a whole **SHALL** gain an `Engine`-compatible adapter (accepting something `ExecutionContext`-shaped, returning something `EngineResult`-shaped, carrying the existing shallow projection — current stage, stage history, shadow flags — as payload), so the whole pipeline can be resolved and invoked the way any other `Engine` is, without touching its internals.

## 11. Reasoning Runtime Responsibilities

- Reaffirms ADR-001, unmodified: new reasoning engines **SHALL** return `EngineResult`, **SHALL** be registered through `EngineRegistry`, and **SHALL** interact with runtime state through `ExecutionContext`.
- Confidence Propagation's existing contracts (`ConfidenceContribution`, `ConfidencePropagationResult`) **SHALL** retain their domain-specific fields (`propagated_scores`, `contributions`) but **SHALL retire their independently-declared `shadow_only`/`affects_reasoning`/`affects_decision` fields** once an actual engine exists, in favor of carrying that same domain-specific data as `EngineResult.payload`. This closes the one already-observed instance of duplicated runtime infrastructure named in §3.
- No future reasoning engine may define its own parallel result type in place of `EngineResult`.

## 12. Integration Rules

- Foundation defines the shared minimal contract. Layer 1 mechanisms **MAY** extend it with their own additional, specialized fields and behavior, but **MUST** remain able to produce a valid `EngineMetadata`/`EngineResult` and consume a valid `ExecutionContext` at their adapted boundary.
- Domain-specific state (investigation stages, capability payload semantics, confidence-graph contributions) **MUST NOT** be pushed down into Foundation to make an adapter easier to write. If a boundary adapter cannot be built without adding domain concepts to Foundation, the adapter is deferred, not Foundation's constraint relaxed.
- Layer 1 mechanisms **MAY** maintain their own specialized registries and validators (Capability's ABI/manifest checks; Thinking's pydantic model validation) where their registration/validation target differs structurally from what `EngineRegistry`/`ExecutionContextValidator` check. They **SHOULD** delegate to Foundation's registry primitive where no additional validation is required, rather than reimplementing a plain name-keyed store from scratch.
- Layer 1 mechanisms **MUST NOT** depend on one another directly. Capability Runtime, Thinking Runtime, and Reasoning Runtime each depend only downward on Foundation, never sideways.
- Any future mechanism proposing a fifth "unit of work" pattern **SHOULD** first document why none of the three existing Layer 1 patterns (or Foundation directly) fit, following the Definition of Ready discipline already established (Handbook Part V).

## 13. Dependency Rules

Extending, not replacing, the Handbook's D-001–D-007 and ADR-001's existing constraint:

- **R-001 — Foundation has no upward or sideways dependency.** `app/foundation/` MUST NOT import from `app.capabilities`, `app.thinking`, `app.reasoning`, `app.brain`, `app.knowledge`, `app.transformer`, or `app.protection`. (Already enforced by the existing architecture-boundary test; unchanged by this ADR.)
- **R-002 — Layer 1 mechanisms depend downward only.** `app/capabilities/`, `app/thinking/`, and `app/reasoning/` MAY depend on `app/foundation/` (once adapted); they MUST NOT depend on each other.
- **R-003 — Domain logic stays out of generic runtime contracts.** Transformer physics, protection logic, and knowledge content MUST NOT be embedded in `foundation/`, in Capability Runtime's generic contracts (`capabilities/contracts.py`, `capabilities/base.py`), or in Thinking's generic contracts (`thinking/contracts.py`, `thinking/stages.py`). Domain logic belongs in domain modules (`app/transformer/`, individual capability implementations, individual stage processors).
- **R-004 — Adapters are additive.** A boundary adapter (§9, §10) MUST NOT alter or remove a mechanism's existing native contract; it wraps or projects it.

## 14. Runtime Contracts

- **`Engine` (Protocol, unchanged):** `metadata: EngineMetadata` (property); `execute(context: ExecutionContext) -> EngineResult`.
- **`ExecutionContext`, `EngineMetadata`, `EngineResult`, `EngineDiagnostics`, `ExecutionStatus` (Foundation, unchanged in shape except the `Literal`-tightening in §8).**
- **`EngineRegistry` (unchanged):** name-keyed register/resolve/exists/unregister/clear/list/count.
- **Boundary-adapter pattern (new, named by this ADR, not yet implemented):** a mechanism-specific function or thin wrapper class that converts a Layer 1 mechanism's native inputs/outputs into `ExecutionContext`/`EngineResult` at the specific point where that mechanism needs to be resolved, invoked, or diagnosed as an `Engine`. The adapter is additive infrastructure; it is not a rewrite of the mechanism it wraps.

No new contract types beyond these are introduced by this ADR.

## 15. Migration Strategy

Sequenced, incremental, each phase independently reviewable and independently revertible — none of it performed by this ADR:

1. **Implement Confidence Propagation as a real `Engine`.** Closes ADR-001's original, still-open gap. Retires `ConfidencePropagationResult`'s duplicate shadow fields per §11.
2. **Tighten `EngineResult`'s shadow-flag fields to `Literal` types** (§8). Verify first whether any existing code constructs `EngineResult` with non-default values for these fields (none currently does, per the repository review — but this must be re-checked at implementation time, not assumed from this ADR).
3. **Add the Capability Runtime boundary adapter** (§9). Additive; existing `EngineeringCapability`/`CapabilityRegistry`/`CapabilityRuntime`/`CapabilityOrchestrator` call sites are unchanged.
4. **Add the Thinking Runtime boundary adapter** (§10). Additive; `run_shadow_thinking_pipeline` and its call site in `EngineeringBrain` are unchanged.
5. **File the future ADRs named in §20**, at the architecture owner's discretion and on no fixed timeline implied by this document.

Each phase is subject to the existing Definition of Done and regression-preservation discipline (Handbook Part V) once implementation begins — not asserted as already satisfied here.

## 16. Backward Compatibility

This decision is additive by design:

- No existing call site (`app/transformer/engineer.py`, `app/brain/engineering_brain.py`, or any test) is required to change as a direct consequence of this ADR.
- `EngineeringCapability`, `CapabilityRegistry`, `CapabilityRuntime`, `CapabilityOrchestrator`, `ThinkingStageProcessor`, and `EngineeringThinkingEngine`'s existing native contracts are preserved unmodified; only new adapter surfaces are added alongside them.
- Existing safety guarantees are preserved, not weakened: Capability's process isolation and `Literal`-locked `affects_decision`, and Thinking's `Literal`-locked shadow flags, are unaffected by this ADR.
- The one field-level change this ADR calls for (`EngineResult`'s `Literal`-tightening, §8) is scoped to a currently-unconsumed contract (Foundation has zero consumers today per the repository review), minimizing the chance of it breaking anything that exists yet.

## 17. Consequences

### Positive

- Establishes one documented, canonical relationship between all four runtime mechanisms, closing the governance gap this ADR was commissioned to resolve.
- Stops further duplication of runtime infrastructure of the kind already found in Reasoning Contracts.
- Brings Capability Runtime under architectural governance for the first time.
- Preserves all currently-tested safety-relevant behavior; no regression risk to existing guarantees.
- Fully incremental and reversible — each migration phase (§15) can be adopted or rolled back independently of the others.

### Trade-offs

- Does not produce a single unified mental model; a newcomer still needs to learn that Capability and Thinking retain machinery beyond bare `Engine`.
- Leaves the orchestration/Kernel question open by design (§20) rather than resolving it, which some stakeholders may find incomplete.
- Requires disciplined follow-through — if the boundary adapters in §15 are never built, this ADR's layering remains aspirational in the same way Foundation's contract has been since ADR-001, i.e. correctly designed but unconsumed.

## 18. Alternatives Considered

### Option A — Minimal Migration

Rejected as the primary decision. Leaves all four mechanisms exactly as they are except implementing Confidence Propagation against Foundation. Lowest risk and lowest cost, but leaves the fragmentation this ADR exists to resolve almost entirely in place, with no forcing function for future convergence.

### Option B — Unified Runtime

Rejected. Collapses all four mechanisms onto a single `Engine`/`ExecutionContext` contract. This re-opens the Kernel question ADR-001 already closed, without a superseding decision to justify reopening it; requires `ExecutionContext` to either absorb domain-carrying data (violating Foundation's own domain-agnosticism constraint) or bury typed, validated data inside untyped dicts (a real loss of type safety already present in Capability and Thinking); and would weaken currently-`Literal`-locked safety guarantees to match Foundation's current, looser typing rather than the reverse. Highest migration cost and highest technical risk of the three options considered.

### No action (status quo)

Not seriously considered as a resolution: leaves Confidence Propagation's already-observed duplicated-infrastructure problem uncorrected and leaves ADR-001's own mandate (new reasoning engines SHALL use `Engine`) unexecuted indefinitely.

## 19. Risks

| Risk | Mitigation |
|---|---|
| Boundary adapters (§15, phases 3–4) are approved in principle but never actually implemented, leaving this ADR's layering aspirational — the same fate Foundation's original contract has had since ADR-001. | Sequence migration in small, independently-shippable phases (§15) rather than one large effort; track each phase against the existing Definition of Done. |
| The Kernel/orchestration question (§20) is deferred indefinitely, leaving Capability Runtime's real orchestration need permanently ungoverned by a first-class decision. | Name it explicitly as a required future ADR (§20) rather than leaving it implicit, so it is tracked rather than forgotten. |
| Tightening `EngineResult`'s flags to `Literal` types could be a breaking change if any code already constructs non-default values for them. | Verify at implementation time (§15, phase 2) before the change is made; not assumed safe by this document alone. |
| "Boundary adapter" work scope-creeps into deeper refactors of Capability or Thinking internals, contrary to the instruction that this decision not invent new functionality. | §9, §10, and R-004 (§13) explicitly restrict adapters to additive wrapping; any internal refactor beyond that requires its own review, not blanket cover from this ADR. |
| This ADR is treated as ACCEPTED without the architecture-owner sign-off its own Status section (§1) requires. | Status is explicitly PROPOSED, not ACCEPTED, in this document. |

## 20. Future ADRs Required

1. **Runtime Orchestration / Kernel ADR.** Whether a general-purpose orchestration layer should be formally adopted platform-wide, given `CapabilityOrchestrator` already demonstrates real, production-exercised orchestration need — evidence that may make ADR-001's original "not yet demonstrated" premise stale for at least the capability case. Not decided by this ADR.
2. **Dedicated Capability Runtime ADR** (optional, deeper governance), if the architecture owner wants Capability Runtime's internal design (process isolation, ABI versioning, pipeline policy) documented at the same level of detail ADR-001 gave Foundation, beyond this ADR's layer-level recognition of it.
3. **Shadow-to-Active Promotion Criteria ADR**, already recorded as an open item in the Handbook (Part VII §17) — required before Confidence Propagation's engine (§15, phase 1) can be promoted out of shadow mode once implemented.
4. **Master Architecture / `docs/ARCHITECTURE.md` reconciliation**, carried over from the Repository Review — out of scope for a runtime-architecture ADR, but unresolved and worth a future decision of its own.

---

## 21. Decision Owner

Chief Architect.

AI reviewers, including this analysis and this ADR's drafting, may provide recommendations but do not own architectural authority. Formal acceptance of this ADR requires the same sign-off ADR-001 required.

---

*This document formalizes an architectural decision. It does not implement one. No repository file, test, or the Handbook is modified by this ADR. Per instruction, work stops here pending approval.*