import logging
import time
import numpy as np
from typing import Dict, Optional, Any, Callable
from .relationship_mapper import RelationshipMapper
from .manifold import Manifold
from .harmony import HarmonyComponents, HarmonyMonitor
from .sni import SelfNarrativeIntegrator
from .reflection_cavity import ReflectionCavity
from .boundary import BoundaryManager, BoundaryMode, SecuritySandbox
from .contradiction_catcher import ContradictionCatcher

class OCHRNodeBase:
    """谐振龙虾节点基类——集成关系测绘、和谐度监测、SNI自我模型"""
    
    def __init__(self, name: str, workspace: str = "."):
        self.name = name
        self.workspace = workspace
        self.mapper = RelationshipMapper(workspace)
        self.harmony_monitor = HarmonyMonitor()
        self.sni = SelfNarrativeIntegrator()
        self.topology: Dict = {}
        self.is_initialized = False

    async def initialize(self):
        self.topology = await self.mapper.map_environment()
        self.is_initialized = True
        logging.info(f"节点 {self.name} 关系测绘完成，已就绪。")

    async def handle_task(self, task_type: str, instruction: str) -> Dict:
        if not self.is_initialized: await self.initialize()
        mock_result = {
            "reply": f"已完成 {task_type}: {instruction[:40]}...",
            "error": False,
            "new_tool_used": (hash(task_type) % 2 == 0),
            "output_consistent": True,
            "token_cost": 0.02
        }
        self.harmony_monitor.update(mock_result)
        harmony = self.harmony_monitor.compute(mock_result.get("token_cost", 0))
        await self.sni.update(task_type, harmony, instruction)
        mode = self.sni.recommend_mode(task_type)
        if mode == "delegate": mock_result["reply"] += " [警告：此项任务信心不足，建议人工介入]"
        return {"harmony": harmony.to_dict(), "mode": mode, "sni_narrative": self.sni.get_self_narrative(), "result": mock_result}


class OCHRNodeV2(OCHRNodeBase):
    """升级版节点——集成映照腔、安全边界、矛盾捕获器，完整解决五大痛点"""
    
    def __init__(self, name: str, workspace: str = "."):
        super().__init__(name, workspace)
        self.reflection = ReflectionCavity()
        self.boundary_manager: Optional[BoundaryManager] = None
        self.sandbox = SecuritySandbox(self.harmony_monitor)
        self.catcher = ContradictionCatcher()
        self.last_reasoning = ""
        self.active_tools = {}
        self.manifold = Manifold()
        self.manifold.add_mover(self.name, 'agent', {'workspace': workspace})

    async def initialize(self):
        await super().initialize()
        self.boundary_manager = BoundaryManager(self.topology)
        await self.reflection.start(self)
        logging.info(f"节点 {self.name} 映照腔与边界管理器已启动")

    async def handle_task(self, task_type: str, instruction: str) -> Dict:
        res = await super().handle_task(task_type, instruction)
        harmony = HarmonyComponents(**res["harmony"])
        resource_id = f"resource_{task_type}"
        if resource_id not in self.manifold.movers:
            self.manifold.add_mover(resource_id, 'resource', {'task': task_type})
        self.manifold.add_edge(self.name, resource_id, '触', weight=0.8)
        harmony_vec = np.array([harmony.U, harmony.D, harmony.A, harmony.compute_h()])
        for mover_id in [self.name, resource_id]:
            mover = self.manifold.movers.get(mover_id)
            if mover:
                mover.vector = harmony_vec
        manifold_contradictions = self.manifold.detect_contradictions()
        for contradiction in manifold_contradictions:
            if not hasattr(self.catcher, 'tension_log'):
                self.catcher.tension_log = []
            self.catcher.tension_log.append({
                'timestamp': time.time(),
                'resource_id': contradiction['source'],
                'agents': [contradiction['source'], contradiction['target']],
                'weight': contradiction['weight'],
                'type': 'manifold'
            })
            self.catcher.accumulated_tension += contradiction['weight'] * 0.1
        self.catcher.update(
            harmony, task_type,
            agent_nodes=getattr(self, 'agent_nodes', None),
            resource_states=getattr(self, 'resource_states', None)
        )
        if harmony.A > 0.8:
            self.boundary_manager.escalate(BoundaryMode.RESTRICTED, f"高对抗性自动降权 (A={harmony.A:.2f})")
        elif harmony.A < 0.3 and self.boundary_manager.mode == BoundaryMode.RESTRICTED:
            self.boundary_manager.mode = BoundaryMode.NORMAL
        if hasattr(self.boundary_manager, 'adaptive_contract') and hasattr(self.catcher, 'tension_log'):
            self.boundary_manager.adaptive_contract(self.catcher.tension_log, harmony)
        res["audit"] = self.reflection.generate_audit(time.time() - 60, time.time())
        res["cost_summary"] = self.catcher.summary()
        await self.sni.update(
            task_type, harmony, instruction,
            tension_log=getattr(self.catcher, 'tension_log', None),
            boundary_state=self.boundary_manager.current_boundary() if self.boundary_manager else None
        )
        if hasattr(self, 'manifold'):
            unfolded = self.manifold.unfold(self.name, depth=2)
            influential_nodes = [uid for uid, w in unfolded if w > 0.5]
            self.last_manifold_context = f"流形影响范围: {influential_nodes}"
        return res

    async def execute_tool_sandboxed(self, tool_name: str, func: Callable, *args, **kwargs) -> Any:
        if self.boundary_manager:
            allowed, reason = self.boundary_manager.check("tool_call", tool_name)
            if not allowed: raise PermissionError(f"边界拒绝: {reason}")
        pre_h = self.harmony_monitor.compute()
        result, post_h = await self.sandbox.execute(tool_name, func, args, kwargs)
        risk = self.sandbox.assess_risk(tool_name, pre_h, post_h)
        if risk == "suspicious": self.boundary_manager.escalate(BoundaryMode.RESTRICTED, f"可疑工具 {tool_name}")
        return result