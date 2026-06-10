"""
OCHR 流形计算内核 (Manifold Kernel)
基于晶脉哲学关系本体论：一切皆动子，存在即关系。
"""
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict
import time
import logging

class Mover:
    """流形上的基本存在单元——动子。取代了 Agent、工具、资源等实体概念。"""
    def __init__(self, uid: str, mover_type: str, properties: Dict[str, Any] = None):
        self.uid = uid
        self.type = mover_type  # 'agent', 'tool', 'resource', 'concept'
        self.properties = properties or {}
        self.position: Optional[np.ndarray] = None  # 在流形上的坐标
        self.vector: Optional[np.ndarray] = None    # 状态向量

class RelationEdge:
    """流形上动子之间的关系边"""
    def __init__(self, source: str, target: str, relation_type: str, weight: float = 0.5):
        self.source = source
        self.target = target
        self.type = relation_type  # '触' (因果), '缠' (共存), '律' (稳定模式)
        self.weight = weight

class Manifold:
    """
    流形计算引擎原型。
    管理动子集合与它们之间的动态关系网络。
    """
    def __init__(self):
        self.movers: Dict[str, Mover] = {}
        self.edges: List[RelationEdge] = []
        self.adjacency: Dict[str, List[Tuple[str, RelationEdge]]] = defaultdict(list)

    def add_mover(self, uid: str, mover_type: str, properties: Dict = None) -> Mover:
        mover = Mover(uid, mover_type, properties)
        self.movers[uid] = mover
        return mover

    def add_edge(self, source: str, target: str, rel_type: str, weight: float = 0.5):
        edge = RelationEdge(source, target, rel_type, weight)
        self.edges.append(edge)
        self.adjacency[source].append((target, edge))
        self.adjacency[target].append((source, edge)) # 缠是无向的，触暂时按有向处理但存储双向索引
        return edge

    def get_relation_tension(self, source: str, target: str) -> float:
        """计算两个动子之间的语义或状态张力。直接升级了矛盾捕获器的功能。"""
        mover_a = self.movers.get(source)
        mover_b = self.movers.get(target)
        if not mover_a or not mover_b or mover_a.vector is None or mover_b.vector is None:
            return 0.0
        
        # 简单的余弦相似度计算张力，可升级为更复杂的几何运算
        sim = np.dot(mover_a.vector, mover_b.vector) / (
            np.linalg.norm(mover_a.vector) * np.linalg.norm(mover_b.vector) + 1e-8)
        return max(0.0, -sim) # 负相关产生张力

    def detect_contradictions(self) -> List[Dict]:
        """在整个流形上检测关系矛盾，完全取代旧版矛盾捕获器的正则匹配。"""
        contradictions = []
        for edge in self.edges:
            if edge.type == '触': # 因果关系中的矛盾可能性更高
                tension = self.get_relation_tension(edge.source, edge.target)
                if tension > 0.3:
                    contradictions.append({
                        'source': edge.source, 'target': edge.target,
                        'weight': tension, 'type': 'relational_tension'
                    })
        return contradictions

    def unfold(self, mover_id: str, depth: int = 1) -> List[Tuple[str, float]]:
        """“展”操作：从一个动子出发，沿关系边追踪N步，返回影响范围。"""
        visited = set()
        result = []
        def _dfs(current_id, current_depth, current_weight):
            if current_depth > depth or current_id in visited:
                return
            visited.add(current_id)
            result.append((current_id, current_weight))
            for neighbor_id, edge in self.adjacency[current_id]:
                _dfs(neighbor_id, current_depth + 1, current_weight * edge.weight)
        _dfs(mover_id, 0, 1.0)
        return result