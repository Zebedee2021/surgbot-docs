# MuJoCo 仿真方案建议

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Zebedee2021/surgbot-docs/blob/main/notebooks/mujoco_demo.ipynb)

!!! tip "方案状态"
    **Phase A 已完成** — 模型准备就绪，Colab 可演示。最近更新：2026-03-18

## 1. 为什么选 MuJoCo

### 与现有方案的对比

| 维度 | Colab Mock 仿真（已完成） | Isaac Sim（进行中） | MuJoCo（本提案） |
|------|------------------------|-------------------|----------------|
| **物理引擎** | 无（纯逻辑模拟） | PhysX 5.x | MuJoCo 3.x |
| **安装门槛** | 零安装（浏览器） | 需 RTX GPU + NVIDIA 驱动 | `pip install mujoco`，CPU 即可 |
| **Colab 支持** | 原生支持 | 不支持 | 支持（官方提供 Colab 教程） |
| **接触力学** | 不支持 | 支持 | 精确接触建模（凸优化求解器） |
| **渲染** | Matplotlib 静态 | Omniverse 高保真 | 内置 OpenGL + 离屏渲染 |
| **URDF 支持** | 不适用 | 原生支持 | 支持（URDF → MJCF 自动转换） |
| **适用场景** | 逻辑验证 / 快速演示 | 高保真视觉仿真 / Sim2Real | 控制算法验证 / 力学仿真 / RL |
| **学习曲线** | 低 | 高 | 中等 |
| **开源协议** | — | 商业（免费教育版） | Apache 2.0 完全开源 |

### MuJoCo 的核心优势

1. **精确接触力学**：基于凸优化的接触求解器，适合模拟夹爪抓取器械时的力反馈
2. **轻量级**：纯 CPU 可运行，无需 GPU，适合在 Colab 和普通笔记本上开发
3. **Colab 原生兼容**：Google DeepMind 官方维护 Colab 教程和 MuJoCo Playground
4. **与现有 Mock 仿真互补**：Mock 验证逻辑流程，MuJoCo 验证物理可行性
5. **Python API 成熟**：`mujoco` 包直接 pip 安装，API 清晰

### 定位：三层仿真体系

```
Level 0: Colab Mock 仿真（已完成）    → 逻辑验证 / 快速迭代
Level 1: MuJoCo 物理仿真（本提案）    → 运动验证 / 力学仿真 / Colab 可用
Level 2: Isaac Sim 高保真仿真（并行）  → 视觉仿真 / Sim2Real 迁移
```

MuJoCo 填补 Level 0 和 Level 2 之间的空白：比 Mock 更真实（有物理引擎），比 Isaac Sim 更轻量（无需 GPU）。

## 2. 技术方案

### 2.1 Dobot CR5 模型获取与转换

#### URDF 来源

Dobot 官方 ROS 仓库提供了 CR 系列 URDF 模型：

