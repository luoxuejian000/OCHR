# OCHR —— 谐振龙虾集群

基于**晶脉哲学**与**谐振理论**构建的 AI Agent 集群框架。

## 核心思想

万物皆为关系网络中的节点。OCHR 将 OpenClaw 龙虾从一个"裸天才"升级为**有自知、可审计、守边界、能协商**的谐振集群。

## 五大痛点与对策

| 痛点 | 解决方案 | 核心模块 |
|------|----------|----------|
| 不好装 | 关系测绘自动生成环境拓扑 | `relationship_mapper.py` |
| 不好用 | SNI 自我模型，信心指数与行为建议 | `sni.py` |
| 不好管 | 映照腔：实时审计推理链 | `reflection_cavity.py` |
| 不安全 | 动态边界声明 + 谐振沙箱 + 自动降权 | `boundary.py` |
| 用不起 | 矛盾捕获器：成本转化为调谐信号 | `contradiction_catcher.py` |

## 四重哲学公理

| 公理 | 核心命题 | 工程映射 |
|------|---------|----------|
| 关系本体论 | 一切由关系网络定义，安装即场域测绘 | `relationship_mapper.py` |
| 矛盾动力论 | 矛盾是演化的引擎，H波动驱动自我调谐 | `harmony.py` + `contradiction_catcher.py` |
| 实践介入论 | 每次操作都介入场域，必须可审计 | `reflection_cavity.py` |
| 谐振调谐论 | 系统朝向更高和谐度自组织，权重可协商 | `config.py` + `orchestrator.py` |

## 快速开始

```bash
pip install -r requirements.txt
python main.py
```

## 项目结构

```
OCHR/
├── README.md
├── LICENSE
├── requirements.txt
├── main.py
└── ochr/
    ├── __init__.py
    ├── config.py
    ├── harmony.py
    ├── relationship_mapper.py
    ├── sni.py
    ├── reflection_cavity.py
    ├── boundary.py
    ├── contradiction_catcher.py
    ├── node.py
    └── orchestrator.py
```

## 和谐度函数

系统核心评估标尺：**H = λᵤ·U + λᴅ·D - λₐ·A - λ꜀·C**

| 维度 | 含义 | 范围 |
|------|------|------|
| U | 统一性（输出一致性） | [0, 1] |
| D | 发展性（探索潜力） | [0, 1] |
| A | 对抗性（内部冲突） | [0, 1] |
| C | 成本（Token/时间） | ≥0 |

## 依赖

OCHR 内嵌 `https://github.com/luoxuejian000/-thinkcheck-lib-/tree/3.0-harmony-sdk` 作为可选评估引擎。

## 运行示例

```
╔══════════════════════════════════════════════════════════╗
║         OCHR 谐振龙虾集群 —— 边界与诚实声明                ║
╚══════════════════════════════════════════════════════════╝

初始化 OCHR 谐振龙虾集群...
创建节点 alpha... beta... gamma...

开始任务分发模拟 (共12轮)...
任务 01 | 类型: data_analysis | 分配至: alpha | U=0.73 D=0.68 A=0.25 | 模式: normal
...

集群健康报告
节点数: 3
平均统一性 U: 0.735
平均发展性 D: 0.592
平均对抗性 A: 0.267
集群和谐度 H: 0.412
```

## 边界声明

**能做的：**
- 关系测绘自动适应环境
- SNI自我模型提供稳定区间与信心
- 映照腔可审计推理链
- 边界声明与沙箱动态安全防御
- 矛盾捕获器优化资源利用
- 多节点集群动态任务分配

**不能做的：**
- 消除所有不安全（沙箱无法防御零日漏洞）
- 让龙虾永不犯错（泛化与不确定性同源）
- 替代人类最终决策

## 作者

李广好

## 协议

Apache License 2.0