# AGENTS.md
## Repository Specifics (Documentation-Driven)
- **Document Source:** Always read feature specs from the `Documentation/` folder before writing code. If docs don't exist, execute "Audit & Document" phase first. Use your native file search/read capabilities to find the relevant `.md` files.
- **Documentation Schema Standard:** Feature docs must contain: Data Model, API Endpoints, UI/Dashboard Elements, Business Rules, Edge Cases.

## Core Modules & Subsystems (NRE v5.0.0+)
- **SlowBurnLorebook (`core/slowburn_lorebook.py`):** Real-time keyword matching and hidden directive context injector (`90% Tension / 10% Action`).
- **Lorebooks Storage (`core/lorebooks/`):** Houses SillyTavern-compatible lorebook JSON files (`Sex_Positions_Kinks_SlowBurn_TH_v10.json`).
- **System Prompts (`core/prompts/`):** Houses base persona system prompts (`slowburn_thai_system.txt`).
- **Control Room Subsystem (`core/control_room/`):** Unified System Control Service managing AgentRegistry, SystemTaskRouter, BackupManager, SecurityAuditor, CronPlanner, and ArchitectureAnalyzer.

