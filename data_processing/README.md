# CNNP 数据处理脚本

这个目录只放论文实验的数据处理脚本，不改动原始 MATLAB 算法主体。

## 1. 环境准备

建议使用 `Python 3.7 + MATLAB R2019a`，并先安装：

```bat
conda create -n cnnp37 python=3.7 -y
conda activate cnnp37
conda install pytorch==1.6.0 torchvision==0.7.0 cpuonly -c pytorch
python -m pip install numpy==1.21.6 opencv-python==4.5.5.64 matplotlib
cd /d D:\download\R2019a\extern\engines\python
python -m pip install .
```

## 1.1 推荐扩样本 8 图名单

推荐使用以下 8 张图：

- `Barbara`
- `Lena`
- `Peppers`
- `yacht`
- `Baboon`
- `Boat`
- `Goldhill`
- `Airplane`

如需查看脚本内置推荐名单：

```bat
python data_processing\prepare_extended_images.py --list-recommended
```

如需批量转成 `512x512` 灰度 `BMP`：

```bat
python data_processing\prepare_extended_images.py --input-dir .\datasets\extended_test_images_raw --output-dir .\datasets\extended_test_images_8
```

## 2. 批量导出实验数据

在仓库根目录执行：

```bat
python data_processing\run_cnnp_batch.py
```

默认会导出：

- `D:\word\tmp\cnnp_results\cnnp_psnr_results.csv`
- `D:\word\tmp\cnnp_assets\per_image_results.csv`
- `D:\word\tmp\cnnp_assets\average_results.csv`
- `D:\word\tmp\cnnp_assets\payload_psnr_trend.csv`
- `D:\word\tmp\cnnp_assets\mode_gap_comparison.csv`
- `D:\word\tmp\cnnp_assets\environment_info.txt`
- `D:\word\tmp\cnnp_results\logs\*.txt`

## 3. 生成论文图

```bat
python data_processing\plot_cnnp_results.py
```

默认会导出：

- `D:\word\tmp\cnnp_assets\payload_psnr_trend.png`
- `D:\word\tmp\cnnp_assets\mode_gap_comparison.png`

## 4. 聚合多随机种子结果

如果已经分别跑完多个随机种子，例如：

- `results\multi_seed_8img\seed_20260406\per_image_results.csv`
- `results\multi_seed_8img\seed_20260407\per_image_results.csv`
- `results\multi_seed_8img\seed_20260408\per_image_results.csv`

可以执行：

```bat
python data_processing\aggregate_multi_seed_results.py --input-root .\results\multi_seed_8img
```

默认会导出到：

- `results\multi_seed_8img\aggregated\mode_payload_summary.csv`
- `results\multi_seed_8img\aggregated\mode_payload_image_summary.csv`
- `results\multi_seed_8img\aggregated\seed_sources.csv`

其中：

- `mode_payload_summary.csv` 可直接用于论文中的 `平均值 ± 标准差` 总表
- `mode_payload_image_summary.csv` 可用于分析不同图像类别的波动情况

## 5. 一键运行 8 图 × 3 种子实验

如果已经准备好：

- `cnnp37` 环境
- `datasets\extended_test_images_8` 目录

可以直接在仓库根目录双击或执行：

```bat
scripts\run_multi_seed_8img_experiment.bat
```

该脚本会自动：

- 跑 `20260406`
- 跑 `20260407`
- 跑 `20260408`
- 最后自动聚合为 `平均值 ± 标准差` 总表
