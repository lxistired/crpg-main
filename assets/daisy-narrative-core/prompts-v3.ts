// ---------------------------------------------------------------------------
// McKee-flavoured prompt templates for CRPG story generation
// ---------------------------------------------------------------------------

interface SkeletonParams {
  keywords: string
  preset?: string             // linear | bifurcating | funnel | web
  complexity: number          // 1-5, controls act count & branch density
  worldSetting?: string
  characters?: Array<{ name: string; description?: string }>
  locale?: string
  poeticMode?: boolean
  detailRichness?: 'concise' | 'standard' | 'detailed' | 'extreme'
  contentLength?: 'short' | 'medium' | 'long'
}

interface Message {
  role: string
  content: string
}

interface PromptPayload {
  model: string
  messages: Message[]
  temperature: number
  maxTokens?: number
}

const MODEL = 'anthropic/claude-sonnet-4-6'

// ---- language instruction ---------------------------------------------------

function langInstruction(locale?: string): string {
  if (locale === 'zh') {
    return `\n\n### LANGUAGE\nAll narrative content (titles, content, choices, edge labels, controllingIdea, valueBefore, valueAfter) MUST be written in **Chinese (中文)**. Only structural fields (id, type, sourceHandle) remain in English.`
  }
  return ''
}

// ---- shared system preamble ------------------------------------------------

const MCKEE_BASE = `You are a CRPG narrative architect deeply versed in Robert McKee's *Story* principles.

### HARD CONSTRAINTS (every scene you generate MUST satisfy ALL six):
1. **Value Shift** — Every scene must turn at least one value (e.g. hope→despair, trust→betrayal). State the before/after explicitly.
2. **Progressive Complication** — Each successive beat raises stakes or narrows options. Never plateau.
3. **Dilemma** — Choice nodes MUST present an irreconcilable dilemma where every option costs something meaningful. No "obviously right" choices.
4. **The Gap** — Between a character's action and the world's reaction there must be a gap — the result is always different (better or worse) than expected.
5. **Controlling Idea** — The whole story expresses ONE controlling idea (theme sentence: value + cause). Keep it consistent across all acts.
6. **Three Levels of Conflict** — Weave inner conflict (psychology), personal conflict (relationships), and extra-personal conflict (society/environment) throughout.

### PLAYER NAME PLACEHOLDER
Use \`{{playerName}}\` as the protagonist's name throughout ALL narrative text (content, choices, successText, failText, epilogue, etc.). Do NOT invent a fixed name for the protagonist. The system will replace the placeholder with the player's actual name at runtime. NPCs should have their own fixed names — only the PLAYER CHARACTER uses the placeholder. Example: "{{playerName}}推开沉重的石门，火把的光芒在甬道尽头摇曳。"


### BRANCHING PHILOSOPHY
- **Delayed Convergence** — After a player makes a choice, do NOT merge branches back immediately. Let each branch develop for at least 3-5 nodes with unique narrative content before any convergence. The player must FEEL the weight of their choice through meaningfully different scenes, encounters, and consequences.
- **Distinct Branch Identity** — Each branch after a choice should explore a different thematic facet, introduce different NPCs or revelations, and shift values in different directions. Branches should not be cosmetic variations of the same plot.

### NODE TYPES
- narrative  — Prose scene or description
- choice     — Player decision point (2-4 options)
- check      — Skill / attribute check gate (pass/fail branches)
- merge      — Converge branches back together
- act_break  — Act boundary marker (inciting incident / midpoint / climax etc.)
- ending     — Terminal node

### OUTPUT FORMAT
Return **strictly valid JSON** (no markdown fences, no commentary) with this shape:
\`\`\`
{
  "controllingIdea": "<one sentence theme>",
  "nodes": [
    {
      "id": "<unique string>",
      "type": "<node type>",
      "data": {
        "title": "<short title>",
        "content": "<narrative text or choice prompt>",
        "choices": ["<option A>", "<option B>", ...],   // only for choice nodes
        "check": { "attribute": "...", "dc": <number> }, // only for check nodes
        "valueBefore": "<value state before>",
        "valueAfter": "<value state after>"
      },
      "actIndex": <0-based act number>,
      "sequenceIndex": <order within act>
    }
  ],
  "edges": [
    {
      "id": "<unique string>",
      "source": "<source node id>",
      "target": "<target node id>",
      "sourceHandle": "<handle name or null>",
      "label": "<optional edge label>"
    }
  ]
}
\`\`\``

