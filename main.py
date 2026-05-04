import asyncio
import logging
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ochr.orchestrator import MacroOrchestrator

BOUNDARY_NOTICE = """
╔══════════════════════════════════════════════════════════╗
║         OCHR 谐振龙虾集群 —— 边界与诚实声明                ║
╠══════════════════════════════════════════════════════════╣
║  本系统基于晶脉哲学与谐振理论构建，旨在解决当前龙虾          ║
║  集群的五大痛点：不好装、不好用、不好管、不安全、用不起。     ║
║  它能做的：                                                ║
║  1. 关系测绘自动适应环境，大幅降低安装门槛                  ║
║  2. SNI自我模型提供稳定区间与信心，减少不稳定输出           ║
║  3. 映照腔提供可审计推理链，管理者不再面对黑箱              ║
║  4. 边界声明与沙箱实现动态安全防御，自动降权对抗风险        ║
║  5. 矛盾捕获器将成本失控转化为调谐信号，优化资源利用        ║
║  6. 多节点集群可根据和谐度动态分配任务，权重社会协商        ║
║  它不能做的：                                              ║
║  1. 不能消除所有不安全：沙箱无法防御零日漏洞                ║
║  2. 不能将龙虾变为永不犯错的员工：泛化与不确定性同源        ║
║  3. 不能替代人类最终决策：系统提供建议，责任仍属人类        ║
║  谐振治理不是消除矛盾，而是让矛盾在可感知、可调谐的          ║
║  场域中定向做功。                                          ║
║  作者：李广好   协议：Apache License 2.0   版本：1.0.0       ║
╚══════════════════════════════════════════════════════════╝
"""

async def full_demo():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    print(BOUNDARY_NOTICE)
    print("\n" + "=" * 60)
    print("初始化 OCHR 谐振龙虾集群...")
    print("=" * 60 + "\n")
    orchestrator = MacroOrchestrator()
    print("创建节点 alpha...")
    await orchestrator.add_node("alpha", "./ws_alpha")
    print("创建节点 beta...")
    await orchestrator.add_node("beta", "./ws_beta")
    print("创建节点 gamma...")
    await orchestrator.add_node("gamma", "./ws_gamma")
    print(f"\n集群就绪，共 {len(orchestrator.nodes)} 个节点。\n")
    print("=" * 60)
    print("开始任务分发模拟 (共12轮)...")
    print("=" * 60 + "\n")
    task_types = ["data_analysis", "code_generation", "summarization", "translation"]
    for i in range(12):
        ttype = task_types[i % len(task_types)]
        instruction = f"执行 {ttype} 任务 #{i+1}"
        res = await orchestrator.distribute_task(ttype, instruction)
        harmony = res["harmony"]
        print(f"任务 {i+1:02d} | 类型: {ttype:20s} | 分配至: {res['assigned_node']:6s} | U={harmony['U']:.2f} D={harmony['D']:.2f} A={harmony['A']:.2f} | 模式: {res['mode']}")
    print("\n" + "=" * 60)
    print("集群健康报告")
    print("=" * 60 + "\n")
    health = orchestrator.compute_cluster_health()
    print(f"节点数:         {health['nodes']}")
    print(f"平均统一性 U:   {health['avg_U']:.3f}")
    print(f"平均发展性 D:   {health['avg_D']:.3f}")
    print(f"平均对抗性 A:   {health['avg_A']:.3f}")
    print(f"集群和谐度 H:   {health['H_cluster']:.3f}")
    print(f"当前协商权重:   U={health['lambdas']['U']:.2f} D={health['lambdas']['D']:.2f} A={health['lambdas']['A']:.2f} C={health['lambdas']['C']:.2f}")
    print("\n" + "=" * 60)
    print("节点自我叙事 (alpha)")
    print("=" * 60 + "\n")
    alpha = orchestrator.nodes["alpha"]
    print(alpha.sni.get_self_narrative())
    print("\n" + "=" * 60)
    print("映照审计报告 (alpha, 最近60秒)")
    print("=" * 60 + "\n")
    audit = alpha.reflection.generate_audit(time.time() - 60, time.time())
    print(audit)
    print("\n" + "=" * 60)
    print("演示完成。")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(full_demo())