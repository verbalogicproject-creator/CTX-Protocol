# CTX Protocol: The AI-Native Context Management System

> **Stop copy-pasting your code. Start injecting architecture.**
> A deterministic, lazy-loading documentation layer designed for LLM-assisted development.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

---

## 🚀 The Problem
Current AI coding assistants (Claude, ChatGPT, Gemini) suffer from two major flaws when working on large codebases:

1.  **The Context Trap:** You paste 50 files into a chat. 40% of those tokens are "noise" (visual formatting, boilerplate, irrelevant functions). The AI gets "lost" in the details and loses the big picture.
2.  **The Hallucination Gap:** Documentation (READMEs) is prose written for humans. It drifts away from the code. If the AI reads a stale README, it confidently suggests code that will never work.

## 💡 The Solution: CTX Protocol
CTX Protocol is a **deterministic, machine-optimized documentation layer** that lives alongside your code. It decouples **"Documentation for Humans"** (Prose) from **"Context for AI"** (Topology).

### The Three Pillars
*   **1. Semantic Precision (.ctx format):** A machine-optimized topology notation. While inspired by visual formats like Mermaid, `.ctx` strips away human-centric rendering baggage to provide a pure, high-density architectural signal for LLM reasoning.
*   **2. Deterministic Lazy Loading:** A hierarchical "routing" system that lets the AI "walk" your codebase on demand. By loading context only at the relevant abstraction layer, it prevents context-window exhaustion and maintains focus.
*   **3. The Shadow Auditor:** A Git-enforced verification layer. If your code changes but your context doesn't, the commit is blocked. This guarantees that the AI’s "Map" is always 100% faithful to the "Territory."

---

## 🛠 How It Works

CTX Protocol uses a **3-file-per-folder** structure:

1.  **`start-here.md` (The Router):** A human-readable index. "What's in this folder and where do I look next?"
2.  **`{folder}.ctx` (The Architecture):** An AI-optimized topology. Nodes (components), Edges (relationships), and Groups (layers).
3.  **`{folder}.md` (The Reference):** Detailed prose and HTML anchors for O(1) specific lookup.

### Example .ctx file:
```
# auth/ — Authentication Layer
# format: ctx/1.0
# last-verified: 2026-04-11
# edges: -> call | ~> subscribe | => API

## Components
  LoginButton  : Trigger for OAuth flow [component]
    -> AuthService
  AuthService  : JWT + OAuth orchestrator [service] @entry
    ~> authStore
    => /api/auth/login

## State
  authStore    : User session state [store]
```

---

## 📦 Key Features

*   **LLM-Agnostic:** Works perfectly with Claude Code, Gemini, ChatGPT, and local models (Llama 3, Mistral).
*   **Zero Drift:** The **Shadow Auditor** ensures your `.ctx` files are 100% accurate before you commit.
*   **Language Independent:** Works for Python, TypeScript, Rust, Go, or any project structure.
*   **Massive Token Savings:** Typical reductions of **40-60%** compared to Mermaid-based documentation.

---

## 🏁 Quick Start (in 30 seconds)

1.  **Clone the scripts** into your project.
2.  **Run the Generator:**
    ```bash
    python3 scripts/generate_basic_ctx.py --root .
    ```
3.  **Install the Auditor Hook:**
    ```bash
    ./scripts/install-ctx-git-hook.sh
    ```
4.  **Tell your AI:** "Read `start-here.md` to understand our architecture."

---

## 📈 Why use this?

### For Beginners: "The Magic Map"
Stop trying to explain your project to the AI. Drop CTX files in, and the AI acts like it’s been your lead architect for years. It knows where every file is and how they connect.

### For Professionals: "Architectural Integrity"
Maintain a high-fidelity "Architectural State" for your project. Use the **Shadow Auditor** to catch missing files or ghost dependencies during CI/CD.

---

## 📜 License
MIT - Created by Eyal Nof.

---

**Star this repo to support AI-Native Development! ⭐**
to support AI-Native Development! ⭐**
