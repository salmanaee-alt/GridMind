# ADR-003 — Runtime Adapter Pattern

## 1. Status

ِACCEPTED. (Revision 2 — controlled revision. The Runtime Adapter Pattern selected in Revision 1 is unchanged. This revision: corrects the authority-flag model from "propagate native flags" to "Foundation's flags are fixed constants; adapters validate native conformance and treat violations as safety failures"; removes a hard-coded Thinking stage-count assumption; marks the `PARTIAL` status mapping and the `EngineExecutionError` exception choice as subject to implementation review rather than settled; separates diagnostics into architectural requirements versus implementation recommendations; fixes the Capability payload mapping to a minimal canonical rule; corrects a file-impact statement that contradicted itself; and reframes the Context section's sourcing note to attribute supplied repository facts to the Decision Owner's own execution rather than implying independent inspection. No section not listed above was substantively changed.)

This ADR defines a contract pattern only. It does not implement code, does not modify the repository, does not redesign Capability Runtime or Thinking Runtime, and does not introduce a Kernel or general orchestration layer. Per ADR-001 and ADR-002's shared precedent, AI-authored analysis may recommend but does not carry architectural authority; formal ACCEPTED status requires the Decision Owner's sign-off (§27).

## 2. Context

ADR-001 established the Runtime Foundation (`app/foundation/`): `ExecutionContext`, `EngineMetadata`, `EngineResult`, `EngineDiagnostics`, the `Engine` protocol, and `EngineRegistry`, kept strictly domain-agnostic.

ADR-002 established the Canonical Layered Runtime Architecture: Foundation as Layer 0; Capability Runtime, Thinking Runtime, and Reasoning Runtime as Layer 1, each retaining its own native machinery; a deferred orchestration question (Layer 2, not decided); and — specifically — deferred the exact contract shape of the `Engine`-compatible boundary adapters Capability Runtime and Thinking Runtime were each required to eventually expose, naming this ADR (ADR-003) as the document that would define it.

**Sourcing note for this Context section.** This ADR was authored from supplied architectural and repository evidence, not from an independent repository inspection performed for this revision. The following implementation state is **supplied, and recorded as verified by the Decision Owner's own execution** — not independently re-inspected by this document:

- `ConfidencePropagationEngine` now consumes Foundation — the gap ADR-001 originally identified and ADR-002 §16 (Migration Strategy, phase 1) named as the first step.
- The duplicate confidence shadow flags previously present on the domain payload (ADR-002 §11, Reasoning Runtime Responsibilities) have been removed.
- `EngineResult`'s safety flags are type-enforced: `shadow_only: Literal[True] = True`, `affects_reasoning: Literal[False] = False`, `affects_decision: Literal[False] = False`. This supersedes ADR-002 Revision 2's "subject to implementation review" framing of this same item with a now-settled, type-enforced fact.
- Full regression: 698 passed.

This is recorded here as **dated implementation context**, attributable to the Decision Owner's own execution — not as an eternal architectural invariant that this ADR itself asserts, re-derives, or re-verifies. The decision in §5 onward is written to hold regardless of the exact current test count or the exact current migration state: it defines the adapter pattern for Capability Runtime and Thinking Runtime, and nothing in the supplied context above claims either of those two mechanisms has changed. Should this recorded state later prove inaccurate, or should it advance further before this ADR is next revisited, that is grounds to update this Context section in a future revision — it is not, by itself, grounds to change this ADR's adapter-pattern decision.

At the time of the repository review preceding ADR-002, neither Capability Runtime nor Thinking Runtime had any `Engine`-compatible boundary, and both were confirmed to be using only their native contracts (`EngineeringCapability`/`CapabilityRequest`/`CapabilityResult` and `ThinkingStageProcessor`/`ThinkingState`, respectively). Nothing in the supplied context above contradicts that remaining true today for these two mechanisms specifically — the supplied changes concern Reasoning, not Capability or Thinking.

## 3. Problem Statement

ADR-002 decided that Capability Runtime and Thinking Runtime each require an `Engine`-compatible boundary adapter, but deliberately left the adapter's contract shape undefined, to avoid conflating the layering decision with the adapter design decision. Without that design now being made explicitly, any future implementation attempt would have to invent the mapping between native contracts and Foundation's contracts ad hoc, which is exactly the condition that produced the original four-pattern fragmentation ADR-002 was written to resolve (Reasoning's `ConfidencePropagationResult` independently reinventing `EngineResult`'s shadow fields being the concrete example already on record, now resolved per §2). A single, canonical adapter pattern — defined once, before either adapter is written — prevents Capability's and Thinking's adapters from independently drifting into two more incompatible shapes.

## 4. Decision Drivers

- Prevent a repeat of the duplicated-contract pattern already observed once (Reasoning Contracts vs. `EngineResult`) from recurring at the adapter layer itself.
- Preserve every safety guarantee Capability Runtime and Thinking Runtime already have (process isolation, `Literal`-locked shadow/authority flags) without exception.
- Keep native contracts (`EngineeringCapability`, `CapabilityRegistry`, `CapabilityRuntime`, `CapabilityOrchestrator`, `ThinkingStageProcessor`, `EngineeringThinkingEngine`) completely unmodified — adapters wrap, they do not replace.
- Keep Foundation's domain-agnosticism intact — no adapter design may require Foundation's typed models to grow domain-specific fields.
- Avoid deciding, or appearing to decide, the orchestration/Kernel question ADR-002 already deferred.
- Produce a pattern specific enough that two different engineers implementing the Capability Adapter and the Thinking Adapter independently would arrive at compatible, not merely similar, designs.
- Treat Foundation's authority contract as fixed and non-negotiable at the adapter boundary, not as something an adapter computes or is trusted to get right at runtime.

## 5. Decision

Define the **Runtime Adapter Pattern**: a stateless wrapper, external to both Foundation and the native Layer 1 module it wraps, that implements the `Engine` protocol by translating at its boundary only — native input in, `ExecutionContext` in; `EngineResult` out, native output in between untouched.

