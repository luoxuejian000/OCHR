import time
from typing import Dict, List
from .harmony import HarmonyComponents
from .config import Config

class SelfNarrativeIntegrator:
    """SNI自我叙事整合器——让龙虾拥有自我模型，解决"不好用"痛点"""
    
    def __init__(self):
        self.task_profiles: Dict[str, HarmonyComponents] = {}
        self.narratives: List[str] = []
        self.last_narrative_time = time.time()

    async def update(self, task_type: str, harmony: HarmonyComponents, context: str = ""):
        if task_type not in self.task_profiles:
            self.task_profiles[task_type] = HarmonyComponents()
        prev = self.task_profiles[task_type]
        alpha = 0.1
        prev.U = (1 - alpha) * prev.U + alpha * harmony.U
        prev.D = (1 - alpha) * prev.D + alpha * harmony.D
        prev.A = (1 - alpha) * prev.A + alpha * harmony.A
        prev.cost = (1 - alpha) * prev.cost + alpha * harmony.cost
        self.task_profiles[task_type] = prev
        if time.time() - self.last_narrative_time > Config.SNI_UPDATE_INTERVAL:
            await self._generate_narrative()

    async def _generate_narrative(self):
        high_u = {t: p.U for t, p in self.task_profiles.items() if p.U > 0.7}
        high_a = {t: p.A for t, p in self.task_profiles.items() if p.A > 0.6}
        low_d = {t: p.D for t, p in self.task_profiles.items() if p.D < 0.3}
        narrative = f"[{time.strftime('%Y-%m-%d %H:%M')}] 自我陈述："
        if high_u: narrative += f"我擅长的领域：{list(high_u.keys())}。"
        if high_a: narrative += f"易冲突区域：{list(high_a.keys())}。"
        if low_d: narrative += f"低成长区：{list(low_d.keys())}。"
        if not any([high_u, high_a, low_d]): narrative += "当前无显著模式，仍在积累自我认知。"
        self.narratives.append(narrative)
        self.last_narrative_time = time.time()

    def get_confidence(self, task_type: str) -> float:
        if task_type in self.task_profiles:
            p = self.task_profiles[task_type]
            return max(0.0, min(1.0, p.U - p.A * 0.5))
        return 0.5

    def recommend_mode(self, task_type: str) -> str:
        conf = self.get_confidence(task_type)
        if conf > Config.HARMONY_THRESHOLD_NORMAL: return "normal"
        elif conf > Config.HARMONY_THRESHOLD_CAUTIOUS: return "cautious"
        else: return "delegate"

    def get_self_narrative(self) -> str:
        return self.narratives[-1] if self.narratives else "尚未生成自我认知"