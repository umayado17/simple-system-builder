# simple-system-builder

A ChatGPT skill for building complete systems from the web UI alone — Chat as the command center, GitHub as the source of truth.

English | [日本語](READMEjp.md)

**Article:** [Building Systems Entirely from ChatGPT with GitHub](https://note.com/norito_hiraoka/n/n50d293161d97?hl=en)

## What this is

A skill for going from requirements to design, implementation, testing, CI, and deployment without opening an IDE or a terminal — without ever leaving the ChatGPT chat screen.

However, this skill is not a code-generation macro. It is a **code of conduct for an AI developer**: it defines how to think about building a system, how far to proceed autonomously, and where to hand judgment back to a human.

At its core are three principles:

1. **Minimum sufficiency.** Choose the simplest mechanism that satisfies the purpose. If one database is enough, don't add another. If microservices aren't needed, a monolith is fine. Simplicity itself is not the goal — the system must be simple *and* fully satisfy its purpose.
2. **Isolate complexity.** Some parts of real-world work — site-specific paperwork formats, computer use — are unavoidably complex. Rather than eliminating that complexity, confine it. Keep it behind an adapter, and never let it into the core business logic.
3. **Don't build the future; just leave room to change.** Never build features in advance. Instead, place cheap seams where change is likely: configuration values, environment variables, templates, adapters, migrations.

What this skill protects above all is not development speed, but this: **even when AI does the building, the system must not become complex.**

## Why this works now

This skill functions because the following technologies have come together.

### The mind

- LLMs' language understanding and design capability have improved — and so have their implementation and verification capabilities.
- The ability to control implementation — through harnesses, contracts, and the like — has improved as well.

### The circuit

- Via MCP, ChatGPT can now interact with GitHub.

### The foundation

- GitHub can hold both documents and systems, and GitHub Actions enables automated execution.
- These properties of GitHub are not new. But the moment an LLM became the primary reader and writer, GitHub took on a different meaning: **the AI's external memory and execution apparatus.**

### The exit

- Systems can now be deployed to either local or cloud environments, as needed.
- The LLM can guide environment setup — and carry out the actual configuration work.

Remove any one of these, and the whole thing stops working.

## Division of roles

```text
Chat   = where instructions and judgments happen
GitHub = where development artifacts and state are recorded (the source of truth)
```

Requirements, architecture, data models, UX, code, prompts, tests, GitHub Actions, deployment settings, and key design decisions all go into GitHub. Chat holds no state. No matter how long a conversation runs, or how many threads it spans, the current state of development can always be restored from the repository.

## Repository layout

```text
simple-system-builder/
├── SKILL.md                 # The skill itself (code of conduct and process)
├── references/              # Operating rules
│   ├── principles.md            # Design principles
│   ├── complexity-boundaries.md # Isolating complexity
│   ├── prototype-enterprise.md  # Prototypes and seams for future change
│   ├── repository-contract.md   # Repository structure conventions
│   ├── tooling.md               # Handling GitHub, cloud, and execution tools
│   └── workflow.md              # Process
├── agents/                  # Agent configuration
├── scripts/                 # Scaffold / state-update / validation scripts
└── assets/project-template/ # Template for generated projects
```

## Installation

1. Zip this repository and register it with ChatGPT as a skill.
2. Connect the GitHub connector (or a GitHub MCP) on the ChatGPT side.

## First-time setup

For the repository under development, two things are done **manually**:

- Creating the repository
- Granting the ChatGPT connector write access to that repository

This is not a workaround for missing functionality. The skill itself stipulates that judgments involving permissions are handed back to humans, so granting permissions is deliberately not automated (see "初回セットアップ" in `references/tooling.md`). A human unlocks the door once — and from then on, development proceeds without leaving the chat screen.

## Usage

The skill is not activated from the start.

1. Requirements gathering, requirements definition, and technical feasibility are worked out together by human and AI in an ordinary chat.
2. When you reach "I can roughly see what we're building — let's turn this into a real system," activate the skill. This is the boundary between exploration and construction.
3. After activation, the development state moves to GitHub, and work proceeds autonomously as a rule.

```text
Ordinary chat
  Requirements → Definition → Technical study → "Let's build this"
━━━━━━━━━━━━━━━━━━
      Skill activated
━━━━━━━━━━━━━━━━━━
  Move development state to GitHub
     ↓
  Data ⇄ UX
     ↓
  Infrastructure ⇄ Permission
     ↓
  Minimum-sufficient architecture fixed
     ↓
  Design → Implementation → Tests → GitHub Actions → Deploy
     ↓
  Continue autonomously as a rule
```

### What gets handed back to humans

The basic policy: **methods are left to the skill; only matters of purpose are decided by humans.** Judgment returns to the human when the requirements themselves change, when the meaning of UX or data is being decided, when permissions or security are involved, when significant costs would be incurred, or when a change would be hard to reverse.

In addition, two areas — **Data ⇄ UX** and **Infrastructure ⇄ Permission** — cannot be decided in one direction, so the skill does not settle them alone; it iterates back and forth with the user.

## Author

Norito Hiraoka, Director, SEIFU AI Institute ([umayado17](https://github.com/umayado17))

## License

MIT License (see [LICENSE](LICENSE))
