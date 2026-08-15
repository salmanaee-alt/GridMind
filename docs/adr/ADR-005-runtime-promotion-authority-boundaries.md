# ADR-005 — Runtime Promotion, Decision Influence, and Authority Boundaries

**Intended repository path:** `docs/adr/ADR-005-runtime-promotion-authority-boundaries.md`

## 1. Status

ACCEPTED. This ADR formalizes the primary architectural conclusion of `docs/reviews/ADR-005-runtime-promotion-authority-analysis.md`, which the Chief AI Architect has reviewed and accepted. Per ADR-001/002/003/004's shared precedent, AI-authored analysis and documentation may recommend but does not carry architectural authority; formal ACCEPTED status requires the Decision Owner's sign-off (§27). This ADR introduces no production behavior, implements no active mode, implements no authorization infrastructure, and does not modify production code, tests, `ARCHITECTURE.md`, or ADR-001 through ADR-004.

## 2. Context

ADR-001 established Foundation's domain-agnostic, non-authoritative-by-default contract (`shadow_only`, `affects_reasoning`, `affects_decision` on `EngineResult`). ADR-002 established the Layered Runtime Architecture. ADR-003 established and the repository has implemented the Runtime Adapter Pattern, preserving that same non-authoritative contract across the Capability and Thinking boundaries. ADR-004 established that orchestration authority is not operational execution authority, and deferred a general-purpose Kernel until repository evidence demonstrates one is needed.

None of ADR-001 through ADR-004 defined what it would mean for a component to move *beyond* its current, uniformly restrictive state. A repository-grounded analysis (`docs/reviews/ADR-005-runtime-promotion-authority-analysis.md`) was performed to answer that question before any such promotion is designed or implemented. That analysis found: every currently-observed safety restriction in the repository defaults to its safest value, but the *mechanism* enforcing that default is not uniform — it ranges from pydantic `Literal[...]`-locked fields that cannot be constructed otherwise, to plain `bool` fields relying on convention, to prose written into an untyped metadata dictionary that nothing reads. It found that GridMind's actual decision-producing code (`EngineeringBrain`) and Thinking's `DecideProcessor` are two disconnected mechanisms sharing the word "decision" without sharing data or logic. It found no execution-authority mechanism of any kind anywhere in the codebase. It found no persistent-memory write path exists, meaning `memory_write_authorized=False` currently guards a write path that does not exist yet. And it found one concrete, present-day architectural risk: `CapabilityMetadata.shadow_only` and `CapabilityManifest.shadow_only` are plain `bool` fields, not type-locked, meaning a future capability could self-declare `shadow_only=False` and structurally bypass `CapabilityRuntime`'s shadow-mode rejection for that capability specifically.

This ADR does not re-derive that evidence; it treats the analysis document as the evidentiary record and formalizes the decision the Chief AI Architect accepted on that basis.

**Sourcing note on the regression baseline.** As in `docs/adr/ADR-003-implementation-closure.md` and `docs/adr/ADR-004-runtime-orchestration-strategy.md`, any regression-count figure referenced in this engagement's context is recorded as an externally reported baseline, not independently executed or asserted by this ADR.

## 3. Problem Statement

GridMind's runtime components are, today, uniformly restricted to their safest computational state: they compute, but nothing they produce is permitted to feed reasoning, influence a decision, be written to persistent memory, or trigger any external action. At some future point, a real, evidenced need may arise for a specific component to move beyond one of these restrictions. Without an architectural answer prepared in advance, the natural failure mode is to reach for the simplest-sounding model — a single "active" switch, or an ordered ladder implying each capability is a prerequisite for the next — either of which would grant more than intended, conflate unrelated concerns, or misrepresent what evidence a specific promotion actually requires. This ADR defines the model runtime promotion SHALL follow, without granting any promotion under it.

## 4. Decision Drivers

