# OpenVLA 进展

## 项目概述

OpenVLA 是当前项目的核心决策模型，是开源的 Vision-Language-Action 模型，接收图像与任务指令，输出机器人动作。

## 环境配置

- 参考 GitHub 开源项目 `ZYangChen/openvla` 提供的中文复现说明
- 主要依赖 RTX 4090 (48GB) 单卡运行

## 已完成工作

1. 基础环境安装配置已通过
2. LIBERO 模拟器能够正常启动并加载任务环境
3. OpenVLA 模型权重能够成功加载
4. LIBERO 数据集下载完成，能够被正确读取
5. `run_libero_eval.py` 评测脚本能够成功运行
6. 基于 libero_spatial 可完成逐个任务的评测

## 评测流程

| 步骤 | 说明 |
|------|------|
| 1 | 读取命令行参数（task_suite_name, 模型权重路径, center crop 等） |
| 2 | 加载 OpenVLA 模型 |
| 3 | 确定评测集（libero_spatial） |
| 4 | 生成对应的任务列表 |
| 5 | 为每个任务创建仿真环境（robosuite / MuJoCo） |
| 6 | 每个任务运行若干 episode（获取图像 → 模型生成动作 → 执行 → 判断成功） |
| 7 | 统计结果并输出成功率 |

## 下一步计划

- 整理安装过程中所有关键问题，形成可复现安装文档
- 排查并修复已知 bug，建立稳定基线
- 推进 Isaac 仿真环境搭建和真实机械臂数据采集
- 推进 sim2real 验证
