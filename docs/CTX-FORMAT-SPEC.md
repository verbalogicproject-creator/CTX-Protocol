# .ctx Format Specification v1.0

> **Status:** Draft
> **Author:** Eyal Nof
> **Date:** 2026-03-26
> **Purpose:** Formal specification for the `.ctx` (context map) file format — a structured architecture notation optimized for LLM context injection.

---

## 1. Overview

### 1.1 What .ctx Is

A `.ctx` file is a **structured architecture map** that encodes the nodes (components, modules, files), edges (dependencies, subscriptions), and groupings (directories, layers) of a software folder in a format optimized for LLM consumption.

`.ctx` files are the machine-readable layer of a **lazy-loading context management system** where:
- `start-here.md` routes readers (human or AI) to the right subfolder
- `{folder}.md` provides detailed prose reference per component
- `{folder}.ctx` provides the full architectural graph in minimum tokens

### 1.2 Design Principles

1. **Zero-explanation parseability.** LLMs must understand the format without preamble. All syntax uses patterns pre-trained in LLM training data: markdown headings, `key : value` pairs, `->` arrows, `[tags]`.
2. **Single-pass reading.** The file reads top-to-bottom. By the time an LLM finishes a node, it knows everything about that node — identity, description, type, outgoing edges. No cross-referencing between sections.
3. **Minimum tokens, maximum information.** Every token in a `.ctx` file carries semantic meaning. No rendering directives, no styling, no visual layout instructions.
4. **Lazy-loadable hierarchy.** A `.ctx` file can reference child `.ctx` files via drill-down links. An AI session loads only the level of detail it needs.

### 1.3 What .ctx Is Not

- Not a diagram format. `.ctx` files are never rendered visually.
- Not a replacement for prose documentation. The `{folder}.md` file carries descriptions; `.ctx` carries structure.
- Not a general-purpose graph format. It is purpose-built for software architecture context injection.

---

## 2. File Structure

A `.ctx` file has two sections in fixed order:

```
┌─────────────────────────┐
│  Header (# comments)    │  ← metadata, format version, edge legend
├─────────────────────────┤
│  Body (groups + nodes)  │  ← the architecture graph
└─────────────────────────┘
```

There is no separate edges section. Edges are inline with their source nodes.

### 2.1 Encoding

- UTF-8
- LF line endings
- No BOM
- File extension: `.ctx`
- Filename: `{foldername}.ctx` where `{foldername}` matches the parent directory name

---

## 3. Header

The header consists of lines beginning with `#` (single hash + space). It must appear at the top of the file before any group or node definitions.

### 3.1 Required Header Fields

```
# {folder}/ — {title}
# format: ctx/1.0
# last-verified: YYYY-MM-DD
# edges: -> call/render | ~> subscribe/read | => HTTP API call
```

| Field | Description |
|---|---|
| **Line 1** | Folder name and human-readable title |
| **format** | Format version. Always `ctx/1.0` for this spec. |
| **last-verified** | Date when this file was last confirmed accurate against source code. ISO 8601 date (YYYY-MM-DD). |
| **edges** | Legend declaring all edge types used in this file. Required so the meaning of `->`, `~>`, and `=>` is never ambiguous. Only include edge types actually used in the file. |

### 3.2 Optional Header Fields

```
# nodes: {N} | edges: {N} | groups: {N}
```

Summary counts. Optional but recommended for large files. Helps an LLM gauge the scope of the architecture before reading the body.

---

## 4. Groups

Groups organize nodes into logical sections. They correspond to directories, layers, or conceptual groupings.

### 4.1 Syntax

```
## {name} — {description}
```

- `##` (double hash) defines a top-level group
- `###` (triple hash) defines a sub-group within the nearest preceding `##`
- Group names should match directory names where applicable
- Description after `—` (em dash) is optional but recommended

### 4.2 Examples

```
## lib/ — Core Engine
  ### aria-core/ — Framework
    AriaCore : Main orchestrator [lib]
  ### App Wiring
    ariaSingleton : App singleton [lib]
```

### 4.3 Nesting Limit

