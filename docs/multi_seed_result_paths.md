# 多随机种子增强实验文件路径说明

本文档用于集中记录本次 `8` 图 × `3` 随机种子增强实验的关键文件及其绝对路径。

## 1. 聚合结果文件

### 总体汇总表

用途：

- 按 `mode + payload` 聚合
- 包含 `平均值 ± 标准差`
- 可直接用于论文总表

绝对路径：

`D:\CNN-Prediction-Based-Reversible-Data-Hiding-main\results\multi_seed_8img\aggregated\mode_payload_summary.csv`

### 单图稳定性汇总表

用途：

- 按 `mode + payload + image` 聚合
- 用于分析不同图像的波动情况

绝对路径：

`D:\CNN-Prediction-Based-Reversible-Data-Hiding-main\results\multi_seed_8img\aggregated\mode_payload_image_summary.csv`

### 随机种子来源清单

用途：

- 记录本次聚合到底使用了哪些种子结果文件

绝对路径：

`D:\CNN-Prediction-Based-Reversible-Data-Hiding-main\results\multi_seed_8img\aggregated\seed_sources.csv`

## 2. 各随机种子结果目录

### 种子 20260406

绝对路径：

`D:\CNN-Prediction-Based-Reversible-Data-Hiding-main\results\multi_seed_8img\seed_20260406`

### 种子 20260407

绝对路径：

`D:\CNN-Prediction-Based-Reversible-Data-Hiding-main\results\multi_seed_8img\seed_20260407`

### 种子 20260408

绝对路径：

`D:\CNN-Prediction-Based-Reversible-Data-Hiding-main\results\multi_seed_8img\seed_20260408`

## 3. 标准 8 图输入目录

### 最终实验输入图目录

用途：

- 已统一为 `512×512` 灰度 `BMP`
- 供多随机种子实验直接使用

绝对路径：

`D:\CNN-Prediction-Based-Reversible-Data-Hiding-main\datasets\extended_test_images_8`

### 原始扩样本目录

用途：

- 存放下载后的原始图像
- 用于批量转换前的输入目录

绝对路径：

`D:\CNN-Prediction-Based-Reversible-Data-Hiding-main\datasets\extended_test_images_raw`

## 4. 相关脚本文件

### 扩样本图片预处理脚本

绝对路径：

`D:\CNN-Prediction-Based-Reversible-Data-Hiding-main\data_processing\prepare_extended_images.py`

### 单次批量实验脚本

绝对路径：

`D:\CNN-Prediction-Based-Reversible-Data-Hiding-main\data_processing\run_cnnp_batch.py`

### 多随机种子聚合脚本

绝对路径：

`D:\CNN-Prediction-Based-Reversible-Data-Hiding-main\data_processing\aggregate_multi_seed_results.py`

### 一键运行 8 图 × 3 种子实验脚本

绝对路径：

`D:\CNN-Prediction-Based-Reversible-Data-Hiding-main\scripts\run_multi_seed_8img_experiment.bat`

## 5. 备注

- 如果只看论文总表，优先使用：
  - `D:\CNN-Prediction-Based-Reversible-Data-Hiding-main\results\multi_seed_8img\aggregated\mode_payload_summary.csv`
- 如果要分析哪张图波动更大，使用：
  - `D:\CNN-Prediction-Based-Reversible-Data-Hiding-main\results\multi_seed_8img\aggregated\mode_payload_image_summary.csv`
