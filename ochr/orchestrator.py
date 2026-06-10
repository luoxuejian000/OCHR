"""
集群管理器 —— 多节点调度与全局和谐度优化

设计原则（谐振调谐论）：
- 全局和谐度 = Σ(权重_i × 节点H_i)
- 通过社会协商动态调整各节点权重
- 实现集群级别的自我组织与优化
"""

import asyncio
import logging
import random
from typing import Dict, List, Optional, Any
from .node import OCHRNodeV2
from .harmony import HarmonyComponents
from .config import Config

class WeightNegotiation:
    """权重社会协商模块——基于和谐度动态调整λ权重"""
    
    def __init__(self):
        self.negotiation_history: List[Dict] = []
        self.current_lambdas = {
            "U": 0.3,
            "D": 0.3,
            "A": 0.25,
            "C": 0.15
        }
    
    def propose_adjustment(self, current_lambdas: Dict[str, float], harmony_trend: float) -> Dict[str, float]:
        """根据和谐度趋势提出权重调整建议"""
        adjustment = current_lambdas.copy()
        
        if harmony_trend < -0.1:
            adjustment["U"] = min(0.9, adjustment["U"] + 0.05)
            adjustment["A"] = min(0.9, adjustment["A"] + 0.05)
        elif harmony_trend > 0.1:
            adjustment["D"] = min(0.9, adjustment["D"] + 0.05)
            adjustment["C"] = max(0.01, adjustment["C"] - 0.02)
        
        self.negotiation_history.append({
            "timestamp": asyncio.get_event_loop().time(),
            "before": current_lambdas,
            "after": adjustment,
            "trend": harmony_trend
        })
        
        return adjustment
    
    def negotiate(self):
        return self.current_lambdas

class InterNodeBus:
    """节点间通信总线——支持集群内消息传递"""
    
    def __init__(self):
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.subscribers: Dict[str, List[asyncio.Future]] = {}
    
    async def send_message(self, target_node: str, message: Dict):
        """向指定节点发送消息"""
        await self.message_queue.put({
            "target": target_node,
            "message": message,
            "timestamp": asyncio.get_event_loop().time()
        })
    
    async def broadcast(self, message: Dict):
        """向所有节点广播消息"""
        await self.message_queue.put({
            "target": "*",
            "message": message,
            "timestamp": asyncio.get_event_loop().time()
        })
    
    async def receive_message(self, node_name: str) -> Optional[Dict]:
        """接收指定节点的消息"""
        while True:
            msg = await self.message_queue.get()
            if msg["target"] == node_name or msg["target"] == "*":
                return msg["message"]

