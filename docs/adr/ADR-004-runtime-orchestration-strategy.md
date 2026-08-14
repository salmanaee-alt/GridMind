# ADR-004 — Runtime Orchestration Strategy and Kernel Deferral

**Intended repository path:** `docs/adr/ADR-004-runtime-orchestration-strategy.md`

## 1. Status

ACCEPTED. This ADR formalizes the primary architectural conclusion of `docs/reviews/ADR-004-runtime-orchestration-analysis.md`, which the Chief AI Architect has reviewed and accepted. Per ADR-001/002/003's shared precedent, AI-authored analysis and documentation may recommend but does not carry architectural authority; formal ACCEPTED status requires the Decision Owner's sign-off (§23). This ADR introduces no production behavior, implements nothing, and does not modify ADR-001, ADR-002, or ADR-003.

## 2. Context

ADR-001 established the Runtime Foundation (`app/foundation/`): `ExecutionContext`, `EngineMetadata`, `EngineResult`, `EngineDiagnostics`, the `Engine` protocol, and `EngineRegistry`, kept strictly domain-agnostic.

ADR-002 established the Canonical Layered Runtime Architecture: Foundation as Layer 0; Capability Runtime, Thinking Runtime, and Reasoning Runtime as Layer 1, each retaining its own native machinery; Layer 2 (Orchestration) explicitly left undecided; and a required future ADR named "Runtime Orchestration / Kernel ADR" to resolve that question.

ADR-003 defined and the repository has since implemented the Runtime Adapter Pattern: `CapabilityFoundationAdapter` and `ThinkingFoundationAdapter`, each an additive, `Engine`-compatible wrapper around one native Layer-1 mechanism, verified in `docs/adr/ADR-003-implementation-closure.md` as implemented without modification to any native contract.

This ADR is the required future ADR ADR-002 named. Before drafting it, a repository-grounded analysis (`docs/reviews/ADR-004-runtime-orchestration-analysis.md`) inspected the current repository — including `app/foundation/`, `app/capabilities/`, `app/thinking/`, `app/reasoning/`, `app/brain/`, `app/transformer/`, and their tests — to determine whether a general-purpose Runtime Orchestration / Kernel layer is currently needed. That analysis found: the repository currently runs as two disconnected verticals (`EngineeringBrain`→Thinking and `TransformerEngineer`→Capabilities); `CapabilityOrchestrator` and `EngineeringThinkingEngine` are each small, single-runtime sequencers with no duplicated responsibility between them; `EngineRegistry` is fully implemented but has never been instantiated by any production code; the ADR-003 adapter pair is implemented and tested but has zero live production callers; and every candidate cross-runtime workflow (Thinking↔Capability, Thinking↔Reasoning, Capability↔Reasoning, Brain↔Capability, Brain↔Reasoning, TransformerEngineer↔Thinking, TransformerEngineer↔Reasoning) was classified **NOT FOUND**. The one mechanism capable of cross-runtime composition — the adapter pair — was classified **SUPPORTED BUT UNUSED**, not LIVE. This ADR does not re-derive that evidence; it treats the analysis document as the evidentiary record and formalizes the decision the Chief AI Architect accepted on that basis.

**Sourcing note on the regression baseline.** A "722 passed" full-regression figure has been referenced in this engagement's context as an externally reported baseline. It has not been independently executed by this ADR or by the analysis it formalizes (no `pytest`-capable environment with network access to install dependencies was available). It is recorded here, as in the ADR-003 implementation closure review, as **dated implementation context**, not a verified fact this ADR asserts.

## 3. Problem Statement

ADR-002 deferred the question of whether GridMind needs a Layer 2, general-purpose Runtime Orchestration / Kernel component and named a future ADR to decide it. That question must now be answered from repository evidence, not assumption: does GridMind's current implementation — two independent verticals, two small single-runtime sequencers, an unused generic registry, and an unused-but-working adapter pair — show a coordination problem that only a general-purpose Kernel would solve? And if not, what should GridMind do instead, both today and the day a genuine cross-runtime workflow appears, without prohibiting a Kernel forever or pretending the question is closed?

## 4. Decision Drivers

