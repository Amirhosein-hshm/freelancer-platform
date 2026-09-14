---
title: "Multi-Agent System Architecture & Dynamic Web Design Intelligence"
version: "2.4.0"
format_standard: "Open Agent Skills (agentskills.io)"
registry_source: "https://skills.sh"
orchestrators_supported: ["LangGraph", "CrewAI", "AutoGen", "Custom Agent Loop"]
---

# Multi-Agent Architecture & Dynamic Web Design Intelligence Protocol

## 1. System Orchestration & Sequential Gatekeeping Schema

```
                     ┌──────────────────────────────────────────────┐
                     │          PHASE 0: DISCOVERY & AUDIT          │
                     │    Gemini: Reads Existing Codebase & Style   │
                     └──────────────────────┬───────────────────────┘
                                            │ Context Dossier
                     ┌──────────────────────┴───────────────────────┐
                     │   PHASE 1: DESIGN RESEARCH & MATURATION      │
                     │  OpenAI: Socratic Interview & Feature Polish │
                     │  Claude & Gemini: Live Web Search (Dribbble, │
                     │   Mobbin, Behance, Pinterest, ui-ux-pro-max) │
                     └──────────────────────┬───────────────────────┘
                                            │ User Selects or Provides Reference Design
                                            ▼
                     ┌──────────────────────────────────────────────┐
                     │          PHASE 2: SYSTEM ARCHITECTURE        │
                     │          OpenAI: Schema, Types, ADRs         │
                     └──────────────────────┬───────────────────────┘
                                            │ Review: Grok checks Security Contract
                                            ▼ [APPROVED]
                     ┌──────────────────────────────────────────────┐
                     │          PHASE 3: UI/UX CRAFT & DEV          │
                     │     Claude: Implements Tailored UI Style     │
                     └──────────────────────┬───────────────────────┘
                                            │ Review: Qwen checks Code Quality & A11y
                                            ▼ [APPROVED]
                     ┌──────────────────────────────────────────────┐
                     │          PHASE 4: SECURITY HARDENING         │
                     │          Grok: Red Team Audit & Patches      │
                     └──────────────────────┬───────────────────────┘
                                            │ Review: OpenAI verifies Architecture Safety
                                            ▼ [APPROVED]
                     ┌──────────────────────────────────────────────┐
                     │          PHASE 5: TDD & DEVOPS               │
                     │       Qwen: Unit/E2E Tests & Dockerfiles     │
                     └──────────────────────┬───────────────────────┘
                                            │ Review: Gemini verifies 100% Tests Pass
                                            ▼ [APPROVED]
                     ┌──────────────────────────────────────────────┐
                     │          PHASE 6: RUNTIME & RUNBOOKS         │
                     │       Gemini: Build Checks & Server Proxy    │
                     │       Kimi: OpenAPI & Documentation          │
                     └──────────────────────────────────────────────┘
```

---

## 2. Dynamic UI/UX Research & Exploration Protocol

### 🛑 Directive 1: Multi-Source Web Design Research (Anti-Template Rule)
* **Never constrain designs to a rigid 6-box preset or default templates.**
* When starting a UI task:
  1. **Live Web Intelligence:** Gemini and Claude search Dribbble, Behance, Mobbin, Pinterest, and Google for real-world trending interfaces tailored to the user's specific domain (e.g., `"fintech crypto trading dribbble"`, `"e-commerce luxury store behance"`).
  2. **Design System Intelligence:** Leverage `ui-ux-pro-max` and `frontend-design` to extract matching color palettes, accessibility tokens, and typography pairings.
  3. **Custom User Ingestion:** Support direct ingestion of user-provided reference links, Figma URLs, or UI screenshots.
  4. **Visual Comparison Showcase:** Present 4 to 6 curated, tailored visual options in a unified comparison frame (or provide direct live links/shots) with numbered choices.

### 🛑 Directive 2: Socratic Design Maturation (`grill-me`)
* Before coding, converse with the user to thoroughly mature the design idea, analyze target user workflows, and resolve all domain edge cases.

### 🛑 Directive 3: Brownfield Codebase Discovery First (Rule 0)
* Inspect existing workspace files, configurations, and packages before creating new setups. Never overwrite existing working infrastructure.

### 🛑 Directive 4: Sequential Gatekeeping & Explicit Approvals
* Every agent output is inspected by its assigned reviewer. The reviewer issues `[APPROVED]` or `[CHANGES_REQUESTED]` with actionable feedback.