class MacroOrchestrator:
    """宏调度器——管理多个OCHR节点，优化全局和谐度"""
    
    def __init__(self):
        self.nodes: Dict[str, OCHRNodeV2] = {}
        self.node_weights: Dict[str, float] = {}
        self.global_harmony_history: List[Dict] = []
        self.global_harmony_log: List[HarmonyComponents] = []
        self.negotiator = WeightNegotiation()
    
    async def add_node(self, name: str, workspace: str = "."):
        """创建并注册节点到集群"""
        node = OCHRNodeV2(name, workspace)
        if not node.is_initialized:
            await node.initialize()
        self.nodes[name] = node
        self.node_weights[name] = 1.0
        logging.info(f"节点 {name} 已注册到集群")
    
    async def remove_node(self, node_name: str):
        """从集群中移除节点"""
        if node_name in self.nodes:
            del self.nodes[node_name]
            del self.node_weights[node_name]
            logging.info(f"节点 {node_name} 已从集群移除")
    
    def compute_global_harmony(self) -> float:
        """计算全局和谐度（加权平均）"""
        if not self.nodes:
            return 0.0
        total_weight = sum(self.node_weights.values())
        if total_weight == 0:
            return 0.0
        
        global_h = 0.0
        for name, node in self.nodes.items():
            h = node.harmony_monitor.compute().compute_h()
            global_h += self.node_weights[name] * h
        return global_h / total_weight
    
    async def adaptive_schedule(self, task_type, instruction, temperature=None):
        if temperature is None:
            recent_global_h = [s.compute_h() for s in self.global_harmony_log[-10:]]
            if recent_global_h:
                avg_h = sum(recent_global_h) / len(recent_global_h)
                temperature = max(0.3, min(2.0, 1.0 - avg_h))
            else:
                temperature = 0.8
        candidates = []
        for name, node in self.nodes.items():
            conf = node.sni.get_confidence(task_type)
            h = node.harmony_monitor.compute()
            candidates.append((name, conf, h))
        if not candidates:
            raise RuntimeError("无可用节点")
        if temperature > 1.2:
            weights = []
            for name, conf, h in candidates:
                noise = random.uniform(0, 0.3)
                weights.append(conf - h.A * 0.5 + noise)
            best_idx = weights.index(max(weights))
        else:
            best_idx = max(range(len(candidates)), key=lambda i: candidates[i][1] - candidates[i][2].A * 0.5)
        best = candidates[best_idx]
        node = self.nodes[best[0]]
        res = await node.handle_task(task_type, instruction)
        self.global_harmony_log.append(node.harmony_monitor.compute())
        if len(self.global_harmony_log) % 10 == 0:
            new_lambdas = self.negotiator.negotiate()
            Config.LAMBDA_U = new_lambdas["U"]
            Config.LAMBDA_D = new_lambdas["D"]
            Config.LAMBDA_A = new_lambdas["A"]
            Config.LAMBDA_C = new_lambdas.get("C", Config.LAMBDA_C)
        res["assigned_node"] = best[0]
        res["temperature"] = temperature
        return res

    async def distribute_task(self, task_type, instruction, preferred=None):
        return await self.adaptive_schedule(task_type, instruction)
    
    def compute_cluster_health(self) -> Dict[str, Any]:
        """计算集群健康度报告"""
        if not self.nodes:
            return {"nodes": 0, "avg_U": 0.0, "avg_D": 0.0, "avg_A": 0.0, "H_cluster": 0.0, "lambdas": {}}
        
        total_u, total_d, total_a = 0.0, 0.0, 0.0
        for node in self.nodes.values():
            h = node.harmony_monitor.compute()
            total_u += h.U
            total_d += h.D
            total_a += h.A
        
        n = len(self.nodes)
        return {
            "nodes": n,
            "avg_U": total_u / n,
            "avg_D": total_d / n,
            "avg_A": total_a / n,
            "H_cluster": self.compute_global_harmony(),
            "lambdas": {
                "U": Config.LAMBDA_U,
                "D": Config.LAMBDA_D,
                "A": Config.LAMBDA_A,
                "C": Config.LAMBDA_C
            }
        }
    
    async def rebalance_weights(self):
        """基于和谐度动态重新协商节点权重"""
        for name, node in self.nodes.items():
            h = node.harmony_monitor.compute().compute_h()
            self.node_weights[name] = max(0.1, min(2.0, h * 1.5))
        logging.info("节点权重已重新协商")
    
    async def get_cluster_status(self) -> Dict[str, Any]:
        """获取集群状态报告"""
        status = {
            "nodes": [],
            "global_harmony": self.compute_global_harmony(),
            "total_nodes": len(self.nodes),
            "timestamp": asyncio.get_event_loop().time()
        }
        
        for name, node in self.nodes.items():
            h = node.harmony_monitor.compute()
            node_status = {
                "name": name,
                "weight": self.node_weights[name],
                "harmony": h.to_dict(),
                "mode": node.sni.recommend_mode("general"),
                "boundary_mode": node.boundary_manager.mode.value if node.boundary_manager else "unknown",
                "violations": node.boundary_manager.violation_count if node.boundary_manager else 0
            }
            status["nodes"].append(node_status)
        
        return status
    
    async def monitor_loop(self, interval: float = 10.0):
        """定期监测集群状态"""
        while True:
            status = await self.get_cluster_status()
            self.global_harmony_history.append({
                "timestamp": status["timestamp"],
                "global_h": status["global_harmony"]
            })
            if len(self.global_harmony_history) > 100:
                self.global_harmony_history.pop(0)
            
            if status["global_harmony"] < Config.HARMONY_THRESHOLD_CAUTIOUS:
                logging.warning(f"全局和谐度偏低: {status['global_harmony']:.3f}")
                await self.rebalance_weights()
            
            await asyncio.sleep(interval)