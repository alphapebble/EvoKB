# LLM Coding Workflow: From Text to Software

**Source:** https://www.alphapebble.io/playbooks/llm-coding-workflow

---

Playbook
AI Coding
Engineering Workflow
Best Practices
LLM Coding Workflow: From Text to Software
A disciplined, AI Engineering workflow for building high-quality software with AI—without losing control of the codebase.
Published
Dec 27, 2025
•
12 min read
Coding with LLMs is not about magic; it's about
orchestration
. The difference between a frustrated developer debugging hallucinations and a 10x engineer is a structured workflow that treats AI as a powerful, but raw, engine requiring precise guidance.
This playbook outlines a battle-tested workflow for effective AI-assisted engineering.
The Workflow Architecture
[!TIP]
The Unix Philosophy Connection
This workflow embodies
The Rule of Generation
(
"Avoid hand-hacking; write programs to write programs when you can"
) and
The Rule of Least Surprise
(
"In interface design, always do the least surprising thing"
).
At a high level, the workflow moves from abstract design to concrete execution in tight, verifiable loops.
graph LR
    A[1. Architect] --> B[2. Context]
    B --> C(3. Execute)

    subgraph Loop [Iterative Cycle]
        direction TB
        C[Code Gen] --> D{Verify}
        D -->|Fail| C
        D -->|Pass| E[Review]
        E -->|Reject| C
    end

    E -->|Approved| F[4. Merge]
Phase 1: Architect First (Specs Before Code)
The "15-Minute Waterfall"
Resist the urge to open the chat window and type "Build me a login page." LLMs thrive on constraints and wither in ambiguity.
Brainstorming
: Use a capable chat model to flesh out requirements. Ask it to quiz
you
about edge cases.
The Spec File
: Crystallize everything into a
spec.md
or
plan.md
. This is your source of truth.
Goals
: What are we building?
Invariants
: What must never change?
Data Models
: Schemas and types.
Testing Strategy
: How will we know it works?
"Writing a spec aligns the human and the AI. It prevents the 'jumbled mess' problem where the model forgets what it's building halfway through."
Phase 2: Context Engineering
An LLM with no context is a junior dev on their first day. An LLM with full context is a senior engineer who knows the system inside out.
The Context Pyramid
graph BT
    A["Global Rules (Rules File)"] --> B[Project Docs]
    B --> C[Active File Content]
    C --> D[Target Task Spec]
Global Rules
: Use project-level rule files (e.g.,
.cursorrules
,
instructions.md
) to enforce style.
"Use functional components."
"No
any
types."
"Prefer Tailwind CSS."
Ingestion Tools
: Use tools like
gitingest
or custom scripts to dump relevant module interfaces into the prompt.
Documentation as Executable Use Cases
:
Don't just paste API references.
LLMs struggle to infer workflow from signatures alone.
Do paste "Golden Paths".
Treat your documentation as a set of executable use cases.
The Recipe Rule
: If you want the AI to use a library, provide a "HELLO
WORLD.md" or "COOKBOOK.md" that shows a full, working example of the _integration path
, not just the class definitions. Models need to see
how
components stream together, not just what they are.
Phase 3: The Iterative Execution Loop
Break it down.
Never ask for the whole feature at once. Iterate in small, verifiable steps.
Prompt
: "Implement Step 1 from
plan.md
."
Code
: AI generates code.
Verify
: Run the test/build.
Refine
: If it fails, feed the error
exactly
back to the AI.
User
: "Lint error on line 42: Variable undefined."
AI
: "Fixing..."
Tip
: "Model Musical Chairs". If one model gets stuck, swap to another. Different models from different providers have unique "personalities" and reasoning paths.
Evaluation Harnesses for Bigger Features
For non-trivial features, create a mini
eval set
before letting the AI loose. This acts as a contract between you and the AI—a set of ground truths that must pass after every generation.
flowchart LR
    A[Define Eval Set] --> B[AI Generates Code]
    B --> C{Run Eval Harness}
    C -->|All Pass| D[Accept Generation]
    C -->|Any Fail| E[Reject & Retry]
    E --> B
