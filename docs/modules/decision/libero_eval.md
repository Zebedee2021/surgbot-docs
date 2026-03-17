# LIBERO 仿真评测

## LIBERO 简介

LIBERO 主要承担"任务集与评测标准"的角色。官方将 130 个任务划分为 4 个 task suite：

| Task Suite | 说明 |
|-----------|------|
| LIBERO-Spatial | 空间关系任务 |
| LIBERO-Object | 物体操作任务 |
| LIBERO-Goal | 目标导向任务 |
| LIBERO-100 | 综合任务集 |

当前项目主要评测 `libero_spatial`，包含 10 个空间操作任务。

## 仿真组件

- **robosuite**：机器人仿真框架，负责将机器人、场景、物体、控制器和观察器组织为可执行的仿真环境
- **MuJoCo**：底层物理引擎，负责刚体动力学、接触碰撞等物理仿真

## 当前状态

libero_spatial 评测可正常运行，但仍有若干待解决的稳定性问题。
