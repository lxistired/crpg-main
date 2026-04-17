// ---------------------------------------------------------------------------
// McKee-flavoured prompt templates for CRPG story generation — V4 Model
// ---------------------------------------------------------------------------
// This is the V4 narrative model (pre-anti-melodrama), preserved for
// independent development on port 3002.
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

// ---- buildSkeletonPrompt (single-step, structure + content) ----------------

export function buildSkeletonPrompt(params: SkeletonParams): PromptPayload {
  const { keywords, preset, complexity, worldSetting, characters, locale } = params
  const poeticMode = params.poeticMode ?? true
  const detailRichness = params.detailRichness ?? 'standard'
  const contentLength = params.contentLength ?? 'medium'

  const temperature = poeticMode ? 0.9 : 0.7
  const detail = DETAIL_CONFIG[detailRichness] ?? DETAIL_CONFIG.standard
  const lengthMul = LENGTH_MULTIPLIER[contentLength] ?? 1.0

  const actCount = Math.min(Math.max(complexity, 1), 5)

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
// Two-step Step 1: structure only, no narrative prose
// -------------------------------------------------------------------------

export function buildSkeletonOnlyPrompt(params: SkeletonParams): PromptPayload {
  const { keywords, preset, complexity, worldSetting, characters, locale } = params
  const poeticMode = params.poeticMode ?? true
  const contentLength = params.contentLength ?? 'medium'

  const temperature = poeticMode ? 0.9 : 0.7
  const lengthMul = LENGTH_MULTIPLIER[contentLength] ?? 1.0
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

### BRANCHING PHILOSOPHY
- **Delayed Convergence** — After a choice, develop each branch for 3-5+ unique nodes before any merge.
- **Distinct Branch Identity** — Each branch explores different thematic facets with different NPCs/revelations.

### NODE TYPES
narrative, choice, check, merge, act_break, ending

### OUTPUT FORMAT — SKELETON ONLY (no narrative prose!)
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
    { "id": "<unique>", "source": "<node id>", "target": "<node id>", "sourceHandle": "<handle or null>", "label": "<optional>" }
  ]
}

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

  return {
    model: MODEL,
    messages: [
      { role: 'system', content: skeletonSystem },
      { role: 'user', content: userContent },
    ],
    temperature,
    maxTokens: 16000,
  }
}

// ---- buildContentBatchPrompt -----------------------------------------------
// Two-step Step 2: fill narrative content for a batch of nodes
// -------------------------------------------------------------------------

interface SkeletonData {
  controllingIdea: string
  nodes: Array<{ id: string; type: string; data: Record<string, unknown>; actIndex?: number; sequenceIndex?: number }>
  edges: Array<{ id: string; source: string; target: string; sourceHandle?: string | null; label?: string }>
}

export function buildContentBatchPrompt(
  skeleton: SkeletonData,
  nodeIds: string[],
  detailRichness: 'concise' | 'standard' | 'detailed' | 'extreme',
  locale?: string,
): PromptPayload {
  const detail = DETAIL_CONFIG[detailRichness] ?? DETAIL_CONFIG.standard
  const isExtreme = detailRichness === 'extreme'

  const skeletonSummary = skeleton.nodes.map((n) => {
    const d = n.data
    let line = `${n.id} [${n.type}] "${d.title}" (act${(n.actIndex ?? 0) + 1})`
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
For NARRATIVE and ACT_BREAK nodes, include a "beats" array — 3-6 dramatic micro-moments:
  "beats": [{ "text": "<40-60 words>", "valueShift": "+" or "-" }, ...]
Beat rules: each beat creates a micro turning point, values alternate (+ → - → +). Include sensory detail, thought, dialogue.
The "content" field still contains ALL beats concatenated for fallback rendering.`
  }

  const systemContent = `You are a CRPG narrative writer versed in Robert McKee's *Story* principles.

### TASK
Write detailed narrative content for specific nodes in a story graph. You have the full story skeleton for context.

### HARD WRITING CONSTRAINTS
1. **Value Shift** — Every scene must turn the value stated in the skeleton's valueBefore→valueAfter.
2. **Progressive Complication** — Raise stakes with each successive scene.
3. **The Gap** — Outcomes differ from expectations.
4. **Three Levels of Conflict** — Weave inner, personal, and extra-personal tension.

### PLAYER NAME
Use \`{{playerName}}\` for the protagonist. NPCs have fixed names.

### WRITING STYLE
${detail.style}
Word limit per content field: ${detail.wordLimit} words (≈${Math.round(detail.wordLimit * 1.5)} Chinese characters). Every word earns its place.
${beatInstruction}

### OUTPUT FORMAT
Return **strictly valid JSON**:
{
  "filledNodes": [
    {
      "id": "<node id>",
      "content": "<narrative prose>",
      "successText": "<for check nodes — what happens on success>",
      "failText": "<for check nodes — what happens on failure>",
      "epilogue": "<for ending nodes — brief epilogue paragraph>"${isExtreme ? ',\n      "beats": [{ "text": "...", "valueShift": "+" }, ...]  // for narrative/act_break nodes' : ''}
    }
  ]
}

Only include fields relevant to each node type. "content" is required for ALL nodes.${langInstruction(locale)}`

  const userContent = `### STORY SKELETON (full context)
**Controlling Idea**: ${skeleton.controllingIdea}

**Nodes**:
${skeletonSummary}

**Edges**:
${edgeSummary}

---

### NODES TO FILL (write content for these ${nodesToFill.length} nodes):
${nodesToFill.map((n) => {
  const d = n.data
  let desc = `- **${n.id}** [${n.type}] "${d.title}" (Act ${(n.actIndex ?? 0) + 1}, Beat ${(n.sequenceIndex ?? 0) + 1})`
  if (d.valueBefore && d.valueAfter) desc += `\n  Value shift: ${d.valueBefore} → ${d.valueAfter}`
  if (d.choices) desc += `\n  Choices: ${(d.choices as string[]).join(' / ')}`
  if (d.check) desc += `\n  Check: ${(d.check as { attribute: string; dc: number }).attribute} DC${(d.check as { attribute: string; dc: number }).dc}`
  if (d.endingType) desc += `\n  Ending type: ${d.endingType}`
  return desc
}).join('\n\n')}

Write vivid, engaging content for each node. Follow the value arcs. Maintain narrative coherence with surrounding nodes.`

  return {
    model: MODEL,
    messages: [
      { role: 'system', content: systemContent },
      { role: 'user', content: userContent },
    ],
    temperature: 0.9,
    maxTokens: Math.min(nodesToFill.length * 2000, 32000),
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
