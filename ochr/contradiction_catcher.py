from typing import List, Dict
from .harmony import HarmonyComponents
from .config import Config

class ContradictionCatcher:
    """矛盾捕获器——将无序探索高成本转化为优化信号（沙漠之树原理），解决"用不起"痛点"""
    
    def __init__(self):
        self.cost_log: List[float] = []
        self.inefficient_tools: Dict[str, int] = {}
        self.exploration_noise: float = Config.EXPLORATION_NOISE_BASE

    def update(self, harmony: HarmonyComponents, tool_used: str = ""):
        self.cost_log.append(harmony.cost)
        if harmony.A > 0.6 and harmony.U < 0.4:
            self.inefficient_tools[tool_used] = self.inefficient_tools.get(tool_used, 0) + 1

    def adjust_noise(self, harmony: HarmonyComponents) -> float:
        base = self.exploration_noise
        if harmony.A > 0.7: return min(0.8, base * 1.5)
        elif harmony.A < 0.3 and harmony.U > 0.7: return max(0.05, base * 0.5)
        return base

    def get_recommended_tools(self, available: List[str]) -> List[str]:
        filtered = [t for t in available if self.inefficient_tools.get(t, 0) < 3]
        return filtered if filtered else available

    def summary(self) -> Dict:
        return {
            "total_cost_estimate": sum(self.cost_log),
            "inefficient_tools": dict(self.inefficient_tools),
            "exploration_noise": self.exploration_noise
        }