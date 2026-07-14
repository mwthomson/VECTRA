# VECTRA — Volunteer Emergency Communications Training & Response Architecture

> Inspired by and forked from the [BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD) by BMad Code, LLC. VECTRA is an independent project and is not officially endorsed or affiliated with BMad Code, LLC.

---

## What This Is

VECTRA is an AI-driven framework engine for large volunteer emergency communications (EMCOMM) groups. It adapts the multi-agent, structured-debate workflow pioneered by the BMAD Method and applies it to Emergency Response Communications planning, stress-testing, and documentation — covering everything from initial mobilization to hospital interfacing to digital mode integration.

This is not a generic AI assistant. Every output is grounded in RF physics, ICS doctrine, FCC regulations, and documented operational practice. Generic AI text is explicitly prohibited by the engine's operating rules.

---

## The Five Personas

| Callsign | Role | Focus |
|---|---|---|
| 📡 **[COML]** | Communications Unit Leader | Mission authority, ICS/NIMS compliance, volunteer safety, resource allocation, FCC Part 97 |
| 🔧 **[Net-Eng]** | Technical Net Engineer | RF design, link budgets, band planning, propagation, power systems, digital modes |
| 🔴 **[Red-Team]** | Disaster Auditor | Protocol destruction testing, SPOF mapping, grid-down simulation, human factors failure analysis |
| 📋 **[SOP-Writer]** | Protocol Documentation Specialist | SOPs, PACE plans, net scripts, go-kit checklists, ICS 205 forms |
| 🟧 **[VoCom]** | Volunteer Communications Coordinator | CERT/ARES integration, volunteer capability matching, credentialing, shift rotation, mutual aid |

---

## The 3-Phase Workflow

For every framework component:

**Phase 1 — Discovery & Agentic Debate**
[COML] and [Net-Eng] pitch the strategy. [Red-Team] immediately attacks with extreme disaster realities. They debate until a resilient compromise is reached. [Red-Team] always gets the last word.

**Phase 2 — Sharding & Refinement**
Break the vetted solution into modular Operational Epics and Tasks. Each task is single-operator, time-bounded, and verifiable (pass/fail).

**Phase 3 — Protocol Export**
[SOP-Writer] formats agreed-upon decisions into field-ready SOPs, PACE plans, net scripts, or ICS 205 forms.

---

## Framework Sections Supported

- Initial Mobilization & Activation
- PACE Plan Development (Primary/Alternate/Contingency/Emergency)
- Tactical Traffic Management
- Net Control Procedures
- Hospital / EOC Interfacing
- Mutual Aid Coordination
- Digital Mode Integration (Winlink, JS8Call, Meshtastic, APRS, AREDN)
- Go-Kit Standards & Verification
- Power System Design (grid-down operations)
- After-Action Review & Lessons Learned

---

## Skills

| Skill | Purpose |
|---|---|
| `emcomm-engine` | Launch the full 3-phase debate engine |
| `emcomm-agent-coml` | Activate [COML] standalone |
| `emcomm-agent-net-eng` | Activate [Net-Eng] standalone |
| `emcomm-agent-red-team` | Activate [Red-Team] standalone |
| `emcomm-agent-sop-writer` | Activate [SOP-Writer] standalone |
| `emcomm-agent-vocom` | Activate [VoCom] standalone |

---

## Outputs

| Type | Location | Format |
|---|---|---|
| SOPs | `sops/SOP-[XXX]-[slug].md` | Numbered, command-verb procedures |
| PACE Plans | `framework/PACE-[slug].md` | Four-tier table with technical parameters |
| Epics/Tasks | `framework/EPIC-[slug].md` | Operational task breakdowns |
| ICS 205 | `framework/ICS205-[slug].md` | Standard incident comms plan format |
| Session notes | `framework/SESSION-[slug]-[date].md` | Debate record |

---

## Upstream

VECTRA tracks [bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) as `upstream`. Pull upstream framework improvements with:

```bash
git fetch upstream
git merge upstream/main
```

The EMCOMM module lives entirely in `src/emcomm-skills/` and does not conflict with the original BMAD modules.

---

## License

MIT — same as upstream BMAD Method.
