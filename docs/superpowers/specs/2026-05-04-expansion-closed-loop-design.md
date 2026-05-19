# Expansion Embedding Closed Loop Design

## Goal

Add a runnable closed loop for `expansion_embedding`: read a carrier image, embed user-provided secret text, save a watermarked image, read that watermarked image, extract the secret text, recover the original carrier matrix, and verify both message and image recovery.

## Scope

- Implement only `expansion_embedding`.
- Treat the recoverable carrier as the 8-bit grayscale image matrix used by the embedding algorithm.
- Use lossless output formats only, such as BMP or PNG.
- Keep the existing batch PSNR/SSIM experiment flow unchanged.

## Approach

The existing embedding path already calls MATLAB `cnn_expansion.m` twice, once for each checkerboard parity. The new extraction path reverses that order:

1. Reverse parity `1` from the final watermarked image.
2. Reverse parity `0` from the intermediate image.
3. Concatenate the recovered payload bits from parity `0` and parity `1`.
4. Decode payload bits as UTF-8 text.

Each stage reads the metadata stored in the tail LSB positions, restores expanded pixels by reversing `D = 2 * d + b`, restores the saved tail LSBs, and returns the payload bits embedded in that stage.

## Components

- `cnn_expansion_extract.m`: MATLAB inverse for one expansion embedding stage.
- `rdh_bits.py`: small Python helpers for text/bit conversion.
- `expansion_closed_loop.py`: Python runtime wrapper for embed, extract, and verify.
- `rdh_cli.py`: command-line entry point.
- `gui/`: add a separate Tkinter tab for running the expansion closed loop from the desktop UI.
- `tests/test_expansion_closed_loop.py`: unit tests for pure Python boundaries and stage ordering.
- `tests/test_gui_config.py`, `tests/test_gui_workers.py`, and `tests/test_gui_labels.py`: GUI-facing tests for paths, worker orchestration, and labels.

## Verification

- Unit tests must cover text-to-bit round trip, even-bit validation, reverse stage ordering, and verification result calculation.
- GUI tests must cover closed-loop path generation, worker orchestration, and visible Chinese labels.
- Real MATLAB/CNN smoke verification should be run in the compatible local environment when MATLAB Engine and model dependencies are available.
