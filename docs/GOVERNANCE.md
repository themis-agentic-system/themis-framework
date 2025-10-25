# Governance and Safety Playbook

The new task-graph runtime introduces additional integrations and requires
clear guardrails for production deployments. This playbook captures
operational expectations for legal-specialist agents.

## Trust Boundaries

- **Connectors** must be registered through `ConnectorRegistry` objects with an
  explicit capability inventory. Document who owns each connector, the data it
  exposes, and any jurisdictional restrictions.
- **Tool capabilities** require schema definitions (`ToolSpec`) so inputs are
  validated before reaching downstream APIs.
- **Tracing data** emitted from the orchestrator is personally identifiable and
  should be retained according to firm policies. Forward traces to secured
  observability platforms with role-based access control.

## Change Management

1. Capture graph updates via code review. `TaskGraph` mutations should link to
   evaluation harness runs that demonstrate no regression in exit-signal
   coverage.
2. Update pack templates when adding or deprecating connectors so downstream
   practice teams inherit the latest guardrails.
3. Maintain scenario coverage inside `qa/evaluation_harness.py` and publish
   regression dashboards for leadership review.

## Incident Response

- **Detection:** Monitor `themis.orchestrator` logs and trace streams for
  `agent_run_error` or `phase_complete` events with `status="failed"`.
- **Containment:** Pause the impacted connector via the registry and replay the
  transcript with the evaluation harness to determine if the fault is
  deterministic.
- **Remediation:** Issue a corrective plan, update tooling schemas or
  connectors, and document lessons learned in this playbook.

For questions, contact the safety steward listed in the internal runbook.
