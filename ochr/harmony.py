"""
和谐度四元组与实时监测器
矛盾动力论的量化表达 —— H = λ_U·U + λ_D·D - λ_A·A - λ_C·C

核心理念：
和谐不是矛盾的消除，而是矛盾各方在运动中达到的积极的、动态的平衡。
- U (Unity): 统一性 —— 输出一致性、逻辑自洽程度 [0, 1]
- D (Development): 发展性 —— 探索潜力、新路径涌现频率 [0, 1]
- A (Antagonism): 对抗性 —— 内部冲突、错误率与重试频率 [0, 1]
- cost: 资源消耗 —— Token数量或执行时间

设计依据（矛盾动力论）：
系统的演化由 H 的梯度流驱动：∂Ψ/∂t = -κ · δH/δΨ
智能体在"目标引导(梯度下降)"与"随机探索(噪声)"之间平衡，
逐步逼近全局和谐态。
"""

import time
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from .config import Config


@dataclass
class HarmonyComponents:
    """
    和谐度四元组快照
    
    四个维度完整刻画系统在某一时刻的"谐振状态"：
    - 高U低A：稳定输出，可自主运行
    - 高D低A：积极创新，风险可控
    - 高U高A：输出一致但内部冲突剧烈（伪和谐）
    - 低U高A：混乱状态，需人工介入
    - 高D高A：探索激进，风险隐患
    """
    U: float = 0.5  # 统一性 (Unity)
    D: float = 0.5  # 发展性 (Development)
    A: float = 0.5  # 对抗性 (Antagonism)
    cost: float = 0.0  # 资源消耗
    timestamp: float = field(default_factory=time.time)

    def compute_h(self, lambdas: Optional[Dict[str, float]] = None) -> float:
        """
        计算加权和谐度 H
        
        公式：H = λ_U·U + λ_D·D - λ_A·A - λ_C·cost
        
        Args:
            lambdas: 权重字典，默认使用Config中的社会协商值
            
        Returns:
            float: 和谐度值，钳制在 [-1.0, 1.0]
                    > 0.7: 高和谐态，可自主运行
                    0.4-0.7: 中等，需监控
                    < 0.4: 低和谐态，需调谐介入
        """
        if lambdas is None:
            lambdas = {
                "U": Config.LAMBDA_U,
                "D": Config.LAMBDA_D,
                "A": Config.LAMBDA_A,
                "C": Config.LAMBDA_C
            }
        h = lambdas["U"] * self.U + lambdas["D"] * self.D \
            - lambdas["A"] * self.A - lambdas["C"] * self.cost
        return max(min(h, 1.0), -1.0)

    def to_dict(self) -> Dict:
        """序列化为字典，便于JSON传输和审计日志"""
        return {
            "U": self.U,
            "D": self.D,
            "A": self.A,
            "cost": self.cost,
            "timestamp": self.timestamp
        }
    
    def __repr__(self) -> str:
        return (f"HarmonyComponents(U={self.U:.3f}, D={self.D:.3f}, "
                f"A={self.A:.3f}, cost={self.cost:.4f}, H={self.compute_h():.3f})")


class HarmonyMonitor:
    """
    实时估计 U, D, A 代理指标
    
    设计原理：
    - U 基于输出一致性：历史输出是否逻辑自洽
    - D 基于探索新颖度：是否使用新工具/新推理路径
    - A 基于错误率：工具调用失败、指令违反、冲突回退
    
    在实际部署中，这些代理指标应替换为更精确的测量：
    - U: 基于LLM输出的语义嵌入余弦相似度
    - D: 基于新工具调用种类/新推理模板的统计
    - A: 基于实际错误率、用户投诉、自我修正次数、Token浪费比例
    """
    
    def __init__(self):
        self.recent_errors: int = 0       # 近期错误计数（用于A）
        self.novelty_level: float = 0.5   # 新颖度 (0-1)（用于D）
        self.consistency: float = 0.7     # 一致性 (0-1)（用于U）
        self.step_count: int = 0          # 总步数

    def update(self, result: Dict[str, Any]):
        """
        根据单步执行结果更新代理指标
        
        Args:
            result: 执行结果字典，需包含:
                - error: bool, 是否出错
                - new_tool_used: bool, 是否使用新工具/路径
                - output_consistent: bool, 输出是否与历史一致
        """
        self.step_count += 1
        
        # 更新错误率 → A (对抗性)
        if result.get("error"):
            self.recent_errors += 1
        else:
            # 成功时缓慢衰减错误计数（遗忘机制）
            self.recent_errors = max(0, self.recent_errors - 0.1)
        
        # 更新新颖度 → D (发展性)
        if result.get("new_tool_used") or result.get("new_path"):
            self.novelty_level = min(1.0, self.novelty_level + 0.15)
        else:
            # 重复模式时缓慢衰减
            self.novelty_level = max(0.0, self.novelty_level - 0.02)
        
        # 更新一致性 → U (统一性)
        if result.get("output_consistent", True):
            self.consistency = min(1.0, self.consistency + 0.03)
        else:
            self.consistency = max(0.0, self.consistency - 0.08)

    def compute(self, token_cost: float = 0.0) -> HarmonyComponents:
        """
        返回当前和谐度快照
        
        A值归一化公式：A = errors / (errors + 3)
        当错误数为0时 A≈0，错误数→∞时 A→1
        """
        a_normalized = min(1.0, self.recent_errors / (self.recent_errors + 3.0))
        return HarmonyComponents(
            U=self.consistency,
            D=self.novelty_level,
            A=a_normalized,
            cost=token_cost
        )
    
    def reset(self):
        """重置所有指标到初始状态"""
        self.recent_errors = 0
        self.novelty_level = 0.5
        self.consistency = 0.7
        self.step_count = 0