Concretely:

- An adapter is a class (or equivalent) that satisfies `Engine` (`metadata` property, `execute(context: ExecutionContext) -> EngineResult`) by internally calling the native runtime's own, unmodified entry point.
- The **native request/state a native runtime needs is carried inside `ExecutionContext.resources`**, under one documented key per adapter type, not as new fields on `ExecutionContext` itself. This is the specific resolution to the tension identified in `RUNTIME_ARCHITECTURE_ANALYSIS.md` (`ExecutionContext` cannot grow domain fields, but Layer 1 mechanisms need to carry domain-specific native input somewhere): `resources` is already an untyped `dict[str, Any]` container that Foundation's own code never inspects or interprets — only the adapter does, and only inside its own module. Foundation's schema does not change.
- Two adapters are defined by this ADR: the **Capability Adapter** (§8) and the **Thinking Adapter** (§9). A third category, **future Knowledge/Physics adapters**, is named but not designed (§10), per ADR-002 §12.
- `CapabilityRuntime` itself is **not** converted into an `Engine`. The adapter sits at the boundary between one capability invocation (or the orchestrator, per implementation choice — see §8) and Foundation; `CapabilityRuntime`'s own orchestration, process isolation, and registry machinery are untouched and continue to be invoked natively by the adapter, not replaced by it.
- The 11 Thinking stage processors are **not** individually migrated to `Engine`. Only the outer `EngineeringThinkingEngine` boundary is adapted, per ADR-002 §10, unchanged by this ADR.
- No new orchestration semantics are introduced. An adapter executes exactly one native call per `execute(context)` invocation; it does not sequence, retry, or schedule anything the native runtime does not already do on its own.
- `EngineResult`'s authority fields (`shadow_only`, `affects_reasoning`, `affects_decision`) are fixed, type-enforced constants of the Foundation boundary (§2). This ADR's adapter pattern is built around that fact directly (§17), not around a "propagate the native flag" model.

This is Option C from `RUNTIME_ARCHITECTURE_ANALYSIS.md`, unmodified in substance.

## 6. Adapter Responsibilities

- Satisfy the `Engine` protocol shape at the boundary of one Layer 1 mechanism.
- Translate `ExecutionContext` into the native input the wrapped mechanism already accepts (§11).
- Invoke the native mechanism's existing, unmodified entry point exactly once.
- Translate the native output into `EngineResult`, `EngineDiagnostics`, and (where applicable) an `execution_summary` (§12).
- Validate that the native result it received remains within its own native safety contract, and ensure every `EngineResult` it emits satisfies Foundation's fixed, type-enforced non-authoritative contract (`shadow_only=True`, `affects_reasoning=False`, `affects_decision=False`) (§17). The adapter does not derive `EngineResult`'s authority fields from native flags — those fields are constants — and it treats a native safety-contract violation as a validation/safety failure, never as data to translate.
- Report native failures as a valid, non-exceptional `EngineResult` with `status=FAILED` wherever the native mechanism itself reports failure as data rather than as an exception (§14). Whether a `PARTIAL` status also applies to certain native configurations is subject to implementation review (§12) and is not decided by this responsibility list.

## 7. Adapter Non-Responsibilities

- An adapter does **not** perform engineering-domain validation, computation, or interpretation of any kind — that remains entirely inside the native mechanism.
- An adapter does **not** alter, extend, or bypass native validation (`EngineeringCapability.validate`, `CapabilityRegistry`'s ABI/manifest checks, `ThinkingState`'s pydantic validation).
- An adapter does **not** orchestrate multiple native calls, retries, or fallbacks. One `execute(context)` call maps to exactly one native invocation.
- An adapter does **not** register capabilities, stage processors, or reasoning engines on the native mechanism's behalf — native registration (`CapabilityRegistry.register`, the fixed processor tuple passed to `EngineeringThinkingEngine`) happens exactly as it does today, independent of whether an adapter exists.
- An adapter does **not** grant, imply, or route toward execution authority under any circumstance, and does **not** compute or influence `EngineResult`'s authority fields — those are fixed Foundation constants, not adapter output (§17).
- An adapter does **not** persist state between calls; it is stateless per invocation, matching `Engine`'s own contract.

## 8. Capability Adapter Boundary

| | |
|---|---|
| **Native input** | `CapabilityRequest` (`request_id`, `payload: dict`, `context: dict`, the latter typically including `"execution_mode": "shadow"`). |
| **Foundation input** | `ExecutionContext`, carrying the `CapabilityRequest` at `resources["capability_request"]`. |
| **Native output** | `CapabilityExecution` (`result: CapabilityResult`, `audit: dict`, `duration_ms: float`, `error: CapabilityError | None`), produced by `CapabilityRuntime.invoke(capability_id=, request=)`. |
| **Foundation output** | `EngineResult`, where **`EngineResult.payload = CapabilityResult.output`** — the canonical, minimal mapping (§12; audit information does not go into `payload`, see below); `CapabilityExecution.duration_ms`/`error` translated into `EngineDiagnostics` (§16); and `EngineResult`'s authority fields set to their fixed values (`shadow_only=True`, `affects_reasoning=False`, `affects_decision=False`) unconditionally, per Foundation's type contract. The adapter validates `CapabilityResult.affects_decision is False`, per the capability's own native `Literal[False]` contract, as a conformance check — not as a source of data for `EngineResult`'s flags (§17). |
| **What gets mapped** | Request identity (`request_id` → `EngineDiagnostics.metadata`), `CapabilityResult.output` as `payload`, execution timing, error classification. `CapabilityResult.affects_decision` is checked for native-contract conformance, not carried forward into `EngineResult`, whose authority fields are fixed constants. |
| **What remains native** | `CapabilityRegistry`'s ABI-version and manifest cross-validation; `CapabilityRuntime`'s shadow-mode enforcement, timeout handling, and process isolation; `CapabilityOrchestrator`'s dependency-ordered pipeline execution (the adapter wraps a single capability invocation — see open question in §26 on whether a second, orchestrator-level adapter is warranted); `EngineeringCapability.validate`/`.execute`/`.audit`. |
| **Must never be mapped into Foundation** | The `CapabilityRegistry`/`CapabilityManifest` ABI-versioning and domain regex constraints (`capability_id` pattern, `domain` field, `requires`/`produces` contract entries) — these are Capability-specific validation concepts and must not become part of `ExecutionContext`, `EngineMetadata`, or any other Foundation model. |

