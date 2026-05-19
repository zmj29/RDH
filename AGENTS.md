# 项目级 Agent 规则

本仓库是 **CNN Prediction Based Reversible Data Hiding** 的复现与实验项目，包含 Python 侧 CNN 预测、MATLAB 可逆数据隐藏算法、批量实验脚本和中文 GUI。

## 项目边界

- `main.py` 是原始命令行实验入口。
- `gui_main.py` 和 `gui/` 是中文 GUI 入口与界面逻辑。
- `utils.py`、`model/`、`model_parameter/` 负责 CNNP 模型加载与预测。
- `matlab/` 保存可逆数据隐藏 MATLAB 算法函数。
- `data_processing/` 保存批量实验、统计汇总和图表生成脚本。
- `datasets/` 保存标准测试图像和扩展测试图像。
- `tests/` 保存 Python 单元测试与 GUI 逻辑测试。
- `results/` 和 `tmp/` 默认为运行输出或临时文件，不要作为核心源码修改。

## 修改原则

- 优先保持论文复现逻辑稳定，算法改动需要说明对 PSNR、SSIM、嵌入容量或恢复流程的影响。
- 不要随意删除模型权重、测试图像、MATLAB 函数或已保存实验结果。
- 新增脚本应放在与用途匹配的目录中，例如批处理脚本放入 `data_processing/`，本地辅助命令放入 `scripts/`。
- GUI 文案默认使用简体中文，代码标识符保持英文。
- 避免把本机绝对路径、个人工作流说明、API Key 或账号凭证写入仓库。

## 常用验证

按改动范围选择最小充分验证：

```powershell
python -m pytest tests
```

GUI 入口检查：

```powershell
python gui_main.py
```

命令行实验 smoke test：

```powershell
python main.py -size 512 512 -model .\model_parameter\model_state.pth -folder .\datasets\standard_test_images -mode histogram_shifting -length 10000
```

批量实验脚本：

```powershell
python data_processing\run_cnnp_batch.py
```

## Git 交付

- 提交信息使用 `<type>(scope): <summary>`，summary 使用中文、动词开头、不加句号。
- 上传前检查 `git status --short`，确认没有缓存、临时文件或私人文档混入。
- 如果无法运行完整实验，必须在交付说明里明确未验证的部分。
