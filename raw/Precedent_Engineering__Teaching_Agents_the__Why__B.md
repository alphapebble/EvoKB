# Precedent Engineering: Teaching Agents the 'Why' Behind Decisions

**Source:** https://www.alphapebble.io/playbooks/precedent-engineering

---

Playbook
AI Engineering Systems
Decision Systems
Organizational Learning
Precedent Engineering: Teaching Agents the 'Why' Behind Decisions
How to capture decision traces and human judgment so AI Engineering Systems can learn from organizational precedent and improve over time.
Published
Jan 14, 2026
•
10 min read
[!NOTE]
Precedents = Apprenticeship & Wisdom
Experts don't just follow rules; they recall precedents.
Behavioral
: "I’ve seen this vibration pattern once before in 2012, and here is what we did."
Engineering
:
Precedent Engineering
captures human judgment traces, allowing the agent to "apprentice" under experts and learn organizational wisdom.
Your
AI Engineering System
knows what your company knows (documents) and what it does (processes via Activity Streams). But does it know
why
—the precedents behind those decisions? That's the missing layer, where
AI agents
evolve from mere suggestions to trusted, autonomous action.
[!NOTE]
Engineering Playbook
This playbook focuses on capturing human judgment. For the platform architecture that delivers context across systems, see
Enterprise Context Layer
.
Phase 0: The Dark Context Problem
The Problem
Systems of record capture
what happened
. But they don't capture
why
. The "why" lives in:
The Slack thread where the VP approved an exception
The email chain explaining the one-time discount rationale
The meeting notes where the policy was debated
The human judgment that overrode the algorithm
This is
dark context
—critical to decisions, invisible to systems.
graph LR
    SOR[Systems of Record] -->|captures| What[What Happened]
    Dark[Dark Context] -->|captures| Why[Why It Happened]
    
    What --> Incomplete{Incomplete Picture}
    Why --> Incomplete

    classDef v-large font-size:24px,font-weight:bold;
    class SOR,What,Dark,Why,Incomplete v-large;
Without the "why," agents can only mimic patterns. With it, they can reason about exceptions.
The Solution: Decision Traces
A
decision trace
is an immutable record that captures not just the outcome, but the reasoning:
Component
Description
Example
Decision
The action taken
"Applied 20% discount"
Context Snapshot
State at decision time
Customer health score, ARR, contract terms
Reasoning
Explicit or inferred logic
"VP override due to strategic account"
Outcome
What happened next
"Renewed for 3 years"
[!TIP]
Proof of Engineering
: Organizations that capture decision traces see 40-60% reduction in escalations to senior staff, as agents can retrieve relevant precedents autonomously.
Phase 1: Decision Trace Anatomy
The Problem
Not all decisions are equal. Capturing everything creates noise. Capturing too little misses the judgment that matters.
The Solution: The Exception-First Schema
Focus on
exceptions and overrides
—the moments where humans deviated from the default. These are the highest-signal decisions.
graph LR
    Request[Request] --> Check{Policy?}
    Check -->|Yes| Auto[Auto]
    Check -->|No| Human[Human]
    Human --> Trace[Trace]
    Trace --> Store[(Store)]

    classDef v-large font-size:24px,font-weight:bold;
    class Request,Check,Auto,Human,Trace,Store v-large;
Schema Design
Field
Type
Purpose
decision_id
UUID
Unique identifier
timestamp
ISO8601
When the decision was made
actor
String
Who made the decision (human or agent)
decision_type
Enum
approval
,
override
,
escalation
,
exception
context
JSON
Snapshot of relevant state at decision time
reasoning
Text
Explicit explanation (if provided)
inferred_factors
Array
Extracted signals from context
outcome
JSON
What happened after (tracked asynchronously)
outcome_score
Float
Did this decision work? (0-1)
What to Capture
High Signal (Capture)
Low Signal (Skip)
Policy overrides
Routine approvals within policy
Escalations to senior staff
Standard workflow completions
Exceptions with explanations
Automated decisions
Decisions later reversed
Decisions with no follow-up
Phase 2: The Precedent Graph
The Problem
Individual decision traces are useful. But the real power emerges when they connect—forming a
Precedent Graph
of organizational judgment.
The Solution: Similarity-Based Retrieval
When an agent faces a new decision, it queries the Precedent Graph for similar past situations.
graph LR
    D1[Decision: Discount A] -->|similar_context| D2[Decision: Discount B]
    D2 -->|precedent_for| D3[Decision: Discount C]
    D1 -->|outcome| O1[Renewed]
    D2 -->|outcome| O2[Churned]

    classDef v-large font-size:24px,font-weight:bold;
    class D1,D2,D3,O1,O2 v-large;
