# CNNP Batch Experiment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增独立数据处理脚本，批量导出论文所需的 CNNP 实验结果、原始日志、环境说明和图表源数据。

**Architecture:** 在 `data_processing/` 下新增一个核心实验模块和两个命令行脚本。核心模块只在运行实验时惰性导入 `torch/cv2/matlab`，把聚合、导出、图表数据生成保持为可单测的纯 Python 逻辑，从而允许在当前不完整环境下先做测试与结构验证。

**Tech Stack:** Python、csv、argparse、pathlib、time、statistics、NumPy、OpenCV、PyTorch、MATLAB Engine、unittest、可选 matplotlib

---

### Task 1: 写聚合逻辑测试

**Files:**
- Create: `tests/test_cnnp_experiment.py`
- Test: `tests/test_cnnp_experiment.py`

- [ ] **Step 1: 写出失败测试**

```python
import unittest

from data_processing.cnnp_experiment import (
    build_chart_rows,
    build_conditions,
    summarize_results,
)


class ExperimentSummaryTests(unittest.TestCase):
    def test_build_conditions_expands_all_mode_payload_image_pairs(self):
        conditions = build_conditions(
            modes=["histogram_shifting", "expansion_embedding"],
            payloads=[10000, 20000],
            images=["Barbara.bmp", "Lena.bmp"],
        )
        self.assertEqual(8, len(conditions))

    def test_summarize_results_groups_by_mode_and_payload(self):
        rows = [
            {"mode": "histogram_shifting", "payload": 10000, "psnr": 50.0, "ssim": 0.99, "elapsed_seconds": 1.0},
            {"mode": "histogram_shifting", "payload": 10000, "psnr": 54.0, "ssim": 0.97, "elapsed_seconds": 3.0},
        ]
        summary = summarize_results(rows)
        self.assertEqual(1, len(summary))
        self.assertEqual(52.0, summary[0]["average_psnr"])
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `python -m unittest tests.test_cnnp_experiment -v`
Expected: FAIL with `ModuleNotFoundError` or missing symbol errors from `data_processing.cnnp_experiment`

- [ ] **Step 3: 写最小实现让测试通过**

```python
def build_conditions(modes, payloads, images):
    conditions = []
    for mode in modes:
        for payload in payloads:
            for image in images:
                conditions.append({"mode": mode, "payload": payload, "image": image})
    return conditions
```

- [ ] **Step 4: 再跑测试确认通过**

Run: `python -m unittest tests.test_cnnp_experiment -v`
Expected: PASS

- [ ] **Step 5: 提交当前任务**

```bash
git add tests/test_cnnp_experiment.py data_processing/cnnp_experiment.py
git commit -m "test(data-processing): 补充实验聚合测试"
```

### Task 2: 实现批量实验与导出脚本

**Files:**
- Create: `data_processing/cnnp_experiment.py`
- Create: `data_processing/run_cnnp_batch.py`
- Modify: `tests/test_cnnp_experiment.py`

- [ ] **Step 1: 为平均耗时、图表源数据和环境文本补失败测试**

```python
    def test_build_chart_rows_creates_gap_table(self):
        summary_rows = [
            {"mode": "histogram_shifting", "payload": 10000, "average_psnr": 55.0},
            {"mode": "expansion_embedding", "payload": 10000, "average_psnr": 47.0},
        ]
        _, gap_rows = build_chart_rows(summary_rows)
        self.assertEqual(1, len(gap_rows))
        self.assertEqual(8.0, gap_rows[0]["psnr_gap"])
```

- [ ] **Step 2: 跑测试确认新断言失败**

Run: `python -m unittest tests.test_cnnp_experiment -v`
Expected: FAIL mentioning missing `build_chart_rows`

- [ ] **Step 3: 实现核心模块与批量命令行入口**

```python
def summarize_results(rows):
    grouped = {}
    for row in rows:
        key = (row["mode"], row["payload"])
        grouped.setdefault(key, []).append(row)
    ...
```

```python
def main():
    args = parse_args()
    run_batch_experiment(...)
```

- [ ] **Step 4: 跑单元测试确认通过**

Run: `python -m unittest tests.test_cnnp_experiment -v`
Expected: PASS

- [ ] **Step 5: 提交当前任务**

```bash
git add data_processing/cnnp_experiment.py data_processing/run_cnnp_batch.py tests/test_cnnp_experiment.py
git commit -m "feat(data-processing): 新增批量实验导出脚本"
```

### Task 3: 实现绘图脚本与使用说明

**Files:**
- Create: `data_processing/plot_cnnp_results.py`
- Create: `data_processing/README.md`
- Modify: `tests/test_cnnp_experiment.py`

- [ ] **Step 1: 为图表源数据排序与字段补失败测试**

```python
        trend_rows, gap_rows = build_chart_rows(summary_rows)
        self.assertEqual(["payload", "mode", "average_psnr"], list(trend_rows[0].keys()))
```

- [ ] **Step 2: 跑测试确认失败**

Run: `python -m unittest tests.test_cnnp_experiment -v`
Expected: FAIL with unexpected key order or missing rows

- [ ] **Step 3: 实现绘图脚本与 README**

```python
def main():
    summary_rows = read_csv_rows(args.average_csv)
    trend_rows, gap_rows = build_chart_rows(summary_rows)
    ...
```

- [ ] **Step 4: 跑测试与脚本帮助命令**

Run: `python -m unittest tests.test_cnnp_experiment -v`
Expected: PASS

Run: `python data_processing/run_cnnp_batch.py --help`
Expected: usage text printed with output path arguments

Run: `python data_processing/plot_cnnp_results.py --help`
Expected: usage text printed with input and output arguments

- [ ] **Step 5: 提交当前任务**

```bash
git add data_processing/plot_cnnp_results.py data_processing/README.md tests/test_cnnp_experiment.py
git commit -m "docs(data-processing): 补充绘图脚本与运行说明"
```