- Repository evidence, not architectural aspiration: ADR-002/003's own methodology requires decisions to be based on what the repository actually does, not on what a layered architecture diagram might imply should eventually exist.
- Zero live cross-runtime workflows exist today (`docs/reviews/ADR-004-runtime-orchestration-analysis.md`, Analysis 4) — a Kernel exists to coordinate multiple runtimes, and no two runtimes are coordinated together anywhere in the codebase, live or otherwise.
- `EngineRegistry` and the ADR-003 adapter pair already provide a tested, working composition mechanism that has simply never been called from production code — the gap is a wiring gap, not a capability gap in Foundation (Analysis 5).
- The Kernel Responsibility Test (Analysis 6) found zero of seventeen candidate Kernel responsibilities classified `NEEDED NOW`.
- Central orchestration carries a specific, non-generic authority risk for GridMind: a component that "sees everything" across runtimes is one refactor away from being read as a control plane, which this ADR must foreclose explicitly rather than leave implicit (Analysis 7).
- ADR-002 requires this question to be decided; it does not predetermine the answer to be "build a Kernel."

## 5. Decision

GridMind SHALL retain specialized orchestration within Layer-1 runtimes at the current stage of the architecture.

Capability Runtime SHALL continue to own its existing capability-specific orchestration (`CapabilityOrchestrator`, `CapabilityRegistry`, `CapabilityPipelinePolicy`).

Thinking Runtime SHALL continue to own its fixed thinking pipeline sequencing (`EngineeringThinkingEngine`, its hard-coded `_STAGE_ORDER`).

A general-purpose Runtime Orchestration / Kernel layer SHALL NOT be introduced at this time.

When the first real cross-runtime workflow appears, GridMind SHOULD first use explicit Foundation-based composition through the existing `ExecutionContext`, `Engine`, `EngineRegistry`, `EngineResult`, `EngineDiagnostics`, `CapabilityFoundationAdapter`, and `ThinkingFoundationAdapter`, before introducing a new general-purpose orchestration layer.

This decision does NOT prohibit a future Kernel. It defers Kernel architecture until repository evidence demonstrates that explicit composition and specialized orchestration are insufficient (§13).

## 6. Current Runtime Topology

Reconstructed from code, per the analysis this ADR formalizes (`docs/reviews/ADR-004-runtime-orchestration-analysis.md`, Analysis 1). Two disconnected verticals, not one pipeline:

- **`POST /brain/test`** → `EngineeringBrain.run(session)` (a hand-written, entirely procedural sequence of internal methods — observe/understand/validate/hypothesize/reason/evaluate/decide/explain/learn) → `run_shadow_thinking_pipeline(session)` → `engineering_session_to_thinking_state(session)` → the native `build_default_thinking_engine().execute(state)` (NOT through `ThinkingFoundationAdapter`) → result merged into `session.metadata["thinking"]`. Capability Runtime, Reasoning Runtime, and Foundation's `Engine`/`ExecutionContext`/`EngineRegistry` are **NOT CONNECTED** anywhere in this path.
- **`POST /transformer/differential-trip`** → `TransformerEngineer.investigate_differential_trip(request)`, which constructs its own `CapabilityRegistry`/`CapabilityRuntime`/`CapabilityOrchestrator` per call and drives four capabilities (`KnowledgeCandidateCapability` → `KnowledgeRelevanceCapability` → `EvidenceInterpretationCapability`, each `depends_on`-chained through `CapabilityOrchestrator.execute_policy()`, plus `TraceableContextCapability` through a second `CapabilityOrchestrator.execute()` call). `EngineeringBrain`, Thinking Runtime, Reasoning Runtime, and the `CapabilityFoundationAdapter` are **NOT CONNECTED** anywhere in this path.
- **`ConfidencePropagationEngine`** (Reasoning Runtime) implements `Engine` directly (no adapter needed — it is Foundation-native) but its `execute()` unconditionally returns `ExecutionStatus.SKIPPED` with an empty payload; no propagation algorithm exists. It is never instantiated or called from anywhere outside its own definition file.
- **`CapabilityFoundationAdapter`** and **`ThinkingFoundationAdapter`** are fully implemented and unit-tested in isolation (verified in `docs/adr/ADR-003-implementation-closure.md`) but have zero production call sites.
- **`EngineRegistry`** is fully implemented and tested but is never instantiated anywhere in `app/` outside `app/foundation/` itself.

This ADR records this topology as it currently exists. It does not change it.

