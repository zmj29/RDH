from __future__ import annotations


TEXT = {
    "app_title": "CNNP 可逆数据隐藏实验控制台",
    "experiment_tab": "批量性能评估",
    "closed_loop_tab": "扩展嵌入闭环",
    "settings_panel": "评估参数",
    "image_folder": "图像目录",
    "model_file": "模型文件",
    "output_folder": "输出目录",
    "payloads": "载荷长度",
    "seed": "随机种子",
    "modes": "嵌入方式",
    "browse": "浏览",
    "run_button": "开始评估",
    "pause_button": "暂停",
    "resume_button": "继续",
    "progress_paused": "已暂停，点击继续后恢复运行",
    "progress_resumed": "已继续运行",
    "closed_loop_panel": "闭环参数",
    "carrier_image": "载体图像",
    "secret_text": "秘密信息",
    "closed_loop_run_button": "运行闭环",
    "closed_loop_queued": "扩展嵌入闭环已加入运行队列",
    "closed_loop_done_title": "闭环完成",
    "closed_loop_result_panel": "闭环结果",
    "closed_loop_ready": "选择载体图像并输入秘密信息后运行",
    "message_match": "消息一致",
    "image_match": "图像一致",
    "output_files": "输出文件",
    "clear_log": "清空日志",
    "progress_panel": "运行进度",
    "progress_idle": "等待开始",
    "progress_queued": "性能评估已加入运行队列",
    "progress_failed": "运行失败",
    "results_panel": "平均指标",
    "log_panel": "运行日志",
    "view_log": "查看运行日志",
    "invalid_settings_title": "参数错误",
    "experiment_failed_title": "评估失败",
    "closed_loop_failed_title": "闭环失败",
}

COLUMN_LABELS = {
    "mode": "嵌入方式",
    "payload": "载荷长度",
    "average_psnr": "平均 PSNR",
    "average_ssim": "平均 SSIM",
    "average_elapsed_seconds": "平均耗时(秒)",
    "image_count": "图像数量",
}

MODE_LABELS = {
    "histogram_shifting": "直方图平移",
    "expansion_embedding": "扩展嵌入",
}


def format_mode_label(mode: str) -> str:
    return MODE_LABELS.get(mode, mode)


def _seed_suffix(event: dict[str, object]) -> str:
    seed = event.get("seed")
    if seed is None:
        return ""
    seed_index = event.get("seed_index")
    seed_count = event.get("seed_count")
    if seed_index and seed_count:
        return f"，种子 {seed}({seed_index}/{seed_count})"
    return f"，种子 {seed}"


def format_progress_message(event: dict[str, object]) -> str:
    stage = event.get("stage")
    current = int(event.get("current", 0) or 0)
    total = int(event.get("total", 0) or 0)
    prefix = f"[{current}/{total}]" if total else ""
    seed_suffix = _seed_suffix(event)

    if stage == "start":
        return f"[0/{total}] 准备运行性能评估，共 {total} 个图像任务"
    if stage == "seed_start":
        return f"{prefix} 开始随机种子实验{seed_suffix}"
    if stage == "seed_complete":
        return f"{prefix} 完成随机种子实验{seed_suffix}，结果已写入 {event.get('output_dir')}"
    if stage == "runtime_ready":
        return f"运行环境初始化完成，已启动 MATLAB 引擎并载入模型{seed_suffix}"
    if stage == "condition_start":
        return (
            f"{prefix} 开始组合：{format_mode_label(str(event.get('mode')))}，"
            f"载荷 {event.get('payload')}{seed_suffix}"
        )
    if stage == "image_start":
        next_index = current + 1
        return (
            f"[{next_index}/{total}] 正在处理：{format_mode_label(str(event.get('mode')))}，"
            f"载荷 {event.get('payload')}，图像 {event.get('image')}{seed_suffix}"
        )
    if stage == "image_done":
        return (
            f"{prefix} 完成图像 {event.get('image')}，"
            f"{format_mode_label(str(event.get('mode')))}，载荷 {event.get('payload')}，"
            f"PSNR={event.get('psnr')}，SSIM={event.get('ssim')}，"
            f"耗时 {event.get('elapsed_seconds')} 秒{seed_suffix}"
        )
    if stage == "condition_done":
        return (
            f"{prefix} 完成组合：{format_mode_label(str(event.get('mode')))}，"
            f"载荷 {event.get('payload')}{seed_suffix}"
        )
    if stage == "complete":
        return f"[{total}/{total}] 性能评估完成，结果已保存到 {event.get('output_dir')}"
    if stage == "closed_loop_start":
        return f"[{current}/{total}] 开始扩展嵌入闭环"
    if stage == "closed_loop_embed_done":
        return f"[{current}/{total}] 嵌入完成，已生成含密图"
    if stage == "closed_loop_extract_done":
        return f"[{current}/{total}] 提取完成，已恢复载体图像"
    if stage == "closed_loop_verify_done":
        return f"[{current}/{total}] 验证完成，正在整理结果"
    return ""
