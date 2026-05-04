import logging
import time
from typing import Dict, Optional, Any, Callable
from .relationship_mapper import RelationshipMapper
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

    async def initialize(self):
        await super().initialize()
        self.boundary_manager = BoundaryManager(self.topology)
        await self.reflection.start(self)
        logging.info(f"节点 {self.name} 映照腔与边界管理器已启动")

    async def handle_task(self, task_type: str, instruction: str) -> Dict:
        res = await super().handle_task(task_type, instruction)
        harmony = HarmonyComponents(**res["harmony"])
        self.catcher.update(harmony, task_type)
        if harmony.A > 0.8: self.boundary_manager.escalate(BoundaryMode.RESTRICTED, f"高对抗性自动降权 (A={harmony.A:.2f})")
        elif harmony.A < 0.3 and self.boundary_manager.mode == BoundaryMode.RESTRICTED: self.boundary_manager.mode = BoundaryMode.NORMAL
        res["audit"] = self.reflection.generate_audit(time.time() - 60, time.time())
        res["cost_summary"] = self.catcher.summary()
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