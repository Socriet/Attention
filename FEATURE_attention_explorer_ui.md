# Feature: Attention Explorer UI

**Branch:** `feature/attention-explorer-ui`
**Type:** Complex feature
**Developed with:** Claude (Anthropic)

## What it does

A desktop application (`ui.py`) that lets you run the model and explore its
attention diagrams without using the terminal.

- **Run bar:** type a sentence containing `[MASK]` and run `mask.py`.
- **Log panel:** shows the program's output (the 3 predictions and any error).
- **Run explorer:** lists every folder in `outputs/` with its number of PNGs,
  newest first. Runs can be renamed, deleted (with confirmation) or opened in
  the system file explorer.
- **Diagram viewer:** shows the diagram for any layer (1-12) and head (1-12),
  scaled to fit the window.
- **Quick-jump buttons:** go straight to notable heads (Layer 2 Head 1,
  Layer 4 Head 2, Layer 3 Head 10).

## How it works

- Built with Tkinter. If `customtkinter` is installed, the window uses its
  dark theme; otherwise it falls back to standard `ttk` widgets.
- `mask.py` is launched with `subprocess.Popen` in a background daemon thread,
  with the sentence sent through stdin. The UI stays responsive, and the result
  is handed back to the main thread with `self.after(0, ...)`.
- It depends on the `outputs/<timestamp>/` folders produced by the
  [timestamped outputs](FEATURE_timestamped_outputs.md) feature.
- Images are loaded with Pillow and redrawn when the window is resized.

## How to run

```bash
pip install -r requirements.txt
python ui.py
```

`customtkinter` is optional.

## How to test

1. Run `python ui.py`.
2. Enter `The [MASK] jumped over the lazy dog.` and click **Run mask.py**.
3. Wait for the status to change to `Done!`. The new run should appear at the
   top of the list and its diagram should be displayed.
4. Change the layer and head, or use a quick-jump button, and check that the
   image changes.
5. Rename a run, then delete it, and check that the list updates.
6. Run it with a sentence without `[MASK]` and check that a warning appears.

## AI usage

**Prompt:** The exact wording was not saved. The request was for a graphical
interface to run `mask.py` and browse the generated attention diagrams.

**Output (summary):** Claude produced `ui.py` with the features above.
[FILL IN: any changes you made by hand afterwards.]

## Limitations

- The layer and head ranges are fixed at 12, which matches `bert-base-uncased`.
- Deleting a run is permanent, although the UI asks for confirmation first.
- Opening the file explorer uses `os.startfile` on Windows, `open` on macOS and
  `xdg-open` on Linux.
- [FILL IN: add a screenshot, e.g. `docs/ui.png`.]
