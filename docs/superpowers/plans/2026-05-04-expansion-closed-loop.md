# Expansion Embedding Closed Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a runnable `expansion_embedding` closed loop for embedding, extracting, recovering, and verifying secret text in grayscale carrier images.

**Architecture:** Keep the existing embedding algorithm intact. Add a MATLAB inverse for one expansion stage, then expose a Python wrapper and CLI that run the two-stage reverse path in parity order `1 -> 0`.

**Tech Stack:** Python, NumPy, OpenCV, PyTorch, MATLAB Engine, existing CNNP model.

---

### Task 1: Bit Helpers

**Files:**
- Create: `rdh_bits.py`
- Test: `tests/test_expansion_closed_loop.py`

- [ ] Add tests for UTF-8 text to bits and back.
- [ ] Implement `text_to_bits`, `bits_to_text`, `ensure_even_bit_count`, and bit-list normalization.
- [ ] Run `python -m unittest tests.test_expansion_closed_loop -v`.

### Task 2: MATLAB Stage Extraction

**Files:**
- Create: `cnn_expansion_extract.m`

- [ ] Mirror `cnn_expansion.m` metadata layout.
- [ ] Read tail LSB metadata.
- [ ] Decode location map with MATLAB `arithdeco`.
- [ ] Extract message bits and restore expanded pixels.
- [ ] Restore saved tail LSBs.

### Task 3: Python Runtime Wrapper

**Files:**
- Create: `expansion_closed_loop.py`
- Test: `tests/test_expansion_closed_loop.py`

- [ ] Add tests that fake the stage extractor and assert reverse order `1 -> 0`.
- [ ] Implement image normalization, model loading, prediction, embedding, extraction, and verification helpers.
- [ ] Save watermarked and recovered images with lossless encoding.

### Task 4: CLI

**Files:**
- Create: `rdh_cli.py`

- [ ] Add `embed`, `extract`, and `verify` subcommands.
- [ ] Wire CLI arguments to `expansion_closed_loop.py`.
- [ ] Print concise JSON summaries for outputs and verification results.

### Task 5: GUI Closed Loop

**Files:**
- Modify: `gui/config.py`
- Modify: `gui/workers.py`
- Modify: `gui/labels.py`
- Modify: `gui/app.py`
- Test: `tests/test_gui_config.py`
- Test: `tests/test_gui_workers.py`
- Test: `tests/test_gui_labels.py`

- [ ] Add a separate `扩展嵌入闭环` tab.
- [ ] Let the user choose carrier image, model file, output folder, and secret text.
- [ ] Run embed, extract, recover, and verify from a background worker.
- [ ] Log extracted text, output paths, and verification results.

### Task 6: Final Verification

**Files:**
- Test: `tests/test_expansion_closed_loop.py`

- [ ] Run targeted unit tests.
- [ ] Run the full existing unit test suite if dependencies allow.
- [ ] If MATLAB Engine is unavailable in the current sandbox, report that real image smoke verification must be run in the configured `cnnp2021_run` environment.
