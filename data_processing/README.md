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