The Eval Set Approach
:
Define 3–8 input/output examples
that capture the core behavior, edge cases, and boundary conditions. Think: happy path, empty inputs, error states, and limits.
Automate verification
: Create a simple test harness that runs all examples after each AI generation. This takes minutes to set up but saves hours of debugging.
Fail fast
: If any example in the eval set breaks, reject the generation immediately—don't let regressions compound across iterations.
[!TIP]
This approach catches the most common AI failure mode: generating code that works for the "happy path" but silently breaks edge cases. The eval set is your safety net.
Phase 4: Automated Quality Gates
Trust, but verify excessively.
Automated tools are the guardrails that keep the AI on the road.
Linters/Formatters
: Enforce style automatically.
Type Checkers
: Catch hallucinations early.
Test Suites
: The ultimate truth.
The Virtuous Cycle
:
The AI writes code -> CI tools catch errors -> AI fixes errors based on CI output.
Regression Protection (Critical)
[!WARNING]
When AI rewrites or refactors code, it often silently breaks existing tests and features. This is one of the most insidious failure modes of LLM-assisted development.
flowchart LR
    A[Baseline Tests] --> B[AI Refactors] --> C{Tests Changed?}
    C -->|Yes| D[Review Diffs]
    C -->|No| E[Proceed]
    D -->|Intentional| E
    D -->|Suspicious| F[Roll Back]
The Regression Shield Protocol
:
Before Major Changes
: Run the full test suite and capture a baseline. This is your "before" snapshot.
After Every AI-Assisted Refactor
:
Run the
complete
test suite, not just the affected module. AI changes often have unexpected ripple effects.
Review the diff of any changed test files. Ask yourself: "Did I intend to change this behavior, or did the AI 'fix' the test to match broken code?"
Compare coverage reports. A drop in coverage is a red flag.
The Red Flag
: If a refactor results in
fewer
test assertions or
deleted
test cases, treat this as a critical incident. Roll back and investigate before proceeding.
Snapshot Comparisons
: For UI work, use visual regression tools (e.g., Chromatic, Percy) to catch unintended visual changes that unit tests miss.
Phase 5: Human in the Loop
You are not the typist; you are the
Lead Engineer
and
Code Reviewer
.
Review Logic
: Does this actually solve the problem?
Review Security
: Did it introduce a vulnerability?
Review Maintainability
: Is this code understandable?
Rule of Thumb
: Never commit code you cannot explain.
Security & Supply-Chain Risks
[!CAUTION]
LLMs can suggest deprecated or vulnerable dependencies, or copy patterns from training data that contain subtle security flaws. This is a growing concern as AI-generated code becomes more prevalent.
Watch for these red flags
:
Outdated packages
: The model may suggest libraries that were popular in its training data but have since been deprecated or marked vulnerable.
Copied vulnerability patterns
: Subtle security anti-patterns (e.g., SQL injection, improper input sanitization) can be embedded in training data and reproduced.
Phantom dependencies
: The AI may hallucinate package names that don't exist—or worse, that have been typosquatted by malicious actors.
Mitigation
: Always run dependency audits (e.g.,
npm audit
,
pip-audit
, Snyk) after AI-generated changes. Treat the AI's dependency suggestions as "untrusted input."
Phase 6: When to Go Agentic
This playbook describes a
classic human-in-the-loop workflow
—ideal for teams building trust with AI-assisted development. But as your team matures, you can progressively hand over more autonomy.
graph LR
    A[Manual Loop] -->|">70% success"| B[Semi-Autonomous]
    B -->|">85% success"| C[Agentic]
    C -->|">95% + guardrails"| D[Fully Autonomous]
