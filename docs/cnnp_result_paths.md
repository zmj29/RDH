# CNNP 实验结果路径说明

本文档用于说明本次 CNNP 论文实验生成的数据文件分别位于哪些路径，以及每个文件可用于什么用途。

## 1. 实验结果总览

本次实验已完成以下数据产物：

- `32` 条逐图像结果
- `8` 条平均结果
- 环境说明文本
- `8` 份原始日志
- 图表源数据 `csv`
- 图表图片 `png`

## 2. 逐图像原始结果

### 主结果表

路径：

`D:\word\tmp\cnnp_results\cnnp_psnr_results.csv`

说明：

- 含 `32` 条记录
- 对应 `2` 种模式 × `4` 个载荷 × `4` 幅图像
- 可作为论文实验原始明细表

字段：

- `mode`
- `payload`
- `image`
- `psnr`
- `ssim`
- `elapsed_seconds`
- `run_datetime`
- `device`
- `model_file`
- `seed`

### 资源目录中的同内容副本

路径：

`D:\word\tmp\cnnp_assets\per_image_results.csv`

说明：

- 与 `cnnp_psnr_results.csv` 为同一批逐图像结果
- 便于与图表、环境说明放在同一目录下统一管理

## 3. 平均结果

路径：

`D:\word\tmp\cnnp_assets\average_results.csv`

说明：

- 含 `8` 条记录
- 对应 `2` 种模式 × `4` 个载荷
- 可直接用于论文中的平均性能对比表

字段：

- `mode`
- `payload`
- `average_psnr`
- `average_ssim`
- `average_elapsed_seconds`
- `image_count`

## 4. 环境说明

路径：

`D:\word\tmp\cnnp_assets\environment_info.txt`

说明：

- 记录本次运行环境
- 可直接作为论文“实验环境”或答辩材料依据

当前记录内容包括：

- 运行时间
- 设备类型 `CPU`
- `Python` 版本
- `Torch` 版本
- `MATLAB` 版本
- 模型文件名
- 图像名列表
- 载荷列表
- 模式名列表
- 随机种子

## 5. 原始日志

目录：

`D:\word\tmp\cnnp_results\logs`

说明：

- 目录中共 `8` 份日志
- 每个日志文件对应一组 `mode + payload`
- 可作为“原始运行快照”留档

文件列表：

- `D:\word\tmp\cnnp_results\logs\histogram_shifting_10000.txt`
- `D:\word\tmp\cnnp_results\logs\histogram_shifting_20000.txt`
- `D:\word\tmp\cnnp_results\logs\histogram_shifting_50000.txt`
- `D:\word\tmp\cnnp_results\logs\histogram_shifting_100000.txt`
- `D:\word\tmp\cnnp_results\logs\expansion_embedding_10000.txt`
- `D:\word\tmp\cnnp_results\logs\expansion_embedding_20000.txt`
- `D:\word\tmp\cnnp_results\logs\expansion_embedding_50000.txt`
- `D:\word\tmp\cnnp_results\logs\expansion_embedding_100000.txt`

## 6. 图表源数据

### 图 5.1 源数据

路径：

`D:\word\tmp\cnnp_assets\payload_psnr_trend.csv`

说明：

- 用于绘制不同载荷下两种模式平均 `PSNR` 变化趋势图

### 图 5.2 源数据

路径：

`D:\word\tmp\cnnp_assets\mode_gap_comparison.csv`

说明：

- 用于绘制两种模式间 `PSNR` 差值对比图

## 7. 图表图片

### 图 5.1 图片

路径：

`D:\word\tmp\cnnp_assets\payload_psnr_trend.png`

### 图 5.2 图片

路径：

`D:\word\tmp\cnnp_assets\mode_gap_comparison.png`

## 8. 建议给论文或老师时优先提交的文件

建议至少提交以下内容：

- `D:\word\tmp\cnnp_results\cnnp_psnr_results.csv`
- `D:\word\tmp\cnnp_assets\per_image_results.csv`
- `D:\word\tmp\cnnp_assets\average_results.csv`
- `D:\word\tmp\cnnp_assets\environment_info.txt`
- `D:\word\tmp\cnnp_results\logs\`
- `D:\word\tmp\cnnp_assets\payload_psnr_trend.csv`
- `D:\word\tmp\cnnp_assets\mode_gap_comparison.csv`
- `D:\word\tmp\cnnp_assets\payload_psnr_trend.png`
- `D:\word\tmp\cnnp_assets\mode_gap_comparison.png`

## 9. 备注

- `D:\word\tmp\cnnp_results\cnnp_psnr_results.csv` 与 `D:\word\tmp\cnnp_assets\per_image_results.csv` 内容一致，属于双份保存
- 本次结果已经包含老师额外要求的 `SSIM` 和运行时间字段
- 本次结果不包含 `BER`、消息提取正确率和原图恢复成功率，因为当前项目未提供统一恢复验证入口