## 7. Specialized Orchestration Responsibilities

Both existing orchestrators are explicitly preserved as-is by this decision, unmodified and un-replaced.

**`CapabilityOrchestrator`** owns, for Capability Runtime only: deterministic sequencing (caller-supplied order or `CapabilityPipelinePolicy.steps` order); a linear `depends_on` satisfaction check (not a general DAG scheduler — no cycle detection, no parallelism). It does not own: data flow between steps (assembled by hand today by the one real caller, `TransformerEngineer`), failure handling beyond what `CapabilityRuntime.invoke()` already returns as data, retries (none exist anywhere in the repository), timeouts or process isolation (owned by `CapabilityRuntime`), registration (owned by `CapabilityRegistry`), or safety enforcement (owned by `CapabilityRuntime` and each capability's own `Literal[False]` contract).

**`EngineeringThinkingEngine`** owns, for Thinking Runtime only: a fixed, hard-coded eleven-stage sequence (`_STAGE_ORDER`), with no dependency resolution needed (linear, not data-driven), no failure handling (no stage processor raises today, and none is caught if it did — see §18), no retries, timeouts, or isolation, context propagation via immutable `ThinkingState.model_copy(update=...)` threading, and diagnostics via `stage_history` accumulation.

Neither is a duplicate of the other, and neither duplicates any Foundation responsibility (`docs/reviews/ADR-004-runtime-orchestration-analysis.md`, Analysis 3). This ADR does not merge, generalize, or extract a shared abstraction from these two orchestrators. **They are not to be replaced by this ADR.**

## 8. Foundation-Based Explicit Composition

Foundation already provides everything a future caller needs to compose across Layer-1 runtimes explicitly, without a Kernel, per Analysis 5 of the accepted review:

- `ExecutionContext.resources: dict[str, Any]` — the carrier ADR-003 purpose-built for passing native inputs across the Foundation boundary; already used correctly by both existing adapters.
- `Engine` — any object satisfying its `metadata`/`execute(context) -> EngineResult` shape (both `CapabilityFoundationAdapter` and `ThinkingFoundationAdapter` already do) can be called directly by a caller holding a reference to it, in whatever order and with whatever conditional logic that caller's own workflow requires.
- `EngineRegistry` — fully implemented `register`/`resolve`/`exists`/`unregister`/`list`/`count`, available for name-based lookup if a future caller prefers it over holding direct references. Currently unused, not missing.
- `EngineResult` / `EngineDiagnostics` — a uniform result and diagnostics shape already returned by both adapters, meaning a caller invoking two or more `Engine`s receives uniformly-shaped results regardless of which native mechanism produced them.

What Foundation does not yet provide — because nothing has needed it yet — is a defined cross-runtime **sequencing policy** (ordering, dependency, and failure semantics that would apply *across* runtimes rather than within one). §13 defines when that gap must be revisited; §9 explains why it is not filled speculatively today.

## 9. Why No Kernel Now

Per the Kernel Responsibility Test in the accepted analysis (Analysis 6), of the seventeen candidate Kernel responsibilities evaluated — Engine discovery, Engine dispatch, single- and cross-runtime sequencing, single- and cross-runtime dependency resolution, context propagation, failure/retry/timeout policy, isolation, diagnostics aggregation, traceability aggregation, workflow state, cancellation, concurrency, resource budgeting, and authorization boundary integration — **zero were classified `NEEDED NOW`**. Thirteen are already owned by an existing, narrower mechanism (`CapabilityOrchestrator`, `CapabilityRuntime`, `CapabilityRegistry`, `EngineeringThinkingEngine`, or Foundation's own types); the remainder have no supporting repository evidence at all, because no cross-runtime workflow — LIVE, SUPPORTED BUT UNUSED, or otherwise — has ever required them (Analysis 4).

Building a general-purpose Kernel against zero live use cases would design against hypothetical requirements, which ADR-002 and ADR-003's own methodology explicitly instructs against ("do not invent architecture"). This ADR declines to do so. This is a decision to defer, not a decision that a Kernel is architecturally wrong — see §17 (Alternatives) and §13 (Reconsideration Triggers) for the conditions under which this conclusion is revisited.

## 10. Safety and Authority Boundary

Runtime orchestration authority is **not** operational execution authority. This is non-negotiable and independent of implementation detail, consistent with the Handbook's Authority Chain (Engineering Analysis → Recommendation → Authorization → Execution) and Safety Principle SF-002 ("AI Has No Default Executive Authority"), and consistent with ADR-003 §17's invariant that `EngineResult`'s authority fields are fixed, type-enforced constants rather than values any component computes or propagates.

No orchestration component — `CapabilityOrchestrator`, `EngineeringThinkingEngine`, the ADR-003 adapters, or any future Kernel, if one is ever introduced — gains authority to: operate breakers, energize or de-energize equipment, change protection settings, issue control commands, override interlocks, or perform any physical action. GridMind AI has no default executive authority. Any future operational execution requires a separate human authorization or independent institutional policy gate that sits outside runtime orchestration entirely — not a feature any orchestration component, present or future, is permitted to implement or absorb.

If a future Kernel is ever introduced under §13's reconsideration process, it SHALL coordinate computation only. Its output must satisfy the same fixed, non-authoritative contract `EngineResult` already guarantees today (`shadow_only=True`, `affects_reasoning=False`, `affects_decision=False`, unconditionally); no Kernel-level aggregation step is permitted to compute a different combined value from the individual results it coordinates; and it must never construct, forward, or reference anything resembling a control or execution instruction. This boundary is a design requirement on any future Kernel proposal, not a matter left to be decided during that proposal's own review.

## 11. Integration Rules

- Existing call sites (`EngineeringBrain`, `TransformerEngineer`) are not required to change as a result of this ADR. Neither currently uses Foundation, the adapters, or `EngineRegistry`, and this ADR does not mandate that they begin doing so.
- A future caller that needs to compose across two or more `Engine`-compatible boundaries SHOULD do so explicitly, at the call site, using `ExecutionContext`, direct `Engine.execute(context)` calls or `EngineRegistry` lookup, and the existing adapters — not by writing a new shared dispatch/sequencing component.
- `CapabilityOrchestrator` and `EngineeringThinkingEngine` remain the sole owners of sequencing within their respective native runtimes. No component introduced under this ADR may re-implement or shadow that sequencing.
- No new module, abstraction, base class, or "lightweight coordinator" that generalizes across `CapabilityOrchestrator` and `EngineeringThinkingEngine` may be introduced under the label of "explicit composition" — doing so would be a Kernel in substance regardless of name, and would require the reconsideration process in §13, not incremental introduction under this ADR.

## 12. Dependency Rules

Extending ADR-002 §14 (R-001–R-004) and ADR-003 §19 (R-005–R-007), specific to the absence of a Kernel:

- **R-008 — No component outside Foundation and the two existing adapters may depend on cross-runtime coordination as a first-class abstraction.** Any future cross-runtime composition is written at the specific call site that needs it, depending directly on Foundation's types and the relevant adapter(s), not on a shared orchestration dependency that does not exist.
- **R-009 — Layer-1 runtimes do not depend on each other.** Unchanged from ADR-002 §14 R-002; this ADR does not create any new sideways dependency between Capability Runtime and Thinking Runtime, nor introduce a component either would depend on that does not already exist.
- **R-010 — Foundation does not gain orchestration policy.** `ExecutionContext`, `Engine`, `EngineRegistry`, `EngineResult`, and `EngineDiagnostics` remain typing/shape/lookup only, per ADR-001. This ADR adds no sequencing, dependency-resolution, retry, timeout, or failure-policy logic to Foundation itself.

## 13. Reconsideration Triggers

The Kernel question SHALL be reopened when repository evidence shows any of the following. These are reconsideration triggers, not implementation authorizations — crossing a trigger requires architecture review first, not automatic Kernel construction.

1. A **LIVE** workflow requires sequencing across two or more Layer-1 runtimes / `Engine`-compatible boundaries.
2. Equivalent cross-runtime orchestration logic appears in two or more independent workflows.
3. A real workflow requires shared cross-runtime policy for dependencies, failure handling, diagnostics, traceability, cancellation, concurrency, or workflow state.
4. Explicit composition using Foundation contracts and existing adapters (§8) proves insufficient without repeated orchestration plumbing.

None of these triggers is met today. Per the accepted analysis, every candidate cross-runtime workflow is currently classified NOT FOUND, and the one cross-runtime-capable mechanism that exists (the adapter pair) is SUPPORTED BUT UNUSED — not LIVE. Reaching trigger 1 specifically requires a workflow to graduate from SUPPORTED BUT UNUSED, PLANNED, or INFERRED to LIVE; this ADR does not treat any currently-unused or planned capability as having done so.

## 14. Migration / Evolution Strategy

No migration is required or scheduled by this ADR. Sequenced only for the day a reconsideration trigger (§13) is met:

1. A concrete cross-runtime workflow requirement is identified from an actual engineering use case.

2. The requirement is classified against the reconsideration triggers in §13 before production implementation.

3. Architecture review determines whether explicit Foundation-based composition remains sufficient.

4. If explicit composition is sufficient, the workflow MAY be implemented at its own call site using the existing Foundation contracts and adapters.

5. If the review demonstrates that explicit composition would create repeated or materially insufficient orchestration plumbing, a separate Kernel architecture ADR SHALL be drafted before Kernel implementation.

6. Any future Kernel remains bound by the safety and authority requirements in §10.

## 15. Backward Compatibility

Purely non-disruptive: `CapabilityOrchestrator`, `EngineeringThinkingEngine`, `CapabilityFoundationAdapter`, `ThinkingFoundationAdapter`, and all Foundation types are unmodified by this ADR's decision. No existing call site, test, or contract is required to change. This ADR changes documentation and decision record only.

## 16. Consequences

- GridMind continues to run as two independent verticals until a real cross-runtime need drives explicit composition; this is an accepted, evidenced-correct current state, not a defect this ADR is obligated to fix.
- Future cross-runtime work has a clear, pre-agreed first response (explicit Foundation-based composition) rather than an open question or an ad hoc decision made under implementation pressure.
- The Kernel question remains genuinely open, not closed — §13's triggers give it a concrete, evidence-based reopening condition instead of leaving it either permanently deferred by default or permanently at risk of informal, undocumented drift toward centralized orchestration.
- `EngineRegistry` remains unused in production for the foreseeable term unless a future caller adopts explicit composition; this ADR does not consider that a problem to solve now.

## 17. Alternatives Considered

### A — General-Purpose Kernel Now

Rejected. Would design a Layer 2 coordination component against zero live cross-runtime use cases (Analysis 4), repeating the exact "invent architecture ahead of evidence" failure mode ADR-002/003's methodology exists to prevent. Highest exposure to the authority-boundary risk in §10, with the largest new surface area and no real workflow to validate the design against.

### B — Minimal Orchestration Contract Now, Implementation Deferred

Considered, not selected as the current decision. Would define the shape a future cross-runtime coordinator must satisfy without building it — cheap, and would capture §10's safety invariant in writing ahead of implementation pressure. Not selected because a contract designed against zero live use cases risks the same speculative-design problem as Option A, on paper instead of in code; ADR-003's own experience (its Context section's sourcing note) already shows contracts written ahead of real usage need revision once usage appears. Remains available as a lighter-weight step the Chief Architect may choose to take independently of this ADR's primary decision; this ADR does not adopt it.

### C — Specialized Layer-1 Orchestration (current architecture)

**Selected as the current architecture.** `CapabilityOrchestrator` continues to own Capability sequencing; `EngineeringThinkingEngine` continues to own Thinking sequencing. This is what the repository already does, correctly and without duplication (Analysis 3), and it costs nothing to keep. §5 formalizes this as the standing decision.

### D — Explicit Foundation-Based Composition (preferred first response to a real cross-runtime need)

**Selected as the preferred first response** when a reconsideration trigger (§13) is met. No Kernel, no new shared dispatch component: a caller that needs cross-runtime composition constructs the relevant adapter(s), optionally uses `EngineRegistry` for lookup, and calls `.execute(context)` on each in the order its own workflow requires — exactly the pattern the ADR-003 adapter test suites already demonstrate works (`test_capability_adapter_end_to_end_with_real_capability`, `test_thinking_adapter_stage_history_matches_native_pipeline`), simply not yet exercised by a real multi-adapter caller. **Option D is not a Kernel and is not to be treated as one** — it is a discipline applied per call site using infrastructure that already exists, not a new component, contract, or abstraction.

## 18. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Without a shared coordination mechanism, repeated cross-runtime call sites could eventually duplicate sequencing/dependency logic. | §13 trigger 2 exists specifically to catch this — equivalent orchestration logic appearing in two or more independent workflows is itself a reconsideration trigger, not a risk left unmonitored. |
| "Explicit composition" (§8, Option D) is a discipline, not an enforced boundary; nothing prevents a future caller from building something Kernel-shaped inside its own module without calling it one. | §11's integration rules explicitly prohibit a generalized cross-`CapabilityOrchestrator`/`EngineeringThinkingEngine` abstraction under this ADR's label; any such construction is itself evidence a reconsideration trigger has likely been met and should be routed through architecture review, not merged quietly. |
| `EngineeringThinkingEngine`'s Thinking Adapter boundary does not currently catch an exception from a future-raising stage processor (a gap independently noted in `docs/adr/ADR-003-implementation-closure.md` §3) — if a cross-runtime caller relied on the adapter's failure semantics being complete, this gap would surface there first. | Not created or worsened by this ADR; already documented in the ADR-003 closure review as a narrow, currently-dormant implementation gap for future implementation review, not a Layer 2 concern. |
| A future Kernel proposal, once a trigger is met, could be designed under time pressure and under-specify the §10 safety boundary. | §10 states the boundary as a requirement on any future Kernel proposal's first draft, not a detail to be resolved during that proposal's own review — reducing the chance it is skipped or weakened later. |
| Deferring indefinitely by never acknowledging a trigger has been met. | §13's triggers are stated as repository-evidence conditions ("a LIVE workflow requires...", "logic appears in two or more..."), not subjective judgment calls, so they can be checked against the repository the same way this ADR's own evidence was gathered. |

## 19. Relationship to ADR-001

ADR-001 established Foundation (`ExecutionContext`, `EngineMetadata`, `EngineResult`, `EngineDiagnostics`, `Engine`, `EngineRegistry`) as domain-agnostic infrastructure. This ADR does not modify any Foundation contract, does not add orchestration policy to Foundation (§12, R-010), and relies on Foundation's existing shape as the basis for Option D (§8, §17). ADR-001 is unaffected.

## 20. Relationship to ADR-002

ADR-002 established the Layered Runtime Architecture (Foundation / Layer 1 runtimes / deferred Layer 2 orchestration) and named "Runtime Orchestration / Kernel ADR" as a required future ADR. This ADR is that required ADR. It does not change ADR-002's layer model, does not promote any Layer 1 mechanism, and does not decide Layer 2 by building it — it decides Layer 2 by formalizing that it remains unbuilt at this time, with defined conditions (§13) under which that decision is revisited. ADR-002's dependency rules (R-001–R-004) are extended, not altered, by §12's R-008–R-010.

## 21. Relationship to ADR-003

ADR-003 defined and the repository has implemented the Runtime Adapter Pattern (`CapabilityFoundationAdapter`, `ThinkingFoundationAdapter`), verified in `docs/adr/ADR-003-implementation-closure.md`. This ADR does not modify either adapter, does not change their contracts, and treats them as the concrete mechanism Option D (§8, §17) is built on. ADR-003's safety and authority invariants (its §17: fixed, type-enforced `EngineResult` constants; native-contract-violation-as-safety-failure) are carried forward unchanged into this ADR's §10 and extended explicitly to any future Kernel.

## 22. Future Architecture Work

- **Kernel design ADR**, if and when a reconsideration trigger (§13) is met — scoped and evidenced against the real workflow(s) that triggered it, not drafted speculatively now.
- **Knowledge Runtime / Physics Runtime adapters**, per ADR-003 §10, once either runtime exists — out of scope here.
- **Adapter adoption decision** for `EngineeringBrain` and `TransformerEngineer` (already named as an open question in ADR-003 §26) — whether either should begin routing through its respective adapter is independent of this ADR's Kernel decision and not resolved here.
- **`docs/adr/ADR-003-implementation-closure.md` §3's narrow Thinking-adapter error-mapping gap** — an implementation follow-up, not a Layer 2 concern, noted here only because §18 references it.
- No standalone orchestration contract is planned at this time. Cross-runtime orchestration contracts SHALL be derived from repository-backed requirements only after a reconsideration trigger in §13 is met.

## 23. Decision Owner

Chief Architect (Chief AI Architect), consistent with ADR-001, ADR-002, and ADR-003. AI-authored analysis and documentation, including this document, may recommend but does not carry architectural authority.