Maximum two levels: `##` and `###`. Deeper hierarchies should use child `.ctx` files via drill-down references (see Section 8).

### 4.4 Directory Groups with Drill-Down

When a group represents a directory that has its own `.ctx` file:

```
## components/ — UI -> components/components.ctx
  ### game/ (46) -> components/game/game.ctx
```

The `-> path/to/child.ctx` suffix tells an AI session where to find the detailed context map for that subdirectory. Paths are relative to the current `.ctx` file's directory.

### 4.5 Empty Groups

```
## models/ — Local Model Weights (empty)
```

The `(empty)` marker indicates the directory exists but contains no source files.

---

## 5. Nodes

Nodes represent individual components, modules, files, stores, services, or any discrete unit of software.

### 5.1 Syntax

```
  {name} : {description} [{type}]
```

| Part | Required | Description |
|---|---|---|
| **indent** | Yes | 2 spaces per nesting level (2 for `##` children, 4 for `###` children) |
| **name** | Yes | Unique identifier within the file. Must be stable across edits. Should match the component/module/file name. |
| **`:`** | Yes | Delimiter between name and description. Surrounded by spaces. |
| **description** | Yes | 1 sentence max. What it is and what it does. |
| **`[type]`** | Yes | Node type tag in square brackets (see Section 5.3). |

### 5.2 Name Rules

- Node names must be unique within the file
- Names should match the source code identifier (component name, file name, store name)
- Names must not contain `:`, `->`, `~>`, `=>`, `[`, `]`, or `#`
- Names are case-sensitive
- When referencing nodes in edges, the name must match exactly

### 5.3 Type Tags

Type tags classify nodes for quick scanning. The following types are defined in v1.0:

| Tag | Meaning | Examples |
|---|---|---|
| `[root]` | Entry point / root component | layout.tsx, main.py |
| `[screen]` | Top-level page or route | /game, /dashboard |
| `[component]` | UI component | ChatPanel, VoiceOrb |
| `[lib]` | Library / engine module | AriaCore, GeminiLive |
| `[store]` | State store | Zustand store, Redux slice |
| `[type]` | Type definition file | TypeScript .d.ts, interfaces |
| `[service]` | Backend service / business logic | GamePipeline, TherapyOrchestrator |
| `[router]` | API route handler | game.py, aria.py |
| `[data]` | Data file, dataset, or DB | JSON dataset, SQLite DB |
| `[test]` | Test file | test_game.py |
| `[config]` | Configuration file | config.py, tsconfig.json |
| `[ext]` | External service or API | Gemini API, HuggingFace |
| `[dir]` | Collapsed child directory | A folder represented as a single node |
| `[doc]` | Documentation file | Research docs, plans |
| `[backend]` | Backend API router (used in Backend Counterpart pattern) | game router, aria router |

Custom types are permitted. If a project needs domain-specific types, they may be added as `[custom-type]` (lowercase, hyphenated). Custom types should be documented in the file header:

```
# types: [cartridge] = persona configuration file
```

### 5.4 Special Markers

Markers are optional suffixes that add metadata to a node:

| Marker | Meaning | Example |
|---|---|---|
| `@entry` | Primary entry point of the folder | `layout : Root HTML [root] @entry` |
| `@hot` | Under active development / recently changed | `GameScreen : Gameplay [component] @hot` |
| `~{N}L` | Approximate line count (complexity signal) | `GameScreen : Gameplay [component] ~490L` |

Markers appear after the type tag, space-separated:

```
  GameScreen : Main gameplay orchestrator [component] @entry ~490L
```

### 5.5 Inline File Paths (v2 — reserved)

Future versions may support inline file paths:

```
  AriaCore : Main orchestrator [lib] @path aria-core/AriaCore.ts
```

This is reserved syntax. Parsers should accept and preserve `@path` markers but v1.0 does not require them.

---

## 6. Edges

Edges represent relationships between nodes. In `.ctx`, edges are **always inline** — they appear indented under their source node.

### 6.1 Syntax

```
  {source} : {description} [{type}]
    -> {target1}, {target2}, {target3}
    ~> {target4}, {target5}
    => {target6}
```

