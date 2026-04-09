"""
BioMedAgent 结果查看工具
用法:
  python view_results.py          # 列出所有任务
  python view_results.py -n 1     # 查看最近第1个任务
  python view_results.py -n 2     # 查看最近第2个任务
  python view_results.py --log    # 同时显示完整对话日志
"""

import os, sys, glob, argparse

TASK_BASE = "task"
LOG_FILE_SVD = "/tmp/biomedagent_run2.log"
LOG_FILE_QQ  = "/tmp/biomedagent_qq.log"

def find_tasks():
    """找到所有任务目录，按时间倒序"""
    dirs = []
    for root, subdirs, files in os.walk(TASK_BASE):
        for d in subdirs:
            full = os.path.join(root, d)
            # 有实际输出文件的才算完成
            contents = [f for f in os.listdir(full) if not f.startswith('.') and f != 'log']
            if len(contents) >= 2:  # 至少有原始数据+1个输出
                dirs.append((os.path.getmtime(full), full, contents))
    dirs.sort(reverse=True)
    return dirs

def show_file_preview(path, max_lines=8):
    """预览文件内容"""
    try:
        if path.endswith('.npz'):
            import numpy as np
            data = np.load(path)
            print(f"    [NPZ文件] 包含: {list(data.keys())}")
            for k in data.keys():
                print(f"      {k}: shape={data[k].shape}, dtype={data[k].dtype}")
            return
        if path.endswith('.json'):
            import json
            with open(path) as f:
                data = json.load(f)
            if isinstance(data, list):
                print(f"    [JSON] {len(data)} 条记录，前2条: {str(data[:2])[:120]}")
            else:
                print(f"    [JSON] {str(data)[:120]}")
            return
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        preview = lines[:max_lines]
        for line in preview:
            print(f"    {line.rstrip()}")
        if len(lines) > max_lines:
            print(f"    ... (共{len(lines)}行)")
    except Exception as e:
        print(f"    [无法预览: {e}]")

def show_task(task_dir, show_log=False):
    contents = [f for f in os.listdir(task_dir)
                if not f.startswith('.') and f != 'log']

    # 判断任务类型
    task_type = "未知"
    if 'svd_results.npz' in contents or 'normalized_heart_disease.csv' in contents:
        task_type = "machine_learning (SVD降维)"
    elif 'ks_test_results.tsv' in contents or 'qq_plot.txt' in contents:
        task_type = "statistics_qq_plot (QQ分析)"
    elif 'heart_disease.csv' in contents and len(contents) <= 2:
        task_type = "未完成/中断"

    print(f"\n{'='*60}")
    print(f"任务类型: {task_type}")
    print(f"目录:     {task_dir}")
    print(f"{'='*60}")

    # 分类显示文件
    input_files = []
    output_files = []
    for f in sorted(contents):
        path = os.path.join(task_dir, f)
        size = os.path.getsize(path)
        if f in ['heart_disease.csv', 'boxplot.tsv', 'plot.tsv',
                  'data1.tsv', 'group1.tsv']:
            input_files.append((f, size))
        else:
            output_files.append((f, size))

    print("\n📥 输入文件:")
    for f, size in input_files:
        print(f"  {f:<40} {size:>8} bytes")

    print("\n📤 输出文件:")
    for f, size in output_files:
        print(f"  {f:<40} {size:>8} bytes")
        show_file_preview(os.path.join(task_dir, f))
        print()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', type=int, default=0, help='查看第N个最近任务(从1开始)')
    parser.add_argument('--log', action='store_true', help='显示对话日志')
    args = parser.parse_args()

    tasks = find_tasks()

    if not tasks:
        print("没有找到已完成的任务")
        return

    if args.n == 0:
        # 列出所有任务
        print(f"\n找到 {len(tasks)} 个已完成任务:\n")
        for i, (mtime, d, contents) in enumerate(tasks, 1):
            import time
            t = time.strftime('%Y-%m-%d %H:%M', time.localtime(mtime))
            output_count = len([f for f in contents
                               if f not in ['heart_disease.csv','boxplot.tsv',
                                           'plot.tsv','data1.tsv','group1.tsv']])
            print(f"  [{i}] {t}  输出{output_count}个文件  {os.path.basename(d)}")
        print(f"\n用 python view_results.py -n 1 查看最新任务")
    else:
        if args.n > len(tasks):
            print(f"只有 {len(tasks)} 个任务")
            return
        _, task_dir, _ = tasks[args.n - 1]
        show_task(task_dir, args.log)

if __name__ == '__main__':
    main()
