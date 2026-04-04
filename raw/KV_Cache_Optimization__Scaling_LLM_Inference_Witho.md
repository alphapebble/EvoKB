# KV Cache Optimization: Scaling LLM Inference Without Buying More GPUs

**Source:** https://www.alphapebble.io/playbooks/kv-cache-optimization

---

Playbook
Inference
GPU Memory
Performance
KV Cache Optimization: Scaling LLM Inference Without Buying More GPUs
The real bottleneck isn't model size—it's memory management. Learn to scale LLM inference without buying more GPUs.
Published
Dec 30, 2025
•
7 min read
When your LLM starts throwing OOM errors on production traffic, the instinct is to buy more GPUs or truncate context. Both approaches are wrong. The real bottleneck isn't model size—it's the KV cache that grows linearly with every token. Understanding memory hierarchy is what separates junior inference engineers from senior ones.
The Real Bottleneck
Everyone focuses on model weights. A 7B parameter model needs ~14GB in FP16. But here's what catches teams off guard:
GPU Memory = Model Weights + KV Cache
As context grows, the KV cache can consume
10× more memory
than the model itself. A 7B model with 8K context? That's ~4GB just for KV cache storage—on top of your model weights.
graph LR
    A[Model Weights] --> C[GPU Memory]
    B[KV Cache] --> C
    C --> D{Available?}
    D -->|Yes| E[Serve Request]
    D -->|No| F[OOM Error]
"Scaling LLM inference is 80% memory management, 20% compute optimization."
Why KV Cache Matters
The Hidden Cost of Long Context
Context Length
KV Cache Size (7B Model)
Impact
2K tokens
~1 GB
Comfortable
8K tokens
~4 GB
Getting tight
32K tokens
~16 GB
Requires strategy
128K tokens
~64 GB
Needs tiered offloading
[!NOTE]
*Illustrative calculations for a representative 7B parameter model in FP16/BF16.
The Idle Session Problem
Your KV cache sits idle in expensive GPU memory between user interactions. User types a message, pauses for 30 seconds, types again. Meanwhile, their 2GB cache is blocking new requests from being served.
This is wasted GPU resources—and wasted money.
Deep Dive: The Math That Matters
Let's work through a concrete example:
Qwen 2.5 (32B parameters)
on a single
NVIDIA A100 80GB
.
The "It Fits" Fallacy
Component
Calculation
Size
Parameters
32B
—
BF16 storage
32B × 2 bytes
64 GB
GPU memory
A100 SXM
80 GB
Free memory
80 - 64
16 GB
Looks fine, right?
Wrong.
Two Bottlenecks, Two Phases
LLM inference has two distinct phases with different bottlenecks:
Phase
Bottleneck
Characteristic
Metric
Prefill
Compute-bound
Single forward pass over entire prompt
Time-to-First-Token (TTFT)
Decoding
Memory-bound
Token-by-token, loads model weights repeatedly
Tokens/sec
The Roofline Model
For A100 80GB SXM:
BF16 peak compute:
~312 TFLOPS
HBM2e bandwidth:
~2,039 GB/s
To fully utilize compute:
2,039 GB/s ÷ 312 TFLOPS ≈ 153 FLOPs/byte
If your workload performs fewer than ~153 math operations per byte loaded,
the GPU is memory-bound and compute units sit idle
.
Decoding Speed Upper Bound
During token generation, the GPU must load almost the entire model for every token. The L2 cache (~40 MB) is far too small for a ~65 GB model.
Tokens/sec = Memory Bandwidth ÷ Model Size
2,039 GB/s ÷ 65 GB ≈ 31 tokens/sec
This is an upper bound—real systems are slower due to kernel inefficiencies and synchronization.
KV Cache Per Token
For Qwen 2.5 32B with GQA (Grouped Query Attention):
Config
Value
Query Heads
40
KV Heads
8 (40 ÷ 5)
Layers
64
Head Dim
128
KV Cache per token
= 2 (K,V) × 64 layers × 8 heads × 128 dim × 2 bytes =
262 KB/token
KV Cache Scaling
Context Length
KV Cache Size
vs Model Size
2K tokens
~1.34 GB
2% of model
8K tokens
~5.37 GB
8% of model
32K tokens
~21.5 GB
33% of model
131K tokens
~85.9 GB
132% of model
[!CAUTION]
At long context,
KV cache > model size
. Parameter count becomes almost irrelevant.
Concurrency Limits
Resource
Value
Total HBM
80 GB
Usable (~95%)
76 GB
Model Weights
65 GB
Remaining for KV Cache
11 GB
Maximum concurrent sequences:
Context
Concurrent Users
2K
~8 sequences
8K
~2 sequences
32K
Cannot serve on single GPU
The Bottom Line
Although Qwen 2.5 32B "fits" in 80GB by parameter count:
Decoding each token streams ~66–86 GB from HBM
This costs
~46–61 ms
while compute takes
<0.3 ms
KV cache grows from ~1.34 GB (2K) to ~85.9 GB (131K)
Batching collapses as context grows
Inference latency and cost are determined by memory bandwidth, KV cache growth, and context length—not parameter count.
The Diagnostic Framework
Before optimizing, you need to diagnose. Here's what senior ML engineers look for:
Symptom
Diagnosis
Action
High GPU utilization + low throughput
KV cache memory bottleneck
Implement offloading
OOM errors on long contexts
No offloading strategy
Add tiered storage
Idle sessions consuming memory
Wasted GPU resources
Session-based cache eviction
Recomputing same context repeatedly
Missing cache reuse
Enable persistent caching
The Memory Hierarchy
Junior engineers keep everything in GPU memory until OOM. Seniors understand the tiered approach.
graph LR
    A[GPU HBM] --> B[CPU RAM] --> C[SSD] --> D[Network]
