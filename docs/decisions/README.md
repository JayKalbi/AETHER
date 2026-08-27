# Architectural Decision Records (ADRs)

This directory maintains an immutable, chronological log of architectural and scientific design decisions for the **AETHER** project.

---

## 1. When to Write an ADR

An ADR must be created whenever a decision:
- Modifies a core architectural component or library interface.
- Freezes or updates a mathematical definition, failure label, or statistical testing protocol.
- Selects, replaces, or deprecates a baseline model or feature group.
- Alters data split boundaries or leakage safeguard rules.

---

## 2. ADR Lifecycle

Each ADR transitions through the following statuses:
* **PROPOSED:** Under team review and evaluation.
* **ACCEPTED:** Approved by the research team and frozen for implementation.
* **DEPRECATED / SUPERSEDED:** Replaced by a subsequent ADR (must link to the superseding ADR).

---

## 3. ADR Index

| ADR # | Title | Date | Status | Summary |
|:---|:---|:---:|:---:|:---|
| [ADR-001](ADR-001-reliability-framework-architecture.md) | Formulation of Hydrologically Informed Reliability & Selective Action | 2026-08-27 | **ACCEPTED** | Freezes EA-LSTM, CQR uncertainty, LightGBM reliability estimator, and Selective Action. |