- Repository evidence shows at least four independently-varying restricted concerns (computation, reasoning participation, decision influence, persistent memory mutation), not one — `docs/reviews/ADR-005-runtime-promotion-authority-analysis.md`, Analyses 1–4 and 6.
- Repository evidence shows no execution-authority mechanism exists anywhere, and that this must remain permanently true regardless of how any other dimension evolves (Analysis 5, Analysis 13).
- Repository evidence shows one field pair (`CapabilityMetadata.shadow_only` / `CapabilityManifest.shadow_only`) is not type-locked, demonstrating concretely what happens when eligibility and authorization are not architecturally separated (Analysis 11, finding 2).
- Repository evidence shows the current "safety gate" (`SafetyGateProcessor`) and provenance-integrity mechanisms are advisory classifications, not blocking gates, despite naming that could suggest otherwise (Analysis 1, Analysis 10).
- ADR-004's orchestration/authority boundary must be preserved without exception as this model is defined (Analysis 13).
- A documentation-only ADR is sufficient and preferred: every finding above can be formalized without any code change, preserving 100% of current fail-closed behavior (Analysis 12).

## 5. Decision

GridMind SHALL NOT use a binary shadow → active promotion model.

GridMind SHALL NOT use an ordered authority ladder such as shadow → reasoning → decision → execution.

Runtime promotion SHALL instead be modeled as independent, explicitly governed dimensions (§6). Promotion in one dimension SHALL NOT implicitly grant another.

This ADR defines the dimension model, the governance concepts that apply to it (§8–§10), the evidence categories a future promotion would need (§11), the fail-closed requirements any future promotion mechanism must satisfy (§12), and the anti-privilege-escalation rules that apply from this point forward (§13). It grants no promotion, implements no mechanism, and requires no code change (§18).

## 6. Authority Dimension Model

At least the following dimensions SHALL be recognized. A future promotion, if evidenced and authorized, applies to exactly one dimension at a time; none is implied by another.

1. **Computation.** A component may execute computation and produce outputs. This is the only broadly exercised runtime capability today — every component in the repository computes something; nothing about this dimension is restricted or promotable, it simply describes what already happens.
2. **Reasoning Participation.** Whether a component's output may be consumed as evidence or input by another reasoning process. This is distinct from merely computing an output — a component can compute a result that is never read by anything else, which is the current state of every `affects_reasoning`-bearing field in the repository. Current fields such as `affects_reasoning` (on `EngineResult`, `ThinkingState`, and several evidence/graph-validation contracts) are safety declarations today, fixed to their safe value, not an implemented permission system — nothing in the repository currently reads `affects_reasoning` to decide whether to consume a result.
3. **Decision Influence.** Whether a component's output may influence an engineering recommendation or decision-support conclusion.

Reasoning Participation and Decision Influence are independently governed dimensions.

Permission in Reasoning Participation SHALL NOT automatically grant Decision Influence.

A future Decision Influence policy MAY require Reasoning Participation, or other prerequisites, where the architecture of that decision path requires them.

The independence defined by this ADR means that permissions are not inherited automatically; it does not require every possible combination of permissions to be valid.

Current `affects_decision` fields remain fixed to their safe value (`False`, `Literal[False]` in most locations) everywhere they are defined.
4. **Persistent Memory Mutation.** Whether information produced during one investigation may be persisted and later consumed by future investigations. This SHALL be treated independently of Reasoning Participation and Decision Influence, because persistent memory can influence future reasoning beyond the lifetime of the current request — a risk not present in the other three dimensions, which are scoped to one execution. No persistent-learning write path currently exists anywhere in the repository (§16).
5. **External Action Request.** No general external-action request mechanism currently exists in the repository, and this ADR SHALL NOT invent one. If such a mechanism is ever proposed in the future, requesting an action MUST remain architecturally distinct from authorization to execute it — a request is, at most, a computed output; it carries no authority of its own.
6. **Operational Execution Authority.** Operational Execution Authority is **not** a runtime-promotion dimension. It is outside GridMind runtime authority under this architecture, not pending future implementation. GridMind runtime SHALL NOT acquire operational authority merely because another computational dimension (1–5 above) is promoted. This is restated in full in §10.

## 7. Current Repository State

