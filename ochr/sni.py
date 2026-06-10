import time
from typing import Dict, List
from .harmony import HarmonyComponents
from .config import Config

class SelfNarrativeIntegrator:
    def __init__(self):
        self.task_profiles: Dict[str, HarmonyComponents] = {}
        self.narratives: List[str] = []
        self.last_narrative_time = time.time()

    def generate_causal_narrative(self, task_type, harmony, tension_log, boundary_state):
        narratives = []
        base_narrative = f"任务类型: {task_type}, U={harmony.U:.2f}, D={harmony.D:.2f}, A={harmony.A:.2f}"
        narratives.append(base_narrative)
        if harmony.A > 0.4:
            recent_tensions = [t for t in tension_log if time.time() - t['timestamp'] < 3600] if tension_log else []
            if recent_tensions:
                resource_conflicts = {}
                for t in recent_tensions:
                    rid = t['resource_id']
                    if rid not in resource_conflicts:
                        resource_conflicts[rid] = []
                    resource_conflicts[rid].append(t)
                most_conflicted = max(resource_conflicts.items(), key=lambda x: len(x[1]))
                causal_narrative = (
                    f"A值升高({harmony.A:.2f})的主要原因是资源'{most_conflicted[0]}'"
                    f"上存在{len(most_conflicted[1])}次状态声明冲突。"
                )
                narratives.append(causal_narrative)
        if boundary_state and boundary_state.get('mode') == 'restricted':
            narratives.append(f"当前边界已自动降级为受限模式，由高A值触发。")
        if harmony.D > 0.6 and harmony.A > 0.4:
            narratives.append(f"系统正在尝试新方法(D={harmony.D:.2f})，但新方法与现有承诺之间存在张力(A={harmony.A:.2f})。")
        return "\n".join(narratives)

    async def update(self, task_type, harmony, context="", tension_log=None, boundary_state=None):
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
            await self._generate_narrative(tension_log, boundary_state)

    async def _generate_narrative(self, tension_log=None, boundary_state=None):
        narrative_parts = []
        for task_type, profile in self.task_profiles.items():
            story = self.generate_causal_narrative(task_type, profile, tension_log, boundary_state)
            narrative_parts.append(story)
        narrative = f"[{time.strftime('%Y-%m-%d %H:%M')}] 自我反思:\n" + "\n---\n".join(narrative_parts)
        self.narratives.append(narrative)
        self.last_narrative_time = time.time()

    def get_confidence(self, task_type):
        if task_type in self.task_profiles:
            p = self.task_profiles[task_type]
            return max(0.0, min(1.0, p.U - p.A * 0.5))
        return 0.5

    def recommend_mode(self, task_type):
        conf = self.get_confidence(task_type)
        if conf > Config.HARMONY_THRESHOLD_NORMAL:
            return "normal"
        elif conf > Config.HARMONY_THRESHOLD_CAUTIOUS:
            return "cautious"
        else:
            return "delegate"

    def get_self_narrative(self):
        return self.narratives[-1] if self.narratives else "尚未生成自我认知"