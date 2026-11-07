# Attention — BERT Masked Language Model

## Introduction

This project was developed for the Artificial Intelligence course. It uses
the pre-trained `bert-base-uncased` model to predict a masked word in a
sentence and to visualize the model's self-attention scores.

Given a sentence containing the `[MASK]` token, the program:

1. Predicts the 3 most likely words to fill the mask.
2. Generates one diagram per attention layer and head (12 layers x 12 heads
   = 144 diagrams), where lighter cells mean higher attention.

## Description

### Core functionality (`mask.py`)

| Function | Purpose |
|---|---|
| `get_mask_token_index` | Finds the position of the `[MASK]` token in the input |
| `get_color_for_attention_score` | Maps an attention score in [0, 1] to a shade of gray in [0, 255] |
| `visualize_attentions` | Generates a diagram for every layer and head |
| `generate_diagram` | Draws and saves the diagram for a single head |

Additional improvements:

- Font path resolved relative to the script, with a default-font fallback.
- TensorFlow and `transformers` log output silenced for cleaner terminal output.
- Diagrams saved in `outputs/<timestamp>/` (see `FEATURE_timestamped_outputs.md`).

### Extra features

| Feature | Branch | Documentation |
|---|---|---|
| Timestamped output folders | `feature/timestamped-outputs` | `FEATURE_timestamped_outputs.md` |
| Attention Explorer UI | `feature/attention-explorer-ui` | `FEATURE_attention_explorer_ui.md` |

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Command line:

```bash
python mask.py
```

```
Text: We turned down a narrow lane and passed by a small [MASK].
```

Graphical interface:

```bash
python ui.py
```

## Project structure

```
.
├── mask.py                          # Main program
├── ui.py                            # Attention Explorer UI
├── assets/fonts/OpenSans-Regular.ttf
├── outputs/                         # Generated diagrams (git-ignored)
├── requirements.txt
├── README.md
├── FEATURE_timestamped_outputs.md
└── FEATURE_attention_explorer_ui.md
```

## AI tools used

| Tool | Used for |
|---|---|
| Claude (Anthropic) | Developing the Attention Explorer UI (`ui.py`), guidance on removing the unwanted extra terminal output (TensorFlow/oneDNN and `transformers` logs), guidance on the Git workflow (branches and conventional commits), and drafting this README |
| Gemini (Google) | Developing this README, general debugging |

All AI-generated code was reviewed, run and tested by me before being committed.

## Git workflow

Development followed a feature-branch workflow with Conventional Commits
(`feat:`, `fix:`, `docs:`, `style:`, `chore:`), and each branch was merged
into `main` through a Pull Request.