Query Patterns
Query Type
Use Case
Example
Similar Context
Find decisions made in comparable situations
"What did we do for enterprise accounts with declining usage?"
Same Entity
Find all decisions for a specific customer/product
"Show me all exceptions we've made for Acme Corp"
Outcome-Filtered
Find decisions that worked (or didn't)
"What discount strategies led to successful renewals?"
Pattern Detection
Find recurring exception types
"We've overridden the 10% cap 47 times—policy gap?"
Embedding Strategy
For similarity retrieval, embed decision traces using:
Context Embedding
— Vector representation of the situation
Reasoning Embedding
— Vector representation of the explanation
Combined Embedding
— Weighted combination for retrieval
[!IMPORTANT]
Don't just embed the decision outcome. Embed the
context
that led to the decision. Similar outcomes don't mean similar situations.
Phase 3: Earning Agent Autonomy
The Problem
Agents today operate in two modes: fully autonomous (dangerous) or always-human-in-the-loop (slow). Neither scales.
The Solution: Precedent-Based Autonomy
Agents earn autonomy by demonstrating they can match human judgment on precedented cases.
graph LR
    New[New Decision] --> Search[Search Precedent Graph]
    Search --> Found{Precedent Found?}
    Found -->|Yes, Strong Match| Auto[Agent Decides]
    Found -->|Weak Match| Suggest[Agent Suggests]
    Found -->|No Match| Escalate[Human Decides]
    
    Escalate --> Trace[Capture Trace]
    Trace --> Graph[(Precedent Graph)]

    classDef v-large font-size:24px,font-weight:bold;
    class New,Search,Found,Auto,Suggest,Escalate,Trace,Graph v-large;
The Autonomy Ladder
Level
Condition
Agent Behavior
0: Suggest
No precedent exists
Escalate to human, capture trace
1: Recommend
Weak precedent match
Suggest action, require confirmation
2: Act + Notify
Strong precedent match
Take action, notify human
3: Act Silently
Very strong match + good outcomes
Fully autonomous
Confidence Scoring
Autonomy Score = (Precedent Similarity × Outcome Success Rate × Recency Weight)
Factor
Weight
Rationale
Precedent Similarity
0.4
How close is this situation to past decisions?
Outcome Success
0.4
Did similar decisions lead to good outcomes?
Recency
0.2
Are the precedents recent (policies may have changed)?
Production Checklist
Exception Capture
: Are you logging human overrides and escalations?
Context Snapshots
: Do traces include the state at decision time?
Reasoning Extraction
: Can you extract or infer the "why"?
Outcome Tracking
: Are you measuring whether decisions worked?
Similarity Retrieval
: Can agents query "what did we do last time?"
Autonomy Levels
: Do agents have graduated authority based on precedent?
The Bottom Line
[!IMPORTANT]
Precedent is the bridge from suggestion to action.
Agents that can point to "here's what we did last time, and it worked" earn trust. Agents that can't remain perpetual assistants.
References & Further Reading
Event Sourcing (Wikipedia)
— The immutability pattern behind decision traces.
Case-Based Reasoning
— The AI paradigm that inspired precedent retrieval.
Anthropic: Constitutional AI
— Training agents on human judgment patterns.
Related Playbooks
The Engineering Manifesto
— AlphaPebble's core philosophy for building high-stakes autonomous AI systems.
Context Engineering
— The prompt-level foundations for delivering context.
Knowledge Graph Engineering
— Entity and relationship extraction for precedent graphs.
Activity-Stream Engineering
— Capturing the "How" of processes—this playbook adds the "Why."
Enterprise Context Layer
— The platform architecture for cross-system context delivery.
This playbook is maintained by the AlphaPebble team. For implementation support,
get in touch
.
Back to Playbooks
