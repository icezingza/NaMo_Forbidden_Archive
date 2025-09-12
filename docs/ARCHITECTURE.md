# Architecture Overview

## System Goals
- Clarity: separate pure logic from IO
- Testability: deterministic units with thin adapters
- Reproducibility: pinned deps + CI checks

## Layers (suggested)
- **core/**: pure business logic, stateless
- **adapters/**: filesystems, APIs, audio/visual IO
- **pipelines/**: orchestration; compose core + adapters
- **app.py**: entrypoint (REST/CLI)

## Data Flow
Input → adapters → core → adapters → output

## Diagrams
- Add a simple block diagram (Mermaid or image) describing major flows.

## Decisions
- Record noteworthy choices here (ADR-lite).