Recorded accurately, as verified in `docs/reviews/ADR-005-runtime-promotion-authority-analysis.md` against the current repository — none of the following is planned behavior described as live:

- GridMind does not currently implement a general active mode. No repository code defines, checks, or branches on an "active" runtime mode of any kind.
- `EngineResult`'s safety fields (`shadow_only`, `affects_reasoning`, `affects_decision`) are currently fixed to their safe values, type-enforced via `Literal[True]`/`Literal[False]`/`Literal[False]`.
- `ThinkingState`'s top-level safety fields are currently fixed to their safe values, the same type-enforced pattern.
- Capability decision influence remains fixed `False` (`Literal[False]`) on `CapabilityResult`, `CapabilityMetadata`, `CapabilityManifest`, and `CapabilityExecutionRecord`.
- `CapabilityPipelineStep.execution_mode` permits shadow execution only (`Literal["shadow"] = "shadow"`).
- Thinking's `DecideProcessor` writes `decide_stage` metadata that is advisory (`advisory_only: True`) and records `execution_authorized: False`.
- Thinking's `LearnProcessor` writes `learn_stage` metadata recording `review_required: True` and `memory_write_authorized: False`.
- No operational execution path exists anywhere in the repository — no code performs, requests, or represents a physical or external action (breaker operation, energization, protection-setting change, or control command).
- No persistent-learning write path exists — `ThinkingState.learning_items` is computed in memory and, at most, summarized back into an in-memory `EngineeringSession`; no database, file, or external store is written anywhere in the repository.
- No promotion mechanism currently exists — no code evaluates eligibility, grants permission, or transitions any component beyond its current fixed-safe state.

## 8. Technical Eligibility

Technical Eligibility is evidence that a component is technically qualified for a specific computational-influence dimension (§6, dimensions 1–5). Examples include, non-exhaustively: deterministic tests, domain validation, physics validation, traceability, failure-mode validation, calibration, and independent technical review (§11 defines these more fully).

**Technical eligibility does not itself grant permission.** A component may be technically eligible — fully tested, domain-validated, traceable — for a dimension and still not be permitted to operate in it, because eligibility answers "is this component capable of operating correctly at this level" while permission (§9) answers a separate question: "is this component allowed to, in this deployment, right now." `CapabilityManifest.status` (`"experimental"` / `"reviewed"` / `"approved"` / `"deprecated"`) is the one field already present in the repository structurally suited to record an eligibility claim of this kind — it exists today, unenforced (§14), and this ADR does not activate it.

## 9. Deployment / Runtime Permission

A governed deployment or runtime policy may determine whether an eligible component (§8) is permitted to participate in a specific computational dimension (§6, dimensions 1–5).

**A component SHALL NOT grant this permission to itself.** Self-declared metadata SHALL NOT constitute sufficient authorization — a field an artifact sets about itself is, at most, an eligibility claim (§8), never a permission grant. Runtime permission MUST fail closed if required policy cannot be verified (§12).

This ADR defines the architectural distinction between eligibility and permission only. **It does not implement such a policy system now.** No policy engine, permission service, approval workflow, or configuration mechanism is created by this ADR.

Deployment / Runtime Permission is not Operational Authorization.

It MAY be granted through independently governed deployment configuration or policy without requiring a human approval for every individual runtime invocation.

However, the component receiving the permission SHALL NOT be the authority that grants, modifies, or verifies its own permission.

## 10. Operational Authorization Boundary

Operational Authorization is the authority to perform an
external or physical operational action.

Under the architecture governed by this ADR, Operational Authorization is outside GridMind AI runtime and is not a runtime-promotion dimension.

No runtime component may derive, inherit, or self-grant Operational Authorization from any computational promotion.

Any future proposal to change this boundary would require a separate architecture decision, independent safety and governance review, and explicit supersession of this ADR.

Foundation, Capability Runtime, Thinking Runtime, Reasoning Runtime, `EngineeringBrain`, the ADR-003 adapters, `EngineRegistry`/`CapabilityRegistry`, orchestration (per ADR-004), and any future Kernel SHALL NOT become the source of operational authorization merely through runtime promotion. Promotion in any of dimensions 1–5 (§6) — including full Decision Influence — grants nothing toward dimension 6. No sequence or combination of promotions defined by this ADR crosses that boundary; it does not exist as a reachable state under this model.

