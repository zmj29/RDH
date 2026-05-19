# CNN 预测可逆数据隐藏实验项目

本项目基于论文 **CNN Prediction Based Reversible Data Hiding**，用于复现实验中的 CNN 预测器、直方图平移与扩展嵌入流程，并提供论文实验数据导出与中文 GUI 演示界面。

参考论文：

> R. Hu and S. Xiang, "CNN Prediction Based Reversible Data Hiding," IEEE Signal Processing Letters, vol. 28, pp. 464-468, 2021, doi: 10.1109/LSP.2021.3059202.

## 运行环境

建议使用 Windows 环境运行。原项目说明环境为：

- Python 3.7
- PyTorch
- OpenCV
- NumPy
- MATLAB R2019a
- MATLAB Engine for Python

建议单独创建兼容的 Python 3.7 环境，并在其中安装 PyTorch、OpenCV、NumPy 与 MATLAB Engine for Python。
在 PyCharm 中请将项目解释器设置为该环境的 Python，并运行根目录下的 `gui_main.py`。

## 目录说明

- `gui/`：中文 GUI 界面代码，负责参数选择、运行进度显示和结果表格展示。
- `gui_main.py`：推荐启动入口，适合在 PyCharm 中直接运行。
- `main.py`：原始命令行实验入口。
- `utils.py`：CNN 预测与 MATLAB 嵌入算法的桥接函数。
- `matlab/`：MATLAB 可逆数据隐藏算法函数，包括扩展嵌入、直方图平移和辅助函数。
- `model/`：CNN 预测模型定义。
- `model_parameter/`：模型权重文件。
- `datasets/standard_test_images/`：原始标准测试图像。
- `datasets/extended_test_images_8/`：扩展 8 图性能评估数据集。
- `datasets/extended_test_images_raw/`：扩展图像原始素材。
- `data_processing/`：批量性能评估、结果汇总与图表生成脚本。
- `scripts/`：本地批处理脚本。
- `results/paper_experiment_2026-04-06/`：已保存的论文实验结果。

## GUI 使用方式

在 PyCharm 中直接运行：

```text
gui_main.py
```

界面功能包括：

- 选择测试图像目录
- 选择模型权重文件
- 选择结果输出目录
- 选择嵌入方式：直方图平移、扩展嵌入
- 设置载荷长度和随机种子
- 显示运行进度、当前图像、PSNR、SSIM 和耗时
- 导出 CSV、日志和汇总结果

每次 GUI 实验默认会将结果写入：

```text
results/gui_runs/run_时间戳/
```

## 原始命令行用法

直方图平移：

```powershell
python main.py -size 512 512 -model .\model_parameter\model_state.pth -folder .\datasets\standard_test_images -mode histogram_shifting -length 10000
```

扩展嵌入：

```powershell
python main.py -size 512 512 -model .\model_parameter\model_state.pth -folder .\datasets\standard_test_images -mode expansion_embedding -length 10000
```

参数说明：

- `-size`：图像尺寸，默认 `512 512`
- `-model`：模型权重路径
- `-folder`：测试图像目录
- `-mode`：嵌入方式
- `-length`：水印载荷长度

## 批量性能评估脚本

导出论文实验 CSV、日志和汇总表：

```powershell
python data_processing\run_cnnp_batch.py
```

根据导出的 CSV 生成论文图表：

```powershell
python data_processing\plot_cnnp_results.py
```

## 已保存结果

项目中保留了一组结构化实验结果：

```text
results/paper_experiment_2026-04-06/
```

该目录包含：

- 逐图像实验结果
- 平均结果表
- 环境信息
- 每种模式和载荷对应的原始日志
- 图表源数据 CSV
- 已生成的图表 PNG

## 注意事项

- GUI 运行实验时会启动 MATLAB Engine，因此第一次运行可能较慢。
- 如果出现依赖缺失，请先确认 PyCharm 使用的解释器不是系统默认 Python，而是兼容项目依赖的 Python 3.7 环境。
- `results/` 下的新增文件通常是实验输出，不属于核心源码。