const KEYWORD_POETIC = ` You are also a poet — you find hidden connections, sensory echoes, and emotional undercurrents in any set of keywords.

### KEYWORD INTERPRETATION
When given keywords or a theme, do NOT treat them as literal plot requirements. Instead, let them evoke atmosphere, mood, metaphor, and sensory imagery. A keyword like "glass" might become a fragile relationship, a mirror of the self, or a barrier between worlds. A keyword like "rain" might become grief, renewal, or a liminal space. Weave the keywords into the story as poetic threads — sometimes explicit, sometimes as subtext.`

const KEYWORD_LITERAL = `

### KEYWORD INTERPRETATION
When given keywords or a theme, treat them as concrete plot elements and story building blocks. Each keyword should appear directly in the narrative — as a character, location, object, event, or central conflict. "Glass" means there should be glass in the story. "Rain" means rain plays a visible role. Be direct and grounded in your use of keywords.`

// ---- detail & length configuration -----------------------------------------

const DETAIL_CONFIG: Record<string, { wordLimit: number; nodeFactor: number; style: string; beats?: boolean }> = {
  concise: {
    wordLimit: 60,
    nodeFactor: 1.0,
    style: 'Tight prose. Action and value shifts only. No dialogue. Max 2-3 sentences per node.',
  },
  standard: {
    wordLimit: 100,
    nodeFactor: 0.8,
    style: 'Balanced prose. Brief dialogue (1-2 lines), key sensory details. Max 4-5 sentences per node.',
  },
  detailed: {
    wordLimit: 150,
    nodeFactor: 0.55,
    style: 'Rich prose with dialogue (2-3 exchanges), sensory detail, and internal reflection. Max 6-8 sentences per node. Do NOT exceed the word limit.',
  },
  extreme: {
    wordLimit: 200,
    nodeFactor: 0.4,
    beats: true,
    style: `Ultra-cinematic prose. Each narrative node MUST include a "beats" array — a sequence of 3-6 dramatic micro-moments (McKee beats). Each beat is a self-contained action-reaction unit that shifts the scene's value polarity.

BEAT FORMAT: Each narrative node's "data" object must include:
  "beats": [
    { "text": "<40-60 words of immersive prose for this beat>", "valueShift": "+" or "-" },
    ...
  ]

BEAT RULES:
- Each beat must create a micro turning point — the value state MUST alternate (+ → - → + or vice versa).
- Beat 1: Establish the scene's emotional baseline.
- Middle beats: Progressive complication — each beat raises stakes or subverts expectations.
- Final beat: The scene's climactic micro-moment that determines the overall value shift.
- Include sensory detail, internal thought, dialogue, and environmental cues across beats.
- The "content" field still contains the FULL text (all beats concatenated), so the story works even without beat-by-beat rendering.
- 3-4 beats for standard narrative nodes, 5-6 beats for act_break or crisis scenes.`,
  },
}

const LENGTH_MULTIPLIER: Record<string, number> = {
  short: 0.6,
  medium: 1.0,
  long: 1.5,
}

const MAX_NODE_CAP = 50

// Compose system prompt from parts
function buildSystemPrompt(poeticMode: boolean, locale?: string): string {
  const base = MCKEE_BASE
  const keywordSection = poeticMode ? KEYWORD_POETIC : KEYWORD_LITERAL
  // Insert poet intro right after the first sentence
  return base.replace(
    "You are a CRPG narrative architect deeply versed in Robert McKee's *Story* principles.",
    "You are a CRPG narrative architect deeply versed in Robert McKee's *Story* principles." + keywordSection,
  ) + langInstruction(locale)
}

// Full system prompt for content/continue (always includes poetic mode)
const MCKEE_SYSTEM_FULL = MCKEE_BASE.replace(
  "You are a CRPG narrative architect deeply versed in Robert McKee's *Story* principles.",
  "You are a CRPG narrative architect deeply versed in Robert McKee's *Story* principles." + KEYWORD_POETIC,
)

// ---- buildSkeletonPrompt ---------------------------------------------------

