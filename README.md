# BioMedAgent — Reproduction

> Reproduction of **"Empowering AI data scientists using a multi-agent LLM framework with self-evolving capabilities for autonomous, tool-aware biomedical data analyses"**  
> Published in *Nature Biomedical Engineering*, 2026. DOI: [10.1038/s41551-026-01634-6](https://doi.org/10.1038/s41551-026-01634-6)  
> Original repository: [BOBQWERA/BioMedAgent](https://github.com/BOBQWERA/BioMedAgent)

---

## What is BioMedAgent?

BioMedAgent is an autonomous biomedical data analysis framework driven by a pipeline of 13 LLM-powered agents. It accepts natural language task descriptions and biomedical data files as input, automatically designs a multi-step workflow, generates and executes code, self-corrects on failure, and produces a structured analysis report.

**Key capabilities:**
- Natural language task initiation — no programming required from the user
- 13 specialized agents collaborating in a fixed pipeline (Linguist → PromptEngineer → ToolScorer → WorkflowDesigner → Programmer → SummaryAnalyst, etc.)
- Interactive Exploration (IE): automatic error detection and code self-correction
- Memory Retrieval (MR): semantic retrieval of past successful experiences to guide new tasks
- Extensible tool ecosystem: drop documentation + code into `tool/` and agents discover it automatically

**Benchmark:** BioMed-AQA (327 curated biomedical questions across 5 categories) — achieved **77% success rate**, outperforming GPT-4o web agents at 47%.

![fig1](asserts/fig1.png)
![fig2](asserts/fig2.png)

---

## Architecture Overview

```
User Input (natural language + data files)
        ↓
┌─────────────────────────────────────┐
│     13-Agent Sequential Pipeline    │
│                                     │
│  Linguist → Translator              │
│  → PromptEngineer → FileAnalyst     │
│  → ToolScorer → ToolDescriptor      │
│  → ToolReScorer → WorkflowDesigner  │
│  → ToolAnalyst → WorkflowFormatter  │
│  → ActionDesigner → Programmer      │
│  → SummaryAnalyst                   │
│                                     │
│  (each agent communicates via Redis)│
└─────────────────────────────────────┘
        ↓
Output Files + Analysis Report
```

All agents call GPT-4o-mini via the OpenAI API. Redis is used as the message broker between agents and background servers (GPT server, Code Executor). No model training is required.

---

## Reproduction Notes

This repo is a reproduction of the original work, tested on **macOS (Apple Silicon, arm64) with Python 3.9** and no Homebrew. Three bugs were identified and fixed compared to the original repository:

| File | Bug | Fix |
|------|-----|-----|
| `server/gpt.py` | Default `OPENAI_BASE_URL` missing `/chat/completions` suffix | Append suffix dynamically |
| `server/code_executor.py` | `tool/code` relative path broken after `os.chdir()` | Convert to absolute path at init |
| `scripts/component.py` | `task_path` relative path causes failures in multi-stage execution | Use `os.path.abspath()` |

Two utility scripts were added:
- `run.sh` — one-command startup with environment checks
- `view_results.py` — browse and preview outputs from completed tasks

---

## Quickstart

### 1. Clone this repo

```bash
git clone https://github.com/JINGEWU/BioMedAgent.git
cd BioMedAgent
```

### 2. Install Redis

Redis is required as the message broker between agents.

```bash
# macOS with Homebrew
brew install redis && brew services start redis

# macOS without Homebrew (compile from source)
cd /tmp
curl -fsSL https://download.redis.io/redis-stable.tar.gz | tar xz
cd redis-stable && make -j4
src/redis-server --daemonize yes

# Ubuntu / Debian
sudo apt install redis-server && sudo systemctl start redis
```

Verify Redis is running:
```bash
redis-cli ping   # should return PONG
```

### 3. Create a Python environment

Python 3.9 or 3.10 is recommended.

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
pip install colorama            # missing from requirements.txt in the original repo
```

### 4. Set your OpenAI API Key

```bash
export OPENAI_API_KEY="sk-your-key-here"
# Windows: set OPENAI_API_KEY=sk-your-key-here
```

### 5. Run a demo task

```bash
# Using the wrapper script (macOS / Linux)
./run.sh machine_learning

# Or directly
python demo.py --task machine_learning
```

Available tasks:

| Task | Description | Requires Docker? |
|------|-------------|-----------------|
| `machine_learning` | SVD dimensionality reduction on heart disease dataset | No |
| `statistics_qq_plot` | QQ plot + KS test between two treatment groups | No |
| `visualization_violin_plot` | Violin plot of WBC distribution by age/gender | No |
| `statistics_t_test` | Independent samples t-test on biomarker data | Yes (`bio_r` image) |
| `visualization_survival_plot` | Kaplan-Meier survival curve | Yes (`bio_r` image) |
| `omics` | CEL microarray to gene expression matrix | Yes (`biogpt_r` image) |

Docker images for `bio_r` and `biogpt_r` are available via the original repository's Baidu Drive links.

### 6. View results

```bash
# List all completed tasks
python view_results.py

# Preview the most recent task's output files
python view_results.py -n 1

# Preview the second most recent
python view_results.py -n 2
```

Output files are saved to `task/<year>-<month>/<day>/<task-id>/`.

---

## How to Use Your Own Data

Edit the `question_info` dictionary in `demo.py`:

```python
question_info = {
    "question": "I have a dataset {your_data.csv}. Please perform PCA and visualize the first two components.",
    "files": [
        {"name": "your_data.csv", "path": "data/your_data.csv"}
    ]
}
```

Place your data file under the `data/` directory and run `python demo.py`.

---

## Extending the Tool Library

BioMedAgent auto-discovers tools from the `tool/` directory. To add a new tool:

1. Add a documentation file to `tool/doc/<tool_name>`
2. Add the corresponding code to `tool/code/<tool_name>`

Agents will automatically score and use the new tool when relevant. The full 65-tool configuration from the paper is documented in `tool_info.json`.

---

## Evaluating Output Correctness

BioMedAgent uses three layers of quality checking:

1. **Execution layer** — each code stage returns `True/False` from a test function
2. **Code review layer** — a Code Reviewer Agent inspects the logic before execution
3. **Semantic scoring layer** — the paper's BioMed-AQA benchmark compares system output summaries against manually annotated ground truth answers using an AutoScoring Agent (GPT-based semantic matching)

Note: a `True` execution result only guarantees the code ran without error, not that the numerical output is correct. End-to-end data flow between stages should be manually verified for critical analyses.

---

## Project Structure

```
BioMedAgent/
├── agent.py               # All 13 agent class definitions
├── demo.py                # Demo entry point
├── config.py              # Redis keys, model names, thresholds
├── utils.py               # Helpers (colorama printing, task ID generation)
├── run.sh                 # One-command startup script (added in reproduction)
├── view_results.py        # Task output browser (added in reproduction)
├── tool_info.json         # Documentation for all 65 tools
├── requirements.txt       # Python dependencies
├── data/                  # Sample datasets for demo tasks
├── tool/
│   ├── doc/               # Tool documentation files (runtime-loaded)
│   └── code/              # Tool code files (injected into executed code)
├── scripts/
│   ├── prompt.py          # All agent system prompts
│   ├── chat.py            # LLM chat session management
│   ├── llm.py             # LLM call / Redis task push
│   ├── component.py       # Task, Status, ToolManager classes
│   ├── executor.py        # Code execution task push
│   └── bot.py             # Auxiliary agents (RequestAnalyst, etc.)
├── server/
│   ├── gpt.py             # GPT API background server
│   ├── code_executor.py   # Code execution background server
│   ├── base.py            # Base server class
│   └── memory_server.py   # Memory retrieval server (BCEmbedding)
└── lab/
    ├── memory_retriever.py # Memory retrieval client
    └── memory.py           # Memory saving agents
```

---

## Citation

If you use this work, please cite the original paper:

```bibtex
@article{bu2026biomedagent,
  title     = {Empowering AI data scientists using a multi-agent LLM framework with 
               self-evolving capabilities for autonomous, tool-aware biomedical data analyses},
  author    = {Bu, Dechao and Sun, Jingbo and Li, Kun and others},
  journal   = {Nature Biomedical Engineering},
  year      = {2026},
  doi       = {10.1038/s41551-026-01634-6}
}
```

---

## Updates

- 2026-04-07: Reproduction on macOS (Python 3.9, no Homebrew). Fixed 3 bugs, added `run.sh` and `view_results.py`.
- 2025-02-27: Original demo added (machine learning, statistics, visualization, omics).