Tier
Speed
Cost
Use Case
GPU HBM
Fastest
Highest
Active inference
CPU RAM
Fast
Medium
Session pauses
SSD
Moderate
Low
Persistent cache
Network
Slowest
Lowest
Shared/distributed
The Maturity Ladder:
Level
Strategy
When to Use
Junior
Keep in GPU until OOM
Never in production
Senior
GPU → CPU → SSD based on access patterns
Standard production
Principal
Predictive offloading using usage analytics
High-scale systems
Use-Case Offloading Strategies
Different workloads need different strategies. One size does not fit all.
Use Case
Offload Target
Rationale
Multi-turn conversations
CPU RAM
Fast resume between user messages
Document analysis
Distributed storage
Share cache across requests for same doc
Code assistance
Local SSD
IDE sessions need persistence
Batch inference
Aggressive disk offloading
Throughput over latency
The Key Metric: TTFT with Cache Reuse
|:-------|:-----------------|:-------|
|
Cache Hit
| Load from Storage |
~14x Faster TTFT
* |
|
Cache Miss
| Compute from Scratch | Full Latency |
[!NOTE]
*Based on representative NVIDIA benchmarks for TensorRT-LLM cache reuse.
The equation that matters:
Cache transfer cost < Recomputation cost
Profile access patterns, measure storage latency, and implement predictive offloading based on session behavior.
Production Reality Check
Here's the brutal truth about production inference:
Scenario
Outcome
Perfect model + no cache strategy
OOM crashes
Smart offloading + slow storage
Latency spikes
Great hardware + poor cache management
Wasted money
Tiered storage + access pattern optimization
Production-ready
You need tiered storage, not just bigger GPUs.
Interview Questions That Reveal Experience
When interviewing inference engineers, these questions separate those who've operated at scale:
"Our model handles 4K context fine!"
Follow-ups that reveal depth:
"What's your KV cache size at 32K tokens?"
"How do you handle multi-user sessions?"
"Where do you store inactive caches?"
No offloading strategy = you don't understand production inference.
The Optimal Offloading Decision
graph LR
    A[Cache Request] --> B{Recent?}
    B -->|Yes| C[GPU]
    B -->|No| D{Active?}
    D -->|Yes| E[CPU]
    D -->|No| F{Reusable?}
    F -->|Yes| G[SSD]
    F -->|No| H[Evict]