export function buildSkeletonPrompt(params: SkeletonParams): PromptPayload {
  const { keywords, preset, complexity, worldSetting, characters, locale } = params
  const poeticMode = params.poeticMode ?? true
  const detailRichness = params.detailRichness ?? 'standard'
  const contentLength = params.contentLength ?? 'medium'

  const temperature = poeticMode ? 0.9 : 0.7
  const detail = DETAIL_CONFIG[detailRichness] ?? DETAIL_CONFIG.standard
  const lengthMul = LENGTH_MULTIPLIER[contentLength] ?? 1.0

  const actCount = Math.min(Math.max(complexity, 1), 5)

  // Preset-specific structure instructions and node targets
  const presetInstructions: Record<string, { structure: string; nodeTarget: number; endingTarget: number }> = {
    linear: {
      structure: `**Structure: LINEAR** — A mostly single-path story. One or two choice points with short branches (2-3 nodes each) before reconverging. The player experiences a focused, tight narrative, but choices still have visible consequences before merging.`,
      nodeTarget: 8 + complexity * 4,
      endingTarget: 2,
    },
    bifurcating: {
      structure: `**Structure: BIFURCATING** — The story shares a common Act 1 (establishing world, characters, and the central dilemma), then a pivotal choice at the end of Act 1 splits into TWO distinct parallel main storylines (Branch A and Branch B). CRITICAL RULES for bifurcation:
- Each branch must develop independently for at least 8-12 nodes with unique scenes, NPCs, and revelations.
- The two branches must NEVER reconverge — no merge nodes connecting them.
- Each branch explores a fundamentally different thematic angle of the controlling idea.
- Each branch has its own internal choices, checks, and escalation.
- Each branch must lead to at least 2 distinct endings (4+ endings total).
- The fork creates a "tree" shape: shared trunk → two independent canopies.`,
      nodeTarget: 15 + complexity * 8,
      endingTarget: 4,
    },
    funnel: {
      structure: `**Structure: FUNNEL** — Branches diverge after each choice/check and develop for at least 3-5 nodes each before reconverging at "funnel" merge points. Each branch must have distinct scenes and consequences — NOT just flavor text variations. Use 2-3 meaningful merge nodes. End with 2-3 distinct endings.`,
      nodeTarget: 18 + complexity * 9,
      endingTarget: 3,
    },
    web: {
      structure: `**Structure: COMPLEX WEB** — A highly interconnected story graph. Branches can cross-link to other branches' nodes. Multiple paths lead to the same scenes from different angles. Use many merge nodes and cross-connections. 3-8 distinct endings reflecting different value polarities. This creates a dense web of possibilities.`,
      nodeTarget: 25 + complexity * 15,
      endingTarget: Math.min(3 + complexity, 8),
    },
  }

  const pInfo = presetInstructions[preset ?? 'linear'] ?? presetInstructions.linear
  const nodeTarget = Math.min(Math.round(pInfo.nodeTarget * lengthMul * detail.nodeFactor), MAX_NODE_CAP)
  const endingTarget = contentLength === 'long'
    ? Math.min(pInfo.endingTarget + 2, 8)
    : contentLength === 'short'
      ? Math.max(pInfo.endingTarget - 1, 1)
      : pInfo.endingTarget

  let userContent = `⚠️ HARD LIMIT: Each node's "content" field must be under ${detail.wordLimit} words (roughly ${Math.round(detail.wordLimit * 1.5)} Chinese characters). Count carefully. Violating this limit will cause the output to be truncated and UNUSABLE.

Generate a CRPG story skeleton with the following parameters:

**Keywords / Theme**: ${keywords}
**Complexity**: ${complexity}/5 — produce roughly ${actCount} acts.

${pInfo.structure}`

  if (worldSetting) {
    userContent += `\n\n**World Setting**:\n${worldSetting}`
  }

  if (characters && characters.length > 0) {
    userContent += `\n\n**Characters**:\n`
    for (const c of characters) {
      userContent += `- **${c.name}**${c.description ? ': ' + c.description : ''}\n`
    }
  }

  userContent += `

Requirements:
- Provide ${actCount} acts, each with at least one choice or check node.
- Total node count: roughly ${nodeTarget}.
- At least ${endingTarget} distinct endings that reflect the controlling idea from different value poles.
- Every choice node must be a genuine dilemma (no obvious "good" answer).
- Include act_break nodes to mark act boundaries.
- Make sure the edges form a valid directed acyclic graph from a single start node.
- ⚠️ ABSOLUTE RULE: Each "content" field MUST be under ${detail.wordLimit} words / ${Math.round(detail.wordLimit * 1.5)} Chinese characters. This is NON-NEGOTIABLE. Write condensed, impactful prose — not sprawling paragraphs.
- The COMPLETE JSON with ALL nodes and edges MUST fit in the output. If in doubt, use FEWER nodes. A truncated JSON is completely useless and wastes the entire generation.
- PRIORITY: Complete JSON > word limit compliance > node count > content richness.

### WRITING STYLE
${detail.style}
Remember: STRICT ${detail.wordLimit}-word limit per node. Every word must earn its place.`

  // Scale max_tokens based on combination weight
  // detailed+long combos need much more room; bifurcating/web presets are especially heavy
  const isHeavyPreset = preset === 'bifurcating' || preset === 'web'
  const isHeavyDetail = detailRichness === 'detailed' || detailRichness === 'extreme'
  const isExtremeDetail = detailRichness === 'extreme'
  const isHeavyLength = contentLength === 'long'
  let maxTokens = 128000
  if (isExtremeDetail || isHeavyLength || (isHeavyPreset && isHeavyDetail)) {
    maxTokens = 196000
  }

  return {
    model: MODEL,
    messages: [
      { role: 'system', content: buildSystemPrompt(poeticMode, locale) },
      { role: 'user', content: userContent },
    ],
    temperature,
    maxTokens,
  }
}

