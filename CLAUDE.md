# CNN Prediction Based Reversible Data Hiding

## Project Overview

Implementation of CNN-based predictor (CNNP) for reversible data hiding, based on:
> R. Hu and S. Xiang, "CNN Prediction Based Reversible Data Hiding," IEEE Signal Processing Letters, vol. 28, pp. 464-468, 2021.

The project embeds secret data into grayscale images and measures image quality via PSNR. It supports two embedding modes: histogram shifting and expansion embedding.

## Environment

- Python 3.7
- PyTorch 1.6.0
- MATLAB 2019a (required — `matlab.engine` is called at runtime)
- OpenCV (`cv2`)
- Windows 10 (original dev environment; Windows 11 also in use)

## Project Structure

```
main.py                  # Entry point; argument parsing, per-image PSNR calculation
utils.py                 # load_model, parse_sample, cnn_histogram_shifting, cnn_expansion
model/
  cnnp.py                # CNNP architecture (multi-scale conv + residual fusion)
  predict_model.py       # PredictModel wrapper (eval/inference only)
model_parameter/
  model_state.pth        # Pre-trained weights (loaded via torch.load)
standard_test_images/    # Barbara, Lena, Peppers, yacht (512×512 BMP)
cnn_histogram_shifting.m # MATLAB embedding logic for histogram shifting
cnn_expansion.m          # MATLAB embedding logic for expansion embedding
calculate_complexity.m   # MATLAB utility
calculate_tp_tn.m        # MATLAB utility
num2bitlist.m            # MATLAB utility
```

## Running the Project

```bash
# Histogram shifting
python main.py -size 512 512 -model ./model_parameter/model_state.pth \n  -folder ./standard_test_images -mode histogram_shifting -length 10000

# Expansion embedding
python main.py -size 512 512 -model ./model_parameter/model_state.pth \n  -folder ./standard_test_images -mode expansion_embedding -length 10000
```

## Key Design Notes

- Images are resized to 512×512 and converted to grayscale before processing.
- The checkerboard sampling strategy (`parse_sample`) splits pixels into two interleaved sets (even/odd by `(i+j) % 2`); each half is processed independently.
- The CNNP predicts pixel values using three parallel conv branches (kernel sizes 3, 5, 7) with residual fusion; output is a single-channel prediction map.
- The Python side handles CNN inference; the MATLAB engine handles the actual embedding (histogram shifting / expansion embedding) via `matlab.engine`.
- `np.float` is deprecated in NumPy >= 1.20. Use `float` or `np.float64` if upgrading NumPy.

## Known Compatibility Issues

- `np.float` (used in `main.py` and `utils.py`) is removed in NumPy 1.24+. Replace with `np.float64`.
- `torch.load` without `weights_only=True` will warn in PyTorch 2.x.
- MATLAB Engine for Python must be installed separately from the MATLAB installation.