`CapabilityExecution.audit` and `CapabilityResult.audit` MAY be surfaced through `EngineDiagnostics.metadata` or `EngineResult.metadata`; neither is carried in `payload`, which is reserved for `CapabilityResult.output` only (§12, §13). This is a deliberate, minimal canonical rule, not left as an implementation choice — a later ADR may change it, this one does not leave it ambiguous.

Pseudocode signature only, not an implementation:

```
class CapabilityAdapter:  # implements Engine
    def __init__(self, capability_id: str, runtime: CapabilityRuntime): ...

    @property
    def metadata(self) -> EngineMetadata: ...
        # derived read-only from the registered capability's own
        # CapabilityMetadata/CapabilityManifest; not re-specified here

    def execute(self, context: ExecutionContext) -> EngineResult:
        request = context.resources["capability_request"]  # type: CapabilityRequest
        execution = self._runtime.invoke(
            capability_id=self._capability_id,
            request=request,
        )
        return _capability_execution_to_engine_result(execution)  # §12, §17
```

## 9. Thinking Adapter Boundary

| | |
|---|---|
| **Native input** | `ThinkingState`, as already produced today by `engineering_session_to_thinking_state(session)` (`app/thinking/session_adapter.py`, unmodified). |
| **Foundation input** | `ExecutionContext`, carrying the initial `ThinkingState` at `resources["thinking_state"]`. |
| **Native output** | The final `ThinkingState` returned by `EngineeringThinkingEngine.execute(state)`, after its configured stage sequence has run. |
| **Foundation output** | `EngineResult`, with a projection of the final `ThinkingState` (current stage, stage-history stage names, `state.metadata`) carried as `payload` — the same shape `run_shadow_thinking_pipeline` already assembles into `session.metadata["thinking"]` today, reused rather than redesigned — and `EngineResult`'s authority fields set to their fixed values (`shadow_only=True`, `affects_reasoning=False`, `affects_decision=False`) unconditionally, per Foundation's type contract. The adapter validates `ThinkingState.shadow_only`/`.affects_reasoning`/`.affects_decision` remain at their own native, type-locked values, as a conformance check — not as a source of data for `EngineResult`'s flags (§17). |
| **What gets mapped** | The stage-history projection, `state.metadata`, and (newly, by the adapter, since the native engine does not measure it) wall-clock execution time for `EngineDiagnostics.execution_time_ms`. `ThinkingState`'s own shadow/authority flags are checked for native-contract conformance, not carried forward into `EngineResult`, whose authority fields are fixed constants. |
| **What remains native** | `ThinkingStage`, `ThinkingStageRecord`, the fixed `_STAGE_ORDER` sequence, all 11 stage processors, and `ThinkingGraphContext`. The full `ThinkingState` object (observations, evidence, hypotheses, physics checks, safety findings, decisions, explanations, learning items) is **not** flattened into `EngineResult.payload` in full — only the same shallow projection already in production use is carried, consistent with "adapters are additive wrappers," not a new serialization design. |
| **Must never be mapped into Foundation** | `ThinkingState`'s domain fields themselves (`observations`, `evidence`, `hypotheses`, `physics_checks`, `safety_findings`, `decisions`, `explanations`, `learning_items`) must never become fields on `ExecutionContext` or `EngineResult` — they stay inside the native `ThinkingState` object, referenced only via the opaque `resources`/`payload` carriers, never promoted to typed Foundation fields. |

The adapter **MUST NOT** independently define Thinking pipeline topology. Any diagnostic value that depends on "how many stages" (§16.2) is derived from the specific `EngineeringThinkingEngine` instance actually invoked (its own configured processor sequence and the resulting `stage_history`), never from a number this ADR or the adapter hard-codes.

Pseudocode signature only, not an implementation:

```
class ThinkingAdapter:  # implements Engine
    def __init__(self, engine: EngineeringThinkingEngine): ...

    @property
    def metadata(self) -> EngineMetadata: ...
        # static identity for "the" default thinking pipeline;
        # not re-specified here

    def execute(self, context: ExecutionContext) -> EngineResult:
        initial_state = context.resources["thinking_state"]  # type: ThinkingState
        started = now()
        final_state = self._engine.execute(initial_state)
        elapsed_ms = now() - started
        return _thinking_state_to_engine_result(final_state, elapsed_ms)  # §12, §17
```

## 10. Future Knowledge/Physics Adapter Expectations

Per ADR-002 §12, Knowledge Runtime and Physics Runtime do not exist yet and are not designed by this ADR. When either is implemented, its adapter is expected to follow the same shape defined in §5–§9: native input carried in `ExecutionContext.resources` under its own documented key (e.g., `resources["knowledge_request"]`, `resources["physics_check_request"]`), native output translated into `EngineResult`/`EngineDiagnostics` without flattening domain-specific fields into Foundation's typed models, and `EngineResult`'s fixed authority constants applied unconditionally, with native-contract conformance validated rather than propagated (§17). This ADR does not specify what those native inputs/outputs would contain, since neither mechanism's native contract exists yet to adapt.

## 11. Input Mapping Rules

- **Native request/state** is the only thing an adapter is responsible for locating and passing through — it does not construct or validate it. For Capability, this is a caller-supplied `CapabilityRequest`; for Thinking, a caller-supplied `ThinkingState` (typically produced by the existing `engineering_session_to_thinking_state`, unmodified).
- **`ExecutionContext`** carries exactly the fields ADR-001 already defined (`correlation_id`, `created_at`, `resources`, `metadata`) — this ADR does not add fields to it.
- **`resources`** is the sole carrier for the native request/state, under one fixed, documented key per adapter (`"capability_request"`, `"thinking_state"`). An adapter **MUST** treat a missing key as an adapter-level precondition failure (§15), not silently substitute a default.
- **`metadata`** carries descriptive, non-executable annotations only (e.g., trace tags, requested-by information) — never domain data that participates in execution, and never re-read by the adapter as an input to its own decision-making (no round-tripping metadata as a second, undocumented control channel).

