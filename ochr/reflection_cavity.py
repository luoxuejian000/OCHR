import asyncio
import time
import logging
from typing import Dict, List, Optional
from .config import Config

class ReflectionCavity:
    """映照腔——实时审计推理链，解决"不好管"痛点"""
    
    def __init__(self, max_entries: int = 5000):
        self.entries: List[Dict] = []
        self.max_entries = max_entries
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self, node, interval: float = Config.REFLECTION_INTERVAL):
        self._running = True
        self._task = asyncio.create_task(self._record_loop(node, interval))
        logging.info(f"映照腔已启动，采样间隔: {interval}秒")

    async def stop(self):
        self._running = False
        if self._task: self._task.cancel()

    async def _record_loop(self, node, interval: float):
        while self._running:
            try:
                snapshot = await self._take_snapshot(node)
                self._add_entry(snapshot)
            except Exception as e:
                logging.error(f"映照腔采样异常: {e}")
            await asyncio.sleep(interval)

    async def _take_snapshot(self, node) -> Dict:
        harmony = node.harmony_monitor.compute()
        reasoning = getattr(node, "last_reasoning", "无")
        tools_active = list(getattr(node, "active_tools", {}).keys())
        boundary_mode = node.boundary_manager.mode.value if node.boundary_manager else "unknown"
        snapshot = {
            "timestamp": time.time(),
            "U": harmony.U, "D": harmony.D, "A": harmony.A, "cost_acc": harmony.cost,
            "reasoning_snippet": str(reasoning)[:200],
            "active_tools": tools_active,
            "boundary_mode": boundary_mode,
            "warnings": []
        }
        if harmony.A > 0.7: snapshot["warnings"].append("高对抗性")
        if harmony.U < 0.3: snapshot["warnings"].append("低统一性")
        if harmony.cost > 100: snapshot["warnings"].append("高成本")
        return snapshot

    def _add_entry(self, entry: Dict):
        self.entries.append(entry)
        if len(self.entries) > self.max_entries: self.entries.pop(0)

    def get_recent(self, n: int = 20) -> List[Dict]:
        return self.entries[-n:]

    def generate_audit(self, start_time: float, end_time: float) -> str:
        relevant = [e for e in self.entries if start_time <= e["timestamp"] <= end_time]
        if not relevant: return "指定时间段内无记录。"
        avg_u = sum(e["U"] for e in relevant) / len(relevant)
        avg_a = sum(e["A"] for e in relevant) / len(relevant)
        total_cost = sum(e.get("cost_acc", 0) for e in relevant)
        report = f"映照审计 [{time.strftime('%H:%M:%S', time.localtime(start_time))} - {time.strftime('%H:%M:%S', time.localtime(end_time))}]\n"
        report += f"平均U: {avg_u:.2f}, 平均A: {avg_a:.2f}, 累计成本: {total_cost:.2f}\n关键事件:\n"
        for e in relevant:
            ts = time.strftime('%H:%M:%S', time.localtime(e["timestamp"]))
            if e.get("warnings"): report += f"  [{ts}] 警告: {e['warnings']}\n"
            report += f"  [{ts}] U={e['U']:.2f} A={e['A']:.2f} 工具:{e['active_tools']}\n"
        return report