### 🛑 Directive 5: Zero Meta-Leaking in Production Code
* Inter-agent dialogues and badges belong strictly to the collaboration interface. Never insert agent badges or commentary into production UI or source code.

---

## 3. Automated Agent Bootstrap (Install Script)

```bash
# Install all required toolkits across agents
npx skills add vercel-labs/skills --skill find-skills -y
npx skills add mattpocock/skills --skill grill-me --skill domain-modeling --skill tdd --skill diagnosing-bugs --skill handoff -y
npx skills add nextlevelbuilder/ui-ux-pro-max-skill --skill ui-ux-pro-max -y
npx skills add anthropics/skills --skill frontend-design --skill doc-coauthoring --skill webapp-testing -y
npx skills add vercel-labs/agent-skills --skill vercel-react-best-practices --skill web-design-guidelines -y
npx skills add BjornMelin/dev-skills --skill docker-architect --skill supabase-ts --skill zod-v4 --skill vitest-dev -y
```

---

## 4. Model-to-Role Skill & Reviewer Matrix

| Agent | Model | Primary Role | Assigned Skills & Tools | Designated Reviewer |
| :--- | :--- | :--- | :--- | :--- |
| **Agent 1** | **OpenAI (o1 / GPT-4o)** | Chief Architect & Socratic Lead | `grill-me`, `domain-modeling`, `zod-v4` | **Grok** (Security & Edge Cases) |
| **Agent 2** | **Claude (3.5 / 3.7)** | Senior UI/UX Craft & Full-Stack | `frontend-design`, `ui-ux-pro-max`, `web-design-guidelines`, Dribbble/Behance extraction | **Qwen** (Code Standards & Typing) |
| **Agent 3** | **Grok (Grok 2 / 3)** | Security Auditor & Red Teamer | `trail-of-bits-security`, `code-review` | **OpenAI** (Architectural Safety) |
| **Agent 4** | **Qwen (2.5 Coder)** | QA, DevOps & Git Automation | `tdd`, `vitest-dev`, `docker-architect` | **Gemini** (Test Execution & Build) |
| **Agent 5** | **Gemini (1.5 / 2.0 Pro)**| Deep Context & Live Web Research | `web_search`, `image_search`, `improve-codebase-architecture` | **OpenAI** (Integration Verification) |
| **Agent 6** | **Kimi (k1.5)** | Technical Writer & Handoff | `doc-coauthoring`, `handoff` | **Claude** (Accuracy with UI/Code) |

---

## 5. Machine-Readable Agent Manifest (JSON)

```json
{
  "orchestrator_version": "2.4.0",
  "pipeline": ["discovery", "web_design_research", "architecture", "ui_ux_dev", "security", "qa_devops", "runtime_docs"],
  "design_exploration_sources": [
    "dribbble.com",
    "behance.net",
    "mobbin.com",
    "pinterest.com",
    "awwwards.com",
    "ui-ux-pro-max-skill"
  ],
  "agents": {
    "architect": {
      "model": "openai/o1",
      "skills": ["mattpocock/skills/grill-me", "mattpocock/skills/domain-modeling", "BjornMelin/dev-skills/zod-v4"],
      "reviewer": "security"
    },
    "developer": {
      "model": "anthropic/claude-3.5-sonnet",
      "skills": ["nextlevelbuilder/ui-ux-pro-max-skill/ui-ux-pro-max", "anthropics/skills/frontend-design", "vercel-labs/agent-skills/vercel-react-best-practices"],
      "reviewer": "qa_devops"
    },
    "security": {
      "model": "xai/grok-2",
      "skills": ["trailofbits/skills/trail-of-bits-security", "mattpocock/skills/code-review"],
      "reviewer": "architect"
    },
    "qa_devops": {
      "model": "qwen/qwen-2.5-coder-32b-instruct",
      "skills": ["mattpocock/skills/tdd", "BjornMelin/dev-skills/docker-architect", "BjornMelin/dev-skills/vitest-dev"],
      "reviewer": "integrator"
    },
    "integrator": {
      "model": "google/gemini-1.5-pro",
      "skills": ["web_search", "image_search", "mattpocock/skills/improve-codebase-architecture"],
      "reviewer": "architect"
    },
    "writer": {
      "model": "moonshot/kimi-k1.5",
      "skills": ["anthropics/skills/doc-coauthoring", "mattpocock/skills/handoff"],
      "reviewer": "developer"
    }
  }
}
```