## 11. Promotion Evidence

**Generic evidence categories** — applicable to a technical-eligibility claim (§8) for any component, in any dimension, as a starting checklist rather than a fixed requirement (§9 still governs whether eligibility becomes permission):

- Deterministic tests.
- Regression integrity (no existing guarantee regresses).
- Traceability / auditability (a record of what was claimed and on what basis).
- Malformed-input behavior.
- Failure-mode behavior.
- Rollback / reversibility.
- Independent technical review.

**Domain-dependent evidence categories** — applicable where the component's own domain makes them meaningful, not required universally:

- Domain validation.
- Physics validation (relevant to components consuming `app/transformer/physics.py`-style calculations; not relevant to, say, a knowledge-candidate capability).
- Conflict handling (relevant wherever an `unresolved_conflicts`/`blocking_conflicts` concept exists, as it already does in `EngineeringBrain` and Thinking's `ResolveConflictsProcessor`).
- Safety validation (relevant wherever `safety_findings` exist; see §15 for why this category cannot yet be satisfied by the current `SafetyGateProcessor` alone).
- Trusted shadow comparison (the natural evidence category for a component whose native algorithm does not yet exist, such as `ConfidencePropagationEngine`).
- Confidence / calibration validation (relevant only where a confidence score is produced; the repository's own `confidence_calibration` metadata already records `is_calibrated_probability: False` today, i.e., acknowledges its own values are not yet calibrated).

**Not every domain-specific criterion is required for every component.** Which domain-dependent categories apply is determined by the component's own domain and the specific dimension being sought, evaluated at the time a real promotion is proposed — this ADR does not pre-assign a fixed checklist to any specific current component.

## 12. Fail-Closed Requirements

Any future runtime-promotion mechanism SHALL fail closed when:

- permission cannot be verified;
- required policy is unavailable;
- promotion state is malformed;
- component identity or version cannot be verified;
- required eligibility evidence is absent;
- safety prerequisites applicable to the requested dimension are not satisfied.

**Missing promotion information SHALL NEVER default to a more permissive state.** This preserves, without modification, the fail-closed pattern the repository already exhibits pervasively today — `Literal`-locked construction failures, `CapabilityRegistry`'s ABI/manifest cross-validation raising on mismatch, and `CapabilityRuntime`'s shadow-mode rejection — extended explicitly to any future promotion mechanism rather than left to be assumed.

## 13. Anti-Privilege-Escalation Rules

The following are explicitly prohibited, effective from this ADR forward, for any future promotion-related work:

- A global "active" switch granting multiple dimensions at once.
- Interpreting a change from `Literal[False]` to plain `bool` on any safety field as promotion implementation — this is a type change that removes a guarantee, not a permission grant, and MUST NOT be treated as equivalent to one.
- Caller-controlled `execution_mode` (or any equivalent caller-supplied value) being sufficient authority on its own.
- Component metadata self-authorizing promotion — an artifact's own declared fields are eligibility evidence (§8) at most, never authorization (§9).
- `CapabilityManifest.status` alone granting runtime permission, now or if it is ever wired up in the future — status remains an eligibility-adjacent field unless and until a separate, explicit permission mechanism is designed to consume it under the rules in §9.
- Decision Influence implying Operational Execution Authority.
- Orchestration authority implying Operational Execution Authority (§10, §24).
- Memory-write authority being inherited automatically from Reasoning Participation or Decision Influence permission — Persistent Memory Mutation (§6, dimension 4) is independently governed (§16) and is never a side effect of another dimension's promotion.
- Bypassing a required future promotion-policy boundary by invoking a native runtime directly instead of through whatever mechanism enforces that policy — mirroring the existing, unenforced risk that a caller today can already invoke `CapabilityRuntime`/`EngineeringThinkingEngine` directly instead of through the ADR-003 adapters.

## 14. Capability shadow_only Risk

Recorded as a repository-backed architectural risk, not fixed by this ADR:

`CapabilityMetadata.shadow_only` and `CapabilityManifest.shadow_only` are plain `bool` fields (`app/capabilities/contracts.py`, `app/capabilities/manifest.py`), not type-locked `Literal[True]` fields — unlike `affects_decision` on those same two classes, which is `Literal[False]`. `CapabilityRuntime.invoke()`'s rejection of non-shadow execution is conditional on `metadata.shadow_only` (`if metadata.shadow_only and execution_mode != "shadow": reject`). Therefore, a future capability that self-declares `shadow_only=False` in its own `metadata()`/manifest could structurally bypass that particular runtime shadow-mode rejection for itself — `CapabilityRegistry.register()` cross-validates that a capability's `metadata` and `manifest` agree with each other on this field, but nothing validates the field's *value* against any external policy.

**This is not evidence of existing operational authority** — every one of the four capabilities currently registered in the repository sets `shadow_only=True`, verified directly, with no exception found. **It is an architectural privilege-escalation risk for any future promotion implementation**, and the concrete illustration of why §9 requires that "a component's own metadata or manifest SHALL NOT be sufficient to grant itself runtime permission" — this finding is the evidence that rule exists to prevent.

This ADR does not fix the code. It is recorded here as follow-up implementation work requiring separate review (§26, item 1).

## 15. Safety Gate Semantics

Recorded accurately: the current Thinking `SafetyGateProcessor` classifies safety findings by severity and records a `safety_status` value in stage metadata. **It does not currently halt the full Thinking pipeline** — `EngineeringThinkingEngine`'s fixed stage sequence runs `DECIDE`, `EXPLAIN`, and `LEARN` unconditionally regardless of `safety_status`, including when `safety_status == "critical_findings"`.

**Therefore the current implementation SHALL NOT be described as a blocking safety gate.** This ADR does not change this behavior. Evaluation of blocking safety semantics — i.e., whether and how a future safety-gate implementation should actually halt or restrict downstream processing — is recorded as separate future architecture/implementation work (§26, item 3) that MUST be resolved before any future component receives Decision Influence permission, since Decision Influence is exactly the dimension a non-blocking safety classification would be least sufficient to guard.

## 16. Persistent Memory Governance

Persistent Memory Mutation (§6, dimension 4) is governed independently of Reasoning Participation and Decision Influence, for the reason stated in §6: information written to persistent memory can influence future reasoning beyond the lifetime of the request that produced it, a risk the other three computational dimensions do not carry.

No persistent-learning write path currently exists. `LearnProcessor` extracts learning-item candidates from `state.decisions`, `state.explanations`, and `state.safety_findings`, appends them to `ThinkingState.learning_items` (an in-memory field on a frozen model), and records `review_required: True` / `memory_write_authorized: False` in stage metadata — but no database, file, or external store is ever written. `EngineeringSession`, the only other candidate location for persisted state, is an in-memory dataclass with no persistence mechanism of its own.

Because no write path exists, `memory_write_authorized: False` currently guards nothing that could otherwise occur — it documents an intended future restriction, not an presently-enforced one. This ADR does not change that. Defining actual persistent-memory governance — what evidence, review, and fail-closed behavior a future write path would require — is recorded as separate future work (§26, item 4), to be resolved before any learning candidate can be written durably, not before this ADR.

## 17. Integration Rules

- This ADR's dimension model (§6) applies conceptually to any current or future `Engine`-compatible component, any native Capability, any Thinking stage, and any future Reasoning/Knowledge/Physics mechanism — it does not require any of them to change today.
- No existing contract, processor, adapter, runtime, or registry is required to add, remove, or rename a field as a result of this ADR.
- Any future promotion-policy implementation (§9) SHALL be evaluated and designed only when a real component becomes a candidate for Reasoning Participation or Decision Influence (§26, item 2) — this ADR does not pre-build that mechanism speculatively, consistent with ADR-002/003/004's shared methodology of not inventing architecture ahead of evidence.
- Any future promotion-policy implementation SHALL be consumed by runtimes (`CapabilityRuntime`, `EngineeringThinkingEngine`, or their successors) as an enforcement point, mirroring how `CapabilityRuntime` already enforces (imperfectly, per §14) a shadow-mode check today — never self-evaluated by the component seeking promotion.

## 18. Backward Compatibility

ADR-005 SHALL require zero production behavior change now. Current fail-closed behavior remains unchanged in every respect. No component is promoted by accepting this ADR. No `Literal` safety restriction is relaxed. No active mode is created. No permission service is created. No operational-action path is created. Every statement in §7 (Current Repository State) remains true immediately after this ADR is accepted.

## 19. Consequences

- Future promotion work has a pre-agreed conceptual model (independent dimensions, eligibility distinct from permission distinct from operational authorization) instead of an ad hoc decision made under implementation pressure, reducing the risk of the exact failure modes named in §13.
- The `CapabilityMetadata`/`CapabilityManifest.shadow_only` risk (§14) is now a documented, named architectural finding rather than a silent gap, giving the Chief AI Architect a concrete, already-evidenced item to schedule.
- `SafetyGateProcessor`'s non-blocking nature (§15) is now explicitly on record, preventing a future implementer from assuming "safety gate" already means "blocks progress."
- Persistent memory is now explicitly flagged as requiring its own governance track (§16) rather than being swept into whatever mechanism eventually governs Reasoning Participation or Decision Influence.
- No new component, service, or runtime behavior exists as a result of this ADR — the entire effect is documentation and constraint, per §18.

## 20. Alternatives Considered

### A — Binary Shadow / Active

Rejected. A single switch cannot express that Reasoning Participation, Decision Influence, and Persistent Memory Mutation are independently-evidenced concerns (`docs/reviews/ADR-005-runtime-promotion-authority-analysis.md`, Analyses 1–4, 6-7) without either conflating them or reducing "active" to mean "the most restrictive dimension is satisfied," which defeats the purpose of the switch. Also the model of promotion this repository's own architecture has never at any point suggested — no code artifact anywhere implies a single active/inactive toggle.

### B — Ordered Promotion Ladder (shadow → reasoning → decision → execution)

Rejected. Implies an enforcement order (e.g., decision influence requires reasoning participation first) not evidenced anywhere in the repository — `docs/reviews/ADR-005-runtime-promotion-authority-analysis.md` Analysis 4 found `DecideProcessor` does not currently consume Thinking's own reasoning output at all, so an ordering assumption of this kind would not even describe the one real decision-adjacent mechanism in the codebase accurately. Also implies execution sits at the top of the same ladder as computational dimensions, directly contradicting §10 and ADR-004 §10's insistence that operational authority is categorically outside runtime authority, not a further rung.

### C — Independent Authority Dimensions (selected)

**Selected**, as detailed in §6. This is the model the repository already exhibits empirically — `shadow_only`, `affects_reasoning`, and `affects_decision` already vary as separate fields in the type system today, even though every current value is the safe one. This ADR formalizes what already exists structurally rather than inventing new architecture.

**Selecting Option C does not mean a generic permission framework must be implemented now.** §9 states this explicitly: this ADR defines the *distinction* between eligibility and permission, not a policy engine. §17 states that any future promotion-policy implementation is designed only when a real candidate component exists (§26, item 2), consistent with §18's zero-code-change requirement. Naming independent dimensions is a documentation and constraint decision; building a mechanism to grant them is separate, later, evidence-gated work this ADR does not authorize.

### D — Runtime-Specific Promotion Policies

Considered, not selected as the primary model. Would let Capability Runtime, Thinking Runtime, and any future Reasoning/Knowledge/Physics runtime each define its own activation policy independently, mirroring ADR-004's Option C for orchestration. Not selected as the primary model because the dimensions themselves (Reasoning Participation, Decision Influence, Persistent Memory Mutation, and the permanent exclusion of Operational Execution Authority) are cross-cutting concerns that should mean the same thing regardless of which runtime is asking — inconsistent per-runtime definitions of "decision influence" would reintroduce exactly the semantic drift `docs/reviews/ADR-005-runtime-promotion-authority-analysis.md` Analysis 2 found already exists around "shadow." The *evidence* required to satisfy a dimension (§11) is legitimately domain-specific and runtime-specific, and this ADR already accommodates that; the *dimension names and their independence from one another* (§6, §13) are not left to per-runtime redefinition.

## 21. Relationship to ADR-001

ADR-001 established Foundation's non-authoritative-by-default contract (`shadow_only`, `affects_reasoning`, `affects_decision` on `EngineResult`) as domain-agnostic, type-enforced constants. This ADR does not modify that contract, and explicitly relies on it as the model for what a properly type-locked safety field looks like (§14 contrasts it with the un-locked `CapabilityMetadata.shadow_only`/`CapabilityManifest.shadow_only`). ADR-001 is unaffected.

## 22. Relationship to ADR-002

ADR-002 established the Layered Runtime Architecture and the principle that Layer 1 runtimes retain their own native machinery. This ADR's dimension model (§6) and evidence categories (§11) apply uniformly across any Layer 1 runtime without altering ADR-002's layer boundaries, and without requiring Capability Runtime or Thinking Runtime internals to change (§17, §18). ADR-002 is unaffected.

## 23. Relationship to ADR-003

ADR-003 defined and the repository has implemented the Runtime Adapter Pattern, preserving Foundation's fixed, non-authoritative `EngineResult` contract across the Capability and Thinking boundaries. This ADR's anti-escalation rules (§13) explicitly extend ADR-003's own safety pattern — native-safety-contract violation treated as a failure, never translated data — to any future promotion mechanism, and explicitly prohibits bypassing the adapters as a way around a future promotion-policy boundary. ADR-003's adapters are not modified by this ADR.

## 24. Relationship to ADR-004

ADR-004 established that orchestration authority is not operational execution authority, and that any future Kernel must coordinate computation only. This ADR preserves that boundary without exception: §10 states that orchestration (along with every other runtime component) SHALL NOT become the source of operational authorization merely through runtime promotion, and §6 (dimension 6) confirms Operational Execution Authority is not reachable through any combination of the promotion dimensions this ADR defines. A future Kernel, if ever introduced under ADR-004 §13's reconsideration triggers, SHALL NOT become an operational-authorization authority simply because it coordinates promoted components — coordinating components with Reasoning Participation or Decision Influence permission is still coordinating computation, not operational execution.

## 25. ARCHITECTURE.md Drift

`docs/ARCHITECTURE.md` materially lags the implemented runtime architecture and does not document current authority boundaries at all — it describes a generic FastAPI/PostgreSQL/Redis/Next.js platform with an "AI Engine" performing autonomous-sounding tasks ("Fault Prediction," "Grid Optimization"), with no mention of Foundation, the layered runtime, shadow-mode enforcement, or any of the authority concepts this ADR and ADR-001 through ADR-004 define. A reader relying on `ARCHITECTURE.md` alone would have no way to know GridMind's actual runtime is this restrictive. This ADR does not modify `ARCHITECTURE.md`. Master reconciliation of `ARCHITECTURE.md` against ADR-001 through ADR-005 remains separate future architecture work (§26, item 5).

## 26. Follow-Up Work

Recorded, without implementing any of the following:

1. Evaluate hardening `CapabilityMetadata.shadow_only` and `CapabilityManifest.shadow_only` so self-declaration cannot become runtime permission (§14).
2. Define a future promotion-policy boundary only when a real component becomes a candidate for Reasoning Participation or Decision Influence (§9, §17).
3. Evaluate blocking safety semantics before any component can receive Decision Influence permission (§15).
4. Define persistent-memory governance before any learning candidate can be written durably (§16).
5. Reconcile `docs/ARCHITECTURE.md` with ADR-001 through ADR-005 in a separate architecture decision or work item (§25).

## 27. Decision Owner

Chief Architect (Chief AI Architect), consistent with ADR-001, ADR-002, ADR-003, and ADR-004. AI-authored analysis and documentation, including this document, may recommend but does not carry architectural authority.