## 12. Output Mapping Rules

- **`EngineResult.status`**: derived from the native result's own success/failure signal — `CapabilityResult.status` maps directly (`"success"` → `SUCCESS`, `"error"` → `FAILED`, `"skipped"` → `SKIPPED`); for Thinking, `SUCCESS` if the final state reached `ThinkingStage.COMPLETED` with no unhandled adapter-level exception, `FAILED` if the adapter itself could not complete the call. **Whether a `PARTIAL` status applies when an `EngineeringThinkingEngine` instance is constructed with fewer than its full configured stage set is SUBJECT TO IMPLEMENTATION REVIEW** — no native Thinking contract currently defines "partial pipeline" as a distinct, reportable condition, and this ADR does not invent that semantic. The adapter reports native semantics as they exist today (`SUCCESS`/`FAILED`); a `PARTIAL` mapping is a candidate for implementation review (§26), not a normative rule of this ADR.
- **`payload`**: `EngineResult.payload = CapabilityResult.output` for Capability — the canonical, minimal mapping; audit/traceability data does **not** go into `payload` (§8, §13). For Thinking, the existing stage-history/metadata projection, reusing production-shape data rather than inventing new serialization. No other native object is flattened into `payload`.
- **`diagnostics`**: an `EngineDiagnostics` instance, populated per §16 — see §16 for the distinction between architectural requirements and implementation mapping recommendations.
- **`execution_summary`**: one adapter-synthesized, human-readable sentence (e.g., `"Capability {capability_id} completed with status {status}."` / `"Thinking pipeline completed through stage {stage}."`). Descriptive only; never used as a control signal.
- **Authority flags**: `EngineResult.shadow_only`, `.affects_reasoning`, and `.affects_decision` are fixed, type-enforced constants (`True`/`False`/`False`) for every `EngineResult` emitted through the Foundation boundary. The adapter does not derive these values from the native result — it validates that the native result remains within its own native safety contract and treats a violation as a validation/safety failure (§17), never as a basis for computing a different `EngineResult` value.

## 13. Metadata Mapping Rules