The Maturity Ladder
:
Stage
Success Rate
Characteristics
Tools
Manual Loop
Building trust
Human reviews every generation
Any chat model
Semi-Autonomous
>70%
AI handles routine tasks, human reviews
Cursor, GitHub Copilot
Agentic Assistants
>85%
AI executes multi-step tasks with checkpoints
Claude Code, Aider, Windsurf
Fully Autonomous
>95% + guardrails
AI handles end-to-end features with rollback
Devin, custom agents
[!IMPORTANT]
Graduation Criteria
: Only move to more autonomous setups when your team consistently achieves >85% success rate on the classic loop. Premature autonomy leads to compounding errors and lost trust.
Phase 7: Refactoring to Patterns
AI-generated code often works but accumulates technical debt. It tends to produce "good enough" solutions that ignore established architectural patterns. Before merging, refactor toward recognized patterns.
Why Patterns Matter for AI Code
Problem
AI Tendency
Pattern Solution
Hardcoded dependencies
Inline instantiation everywhere
Factory
,
Dependency Injection
God classes
Single class doing too much
Strategy
,
Command
,
Facade
Duplicated conditionals
Copy-paste switch statements
State
,
Template Method
Tight coupling
Direct calls between modules
Observer
,
Mediator
,
Adapter
Integration spaghetti
Point-to-point API calls
Message Broker
,
Pipes and Filters
GoF Patterns to Watch For
graph LR
    A[AI Output] --> B{Code Smell?}
    B -->|Duplication| C[Template Method]
    B -->|Conditionals| D[Strategy/State]
    B -->|Dependencies| E[Factory/DI]
    B -->|Coupling| F[Observer/Mediator]
Common Refactoring Opportunities
:
Factory Pattern
: When AI creates objects with
new
scattered everywhere, extract to factories.
Strategy Pattern
: When AI uses long if-else chains for behavior variants, extract to strategies.
Observer Pattern
: When AI passes callbacks through many layers, consider event-based decoupling.
Adapter Pattern
: When AI wraps third-party APIs inconsistently, standardize with adapters.
Enterprise Integration Patterns
For system integration work, AI often produces brittle point-to-point connections. Refactor toward:
Pattern
Use When
AI Anti-Pattern
Message Channel
Async communication needed
Direct HTTP calls everywhere
Content-Based Router
Multiple destinations by type
Hardcoded routing logic
Pipes and Filters
Data transformation chains
Monolithic processing functions
Saga/Choreography
Distributed transactions
Nested try-catch blocks
Circuit Breaker
External service resilience
No failure handling
The Refactoring Checklist
Before merging AI-generated code, ask:
Does this follow
SOLID
principles?
Are there opportunities to apply
GoF patterns
?
For integrations, does it follow
EIP patterns
?
Is the code
testable
in isolation?
Would a senior engineer recognize this as idiomatic?
[!TIP]
Use the AI itself to refactor. Prompt: "Refactor this code to use the Strategy pattern for the payment processing logic." The AI is often better at applying patterns when explicitly asked.
Summary Checklist
Plan
: Do I have a written spec?
Context
: Does the AI have the relevant files and rules?
Chunking
: Is the current task small enough?
Automation
: Are linters and tests running?
Regression Check
: Did I run the full test suite and review any modified tests?
Security Audit
: Did I check for vulnerable or deprecated dependencies?
Pattern Review
: Does the code follow GoF/EIP patterns where applicable?
Review
: Have I read and understood the output?
The Bottom Line
LLM-assisted coding is a force multiplier—but only with discipline. The teams that succeed treat AI as a powerful junior engineer that needs supervision, not a magic wand.
The workflow:
Plan → Context → Execute → Verify → Review → Refactor
.
Master this loop, and you'll ship faster with fewer bugs than teams that skip the structure.
References & Further Reading
Anthropic: Building with Claude
— Best practices for AI-assisted development.
GitHub Copilot Research
— Productivity impact studies on AI coding assistants.
Gang of Four Design Patterns
— Classic design patterns reference.
Enterprise Integration Patterns
— Integration architecture patterns.
Related Playbooks
The Engineering Manifesto
— AlphaPebble's core philosophy for building high-stakes autonomous AI systems.
Context Engineering
— Deep dive into RAG, memory architectures, and maximizing context windows.
Agentic Engineering
— The broader system architecture for building autonomous agents.
Data Engineering Fundamentals
— Building the data pipelines that power your AI models.
Precedent Engineering (Coming Soon)
— Applying the discipline of coding to the capture of human judgment.
This playbook is maintained by the AlphaPebble team. For implementation support,
get in touch
.
Back to Playbooks