// ---- buildContentPrompt ----------------------------------------------------

interface NodeMetadata {
  id: string
  type: string
  title: string
  actIndex: number
  sequenceIndex: number
}

interface PathContext {
  controllingIdea: string
  previousNodes: Array<{ title: string; valueBefore: string; valueAfter: string }>
}

export function buildContentPrompt(
  nodeMetadata: NodeMetadata,
  pathContext: PathContext,
  locale?: string,
): PromptPayload {
  const systemContent = `${MCKEE_SYSTEM_FULL}${langInstruction(locale)}

You are now writing the FULL detailed content for a single node in the story graph.
Maintain consistency with the controlling idea and the value arc established by previous nodes.
Output strictly valid JSON with this shape:
{
  "content": "<full narrative text, 150-300 words>",
  "valueBefore": "<value state before this scene>",
  "valueAfter": "<value state after this scene>",
  "innerConflict": "<character's psychological tension>",
  "personalConflict": "<interpersonal tension>",
  "extraPersonalConflict": "<societal/environmental tension>"
}`

  const userContent = `### Node to expand
- **ID**: ${nodeMetadata.id}
- **Type**: ${nodeMetadata.type}
- **Title**: ${nodeMetadata.title}
- **Act ${nodeMetadata.actIndex + 1}, Beat ${nodeMetadata.sequenceIndex + 1}**

### Controlling Idea
${pathContext.controllingIdea}

### Path so far (value arc)
${pathContext.previousNodes
  .map((n, i) => `${i + 1}. "${n.title}" — ${n.valueBefore} → ${n.valueAfter}`)
  .join('\n')}

Write the detailed content for this node. Follow the six hard constraints.`

  return {
    model: MODEL,
    messages: [
      { role: 'system', content: systemContent },
      { role: 'user', content: userContent },
    ],
    temperature: 0.9,
  }
}

// ---- buildContinuePrompt ---------------------------------------------------

interface AffectedNode {
  id: string
  type: string
  title: string
  content: string
}

export function buildContinuePrompt(
  editSummary: { nodeId: string; oldContent: string; newContent: string },
  graphContext: { controllingIdea: string; totalNodes: number; totalEdges: number },
  affectedNodes: AffectedNode[],
  locale?: string,
): PromptPayload {
  const systemContent = `${MCKEE_SYSTEM_FULL}${langInstruction(locale)}

The user has edited a node in an existing story graph. You must rewrite the AFFECTED downstream nodes so the narrative stays coherent with the edit while still satisfying all six hard constraints.

Output strictly valid JSON:
{
  "updatedNodes": [
    {
      "id": "<existing node id>",
      "data": {
        "title": "...",
        "content": "...",
        "valueBefore": "...",
        "valueAfter": "...",
        "choices": [...]   // if choice node
      }
    }
  ]
}`

  const userContent = `### Edit Summary
**Node ${editSummary.nodeId}** was changed.

**Old content**:
${editSummary.oldContent}

**New content**:
${editSummary.newContent}

### Graph Context
- Controlling Idea: ${graphContext.controllingIdea}
- Graph size: ${graphContext.totalNodes} nodes, ${graphContext.totalEdges} edges

### Affected Downstream Nodes (rewrite these)
${affectedNodes
  .map(
    (n) => `- **${n.id}** (${n.type}) "${n.title}"
  Current content: ${n.content}`,
  )
  .join('\n\n')}

Rewrite each affected node to maintain narrative coherence after the edit. Preserve node IDs.`

  return {
    model: MODEL,
    messages: [
      { role: 'system', content: systemContent },
      { role: 'user', content: userContent },
    ],
    temperature: 0.9,
  }
}
