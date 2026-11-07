# Feature: Timestamped Outputs

**Branch:** `feature/timestamped-outputs`
**Type:** Simple feature
**Developed with:** [FILL IN: AI tool used, e.g. Claude]

## What it does

Each run of `mask.py` now saves its 144 attention diagrams in its own folder,
`outputs/<YYYY-MM-DD_HH-MM-SS>/`, instead of writing them to the working
directory. The path of the folder is printed when the diagrams are generated.

## Why

Previously every run overwrote the `Attention_Layer*_Head*.png` files of the
previous run, so results from different sentences could not be compared or
kept.

## How it works

- `visualize_attentions` creates the folder
  `BASE_DIR / "outputs" / <timestamp>` and prints its path.
- The folder is passed to `generate_diagram` through the new optional
  `output_dir` parameter.
- If `output_dir` is not given, `generate_diagram` falls back to `BASE_DIR`,
  so existing callers keep working.
- `outputs/` is listed in `.gitignore`.

## How to test

```bash
python mask.py
```

```
Text: We turned down a narrow lane and passed by a small [MASK].
```

Check that:

1. The terminal prints `Saving attention diagrams to: .../outputs/<timestamp>`.
2. That folder contains 144 files named `Attention_Layer{N}_Head{M}.png`.
3. Running the program a second time creates a second folder and leaves the
   first one untouched.

## AI usage

**Prompt:** [FILL IN the real prompt, or: The exact wording was not saved. The
request was to save each run's diagrams in a separate timestamped folder.]

**Output (summary):** the `datetime`-based folder creation in
`visualize_attentions` and the `output_dir` parameter in `generate_diagram`.

## Limitations

- The folder is created next to `mask.py`, not in the current directory.
- Diagrams are no longer written to the working directory. [FILL IN: note the
  result of running `check50` with this change.]