Wrong approach:
"Move old data to disk."
Right approach:
Calculate thresholds where
Transfer_cost < Recomputation_cost
.
Profile access patterns, measure storage latency, and implement predictive offloading based on session behavior.
Tools & Implementation
Tool
Purpose
Best For
LMCache
Tiered KV cache offloading
Production deployments
vLLM
Paged attention + efficient memory
General inference
TensorRT-LLM
NVIDIA-optimized inference
High-throughput scenarios
FlexGen
Offloading to CPU/disk
Limited GPU memory
[!TIP]
When implementing, start with CPU RAM offloading. It's the easiest win with lowest latency impact.
Production Checklist
Profiled
KV cache memory usage at various context lengths
Implemented
tiered storage (GPU → CPU → SSD)
Defined
offloading thresholds based on access patterns
Monitored
cache hit rates in production
Benchmarked
transfer cost vs recomputation cost
Set up
session-based cache eviction policies
Tested
TTFT with and without cache reuse
Summary
Understanding memory hierarchy > buying bigger GPUs.
The path to production-ready LLM inference:
Diagnose
— Identify if KV cache is your bottleneck
Tier
— Implement GPU → CPU → SSD → Network hierarchy
Measure
— Track TTFT with cache reuse, cache hit rates
Optimize
— Predictive offloading based on access patterns
Monitor
— Continuous profiling in production
Offload smart. Serve more.
Continual Learning: Self-Improving Inference
The most advanced inference systems don't just serve requests—they learn and improve over time. This is
"poor man's continual learning"
: no model weight updates, just smarter context.
The Learning Loop
graph LR
    A[Request] --> B[Retrieve Context]
    B --> C[Generate]
    C --> D{Success?}
    D -->|Yes| E[Capture to KB]
    D -->|No| F[Log Failure]
    E --> B
    F --> B
Why Context Beats Fine-Tuning
Approach
Update Speed
Reversibility
Debuggability
Fine-tuning
Slow (hours)
Hard
Opaque
Continual Learning (KB)
Instant
Easy
Transparent
Key insight
: Agent failures aren't model failures—they're context failures. Every successful query becomes future context. Every mistake becomes a rule.
Dynamic Context Patterns
Instead of static prompts, build systems that retrieve the right context at runtime:
Context Type
When to Retrieve
Example
Session state
Every request
User preferences, conversation history
Domain knowledge
Query-specific
Metric definitions, business rules
Usage patterns
Pattern matching
"This query worked before"
Known gotchas
Entity detection
"Status lives in orders.state, not orders.status"
The Knowledge Base Design
Structure your knowledge base for retrieval:
Schemas & relationships
: Table structures, join keys
Query templates
: Known-good queries for common patterns
Metric definitions
: Business logic encoded as retrievable context
Error corrections
: Past mistakes captured as rules
[!TIP]
The best queries become future context. Every clarification becomes shared knowledge. This is how systems improve without retraining.
Production Implementation
Hybrid retrieval
: Combine semantic search with entity detection
Regression harness
: Test knowledge base before and after updates
Human-in-the-loop
: Let users confirm successful results before capture
Version control
: Track knowledge base changes like code
Common Anti-Patterns
Anti-Pattern
Problem
Solution
GPU-only thinking
Treating GPU memory as infinite until OOM
Implement tiered offloading from day one
Ignoring idle sessions
Inactive caches block new requests
Session-based eviction policies
Context truncation
Losing valuable context to fit memory
Smart offloading preserves full context
One-size-fits-all
Same strategy for all workloads
Use-case specific offloading (chat vs batch)
Ignoring cache reuse
Recomputing same context repeatedly
Persistent caching across requests
Premature optimization
Optimizing before measuring
Profile first, then optimize bottlenecks
Getting Started
Phase
Focus
Deliverable
Measure
Profile current KV cache usage
Memory breakdown by context length
Baseline
Benchmark current TTFT and throughput
Performance metrics before optimization
Tier
Implement GPU → CPU offloading
Basic LMCache or vLLM PagedAttention setup
Tune
Optimize thresholds based on access patterns
Eviction policies matched to workload
Scale
Add SSD/network tiers if needed
Full tiered storage pipeline
References & Further Reading
NVIDIA KV Cache Optimization
— NVIDIA's approach to inference acceleration.
vLLM: PagedAttention
— Memory-efficient attention for high-throughput serving.
LMCache Documentation
— Open-source tiered KV cache management.
FlexGen
— High-throughput generation with limited GPU memory.
Related Playbooks
The Engineering Manifesto
— AlphaPebble's core philosophy for building high-stakes autonomous AI systems.
Context Engineering
— Optimize what goes into context before worrying about cache.
Agentic Engineering
— Build agents that manage their own memory efficiently.
Data Engineering Fundamentals
— The data pipelines that feed your inference systems.
This playbook is maintained by the AlphaPebble team. For implementation support,
get in touch
.
Back to Playbooks
