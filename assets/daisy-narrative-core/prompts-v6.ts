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


### ACT 1 SETUP (建置) — MANDATORY
The story MUST begin with 1 narrative node that establishes the world and protagonist through ACTIVE GAMEPLAY — the player exploring, talking to someone, or doing a routine task that reveals the setting. NOT a passive description paragraph. The setup should feel interactive: the player discovers the world by doing things in it.
The **inciting incident** should come quickly (2nd or 3rd node) — this is a game, not a novel. Players want to get into the action.

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
      "sourceHandle": "<see rules below>",
      "label": "<optional edge label>"
    }
  ]
}
\`\`\`

### EDGE sourceHandle RULES (CRITICAL — wrong values break the graph!)
- **narrative, merge, act_break** → sourceHandle MUST be \`null\` (single output)
- **ending** → NEVER has outgoing edges (terminal node)
- **choice** → sourceHandle = \`"0"\`, \`"1"\`, \`"2"\`, etc. (zero-based index matching the choices array order)
- **check** → sourceHandle = exactly \`"success"\` or \`"fail"\` (not "pass", "failure", or any other variant)

### JSON SAFETY — DIALOGUE QUOTES
When writing dialogue in content fields, you MUST use Chinese bracket quotes 「」 (not ASCII double quotes ""). ASCII double quotes inside JSON strings will BREAK the JSON. Example:
- CORRECT: 「你也感觉到了吗？」她低声说。
- WRONG: "你也感觉到了吗？"她低声说。`

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
    style: 'Game-quality prose: short action sentences, punchy dialogue (2-3 exchanges), concrete details the player can interact with. Show character through what they DO and SAY. Max 6-8 sentences per node. Do NOT exceed the word limit.',
  },
  extreme: {
    wordLimit: 80,
    nodeFactor: 1.8,
    style: `BEAT-LEVEL GRANULARITY: Each node represents a single BEAT — the smallest dramatic unit in McKee's hierarchy. A beat is ONE action-reaction exchange: something happens, the value shifts.

Each beat-node: 40-80 words. One action, one reaction, one value shift. Sharp and punchy.
Beats are grouped into SEQUENCES (named groups of 2-5 beats forming a mini-arc within a scene).

BEAT RULES:
- Each beat creates a micro turning point — the value state alternates (+ → - → + or - → + → -).
- Within a sequence, beats build progressively: each raises stakes or subverts expectations.
- The final beat in a sequence is its micro-climax.
- Write in active voice. Short sentences. Concrete actions. The player DOES things.
- Choice and check nodes are also beat-level: they represent the moment of decision/test, not a full scene.`,
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

// ---- buildSkeletonOnlyPrompt -----------------------------------------------
// Two-step generation Step 1: structure only, no narrative prose
// -------------------------------------------------------------------------

export function buildSkeletonOnlyPrompt(params: SkeletonParams): PromptPayload {
  const { keywords, preset, complexity, worldSetting, characters, locale } = params
  const poeticMode = params.poeticMode ?? true
  const contentLength = params.contentLength ?? 'medium'
  const isExtreme = (params.detailRichness ?? 'standard') === 'extreme'

  const temperature = poeticMode ? 0.9 : 0.7
  const lengthMul = LENGTH_MULTIPLIER[contentLength] ?? 1.0
  // Use standard node factor for skeleton — detail doesn't affect structure count
  const detail = DETAIL_CONFIG[params.detailRichness ?? 'standard'] ?? DETAIL_CONFIG.standard

  const actCount = Math.min(Math.max(complexity, 1), 5)

  const presetInstructions: Record<string, { structure: string; nodeTarget: number; endingTarget: number }> = {
    linear: {
      structure: `**Structure: LINEAR** — A mostly single-path story. One or two choice points with short branches (2-3 nodes each) before reconverging.`,
      nodeTarget: 8 + complexity * 4,
      endingTarget: 2,
    },
    bifurcating: {
      structure: `**Structure: BIFURCATING** — Shared Act 1 then a pivotal choice splits into TWO distinct parallel storylines. Each branch must develop independently for 8-12 nodes with unique scenes. The two branches NEVER reconverge. Each branch leads to 2+ endings (4+ total).`,
      nodeTarget: 15 + complexity * 8,
      endingTarget: 4,
    },
    funnel: {
      structure: `**Structure: FUNNEL** — Branches diverge after each choice/check and develop for 3-5 nodes each before reconverging at merge points. 2-3 merge nodes. End with 2-3 distinct endings.`,
      nodeTarget: 18 + complexity * 9,
      endingTarget: 3,
    },
    web: {
      structure: `**Structure: COMPLEX WEB** — Highly interconnected. Branches cross-link. Multiple paths lead to same scenes from different angles. 3-8 distinct endings.`,
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

  const skeletonSystem = `You are a CRPG narrative architect deeply versed in Robert McKee's *Story* principles.
${poeticMode ? KEYWORD_POETIC : KEYWORD_LITERAL}

### HARD CONSTRAINTS (structure must satisfy ALL six):
1. **Value Shift** — Every scene turns at least one value. State valueBefore/valueAfter as brief tags (2-5 words each).
2. **Progressive Complication** — Each successive beat raises stakes or narrows options.
3. **Dilemma** — Choice nodes present irreconcilable dilemmas. No obvious answers.
4. **The Gap** — Results always differ from expectations.
5. **Controlling Idea** — ONE theme sentence across all acts.
6. **Three Levels of Conflict** — Inner, personal, and extra-personal conflict throughout.

### PLAYER NAME PLACEHOLDER
Use \`{{playerName}}\` for the protagonist in choice texts. NPCs have fixed names.

### ACT 1 SETUP (建置) — MANDATORY
Begin with 1 node that establishes the world through active gameplay (exploring, talking, doing a task). Get to the inciting incident by node 2-3. This is a game — don't make players wait.

### BRANCHING PHILOSOPHY
- **Delayed Convergence** — After a choice, develop each branch for 3-5+ unique nodes before any merge.
- **Distinct Branch Identity** — Each branch explores different thematic facets with different NPCs/revelations.

### NODE TYPES
narrative, choice, check, merge, act_break, ending

${isExtreme ? `### BEAT-LEVEL GRANULARITY (EXTREME MODE)
In extreme mode, each node = ONE BEAT (McKee's smallest dramatic unit), NOT a full scene.

**Hierarchy (top to bottom):**
- ACT (幕) — the largest unit, defined by actIndex
- SEQUENCE (序列) — a mini-arc of 2-5 beats within an act, building to its own micro-climax
- BEAT (节拍) = each individual NODE — a single action-reaction moment

**What this means:**
- Where standard mode has 1 scene node "探索废弃空间站", extreme mode splits it into 3-4 beat-nodes:
  - Beat 1: "推开气闸舱门，空气涌入" (action)
  - Beat 2: "发现墙上的抓痕和血迹" (discovery → tension)
  - Beat 3: "终端闪烁，自动播放最后一条日志" (revelation)
- Each beat-node is short (40-80 words), punchy, ONE thing happens.
- Beats within a sequence alternate value polarity (+/-/+/- or -/+/-/+).
- Sequences give the graph a visual "rhythm" — groups of beats forming mini-arcs.

### OUTPUT FORMAT — EXTREME SKELETON (beat-level nodes, grouped by sequences)
Return **strictly valid JSON** with this shape:
{
  "controllingIdea": "<one sentence theme>",
  "sequences": [
    {
      "id": "<unique, e.g. seq-1-1>",
      "actIndex": <0-based act number>,
      "order": <0-based order within the act>,
      "name": "<sequence purpose, 3-8 words, e.g. 觉醒与探索, 信任瓦解>",
      "valueBefore": "<value state at sequence start>",
      "valueAfter": "<value state at sequence end>"
    }
  ],
  "nodes": [
    {
      "id": "<unique string>",
      "type": "<node type>",
      "data": {
        "title": "<beat title, 5-12 words — what happens in this ONE moment>",
        "choices": ["..."],  // ONLY for choice nodes
        "check": { "attribute": "...", "dc": <number> },  // ONLY for check nodes
        "endingType": "<positive|negative|ironic|ambiguous>",  // ONLY for ending nodes
        "valueBefore": "<2-5 word value state>",
        "valueAfter": "<2-5 word value state>"
      },
      "actIndex": <0-based act number>,
      "sequenceId": "<references a sequence id>",
      "beatIndex": <0-based order within the sequence>
    }
  ],
  "edges": [
    { "id": "<unique>", "source": "<node id>", "target": "<node id>", "sourceHandle": "<see rules>", "label": "<optional>" }
  ]
}` : `### OUTPUT FORMAT — SKELETON ONLY (no narrative prose!)
Return **strictly valid JSON** with this shape:
{
  "controllingIdea": "<one sentence theme>",
  "nodes": [
    {
      "id": "<unique string>",
      "type": "<node type>",
      "data": {
        "title": "<descriptive title, 5-15 words — enough to convey the scene>",
        "choices": ["<option A, 1 sentence>", "<option B, 1 sentence>"],  // ONLY for choice nodes
        "check": { "attribute": "<skill name>", "dc": <number> },  // ONLY for check nodes
        "endingType": "<positive|negative|ironic|ambiguous>",  // ONLY for ending nodes
        "valueBefore": "<2-5 word value state>",
        "valueAfter": "<2-5 word value state>"
      },
      "actIndex": <0-based act number>,
      "sequenceIndex": <order within act>
    }
  ],
  "edges": [
    { "id": "<unique>", "source": "<node id>", "target": "<node id>", "sourceHandle": "<see rules below>", "label": "<optional>" }
  ]
}`}

### EDGE sourceHandle RULES (CRITICAL — wrong values break the graph!)
- narrative, merge, act_break → sourceHandle = null (single output)
- ending → NO outgoing edges (terminal node)
- choice → sourceHandle = "0", "1", "2" (zero-based index of choices array)
- check → sourceHandle = "success" or "fail" (exactly these strings, no variants)

⚠️ CRITICAL: Do NOT include a "content" field. This is a STRUCTURE-ONLY skeleton. Titles should be descriptive enough to convey each scene's purpose and value shift. Full narrative prose will be generated in a separate step.${langInstruction(locale)}`

  let userContent = `Generate a CRPG story SKELETON (structure only) with:

**Keywords / Theme**: ${keywords}
**Complexity**: ${complexity}/5 — roughly ${actCount} acts.

${pInfo.structure}`

  if (worldSetting) userContent += `\n\n**World Setting**:\n${worldSetting}`
  if (characters && characters.length > 0) {
    userContent += `\n\n**Characters**:\n`
    for (const c of characters) {
      userContent += `- **${c.name}**${c.description ? ': ' + c.description : ''}\n`
    }
  }

  userContent += `

Requirements:
- ${actCount} acts, each with at least one choice or check.
- Roughly ${nodeTarget} nodes total.
- At least ${endingTarget} distinct endings reflecting different value poles.
- Every choice = genuine dilemma. Include act_break nodes.
- Valid DAG from a single start node.
- NO "content" field — titles, choices, and value tags only.`

  if (isExtreme) {
    userContent += `
- ⚡ EXTREME MODE — BEAT-LEVEL NODES:
  - Each node = ONE BEAT (single action-reaction moment), NOT a full scene.
  - A standard "scene" should be split into 2-4 beat-nodes.
  - Group beats into SEQUENCES (2-5 beats per sequence, 2-4 sequences per act).
  - Include a "sequences" array at the top level.
  - Each node must have "sequenceId" and "beatIndex".
  - Beat value shifts should alternate (+/-) within each sequence.
  - More nodes than standard mode! Expect ${Math.round(nodeTarget * 1.5)}-${nodeTarget * 2} beat-nodes.
  - Choice/check nodes are also beat-level: the moment of decision, not a full scene leading up to it.`
  }

  return {
    model: MODEL,
    messages: [
      { role: 'system', content: skeletonSystem },
      { role: 'user', content: userContent },
    ],
    temperature,
    maxTokens: isExtreme ? 24000 : 16000,  // Extreme skeleton is larger due to sequences
  }
}

// ---- buildContentBatchPrompt -----------------------------------------------
// Two-step generation Step 2: fill narrative content for a batch of nodes
// -------------------------------------------------------------------------

interface SequenceInfo {
  id: string
  actIndex: number
  order: number
  name: string
  valueBefore: string
  valueAfter: string
}

interface SkeletonData {
  controllingIdea: string
  sequences?: SequenceInfo[]
  nodes: Array<{ id: string; type: string; data: Record<string, unknown>; actIndex?: number; sequenceIndex?: number; sequenceId?: string; beatIndex?: number }>
  edges: Array<{ id: string; source: string; target: string; sourceHandle?: string | null; label?: string }>
}

export function buildContentBatchPrompt(
  skeleton: SkeletonData,
  nodeIds: string[],
  detailRichness: 'concise' | 'standard' | 'detailed' | 'extreme',
  locale?: string,
  poeticMode?: boolean,
): PromptPayload {
  const detail = DETAIL_CONFIG[detailRichness] ?? DETAIL_CONFIG.standard
  const isExtreme = detailRichness === 'extreme'
  const isPoetic = poeticMode ?? false

  // Build sequence map for extreme mode
  const seqMap = new Map<string, SequenceInfo>()
  if (skeleton.sequences) {
    for (const seq of skeleton.sequences) seqMap.set(seq.id, seq)
  }

  // Build a compact skeleton summary for context
  const skeletonSummary = skeleton.nodes.map((n) => {
    const d = n.data
    let line = `${n.id} [${n.type}] "${d.title}" (act${(n.actIndex ?? 0) + 1}`
    // Include sequence info if available
    const seq = n.sequenceId ? seqMap.get(n.sequenceId) : undefined
    if (seq) line += `, seq:"${seq.name}" beat#${(n.beatIndex ?? 0) + 1}`
    line += ')'
    if (d.valueBefore && d.valueAfter) line += ` | ${d.valueBefore} → ${d.valueAfter}`
    if (d.choices) line += ` | choices: ${(d.choices as string[]).join(' / ')}`
    if (d.check) line += ` | check: ${(d.check as { attribute: string; dc: number }).attribute} DC${(d.check as { attribute: string; dc: number }).dc}`
    if (d.endingType) line += ` | ${d.endingType} ending`
    return line
  }).join('\n')

  const edgeSummary = skeleton.edges.map((e) =>
    `${e.source} → ${e.target}${e.sourceHandle ? ` [${e.sourceHandle}]` : ''}${e.label ? ` "${e.label}"` : ''}`
  ).join('\n')

  const nodesToFill = skeleton.nodes.filter((n) => nodeIds.includes(n.id))

  let beatInstruction = ''
  if (isExtreme) {
    beatInstruction = `
EXTREME MODE: Each node IS a beat — the smallest dramatic unit. Write ONE focused moment per node.
- 40-80 words per node. ONE action, ONE reaction, ONE value shift.
- Short, punchy sentences. Active voice. The player does things.
- No need for "beats" array — the node itself is the beat.`
  }

  const systemContent = `You are a CRPG narrative game writer. You combine Robert McKee's story craft with interactive game design.

### TASK
Write narrative content for nodes in an interactive story graph. This is a GAME, not a novel. The player must feel like an active participant, not a passive reader.

### HARD WRITING CONSTRAINTS
1. **Value Shift** — Every scene turns the value stated in the skeleton's valueBefore→valueAfter.
2. **Progressive Complication** — Raise stakes with each successive scene.
3. **The Gap** — Outcomes differ from expectations.
4. **Three Levels of Conflict** — Weave inner, personal, and extra-personal tension.

### PLAYER NAME
Use \`{{playerName}}\` for the protagonist. NPCs have fixed names.

### WRITING STYLE
${detail.style}
Word limit per content field: ${detail.wordLimit} words (≈${Math.round(detail.wordLimit * 1.5)} Chinese characters). Every word earns its place.
${beatInstruction}

### GAME WRITING RULES (CRITICAL — this is a GAME, not a novel)
1. **Player as agent** — {{playerName}} DOES things: opens doors, picks up objects, talks to people, makes decisions. Write in active voice. The player drives the action, not the narrator.
2. **Show the world through interaction** — Don't describe a room in a paragraph. Let the player discover details by touching, examining, talking. "{{playerName}}拉开抽屉，里面是一把生锈的钥匙和一张字条" beats "抽屉里静静躺着一把钥匙".
3. **Keep it punchy** — Short sentences for action. Max 2-3 sentences of description before something HAPPENS (dialogue, discovery, event, decision). No long atmospheric paragraphs.
4. **Concrete game information** — Include things the player cares about: objects they can use, NPCs they can talk to, threats they need to handle, clues they find. Every detail should be actionable or foreshadow something actionable.
5. **Dialogue is gameplay** — NPC dialogue should reveal information, present dilemmas, or create tension. NPCs have distinct voices and agendas. Keep exchanges short and sharp.
6. **Tension through stakes, not prose** — Create tension through WHAT happens (time pressure, scarce resources, difficult choices), not through HOW you describe it. "氧气还剩三小时" is more tense than any purple prose.
7. **Setup nodes are active too** — Even world-building scenes should have the player DOING something (exploring, talking, investigating), not passively observing.

### ANTI-MELODRAMA (keep it grounded)
- Don't name emotions directly. Show through action and dialogue.
- Max ONE physical sensation per node (heartbeat, trembling, etc.).
- No overwrought metaphors. Plain, precise language.
- Not every scene is a crisis — include humor, awkwardness, mundane texture.${isPoetic ? '' : `
- Write like a game script, not poetry. Concrete actions, specific objects, real dialogue.`}

### JSON SAFETY — DIALOGUE QUOTES
When writing dialogue in content fields, you MUST use Chinese bracket quotes 「」 (not ASCII double quotes ""). ASCII double quotes inside JSON strings will BREAK the JSON. Example:
- CORRECT: 「你也感觉到了吗？」她低声说。
- WRONG: "你也感觉到了吗？"她低声说。

### OUTPUT FORMAT
Return **strictly valid JSON**:
{
  "filledNodes": [
    {
      "id": "<node id>",
      "content": "<narrative prose>",
      "successText": "<for check nodes — what happens on success>",
      "failText": "<for check nodes — what happens on failure>",
      "epilogue": "<for ending nodes — brief epilogue paragraph>"
    }
  ]
}

Only include fields relevant to each node type. "content" is required for ALL nodes.${langInstruction(locale)}`

  // Build sequence summary for extreme mode
  let sequenceSummary = ''
  if (isExtreme && skeleton.sequences && skeleton.sequences.length > 0) {
    sequenceSummary = `\n**Sequences**:\n${skeleton.sequences.map((s) =>
      `${s.id} (act${s.actIndex + 1}, #${s.order + 1}) "${s.name}" | ${s.valueBefore} → ${s.valueAfter}`
    ).join('\n')}\n`
  }

  const userContent = `### STORY SKELETON (full context)
**Controlling Idea**: ${skeleton.controllingIdea}
${sequenceSummary}
**Nodes**:
${skeletonSummary}

**Edges**:
${edgeSummary}

---

### NODES TO FILL (write content for these ${nodesToFill.length} nodes):
${nodesToFill.map((n) => {
  const d = n.data
  const seq = n.sequenceId ? seqMap.get(n.sequenceId) : undefined
  let desc = `- **${n.id}** [${n.type}] "${d.title}" (Act ${(n.actIndex ?? 0) + 1}`
  if (seq) desc += `, Sequence: "${seq.name}", Beat ${(n.beatIndex ?? 0) + 1}/${skeleton.nodes.filter(sn => sn.sequenceId === n.sequenceId).length}`
  else desc += `, Beat ${(n.sequenceIndex ?? 0) + 1}`
  desc += ')'
  if (d.valueBefore && d.valueAfter) desc += `\n  Value shift: ${d.valueBefore} → ${d.valueAfter}`
  if (seq) desc += `\n  Sequence arc: ${seq.valueBefore} → ${seq.valueAfter}`
  if (d.choices) desc += `\n  Choices: ${(d.choices as string[]).join(' / ')}`
  if (d.check) desc += `\n  Check: ${(d.check as { attribute: string; dc: number }).attribute} DC${(d.check as { attribute: string; dc: number }).dc}`
  if (d.endingType) desc += `\n  Ending type: ${d.endingType}`
  return desc
}).join('\n\n')}

Write game-ready content. The player should feel like they're PLAYING, not reading. Every node should have the player doing something or learning something they can act on. Follow the value arcs.${isExtreme ? ' Each scene must serve its SEQUENCE arc — build toward the sequence\'s value climax.' : ''} Keep it tight.`

  return {
    model: MODEL,
    messages: [
      { role: 'system', content: systemContent },
      { role: 'user', content: userContent },
    ],
    temperature: isPoetic ? 0.9 : 0.7,
    maxTokens: Math.min(nodesToFill.length * 2000, 32000),
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
