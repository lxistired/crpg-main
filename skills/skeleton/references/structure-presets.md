# Structure Presets

Four structure modes map the story graph's topology. Pick one based on the brief (default: bifurcating). Each preset constrains beat count, edge pattern, and ending count.

## Preset: linear

Mostly single-path. One or two choice points with short branches (2-3 beats each) before merging back. Player feels a focused, tight narrative with visible-but-contained consequences.

- **Beat count by contentLength**: short=3, medium=8-12, long=20-30
- **Endings**: 1-2
- **Edge pattern**: mostly straight chain, 1-2 small loops via merge nodes
- **When to use**: short stories, tight emotional arcs, tutorials, constrained scope

## Preset: bifurcating

Shared Act 1 (establishing world + central dilemma), then a pivotal choice at Act 1's end splits into TWO parallel storylines (Branch A and Branch B).

**Hard rules for bifurcating:**
- Each branch develops independently for at least 3 beats (short) / 8-12 beats (medium/long) with unique scenes
- The two branches NEVER reconverge — no merge nodes bridging them
- Each branch explores a fundamentally different thematic angle of the controlling idea
- Each branch has its own climax + ending (so: 2 climaxes + 2-4 endings)

- **Beat count by contentLength**: short=3 (shared=1 + A=1 + B=1), medium=15-18, long=50-60
- **Endings**: 2-4
- **Edge pattern**: one shared trunk → one fork → two independent canopies
- **When to use**: "what if" stories, moral dilemmas with incomparable outcomes, default for crpg M1

## Preset: funnel

Branches diverge after each choice/check and develop 3-5 beats each before reconverging at "funnel" merge points. 2-3 meaningful merge nodes. Ends with 2-3 distinct endings.

- **Beat count by contentLength**: short=6-8, medium=15-25, long=40-60
- **Endings**: 2-3
- **Edge pattern**: diamond segments (split → develop → merge → split → develop → merge → ending-fork)
- **When to use**: mystery with multiple suspects, investigation, episodic with recurring cast

## Preset: web

Highly interconnected graph. Branches cross-link. Multiple paths lead to the same beats from different angles. Many merge nodes + cross-connections. 3-8 distinct endings reflecting different value polarities.

- **Beat count by contentLength**: short=not applicable (too dense), medium=25-40, long=50-60 (capped)
- **Endings**: 3-8 (scale with complexity)
- **Edge pattern**: directed graph with many cross-edges, no tree structure
- **When to use**: open-world, exploration-heavy, replayability-focused

## Mapping contentLength → targetWordCount per beat

This is what Script skill respects when writing prose. Skeleton emits `targetWordCount` on every beat.

| detailRichness | per-beat target |
|----------------|----------------:|
| concise | 1500 |
| standard | 2200 |
| detailed | 2500 |
| extreme | 3500 (beat = single action-reaction unit, smaller) |

## Mapping detailRichness → targetShotCount per beat

| detailRichness | shots per beat |
|----------------|---------------:|
| concise | 1-2 |
| standard | 2-3 |
| detailed | 4-6 |
| extreme | 6-10 |

## Climax placement inside each preset

- **linear**: climax = second-to-last beat before the sole ending
- **bifurcating**: each branch gets its own climax at branch-end-minus-1; endings come after
- **funnel**: final converged segment's second-to-last beat
- **web**: every path to a major ending passes through a climax beat (may need multiple climaxes for different endings)

## DAG validity

Every skeleton must be a valid directed acyclic graph with a single start node. Before emitting, verify:

- Exactly one beat with no incoming edges (the start)
- Every `ending` beat has no outgoing edges
- No cycles (topological sort exists)
- Every beat is reachable from the start
- Every non-ending beat has at least one outgoing edge
