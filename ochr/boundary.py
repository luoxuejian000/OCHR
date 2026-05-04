import asyncio
import logging
import os
from typing import Dict, Tuple, Any, Callable, Set
from enum import Enum
from .harmony import HarmonyComponents, HarmonyMonitor

class BoundaryMode(Enum):
    NORMAL = "normal"
    RESTRICTED = "restricted"
    LOCKDOWN = "lockdown"

class BoundaryManager:
    """边界声明——根据关系测绘设定操作域，动态调整权限"""
    
    def __init__(self, topology: Dict):
        self.allowed_paths = set(topology.get("filesystem", {}).keys())
        self.allowed_networks = set()
        net_info = topology.get("network", {})
        for key, status in net_info.items():
            if status == "reachable": self.allowed_networks.add(key)
        self.allowed_tools = set(topology.get("tools", {}).keys())
        self.explicit_deny: Set[str] = set()
        self.mode = BoundaryMode.NORMAL
        self.violation_count = 0

    def current_boundary(self) -> Dict:
        return {
            "mode": self.mode.value,
            "allowed_paths_sample": list(self.allowed_paths)[:10],
            "allowed_networks": list(self.allowed_networks),
            "allowed_tools": list(self.allowed_tools),
            "violation_count": self.violation_count
        }

    def check(self, action_type: str, target: str) -> Tuple[bool, str]:
        if self.mode == BoundaryMode.LOCKDOWN: return False, "系统锁定"
        if self.mode == BoundaryMode.RESTRICTED and action_type != "file_access":
            return False, "受限模式：仅允许基本文件读取"
        if action_type == "file_access":
            if target in self.explicit_deny:
                self.violation_count += 1
                return False, f"文件 {target} 被禁止"
            if target in self.allowed_paths: return True, ""
            for path in self.allowed_paths:
                if target.startswith(path + os.sep) or target == path: return True, ""
            self.violation_count += 1
            return False, f"路径 {target} 不在允许范围内"
        elif action_type == "network":
            if target in self.allowed_networks: return True, ""
            return False, f"网络目标 {target} 未授权"
        elif action_type == "tool_call":
            if target in self.allowed_tools and target not in self.explicit_deny: return True, ""
            return False, f"工具 {target} 未授权或禁止"
        return False, "未知操作"

    def escalate(self, new_mode: BoundaryMode, reason: str = ""):
        if new_mode.value != self.mode.value:
            logging.warning(f"边界升级: {self.mode.value} -> {new_mode.value}, 原因: {reason}")
        self.mode = new_mode

    def reset_violations(self): self.violation_count = 0


class SecuritySandbox:
    """谐振沙箱——在受限环境试运行工具，监测和谐度变化评估风险"""
    
    def __init__(self, harmony_monitor: HarmonyMonitor):
        self.monitor = harmony_monitor
        self.risk_scores: Dict[str, float] = {}

    async def execute(self, tool_name: str, func: Callable, args: tuple, kwargs: dict) -> Tuple[Any, HarmonyComponents]:
        pre_h = self.monitor.compute()
        try:
            result = await asyncio.wait_for(asyncio.to_thread(func, *args, **kwargs), timeout=10.0)
        except Exception:
            self.monitor.update({"error": True, "output_consistent": False})
            post_h = self.monitor.compute()
            return None, post_h
        else:
            self.monitor.update({"error": False, "output_consistent": True})
            post_h = self.monitor.compute()
            return result, post_h

    def assess_risk(self, tool_name: str, pre: HarmonyComponents, post: HarmonyComponents) -> str:
        delta_a = post.A - pre.A
        delta_u = post.U - pre.U
        risk = delta_a - delta_u
        self.risk_scores[tool_name] = risk
        if risk > 0.3: return "suspicious"
        elif risk < -0.1: return "safe"
        else: return "neutral"