- `EngineResult.metadata` holds adapter- and native-runtime bookkeeping useful for traceability (e.g., `capability_id`, pipeline version, `request_id`) — descriptive, not executable.
- `EngineDiagnostics.metadata` (a separate dict field already defined on `EngineDiagnostics`) is reserved for diagnostic-specific bookkeeping the native mechanism already produces (e.g., Capability's `retryable` flag from `CapabilityError`, per §14) rather than duplicating what belongs in `EngineResult.metadata`.
- `CapabilityExecution.audit` / `CapabilityResult.audit`, if surfaced at all, belongs in one of the two metadata locations above — never in `payload`, which is reserved for `CapabilityResult.output` only (§8, §12). This rule stands unless a later ADR explicitly changes it.
- Neither metadata dict may be the sole carrier of information required for correctness — anything load-bearing belongs in `payload` or a typed field; metadata is for context a human or log reader needs, not for data the next step in a pipeline depends on.

## 14. Error Mapping Rules

- **Capability errors**: `CapabilityExecution.error` (a `CapabilityError` with `error_type`, `message`, `capability_id`, `request_id`, `stage`, `retryable`) maps to `EngineResult.status = FAILED`, `diagnostics.errors = (error.message,)`, `diagnostics.metadata["error_type"] = error.error_type`, `diagnostics.metadata["retryable"] = error.retryable`, and `execution_summary` naming the failing stage (`validate`/`execute`/`audit`/`runtime`).
- **Thinking errors**: none of the current 11 stage processors raise on failure — each always returns a valid `ThinkingState`. If a future stage processor were to raise, the adapter maps any exception surfaced during the native `.execute(state)` call to `EngineResult.status = FAILED` with the exception's message in `diagnostics.errors`, and does not let the exception propagate past the adapter boundary uncaught.
- **Adapter-level failures** (e.g., the documented `resources` key is missing, §11) are a distinct category from native-runtime failures and are raised as an adapter-specific precondition error, not silently converted into a `FAILED` `EngineResult` — a caller that forgot to populate `resources` correctly has made a programming error, not triggered a business-logic failure, and the two should not look the same to a caller.
- **Native safety-contract violations** (§17) are a third, distinct category: a native result that does not conform to its own expected native safety contract (for example, if a future capability or component somehow produced `affects_decision != False` despite its own typing) **MUST NOT** be translated into a `FAILED`-but-otherwise-normal `EngineResult`, and **MUST NOT** be silently coerced into a safe-looking result either. It is treated as a validation/safety failure, distinct from both adapter-precondition errors and ordinary native business failures.
- **The use of `EngineExecutionError`** (defined in ADR-001, currently unused anywhere in the repository) for adapter precondition failures, and/or for native safety-contract violations, **is subject to implementation review against the current Foundation exception contract**. This ADR does not assert `EngineExecutionError` as the definitive canonical exception for either case merely because it currently exists unused, and this ADR does not define a new exception type.

## 15. Validation Boundaries

- `ExecutionContextValidator` (Foundation, unchanged) MAY be run by a caller before invoking an adapter, exactly as it could be run before any other `Engine`. Its checks (non-blank `correlation_id`, a warning if `resources` is empty) are unchanged and are not adapter-specific.
- All engineering-domain validation remains entirely native and unduplicated: `EngineeringCapability.validate(request)`, `CapabilityRegistry`'s ABI/manifest cross-validation, and `ThinkingState`'s own pydantic field validation are unaffected by, and not repeated by, the adapter.
- This ADR introduces **two** narrow, additive validation responsibilities, not one:
  1. An adapter confirms its documented `resources` key is present and holds an object of the expected native type, before attempting to use it — a precondition check; failure here is an adapter-level error (§14).
  2. An adapter validates that the native result it received remains within its own native safety contract before constructing an `EngineResult` from it (§17) — a safety check, not new business validation; failure here is a validation/safety failure (§14), distinct from an ordinary precondition error.

## 16. Diagnostics Mapping

### 16.1 Architectural Requirements

The following are normative (MUST), independent of implementation choice:

- Every `EngineResult` emitted by an adapter MUST include an `EngineDiagnostics` instance, populated with real values wherever the native result provides an unambiguous signal — not left at defaults when real data exists.
- `EngineDiagnostics.errors` MUST contain the native failure message whenever the native result reports failure (§14).
- Diagnostics MUST NOT be used to carry information that contradicts, or attempts to influence, `EngineResult`'s fixed authority fields (§17) — diagnostics is descriptive telemetry, never an authority channel.
- Diagnostics MUST NOT contain fabricated data that cannot be derived from the native result or from the adapter's own direct observation of the call (adapter-measured wall-clock time is a direct observation and is permitted; an invented score or metric would not be).

### 16.2 Implementation Mapping Recommendations (subject to implementation review)

The following is a recommended default mapping, not a normative requirement of this ADR. Where a field is directly and unambiguously supported by an existing native contract field, that is noted; where a field requires the adapter to compute a value, the source of that computation is stated explicitly, and no hard-coded topology constant is used.

| `EngineDiagnostics` field | Capability Adapter (recommended) | Thinking Adapter (recommended) |
|---|---|---|
| `execution_time_ms` | `CapabilityExecution.duration_ms`, direct passthrough — directly supported by the existing native contract. | Wall-clock time measured by the adapter around the native call — the native engine does not measure this itself; this is adapter-side instrumentation, not a native contract value. |
| `processed_items` / `skipped_items` | Recommended: `1`/`0` split based on whether the capability reached `execute`. Not mandated by any native contract field; subject to implementation review. | Recommended: derived from the length of the resulting `stage_history` compared against the specific `EngineeringThinkingEngine` instance's own configured processor sequence (e.g., `len(engine.processors)`) — **read from the invoked engine instance itself, never a hard-coded stage-count constant.** The adapter must not independently define Thinking pipeline topology. |
| `coverage` | Not populated unless a future capability defines a meaningful notion of partial coverage; `None` by default. | Recommended: stages present in `stage_history` ÷ the invoked engine's own configured stage count — the same repository-derived count used for `processed_items`, never a hard-coded number. |
| `warnings` | Empty tuple today (no native warning channel exists on `CapabilityResult`). | Empty tuple today (no native warning channel exists on `ThinkingState`). |
| `traceability` | `(request.request_id,)` at minimum — directly supported. | The mapped `stage_history` stage names, as already produced today by `run_shadow_thinking_pipeline` — directly supported by existing production behavior. |
| `metadata` | `error_type`/`retryable` (§14), `capability_id`; `CapabilityExecution.audit`/`CapabilityResult.audit` MAY also be surfaced here (§13). | Pipeline identity/version, if supplied by the caller via `ExecutionContext.metadata`. |

None of the formulas above is an architectural invariant. They are a recommended starting point for implementation, to be confirmed or revised during implementation review against the actual native contracts at build time (§26).

## 17. Safety and Authority Invariants

These are non-negotiable, independent of implementation detail:

- Foundation's `EngineResult` contract type-enforces `shadow_only: Literal[True] = True`, `affects_reasoning: Literal[False] = False`, `affects_decision: Literal[False] = False` (§2). These are **constants of the Foundation boundary itself**, not values an adapter computes, derives, or propagates from anywhere. Every `EngineResult` an adapter emits **MUST** satisfy these three values, unconditionally.
- The adapter **MAY** validate that the native result it received remains within its own native safety contract — for example, confirming `CapabilityResult.affects_decision is False` per the capability's own `Literal[False]` typing, or confirming `ThinkingState.shadow_only is True` per its own `Literal[True]` typing. This is a consistency check, not a source of data for `EngineResult`'s authority fields.
- The adapter **MUST NOT** use native flags — or their absence — to elevate, weaken, or otherwise influence Foundation's fixed authority contract in any direction. There is nothing to "propagate," "default," or "upgrade": the Foundation-side values are fixed regardless of what the native side reports.
- **A native result that violates its own expected native safety contract MUST NOT be translated into an `EngineResult` at all — including a superficially safe-looking one.** This condition **MUST** be treated as a validation/safety failure (§14, §15), surfaced to the caller as such, not silently absorbed by emitting a compliant-looking `EngineResult` over a non-compliant native result. Papering over a native safety violation with Foundation's fixed-safe defaults would hide the violation rather than report it, which would itself be a safety failure of the adapter.
- No adapter, under any circumstance, constructs, forwards, or references a control/execution instruction of any kind. Adapters translate result *representations*; they do not touch — and Foundation's contracts do not define — anything resembling an execution command.
- This is the same Authority Chain the Handbook establishes at every other layer (Engineering Analysis → Recommendation → Authorization → Execution): an adapter operates entirely within "Recommendation" and never approaches "Authorization" or "Execution." Because `EngineResult`'s authority fields are type-fixed constants rather than adapter-computed values, this boundary is enforced by Foundation's own type system at the point of construction, not solely by adapter discipline.

## 18. Registry Behavior

- Foundation defines the canonical registry contract (`EngineRegistry`: register/resolve/exists/unregister/clear/list/count), per ADR-002 §13, unchanged by this ADR.
- **Adapters do not imply, require, or create one global registry instance.** A `CapabilityAdapter` or `ThinkingAdapter` MAY be registered into an `EngineRegistry` if and when a caller wants to resolve it by name alongside other `Engine`s, but nothing in this ADR mandates that every adapter be registered, or that all adapters share one registry instance across the application.
- `CapabilityRegistry` remains its own specialized registry, performing ABI/manifest validation `EngineRegistry` does not and was never asked to perform (ADR-002 §13). It is not replaced, wrapped, or subsumed by `EngineRegistry` as part of adopting the adapter pattern.
- An adapter's own identity (its `EngineMetadata.name`) is independent of the native mechanism's own registration key (a capability's `capability_id`, or the fact that Thinking has no registration concept at all today) — the adapter chooses its own `EngineMetadata.name` for `EngineRegistry` purposes, if it is registered at all.

## 19. Dependency Rules

Extending ADR-002 §14 (R-001–R-004), specific to adapters:

- **R-005 — Adapters live in their native module, not in Foundation.** The Capability Adapter belongs to `app/capabilities/`; the Thinking Adapter belongs to `app/thinking/`. Neither lives in, nor is imported by, `app/foundation/`.
- **R-006 — Adapters depend downward only.** An adapter module imports from its own native package and from `app.foundation`. It does not import from any other Layer 1 package (the Capability Adapter does not import anything from `app.thinking`, and vice versa), consistent with ADR-002's R-002 (no sideways dependency between Layer 1 mechanisms).
- **R-007 — Foundation never imports an adapter.** Enforced by the existing Architecture Boundary Test's scope (it already forbids `foundation/` from importing `app.capabilities`/`app.thinking`; adapters living outside `foundation/` do not change this).

## 20. Backward Compatibility

- Purely additive: `EngineeringCapability`, `CapabilityRegistry`, `CapabilityRuntime`, `CapabilityOrchestrator`, `ThinkingStageProcessor`, and `EngineeringThinkingEngine` are unmodified by this ADR's decision.
- No existing call site (`app/transformer/engineer.py`, `app/brain/engineering_brain.py`) is required to change, or to adopt the adapter, as a consequence of this ADR. Adapters exist as an additional integration surface, not a replacement for the direct native calls those files already make.
- No currently-passing test is expected to require modification as a direct result of adopting this pattern; new tests are added (§22), none are changed.

## 21. Migration Sequence

Sequenced, incremental, none of it performed by this ADR:

1. Implement the Capability Adapter as a new module (§8), tested in isolation against a dummy or existing registered capability.
2. Implement the Thinking Adapter as a new module (§9), tested in isolation against `build_default_thinking_engine()`.
3. Optionally register either or both adapters into an `EngineRegistry` instance, if and when a consumer needs to resolve them by name — not required by this ADR (§18).
4. No change to existing call sites is scheduled by this migration sequence. Whether and when `app/transformer/engineer.py` or `app/brain/engineering_brain.py` adopt the adapters (instead of, or alongside, their current direct native calls) is a separate decision, out of scope here.
5. Revisit §26's open questions once both adapters exist and have real usage to evaluate against.

## 22. Test Requirements

For each adapter (Capability, Thinking), at minimum:

- `metadata` property returns a valid `EngineMetadata`.
- `execute()` with a well-formed `ExecutionContext` (correct `resources` key populated) and a successful, native-safety-conformant outcome produces an `EngineResult` with `status=SUCCESS`, correctly populated `payload`, and `diagnostics` matching §16's mapping table.
- `execute()` with a native failure outcome produces `status=FAILED`, non-empty `diagnostics.errors`, and a descriptive `execution_summary`.
- `execute()` with a missing `resources` key raises the adapter-level precondition error defined in §14/§15, not a silent default or a misleading `EngineResult`.
- **Authority flags, always-fixed:** a dedicated test asserting the adapter's output `EngineResult` has `shadow_only=True`, `affects_reasoning=False`, `affects_decision=False` in every tested case, confirming these are Foundation-side constants, not values that vary with native input.
- **Native safety-contract violation handling:** a dedicated test asserting that a native result which fails its own native safety contract (e.g., a mocked or simulated non-conforming result) causes the adapter to raise a validation/safety failure rather than emit any `EngineResult`, including a compliant-looking one.
- (Capability Adapter only) An end-to-end test using one of the four already-registered capabilities (`evidence_interpretation`, `knowledge` candidate, `knowledge_relevance`, `traceable_context`) through the adapter, confirming parity with calling `CapabilityRuntime.invoke` directly.
- (Thinking Adapter only) A test confirming the adapter's mapped `stage_history` matches what `run_shadow_thinking_pipeline` already produces natively for the same input, confirming the adapter is a faithful projection, not a divergent one.

## 23. Architecture Boundary Tests

- The existing `test_foundation_has_no_forbidden_dependencies` test (scoped to `app/foundation/`) requires no change — adapters live outside `foundation/` and do not alter what that test checks.
- A **new** boundary test is recommended (not created by this ADR): confirm that `app/capabilities/`'s adapter module does not import from `app.thinking`, and that `app/thinking/`'s adapter module does not import from `app.capabilities` — enforcing R-006 (§19) the same way the existing test enforces R-001.
- A **second new** boundary test is optionally recommended: a positive-direction check confirming each adapter module *does* import from `app.foundation`, so an adapter that silently stops satisfying `Engine` (e.g., after a refactor) is caught by CI rather than discovered later. This is optional and named here as a recommendation, not a requirement of this ADR.

## 24. Risks

| Risk | Mitigation |
|---|---|
| The `resources["capability_request"]` / `resources["thinking_state"]` key convention is undocumented outside this ADR and could drift or be typo'd at call sites with no compile-time check (since `resources` is `dict[str, Any]`). | Centralize the key names as named constants in each adapter module at implementation time; cover with the missing-key test in §22. |
| An adapter is implemented for Capability or Thinking but never adopted by any real caller, leaving it in the same unconsumed state Foundation itself has been in since ADR-001. | Track adoption as part of the migration sequence (§21) review; this is a known, named risk pattern in this project already (ADR-002 §20 raised the same risk about Foundation itself). |
| A future contributor treats the adapter's `payload` projection as a stable, complete substitute for the native result and builds logic against it that the native result would have supported but the projection omits (e.g., full `ThinkingState` fields not carried into `payload`). | §9 and §12 explicitly scope `payload` to the existing production projection, not the full native object; this should be stated in the adapter's own docstring at implementation time. |
| Wall-clock timing added at the Thinking Adapter boundary (§16.2) could diverge from a future native timing mechanism if one is ever added to `EngineeringThinkingEngine` itself, producing two inconsistent timing sources. | Flagged here; not resolved by this ADR. If native timing is ever added, the adapter should prefer it over its own measurement. |
| The native-safety-contract validation check itself (§17) could be implemented incorrectly — too strict (rejecting valid native results) or too lenient (missing a genuine violation) — since this ADR defines the rule but not the concrete implementation. | Implementation review and the dedicated safety-violation test (§22) are the intended safeguards; this ADR does not implement the check itself. |
| Scope creep: an implementer uses "building the adapter" as an opportunity to also refactor `CapabilityRuntime` or `EngineeringThinkingEngine` internals. | §6, §7, and the Absolute Constraints governing this ADR explicitly restrict adapters to additive wrapping; any internal refactor requires its own separate review. |

## 25. Alternatives Considered

### Adapter as a subclass or mixin of the native class

Rejected. Would blur the boundary between native contract and Foundation contract, making it harder to verify (by inspection or by test) that the native contract is genuinely untouched. A separate, external wrapper class keeps the two contracts visibly and mechanically distinct.

### Modify `EngineeringCapability` / `ThinkingStageProcessor` to satisfy `Engine` directly

Rejected. This is precisely what ADR-002 already declined to do (§9, §10 of ADR-002: native contracts are not replaced) and what this ADR's own absolute constraints reiterate. It would also require changing tested, live-wired production code as a side effect of a documentation decision.

### One universal adapter base class for all Layer 1 mechanisms

Rejected. Capability's and Thinking's native input/output shapes differ enough (a discrete request/result pair vs. a threaded, accumulating state) that a shared base class would either be too abstract to provide real value or would leak assumptions from one mechanism into the other. Each adapter is independently defined against its own native shape, following the same *pattern* (§5–§7) rather than sharing a common superclass.

### Adapt at the `CapabilityOrchestrator` level instead of the single-capability level

Considered, not decided. Wrapping the orchestrator (multi-capability, dependency-ordered execution) as a single `Engine` was considered as an alternative or complement to wrapping individual capabilities. This ADR defines the single-capability adapter (§8) as the canonical unit, since it is the smaller, more composable boundary consistent with `Engine`'s own single-unit-of-work shape; whether an orchestrator-level adapter is also warranted is left as an open question (§26), not decided here.

### Let the adapter propagate native authority flags into EngineResult

Considered in Revision 1 of this ADR; rejected in this revision. With `EngineResult`'s authority fields now confirmed type-enforced as fixed constants (§2), there is nothing meaningful to "propagate" — the Foundation-side values do not vary. The adapter's role with respect to native flags is validation of native-contract conformance, not translation of a variable value (§17).

## 26. Future ADRs

- **Runtime Orchestration / Kernel ADR** (already named in ADR-002 §21) — unaffected by this ADR; still deferred.
- **Knowledge Adapter / Physics Adapter design**, once either runtime exists (§10) — this ADR only names the expectation, not the design.
- **Orchestrator-level Capability Adapter**, if the single-capability adapter defined here proves insufficient once real usage is evaluated (§25's open alternative).
- **Adapter adoption decision** for `app/transformer/engineer.py` and `app/brain/engineering_brain.py` — whether and when either call site should route through an adapter instead of (or in addition to) calling the native runtime directly, once both adapters exist.
- **Implementation review outcomes** for the items explicitly marked "subject to implementation review" in this ADR: the `PARTIAL` status question (§12), the `EngineDiagnostics` field-mapping recommendations (§16.2), and the `EngineExecutionError` exception-choice question (§14) — each may be settled by a future ADR, an implementation-review note, or left as implementation discretion, but none is settled by this ADR.

---

## Final Adapter Contract Summary

| Element | Capability Adapter | Thinking Adapter |
|---|---|---|
| Native carrier key in `resources` | `"capability_request"` | `"thinking_state"` |
| Native call wrapped | `CapabilityRuntime.invoke(capability_id=, request=)` | `EngineeringThinkingEngine.execute(state)` |
| `EngineResult.payload` source | `CapabilityResult.output` (canonical, minimal — audit goes to diagnostics/metadata, §8, §12, §13) | Existing stage-history/metadata projection |
| Authority flags | Fixed Foundation constants (`shadow_only=True`, `affects_reasoning=False`, `affects_decision=False`) for every `EngineResult`; the adapter validates native conformance (`CapabilityResult.affects_decision is False`) but does not derive Foundation's flags from it | Fixed Foundation constants (same); the adapter validates native conformance (`ThinkingState`'s own `Literal`-locked flags) but does not derive Foundation's flags from it |
| Diagnostics stage-count basis | N/A | Derived from the invoked engine's own configured stage sequence — never a hard-coded constant (§16.2) |
| Status mapping certainty | `SUCCESS`/`FAILED`/`SKIPPED` — directly supported | `SUCCESS`/`FAILED` directly supported; `PARTIAL` subject to implementation review (§12) |
| New instrumentation introduced | None (duration already native) | Wall-clock execution timing (native engine does not measure this) |
| Native contract changed? | No | No |
| Registered in `EngineRegistry`? | Optional, not mandated | Optional, not mandated |

## Mandatory Invariants

1. Adapters are additive wrappers only; no native contract is altered.
2. Foundation's schema (`ExecutionContext`, `EngineMetadata`, `EngineResult`, `EngineDiagnostics`) gains no new fields; native data travels only through `resources` (in) and `payload`/`metadata` (out).
3. `EngineResult.shadow_only=True`, `.affects_reasoning=False`, `.affects_decision=False` are fixed, type-enforced constants for every `EngineResult` emitted through the Foundation boundary — not values derived, propagated, or computed from native flags. An adapter validates that the native result remains within its own native safety contract; a native result that violates that contract MUST NOT be translated into an `EngineResult` and MUST be treated as a validation/safety failure, not silently coerced into a safe-looking result.
4. No sideways dependency between Layer 1 adapters (Capability Adapter and Thinking Adapter do not import each other).
5. No orchestration semantics beyond a single native call per `execute(context)`.
6. The 11 Thinking stage processors are not individually adapted; only the outer `EngineeringThinkingEngine` boundary is.
7. `CapabilityRuntime` is not itself converted into an `Engine`; adaptation occurs at the single-capability invocation boundary (§8), pending resolution of the orchestrator-level question (§26).
8. `EngineResult.payload` for the Capability Adapter is exactly `CapabilityResult.output`; audit/traceability data is carried in diagnostics/metadata, never in payload, unless a later ADR changes this rule.
9. The Thinking Adapter never independently defines Thinking pipeline topology; any stage-count-dependent diagnostic value is derived from the actually-invoked engine instance's own configured stage sequence, never a hard-coded constant.

## Implementation Checklist

*(For a future implementation phase — not performed by this ADR.)*

- [ ] Define `resources` key constants for each adapter.
- [ ] Implement `CapabilityAdapter` (§8) as a new, additive module.
- [ ] Implement `ThinkingAdapter` (§9) as a new, additive module.
- [ ] Implement the input/output/error/diagnostics mapping functions per §11–§16, treating §16.2's formulas as a starting point subject to review, not a fixed spec.
- [ ] Implement the native-safety-contract validation check (§17) and confirm its failure path (§14) before relying on it.
- [ ] Resolve, at implementation time, whether `EngineExecutionError` or another mechanism is used for adapter-level and safety-violation failures (§14, §26).
- [ ] Resolve, at implementation time, whether `PARTIAL` status is adopted for Thinking (§12, §26).
- [ ] Write the test suite per §22.
- [ ] Add the two boundary tests recommended in §23.
- [ ] Verify no existing test's behavior changes.
- [ ] Confirm regression count moves only by addition (new tests), not by modification of existing ones.
- [ ] Circulate for architecture-owner review before treating any part of this checklist as ACCEPTED practice.

## Exact Files Likely to Be Affected by Implementation

Implementation is primarily additive. Most listed files are new; one existing file is expected to receive additive assertions, not a rewrite:

- `backend/app/capabilities/foundation_adapter.py` (new — Capability Adapter)
- `backend/app/thinking/foundation_adapter.py` (new — Thinking Adapter)
- `backend/tests/test_capability_foundation_adapter.py` (new)
- `backend/tests/test_thinking_foundation_adapter.py` (new)
- `backend/tests/foundation/test_architecture_boundaries.py` (existing file — expected to receive additive assertions per §23; its current content is not rewritten)

No existing file under `backend/app/foundation/`, `backend/app/capabilities/`, or `backend/app/thinking/` is expected to require modification. The only expected modification to an existing file is the additive extension of `backend/tests/foundation/test_architecture_boundaries.py` noted above.

## Exact Tests That Should Be Created

- `test_capability_adapter_metadata_valid`
- `test_capability_adapter_success_mapping`
- `test_capability_adapter_failure_mapping`
- `test_capability_adapter_missing_resources_key`
- `test_capability_adapter_engineresult_flags_always_fixed_safe`
- `test_capability_adapter_native_safety_violation_is_treated_as_failure`
- `test_capability_adapter_end_to_end_with_registered_capability`
- `test_thinking_adapter_metadata_valid`
- `test_thinking_adapter_success_mapping`
- `test_thinking_adapter_missing_resources_key`
- `test_thinking_adapter_engineresult_flags_always_fixed_safe`
- `test_thinking_adapter_native_safety_violation_is_treated_as_failure`
- `test_thinking_adapter_stage_history_matches_native_pipeline`
- `test_foundation_adapters_do_not_import_each_other` (boundary test, §23)
- `test_foundation_adapters_import_foundation` (optional boundary test, §23)

## Open Questions That Remain Intentionally Unresolved

1. Whether a second, orchestrator-level Capability Adapter (wrapping `CapabilityOrchestrator` rather than a single capability) is also warranted — named in §25, not decided.
2. Whether either adapter should ever be registered into a shared `EngineRegistry` by default, or only on a per-consumer, opt-in basis (§18) — left to the implementer/consumer, not mandated here.
3. Whether `app/transformer/engineer.py` or `app/brain/engineering_brain.py` should eventually route through their respective adapters instead of calling native runtimes directly — explicitly out of scope (§26).
4. Whether the wall-clock timing the Thinking Adapter must introduce (§16.2) should eventually be replaced by native instrumentation inside `EngineeringThinkingEngine` itself — flagged as a future possibility, not decided.
5. Whether `ThinkingState` should support a `PARTIAL`-equivalent outcome tied to a reduced configured stage set — subject to implementation review (§12), not decided here.
6. Whether the `processed_items`/`skipped_items`/`coverage` formulas in §16.2 should be adopted as written, revised, or replaced entirely once real implementation usage exists — subject to implementation review, not decided here.
7. Whether `EngineExecutionError` is the correct exception type for adapter precondition failures and/or native safety-contract violations, or whether a different existing or new Foundation exception should be used — subject to implementation review against the current Foundation exception contract (§14); not resolved by this ADR, which does not define a new exception type.
8. Whether the implementation-context record in §2 (Confidence Propagation's Foundation adoption, the removal of duplicate confidence shadow flags, `EngineResult`'s flag typing, and the 698 test count) should be captured in a separate, versioned changelog document rather than living solely inside this ADR's Context section, so this ADR's own text does not need to be revised again each time the repository's implementation state moves forward.

---

## 27. Decision Owner

Chief Architect, consistent with ADR-001 and ADR-002. AI-authored analysis, including this document, may recommend but does not carry architectural authority.

---

*This document defines a contract pattern only. It does not implement code, modify the repository, redesign Capability Runtime or Thinking Runtime, or introduce orchestration. Per instruction, work stops here.*