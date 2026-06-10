import time
import numpy as np
from typing import List, Dict
from .harmony import HarmonyComponents
from .config import Config

class ContradictionCatcher:
    def __init__(self):
        self.cost_log: List[float] = []
        self.inefficient_tools: Dict[str, int] = {}
        self.exploration_noise: float = Config.EXPLORATION_NOISE_BASE
        self.tension_log: List[Dict] = []
        self.accumulated_tension: float = 0.0
        self.semantic_model = None
        try:
            from sentence_transformers import SentenceTransformer
            self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception:
            pass

    def _compute_tension_weight(self, claim_a, claim_b):
        base_weight = 0.3
        if self.semantic_model is not None:
            try:
                text_a = str(claim_a.get('status', ''))
                text_b = str(claim_b.get('status', ''))
                emb_a = self.semantic_model.encode([text_a], convert_to_numpy=True)[0]
                emb_b = self.semantic_model.encode([text_b], convert_to_numpy=True)[0]
                sim = np.dot(emb_a, emb_b) / (np.linalg.norm(emb_a) * np.linalg.norm(emb_b) + 1e-8)
                if sim < -0.15:
                    base_weight = min(1.0, base_weight + abs(sim))
            except Exception:
                pass
        time_diff = abs(claim_a.get('timestamp', 0) - claim_b.get('timestamp', 0))
        time_boost = max(0, 1.0 - time_diff / 3600) * 0.2
        return min(1.0, base_weight + time_boost)

    def _detect_relational_tensions(self, agent_nodes, resource_states):
        tensions = []
        for resource_id, claims in resource_states.items():
            if len(claims) < 2:
                continue
            for i in range(len(claims)):
                for j in range(i + 1, len(claims)):
                    claim_a = claims[i]
                    claim_b = claims[j]
                    if claim_a.get('agent_id') == claim_b.get('agent_id'):
                        continue
                    if claim_a.get('status') != claim_b.get('status'):
                        tension_weight = self._compute_tension_weight(claim_a, claim_b)
                        tensions.append({
                            'type': 'relational',
                            'resource_id': resource_id,
                            'agent_a': claim_a.get('agent_id'),
                            'agent_b': claim_b.get('agent_id'),
                            'claim_a': claim_a.get('status'),
                            'claim_b': claim_b.get('status'),
                            'weight': tension_weight,
                            'timestamp': time.time()
                        })
        return tensions

    def _log_tension(self, tension):
        self.tension_log.append({
            'timestamp': tension['timestamp'],
            'resource_id': tension['resource_id'],
            'agents': [tension['agent_a'], tension['agent_b']],
            'weight': tension['weight'],
            'type': 'relational'
        })

    def update(self, harmony, tool_used="", agent_nodes=None, resource_states=None):
        self.cost_log.append(harmony.cost)
        if harmony.A > 0.6 and harmony.U < 0.4:
            self.inefficient_tools[tool_used] = self.inefficient_tools.get(tool_used, 0) + 1
        if agent_nodes is not None and resource_states is not None:
            relational_tensions = self._detect_relational_tensions(agent_nodes, resource_states)
            for tension in relational_tensions:
                self._log_tension(tension)
                self.accumulated_tension += tension['weight'] * 0.1

    def adjust_noise(self, harmony):
        base = self.exploration_noise
        if harmony.A > 0.7:
            return min(0.8, base * 1.5)
        elif harmony.A < 0.3 and harmony.U > 0.7:
            return max(0.05, base * 0.5)
        return base

    def get_recommended_tools(self, available):
        return [t for t in available if self.inefficient_tools.get(t, 0) < 3] or available

    def summary(self):
        return {
            "total_cost_estimate": sum(self.cost_log),
            "inefficient_tools": dict(self.inefficient_tools),
            "exploration_noise": self.exploration_noise,
            "accumulated_tension": self.accumulated_tension,
            "tension_count": len(self.tension_log)
        }