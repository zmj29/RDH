# CNNP Batch Experiment Design

## Goal

在不改动 MATLAB 嵌入算法主体的前提下，新增一组独立的数据处理脚本，用于批量运行 `4` 幅标准图像在 `2` 种模式、`4` 个载荷下的实验，并导出论文所需的原始日志、逐图像结果、平均结果、环境说明与图表源数据。

## Scope

- 新增独立文件夹 `data_processing/`
- 批量运行 `histogram_shifting` 与 `expansion_embedding`
- 固定随机种子，统一图像顺序
- 导出 `per_image_results.csv`
- 导出 `average_results.csv`
- 导出 `cnnp_psnr_results.csv`
- 导出环境说明文本
- 导出原始日志文本
- 导出图表源数据
- 可选生成图表 PNG

## Non-Goals

- 不修改 `cnn_expansion.m`、`cnn_histogram_shifting.m`
- 不新增消息提取、恢复验证或 BER 计算
- 不重构现有 `main.py` 入口
- 不引入数据库、Web 界面或复杂配置系统

## Recommended Approach

采用“外层独立批处理脚本 + 惰性导入算法依赖 + 纯 Python 聚合导出”的方案。

核心脚本直接复用仓库已有的 `utils.py`、`model/predict_model.py`、MATLAB Engine 与模型权重，但把批量实验控制、结果汇总、CSV 导出、日志落盘全部放在 `data_processing/` 下。这样可以避免对现有主入口做行为性修改，也更符合“脚本代码单独放一个文件夹作为数据处理”的要求。

## Files

- `data_processing/cnnp_experiment.py`
  - 批量实验核心逻辑
  - 条件展开、单图运行、指标聚合、CSV 与日志导出
- `data_processing/run_cnnp_batch.py`
  - 命令行入口
- `data_processing/plot_cnnp_results.py`
  - 从平均结果生成图表与图表源数据
- `data_processing/README.md`
  - 运行说明
- `tests/test_cnnp_experiment.py`
  - 纯聚合与导出辅助逻辑测试

## Data Flow

1. 读取模型路径、图像路径、模式列表、载荷列表、随机种子与输出目录。
2. 对每组 `mode + payload + image` 运行一次嵌入流程。
3. 记录每张图的 `psnr`、`ssim`、耗时、图像名、模式、载荷。
4. 按 `mode + payload` 聚合平均 `psnr`、平均 `ssim`、平均耗时。
5. 写出逐图像 CSV、平均 CSV、环境文本、原始日志与图表源数据。
6. 可选调用绘图脚本，输出折线图与柱状图。

## Error Handling

- 启动前检查图像目录、模型文件是否存在
- 导入 `matlab.engine` 失败时给出明确错误
- 导入 `torch/cv2/numpy` 失败时给出明确错误
- 输出目录不存在时自动创建
- `matplotlib` 缺失时只跳过 PNG 绘图，不影响 CSV 导出

## Verification

- 单元测试覆盖：
  - 条件展开数量
  - 平均结果聚合
  - 图表源数据生成
  - 环境文本格式中的关键字段
- 运行级验证：
  - 脚本帮助信息可正常输出
  - 在缺少 MATLAB Engine 的环境下，纯测试仍可执行
  - 在完整环境下可按单条件运行并生成结构化文件

## Output Contract

默认输出目标与用户论文要求保持一致：

- `D:\word\tmp\cnnp_results\cnnp_psnr_results.csv`
- `D:\word\tmp\cnnp_assets\per_image_results.csv`
- `D:\word\tmp\cnnp_assets\average_results.csv`
- `D:\word\tmp\cnnp_assets\payload_psnr_trend.csv`
- `D:\word\tmp\cnnp_assets\mode_gap_comparison.csv`
- `D:\word\tmp\cnnp_assets\payload_psnr_trend.png`
- `D:\word\tmp\cnnp_assets\mode_gap_comparison.png`
- `D:\word\tmp\cnnp_assets\environment_info.txt`
- `D:\word\tmp\cnnp_results\logs\*.txt`
