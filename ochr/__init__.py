"""
OCHR (OpenClaw-Hermes-Resonance) 谐振龙虾集群

基于晶脉哲学四重公理构建的下一代 AI Agent 集群框架：
- 关系本体论：一切由关系网络定义。安装即场域测绘。
- 矛盾动力论：矛盾是演化的引擎。和谐度H驱动自我调谐。
- 实践介入论：每次操作都介入场域。映照腔记录每一步。
- 谐振调谐论：系统朝向更高和谐度自组织。权重可社会协商。

本项目将 OpenClaw 龙虾从"裸天才"升级为：
拥有自我叙事(SNI)、可审计推理(映照腔)、动态安全边界、
成本矛盾捕获能力的谐振集群。

核心模块：
- config.py           全局配置与λ权重
- harmony.py          和谐度四元组(H = λU*U + λD*D - λA*A - λC*C)
- relationship_mapper 关系测绘器(解决"不好装")
- sni.py              SNI自我叙事整合器(解决"不好用")
- reflection_cavity   映照腔审计系统(解决"不好管")
- boundary.py         动态边界与安全沙箱(解决"不安全")
- contradiction_catcher 矛盾捕获器(解决"用不起")
- node.py             OCHR节点(集成所有模块)
- orchestrator.py     集群管理器(多节点调度与全局和谐度)

版本：1.0.0
作者：李广好
协议：Apache License 2.0
"""

__version__ = "1.0.0"
__author__ = "李广好"
__license__ = "Apache License 2.0"

# 公开核心接口，方便外部调用
from .harmony import HarmonyComponents, HarmonyMonitor
from .node import OCHRNodeV2
from .orchestrator import MacroOrchestrator

__all__ = [
    "HarmonyComponents",
    "HarmonyMonitor",
    "OCHRNodeV2",
    "MacroOrchestrator",
]