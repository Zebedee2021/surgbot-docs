# Isaac Sim 环境搭建

## 概述

Isaac Sim 是 NVIDIA 推出的机器人仿真平台，基于 Omniverse 构建，支持高保真物理仿真和传感器模拟。

## 搭建步骤

1. 安装 NVIDIA Omniverse Launcher
2. 通过 Launcher 安装 Isaac Sim
3. 配置 ROS2 Bridge（可选）
4. 导入机械臂 URDF/MJCF 模型
5. 搭建虚拟手术室场景

## 机器人模型

- 导入越疆 CR5 系列机械臂 URDF
- 末端夹爪配置（双指 + 力/位传感）

## 传感器配置

| 传感器 | 类型 | 用途 |
|-------|------|------|
| 俯视相机 | RGB-D（固定） | 器械台俯拍 |
| 腕部相机 | eye-in-hand | 近距离精确识别 |
| 接近检测 | ToF/红外 | 递交区手部检测 |

## 与 VLA 的集成

Isaac Sim 环境产生的数据可用于：

- OpenVLA 模型的仿真评测
- 仿真数据采集用于模型训练
- sim2real 迁移验证