- 仓库地址：[Dobot-Arm/TCP-IP-ROS-6AXis](https://github.com/Dobot-Arm/TCP-IP-ROS-6AXis)
- 关键路径：`dobot_description/urdf/` 下包含 CR5 的 URDF 和 mesh 文件
- 备选仓库：[hans199904/CR_ROS](https://github.com/hans199904/CR_ROS)（含 `dobot_description` + `cr5_moveit`）

#### URDF → MJCF 转换流程

```python
# 方法 1: MuJoCo 内置编译器（推荐）
import mujoco

# 加载 URDF 并自动转换为 MJCF
model = mujoco.MjModel.from_xml_path("cr5.urdf")
# 保存为 MJCF XML 以便后续编辑
mujoco.mj_saveLastXML("cr5.xml", model)
```

```bash
# 方法 2: 命令行工具
python -m mujoco.viewer --mjcf cr5.urdf
```

#### 转换后需要的调整

| 项目 | 说明 |
|------|------|
| 关节限位 | 校验 CR5 六轴关节限位与真实参数一致 |
| 惯性参数 | 验证连杆质量、惯量矩阵的合理性 |
| 碰撞体 | 简化 mesh 碰撞体为凸包或基本几何体（提升仿真速度） |
| 执行器 | 添加关节电机 `<motor>` 或位置伺服 `<position>` 执行器 |
| 夹爪 | 添加 DH-3 夹爪模型（平行夹爪，两指联动） |

### 2.2 手术器械模型

对 4 种器械建立简化几何模型（先用基本几何体，后续可替换为精确 mesh）：

```xml
<!-- instruments.xml - 简化器械模型 -->
<mujoco>
  <worldbody>
    <body name="instrument_rack" pos="0.3 -0.1 0.8">
      <!-- 刀柄 (id=0): 圆柱体模拟手柄 -->
      <body name="scalpel_handle" pos="0 0 0">
        <joint name="scalpel_free" type="free"/>
        <geom type="cylinder" size="0.005 0.06" mass="0.05"
              rgba="0.7 0.7 0.7 1"/>
      </body>
      <!-- 镊子 (id=1): 细长锥体 -->
      <body name="tweezers" pos="0.04 0 0">
        <joint name="tweezers_free" type="free"/>
        <geom type="capsule" size="0.002 0.07" mass="0.03"
              rgba="0.7 0.7 0.7 1"/>
      </body>
      <!-- 剪刀 (id=2): 交叉体 -->
      <body name="scissors" pos="0.08 0 0">
        <joint name="scissors_free" type="free"/>
        <geom type="capsule" size="0.003 0.06" mass="0.06"
              rgba="0.7 0.7 0.7 1"/>
      </body>
      <!-- 持针钳 (id=3): 粗锥体 -->
      <body name="needle_holder" pos="0.12 0 0">
        <joint name="needle_holder_free" type="free"/>
        <geom type="capsule" size="0.004 0.065" mass="0.07"
              rgba="0.7 0.7 0.7 1"/>
      </body>
    </body>
  </worldbody>
</mujoco>
```

### 2.3 场景组装

```xml
<!-- surgbot_scene.xml - 完整仿真场景 -->
<mujoco model="surgbot_v2">
  <compiler angle="degree" meshdir="meshes/"/>
  <option timestep="0.002" gravity="0 0 -9.81"/>

  <default>
    <joint damping="1"/>
    <geom condim="4" friction="1 0.5 0.005"/>
  </default>

  <worldbody>
    <!-- 地面 -->
    <geom type="plane" size="2 2 0.01" rgba="0.9 0.9 0.9 1"/>

    <!-- 手术台 -->
    <body name="table" pos="0 0 0.75">
      <geom type="box" size="0.5 0.3 0.02" rgba="0.3 0.5 0.3 1"/>
    </body>

    <!-- CR5 机械臂底座 -->
    <include file="cr5_robot.xml"/>

    <!-- 器械支架 + 器械 -->
    <include file="instruments.xml"/>

    <!-- 交付点标记 -->
    <body name="delivery_point" pos="-0.2 0.3 0.85">
      <geom type="cylinder" size="0.05 0.005"
            rgba="0 0.8 0 0.5" contype="0" conaffinity="0"/>
    </body>
  </worldbody>

  <!-- 执行器 -->
  <actuator>
    <position name="j1_ctrl" joint="cr5_j1" kp="100"/>
    <position name="j2_ctrl" joint="cr5_j2" kp="100"/>
    <position name="j3_ctrl" joint="cr5_j3" kp="100"/>
    <position name="j4_ctrl" joint="cr5_j4" kp="100"/>
    <position name="j5_ctrl" joint="cr5_j5" kp="100"/>
    <position name="j6_ctrl" joint="cr5_j6" kp="100"/>
    <position name="gripper_l" joint="gripper_left" kp="50"/>
    <position name="gripper_r" joint="gripper_right" kp="50"/>
  </actuator>

  <!-- 传感器 -->
  <sensor>
    <force name="gripper_force" site="gripper_site"/>
    <touch name="gripper_touch" site="gripper_pad"/>
  </sensor>
</mujoco>
```

### 2.4 核心仿真控制器

```python
import mujoco
import numpy as np

class SurgBotMuJoCoSim:
    """MuJoCo 仿真控制器 - 对接 v2 固定位置模式"""

    def __init__(self, model_path="surgbot_scene.xml"):
        self.model = mujoco.MjModel.from_xml_path(model_path)
        self.data = mujoco.MjData(self.model)

        # 从 instruments.ini 加载的固定位置（笛卡尔坐标, mm）
        self.fixed_positions = {
            0: [250.5, -120.3, -85.2, 45.0],   # 刀柄
            1: [280.1, -95.7, -82.0, 30.0],     # 镊子
            2: [310.3, -130.5, -80.5, 60.0],    # 剪刀
            3: [340.0, -110.2, -83.0, 15.0],    # 持针钳
        }
        # 复位关节角 (deg)
        self.RESET_JOINTS = [0, 32.6, -129.1, 6.7, 90, -90]
        # 交付关节角 (deg)
        self.TARGET_JOINTS = [0, -50.2, -67.3, 112.5, 90, -90]

    def move_to_joint_target(self, joint_angles_deg, steps=500):
        """位置伺服：驱动关节到目标角度"""
        for i, angle in enumerate(joint_angles_deg[:6]):
            self.data.ctrl[i] = np.radians(angle)
        for _ in range(steps):
            mujoco.mj_step(self.model, self.data)

    def close_gripper(self, width=0.01):
        """闭合夹爪"""
        self.data.ctrl[6] = width
        self.data.ctrl[7] = -width
        for _ in range(200):
            mujoco.mj_step(self.model, self.data)

    def open_gripper(self):
        """张开夹爪"""
        self.data.ctrl[6] = 0.04
        self.data.ctrl[7] = -0.04
        for _ in range(200):
            mujoco.mj_step(self.model, self.data)

    def get_contact_force(self):
        """读取夹爪接触力"""
        total_force = 0
        for i in range(self.data.ncon):
            force = np.zeros(6)
            mujoco.mj_contactForce(self.model, self.data, i, force)
            total_force += np.linalg.norm(force[:3])
        return total_force

    def robot_move_fixed(self, instrument_id):
        """
        复现 v2 固定位置模式的三阶段运动序列
        Phase 1: 悬停 → 下降 → 夹取
        Phase 2: 抬升 → 复位 → 交付 → 松开
        Phase 3: 归位
        """
        pos = self.fixed_positions[instrument_id]

        # Phase 1: Grasp
        hover = self.ik_solve(pos[0], pos[1], pos[2] + 150)
        self.move_to_joint_target(hover)
        grasp = self.ik_solve(pos[0], pos[1], pos[2] + 1)
        self.move_to_joint_target(grasp)
        self.close_gripper()

        # Phase 2: Deliver
        self.move_to_joint_target(hover)
        self.move_to_joint_target(self.RESET_JOINTS)
        self.move_to_joint_target(self.TARGET_JOINTS)
        self.open_gripper()

        # Phase 3: Return
        self.move_to_joint_target(self.RESET_JOINTS)
```

### 2.5 Colab 集成方案

MuJoCo 在 Colab 中使用离屏渲染 + mediapy 展示视频：

```python
# Colab 安装
!pip install mujoco mediapy

import mujoco
import mediapy as media
import numpy as np

# 离屏渲染器
renderer = mujoco.Renderer(model, height=480, width=640)

def render_trajectory(sim, instrument_id, fps=30):
    """录制抓取全流程视频并在 Colab 中播放"""
    frames = []
    # hook 到 mj_step 中采集帧
    original_step = mujoco.mj_step
    def step_and_capture(m, d):
        original_step(m, d)
        renderer.update_scene(d)
        frames.append(renderer.render().copy())
    # 执行运动并采集
    sim.robot_move_fixed(instrument_id)
    media.show_video(frames, fps=fps)
```

## 3. 实施路线

### Phase A: 模型准备

| 步骤 | 内容 | 产出 |
|------|------|------|
| A1 | 从 Dobot ROS 仓库获取 CR5 URDF + mesh | URDF 文件 + STL mesh |
| A2 | URDF → MJCF 转换 + 参数校验 | `cr5_robot.xml` |
| A3 | 添加 DH-3 夹爪模型 | 集成到 CR5 模型末端 |
| A4 | 创建器械简化模型 | `instruments.xml` |
| A5 | 组装完整场景 | `surgbot_scene.xml` |

### Phase B: 控制逻辑

| 步骤 | 内容 | 产出 |
|------|------|------|
| B1 | 实现关节位置伺服控制 | `SurgBotMuJoCoSim` 基类 |
| B2 | 集成逆运动学求解（数值雅可比 IK） | `ik_solve()` 方法 |
| B3 | 复现三阶段运动序列 | `robot_move_fixed()` |
| B4 | 夹爪抓取 + 接触力检测 | 力反馈验证 |

### Phase C: 可视化与集成

| 步骤 | 内容 | 产出 |
|------|------|------|
| C1 | Colab notebook 集成（离屏渲染 + 视频） | `mujoco_simulation.ipynb` |
| C2 | 四种器械轮换演示视频 | Colab 内可播放 |
| C3 | 接触力可视化图表 | 力-时间曲线 |
| C4 | 与 Level 0 Mock 仿真结果对比 | 验证一致性 |

## 4. 关键挑战与应对

| 挑战 | 风险等级 | 应对策略 |
|------|---------|---------|
| CR5 URDF 质量不确定 | 中 | 先用 MuJoCo viewer 目视检查，必要时手动修正 DH 参数 |
| mesh 文件缺失或格式问题 | 中 | 降级为基本几何体（cylinder/box）替代 |
| 逆运动学求解 | 高 | 使用 MuJoCo 内置 `mj_inverse` 或数值雅可比法 |
| Colab 渲染性能 | 低 | 使用离屏渲染 + mediapy，无需 GPU |
| 夹爪-器械接触稳定性 | 中 | 调整接触参数（`solref`/`solimp`），使用 `condim=4` |

## 5. 与 Isaac Sim 的协同

MuJoCo 和 Isaac Sim 不互斥，而是互补：

```
开发调试（快速迭代）  →  MuJoCo（Colab / 本地 CPU）
  ↓ 验证通过
高保真仿真 + 视觉    →  Isaac Sim（GPU 服务器）
  ↓ 模型训练
Sim2Real 迁移        →  真实 CR5 机械臂
```

- **共享模型**：URDF 作为统一中间格式，两个引擎各自转换
- **共享控制接口**：抽象出 `RobotController` 接口，适配 MuJoCo / Isaac / 真实机器
- **分工明确**：MuJoCo 负责控制逻辑验证和力学仿真，Isaac Sim 负责视觉仿真和数据生成

## 6. 预期产出

- [x] MuJoCo 方案建议文档（本文）
- [x] `cr5_robot.xml` — CR5 MJCF 模型（从官方 URDF 转换，含 STL mesh）
- [x] `instruments.xml` — 器械模型（4 种器械 + 托盘）
- [x] `surgbot_scene.xml` — 完整场景（CR5 + 夹爪 + 器械 + 桌面）
- [x] `mujoco_demo.ipynb` — Colab notebook（多角度渲染 + 运动动画）
- [ ] 四种器械 pick-and-place 演示视频（Phase B）
- [ ] 接触力仿真报告（Phase B）

## 相关链接

- [MuJoCo 官方文档](https://mujoco.readthedocs.io/)
- [MuJoCo Playground](https://github.com/google-deepmind/mujoco_playground)
- [Dobot ROS SDK (含URDF)](https://github.com/Dobot-Arm/TCP-IP-ROS-6AXis)
- [Level 0: Colab Mock 仿真](../../progress/v2_fixed_position.md)
- [v2 固定位置模式方案](../../progress/v2_fixed_position.md)