- Edges are indented 2 spaces deeper than their source node
- `->` = direct dependency (call, render, import, instantiate)
- `~>` = reactive dependency (subscribe, read, observe, use)
- `=>` = HTTP API call (frontend component calls backend router)
- Multiple targets on one line, comma-separated
- A node may have multiple edge lines (one `->`, one `~>`, one `=>`, or multiple of each)

### 6.2 Edge Types

v1.0 defines three edge types:

| Syntax | Name | Semantics | Examples |
|---|---|---|---|
| `->` | **call** | Source directly invokes, renders, imports, or instantiates target. Synchronous, explicit dependency. If target breaks, source breaks. | Component renders child, function calls function, router calls service |
| `~>` | **subscribe** | Source reactively reads, observes, or subscribes to target. Indirect, decoupled dependency. Source consumes target's output but doesn't control it. | Component reads store, service queries database, module uses type definitions |
| `=>` | **http** | Source makes HTTP API calls to target. Cross-boundary dependency — frontend to backend, service to service, or any network call. | Component fetches from API router, service calls external API |

The edge type set is **closed** in v1.0. No additional edge types may be defined. Three types distinguish direct dependencies, reactive subscriptions, and network boundaries — the three fundamental categories of coupling in modern full-stack applications.

### 6.3 Edge Labels

Optional labels provide context for non-obvious relationships:

```
    -> backend "proxy /api/*"
    ~> chatStore "voice status only"
```

Labels appear at the end of the line in double quotes. They should be short (under 30 characters). If a label is needed on a multi-target line, it applies to the last target:

```
    -> GeminiLive, backend "WebSocket"
```

For clarity, labeled edges should be on their own line when the label is important.

### 6.4 Compact Edge Syntax

When a node has a single outgoing edge of one type, it may be placed on the same line as the node definition:

```
  GeminiLive : WebSocket provider [lib] -> geminiAPI
  gameStore  : Screens, config, stats [store] ~> gameTypes
```

This is syntactic sugar. It is equivalent to:

```
  GeminiLive : WebSocket provider [lib]
    -> geminiAPI
```

Use compact syntax only for single-target, unlabeled edges. If a node has both `->` and `~>` edges, use separate indented lines.

### 6.5 No Edge Target Definitions

Edge targets must reference nodes defined elsewhere in the same file. If a target is an external node not defined in this file, it must appear in an `## External` group or be referenced via a cross-file drill-down.

Dangling edges (referencing undefined nodes) are a spec violation. Parsers should warn on them.

---

## 7. Collapse Syntax

Large folders may have too many nodes for a concise context map. The collapse syntax allows summarizing groups of similar nodes into a single line.

### 7.1 Syntax

```
  ... ({N}) : {name1}, {name2}, {name3}, ... [{type}]
```

- `...` prefix signals a collapsed/summarized group
- `({N})` is the count of collapsed nodes
- The description is a comma-separated list of node names
- The type tag applies to all collapsed nodes

### 7.2 Examples

```
## store/ — Zustand State (14)
  chatStore : Messages, voice status [store]
  gameStore : Screens, config, stats [store]
  dashStore : Mood, flags, notes [store]
  labStore  : Logic editor canvas [store]
  cartStore : Shopping cart [store]
  ... (9)   : tab, ariaMode, gameVoice, gameTheme, transcript, devLog, products, kg, sdk [store]
```

### 7.3 Rules

- Collapsed nodes cannot be edge targets. If a node needs to be referenced by an edge, it must be fully defined, not collapsed.
- The `({N})` count must match the number of names listed.
- Collapse should only be used for nodes that are similar in type and not individually important to the architecture overview.

---

## 8. Cross-File References

The `.ctx` format supports a lazy-loading hierarchy where each folder's `.ctx` file references child folders' `.ctx` files.

### 8.1 Drill-Down References

Drill-down references appear on group headers:

```
## components/ — UI -> components/components.ctx
  ### game/ (46) -> components/game/game.ctx
```

