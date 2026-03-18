# 仿真模块

## 概述

仿真模块使用 **Isaac Sim + Omniverse** 构建虚拟手术室场景，用于在虚拟环境中验证机器人任务逻辑，并为 sim2real 迁移提供支撑。

## 总体目标

1. 构建虚拟手术室场景，还原真实手术室布局
2. 利用 Isaac Sim 进行物理仿真 + 机器人控制
3. 利用 Omniverse 提供高保真可视化 + 多用户协作
4. 实现器械识别、抓取、递交流程的虚拟验证
5. 为 sim2real 迁移提供数据采集环境

## 负责人

谭文韬

## 当前工作

- VLA 模型在真实机械臂平台上的部署与功能测试
- Isaac Sim 仿真环境搭建与机械臂部署
- 仿真环境中数据采集
- 实验室服务器 VLA 镜像安装

## 子页面

- [Isaac Sim 环境搭建](isaac_sim_setup.md)
- [虚拟手术室方案](surgery_room_sim.md)
- [MuJoCo 仿真方案（提案）](mujoco_proposal.md)

---

## 待决策问题

!!! question "需要团队讨论确定"

| 编号 | 问题 | 备选方案 | 状态 |
|------|------|---------|------|
| D-SM-01 | Isaac Sim 版本选择？ | A: 2023.1.1（稳定版） / B: 4.x（最新版） | ⬚待讨论 |
| D-SM-02 | 是否与 MuJoCo/robosuite 双线并进？ | A: 仅 Isaac Sim / B: 双线并进保持兼容 | [方案已提交](mujoco_proposal.md) |

## 已知瓶颈

!!! warning "当前阻碍进展的问题"

| 瓶颈 | 影响 | 关联问题 | 缓解方向 |
|------|------|---------|---------|
| Isaac Sim 环境搭建进度 | Level 2 仿真无法启动，阻塞高保真验证 | [ISS-12](../../progress/issue_tracker.md) | 确定版本后集中攻坚 |
| Sim2Real gap 量化方法待定 | 无法衡量仿真与真实的差距 | [Sim2Real 仪表盘](../../progress/sim2real_dashboard.md) | 定义量化指标 + 对比实验方案 |

## 本周行动

> 更新日期：2026-03-18

- [ ] 完成 Isaac Sim 版本选型评估
- [ ] 尝试导入 CR5 URDF 模型到 Isaac Sim
- [ ] 制定 Sim2Real gap 量化方案初稿