The `-> path/to/child.ctx` tells an AI session: "for the full architecture of this subfolder, read this file."

### 8.2 Directory Nodes

When a child directory is represented as a single collapsed node:

```
  SRC : 188 files — Next.js frontend [dir] -> src/src.ctx
```

The `[dir]` type and `-> path.ctx` reference work together to signal "this is a folder, drill down for details."

### 8.3 Path Resolution

All paths in drill-down references are relative to the directory containing the current `.ctx` file.

```
# In /root/project/src/src.ctx:
## components/ — UI -> components/components.ctx
# Resolves to: /root/project/src/components/components.ctx
```

### 8.4 External Nodes

Nodes representing external services, APIs, or systems outside the project use the `[ext]` type and do not have drill-down references:

```
## External
  geminiAPI : Gemini Live API — WebSocket streaming [ext]
  backend   : Python Backend — Game, Dashboard, NAI APIs [ext]
```

For cross-references to sibling directories within the same project (e.g., frontend referencing backend), use a comment:

```
## External (see ../backend/backend.ctx)
  backend : Python Backend [ext]
```

---

## 9. Indentation

Indentation uses spaces (not tabs) and encodes hierarchy.

| Context | Indent | Example |
|---|---|---|
| Header lines | 0 | `# format: ctx/1.0` |
| Top-level group (`##`) | 0 | `## lib/ — Core Engine` |
| Sub-group (`###`) | 2 | `  ### aria-core/` |
| Node under `##` | 2 | `  AriaCore : Main orchestrator [lib]` |
| Node under `###` | 4 | `    AriaCore : Main orchestrator [lib]` |
| Edge under node (##) | 4 | `    -> GeminiLive, NLKE` |
| Edge under node (###) | 6 | `      -> GeminiLive, NLKE` |

General rule: each nesting level adds 2 spaces. Edges are always 2 spaces deeper than their source node.

---

## 10. Comments and Blank Lines

### 10.1 Comments

Lines beginning with `#` (in the header) or inline after content are comments:

```
# This is a header comment
## lib/ — Core Engine  # this inline comment is NOT supported
```

Within the body, full-line comments use `#` with no leading whitespace:

```
# Authentication flow
  AuthGuard : Route protector [component]
    -> LoginScreen, Dashboard
```

Body comments are for human readers and AI context. They are not metadata.

### 10.2 Blank Lines

Blank lines are permitted anywhere and are semantically insignificant. They are encouraged between groups for readability.

---

## 11. Complete Grammar (ABNF-like)

```
file           = header CRLF body
header         = title-line format-line verified-line edges-line *optional-header
title-line     = "# " folder-name " — " title
format-line    = "# format: ctx/" version
verified-line  = "# last-verified: " date
edges-line     = "# edges: " edge-legend
optional-header = "# " key ": " value

body           = *( group / comment / blank-line )
group          = group-header *( subgroup / node / collapse / comment / blank-line )
group-header   = "## " name [ " — " description ] [ " -> " path ]
subgroup       = subgroup-header *( node / collapse / comment / blank-line )
subgroup-header = "  ### " name [ " (" count ")" ] [ " -> " path ]

node           = indent name " : " description " [" type "]" *marker [ compact-edge ]
marker         = " @entry" / " @hot" / " ~" digits "L"
compact-edge   = " -> " target / " ~> " target

edge-line      = indent+2 edge-op targets [ label ]
edge-op        = "-> " / "~> "
targets        = target *( ", " target )
target         = name
label          = ' "' text '"'

collapse       = indent "... (" count ") : " name-list " [" type "]"
name-list      = name *( ", " name )

comment        = "#" text
blank-line     = ""

name           = 1*(ALPHA / DIGIT / "/" / "-" / "_" / ".")
type           = 1*(ALPHA / "-")
path           = 1*(ALPHA / DIGIT / "/" / "-" / "_" / ".")
version        = DIGIT "." DIGIT
date           = DIGIT{4} "-" DIGIT{2} "-" DIGIT{2}
```

---

## 12. Validation Rules

A `.ctx` file is **valid** if:

1. The header contains all four required fields (title, format, last-verified, edges)
2. Every node has a unique name within the file
3. Every edge target references a node defined in the same file (or in an `## External` group)
4. Every collapse count `({N})` matches the number of names in the list
5. Indentation follows the 2-space-per-level rule consistently
6. Every node has exactly one type tag
7. No node name contains reserved characters (`:`, `->`, `~>`, `[`, `]`, `#`)

A `.ctx` file is **well-formed** (valid + best practices) if it additionally:

8. Has `@entry` on at least one node (or the folder has no clear entry point)
9. Uses collapse syntax for groups of 6+ similar nodes
10. Includes drill-down references for all child directories that have their own `.ctx` files
11. Has a `last-verified` date within 30 days of the current date

---

## 13. Migration from .mmd

To convert an existing Mermaid `.mmd` file to `.ctx`:

### 13.1 What to Drop

| Mermaid syntax | Action |
|---|---|
| `graph TD` / `graph LR` | Drop — `.ctx` has no direction directive |
| `classDef name fill:... stroke:... color:...` | Drop — visual styling |
| `class node1,node2 className` | Drop — replace with `[type]` tags on each node |
| `["<b>Name</b><br/>desc"]` | Convert to `Name : desc [type]` |
| `[("cylinder label")]` | Convert to `name : label [store]` |
| `subgraph name["label"]` ... `end` | Convert to `## label` or `### label` |
| `end` | Drop — grouping is by indentation |
| `-->` | Convert to `->` (inline under source node) |
| `-.->` | Convert to `~>` (inline under source node) |
| `-->|"label"|` | Convert to `-> target "label"` |
| `%% comment` | Convert to `# comment` |
| `:::className` | Drop |

### 13.2 What to Add

| `.ctx` feature | Source |
|---|---|
| `# format: ctx/1.0` | New — add to header |
| `# edges:` legend | New — add to header |
| `[type]` tags | Derive from Mermaid `class` assignments or infer from context |
| `@entry` marker | Identify from the architecture (root component, main server) |
| Drill-down references | Add for child directories that have their own `.ctx` files |
| Collapse syntax | Apply to groups of 6+ similar nodes |

---

## 14. Versioning

The format version follows `major.minor`:
- **Major** increments indicate breaking changes (new required fields, changed edge semantics)
- **Minor** increments indicate additive changes (new optional markers, new type tags)

v1.0 is the initial release. The `# format: ctx/1.0` header ensures forward compatibility — future parsers can detect and handle older format versions.

### 14.1 Reserved for v2.0

The following features are reserved for future versions:
- `@path` inline file path annotations
- Additional edge types beyond `->` and `~>`
- Conditional/optional edge markers (`->?`)
- Critical-path edge markers (`->!`)
- Weighted edges for dependency importance

---

## 15. Examples

### 15.1 Minimal .ctx File

```
# utils/ — Utility Functions
# format: ctx/1.0
# last-verified: 2026-03-26
# edges: -> call/render | ~> subscribe/read

## Utils
  formatDate  : Date formatting helpers [lib]
  parseConfig : Config file parser [lib] -> validateSchema
  validateSchema : Zod schema validator [lib]
```

### 15.2 Full .ctx File (src/)

```
# src/ — Context Map
# format: ctx/1.0
# last-verified: 2026-03-26
# nodes: 42 | edges: 54 | groups: 7
# edges: -> call/render | ~> subscribe/read

## app/ — Routes
  layout          : Root HTML, fonts, metadata [root] @entry
    -> home
  home            : Home — TabBar + tabs [screen]
    -> TabBar, TabContainer, ChatPanel
  dashboard/page  : /dashboard route [screen]
    -> DashboardShell
  game/page       : /game route [screen]
    -> GameShell
  su/page         : /su route [screen]
    -> SUShell
  docs/page       : /docs route [screen]

## components/ — UI -> components/components.ctx
  ### Chat Interface (13)
    ChatPanel     : Chat orchestrator [component]
      -> VoiceOrb, ChatInput, ariaSingleton
      ~> chatStore
    VoiceOrb      : 5-state voice button [component]
      ~> chatStore
    ChatInput     : Text + slash commands [component]
    TabBar        : Top navigation [component]
    TabContainer  : Lazy tab router [component]
      -> SdkDashboard, StorePage, RoadmapPage
  ### game/ (46) -> components/game/game.ctx
    GameShell     : Game orchestrator [component]
      -> gameAdapter
      ~> gameStore
  ### dashboard/ (9)
    DashboardShell : 6-tab clinical panel [component]
      -> backend
      ~> dashStore
  ### su/ (3)
    SUShell       : Visual canvas shell [component]
      -> AriaEngine, SUPersona
      ~> labStore
  ### sdk/ (5)
    SdkDashboard  : SDK dev tools [component]
  ### store/ (8)
    StorePage     : E-commerce shell [component]
      ~> cartStore
  ### roadmap/ (1)
    RoadmapPage   : Project roadmap [component]

## lib/ — Core Engine -> lib/lib.ctx
  ### aria-core/ — Framework
    AriaCore      : Main orchestrator [lib]
      -> GeminiLive, NLKE, StateMachine, ContextEngine, CommandRouter, AudioPipeline
    GeminiLive    : WebSocket provider [lib] -> geminiAPI
    NLKE          : Knowledge engine [lib]
    StateMachine  : Connection states [lib]
    ContextEngine : Prompt assembly [lib]
    CommandRouter : Function dispatch [lib]
    AudioPipeline : Mic to PCM to playback [lib]
  ### App Wiring
    ariaSingleton : App singleton [lib]
      -> AriaCore, dbSqlite, sessionAdapter, kgAdapter, memoryInjector
      ~> chatStore
    dbSqlite      : SQLite WASM [lib] ~> sqliteTypes
    sessionAdapter : Session persistence [lib]
    kgAdapter     : KG persistence [lib]
    memoryInjector : NLKE to prompt [lib]
  ### Game Layer
    gameAdapter   : 23 voice functions [lib]
      -> gameApi
      ~> gameStore, gameTypes
    gameApi       : Backend fetch wrapper [lib] -> backend
    logicEngine   : 7 block types [lib]
  ### Voice Engines
    AriaEngine    : Domain-agnostic voice [lib]
    SUPersona     : ~95 voice functions [lib]
  localAria       : FunctionGemma on-device [lib]

## store/ — Zustand State (14) -> store/store.ctx
  chatStore       : Messages, voice status [store]
  gameStore       : Screens, config, stats [store] ~> gameTypes
  dashStore       : Mood, flags, notes [store] ~> dashTypes
  labStore        : Logic editor canvas [store]
  cartStore       : Shopping cart [store]
  ... (9)         : tab, ariaMode, gameVoice, gameTheme, transcript, devLog, products, kg, sdk [store]

## types/ — Shared Types (3) -> types/types.ctx
  gameTypes       : Game engine types [type]
  dashTypes       : Dashboard types [type]
  sqliteTypes     : SQLite WASM ambient [type]

## External
  backend         : Python Backend — Game, Dashboard, NAI APIs [ext]
  geminiAPI       : Gemini Live API — WebSocket streaming [ext]
```

### 15.3 Root-Level .ctx with Collapsed Children

```
# aria-personal/ — Project Root
# format: ctx/1.0
# last-verified: 2026-03-26
# edges: -> call/render | ~> subscribe/read

## Source
  SRC             : 188 files — Next.js frontend [dir] -> src/src.ctx
  BACKEND         : 145 files — FastAPI backend [dir] -> backend/backend.ctx

## Config
  package.json    : Project manifest — next 15, react 19, zustand 5 [config] @entry
  next.config.ts  : API proxy to :8095, COOP/COEP headers [config]
    -> SRC
    -> BACKEND "proxy /api/*"
  tailwind.config.ts : Dark theme — aria purple, gold accents [config] -> SRC
  tsconfig.json   : Strict TS, bundler resolution, @/* alias [config] -> SRC

## Support
  DOCS            : 28 files — research, plans, therapy KB [dir] -> docs/docs.ctx
  DATA            : 6 files — FunctionGemma training data [dir] -> data/data.ctx
  SCRIPTS         : 5 files — FunctionGemma utilities [dir] -> scripts/scripts.ctx
  CTX_PACKETS     : 10 files — session continuity [dir] -> context-packets/context-packets.ctx

## External
  geminiAPI       : Gemini Live API — WebSocket streaming [ext]
  huggingface     : HuggingFace Hub — model hosting [ext]
```

---

## 16. Design Rationale

### 16.1 Why Not Mermaid?

Mermaid was the predecessor format. It works because LLMs are pre-trained on it, but it carries rendering baggage:
- `classDef`/`class` CSS directives (~200 tokens wasted per file)
- HTML tags in node labels (`<b>`, `<br/>`) (~100+ tokens wasted)
- `subgraph`/`end` bracket syntax (verbose for grouping)
- Arrow rendering distinctions (`-->` vs `-.->`) that could be simpler

The `.ctx` format achieves **45-61% token reduction** over equivalent Mermaid while preserving all semantic information.

### 16.2 Why Not JSONL?

JSONL has excellent lazy-loading properties (line-level independence) but:
- JSON syntax is verbose for expressing relationships (lots of quotes, braces)
- LLMs reconstruct graph structure less naturally from flat records than from a visual-ish notation
- The `name : desc [type]` + `-> target` syntax is more scannable for both humans and LLMs

### 16.3 Why Not YAML?

YAML is structured and LLM-friendly but:
- Not lazy-loadable (requires full parse)
- Indentation-sensitive in fragile ways (wrong indent = wrong semantics)
- Verbose for graph edges (nested arrays of objects)

### 16.4 Why Inline Edges?

The prototype used a separate edges section (nodes first, then all edges). This was changed because:
- Separate sections force two-pass reading (nodes, then edges, cross-referencing by name)
- Inline edges make the file **single-pass** — each node is self-contained
- Inline edges eliminate repeated node names (the source name appears once, not once in the node section and N times in the edges section)
- Inline edges reduce total file size by ~15-25%

### 16.5 Why Exactly Two Edge Types?

Two types is the minimum set that captures the fundamental distinction in software architecture:
- **Direct dependencies** (`->`): if B changes its API, A must change. Build-time coupling.
- **Reactive dependencies** (`~>`): A reads B's output. B doesn't know A exists. Runtime coupling.

Additional types (optional, critical, re-export) were considered and deferred to v2. Each additional type increases cognitive load for every reader of every `.ctx` file. The two-type system covers 95%+ of real-world relationships.

---

## Appendix A: Token Efficiency Comparison

Measured on the `src/` folder of the aria-personal project:

| Format | Lines | Chars | Est. Tokens | vs .mmd |
|---|---|---|---|---|
| Mermaid (.mmd) | 168 | 7,098 | ~1,774 | baseline |
| .ctx v1 (separate edges) | 134 | 3,912 | ~978 | -45% |
| .ctx v2 (inline edges) | ~95 | ~2,800 | ~700 | -61% |

Token savings come from:
- Dropping CSS/styling directives: ~200 tokens
- Dropping HTML tags: ~140 tokens
- Dropping `subgraph`/`end` syntax: ~80 tokens
- Inline edges eliminating repeated names: ~200 tokens
- Simpler edge syntax (`->` vs `-->`): ~50 tokens
- Markdown headings vs `subgraph["label"]`: ~50 tokens

---

## Appendix B: Staleness Enforcement

`.ctx` files include `# last-verified: YYYY-MM-DD` for staleness detection. The recommended enforcement mechanism is a two-layer system:

1. **Hook layer (fast gate):** A PreToolUse hook on file reads that compares the `last-verified` date against file modification timestamps. Fires on every read of a `.ctx` file, costs <5ms (using `jq` for JSON parsing).

2. **Script layer (deep audit):** An on-demand script that parses the node definitions in `.ctx` files and compares against actual files on disk. Reports new/missing files and days since last verification.

See the project's `scripts/check-doc-staleness.py` and `scripts/doc-staleness-hook.sh` for reference implementations.
