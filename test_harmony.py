print("=== 和谐度组件测试 ===")
from ochr.config import Config
from ochr.harmony import HarmonyComponents, HarmonyMonitor

print("\n1. 测试 HarmonyComponents 计算和谐度")
h = HarmonyComponents(U=0.8, D=0.6, A=0.2, cost=0.01)
harmony_value = h.compute_h()
print(f"输入: U=0.8, D=0.6, A=0.2, cost=0.01")
print(f"权重: λU={Config.LAMBDA_U}, λD={Config.LAMBDA_D}, λA={Config.LAMBDA_A}, λC={Config.LAMBDA_C}")
print(f"计算结果: H = {harmony_value:.4f}")
print(f"公式: H = λU*U + λD*D - λA*A - λC*cost")
print(f"计算过程: {Config.LAMBDA_U}*{0.8} + {Config.LAMBDA_D}*{0.6} - {Config.LAMBDA_A}*{0.2} - {Config.LAMBDA_C}*{0.01} = {Config.LAMBDA_U*0.8 + Config.LAMBDA_D*0.6 - Config.LAMBDA_A*0.2 - Config.LAMBDA_C*0.01:.4f}")

print("\n2. 测试 HarmonyMonitor 更新")
monitor = HarmonyMonitor()
print(f"初始状态: U={monitor.consistency:.3f}, D={monitor.novelty_level:.3f}, 错误数={monitor.recent_errors}")

monitor.update({"error": False, "new_tool_used": True, "output_consistent": True})
current = monitor.compute()
print(f"更新后状态: U={current.U:.3f}, D={current.D:.3f}, A={current.A:.3f}")

print("\n3. 测试多次更新")
for i in range(5):
    monitor.update({"error": False, "new_tool_used": (i % 2 == 0), "output_consistent": True})
final = monitor.compute()
print(f"5次更新后: U={final.U:.3f}, D={final.D:.3f}, A={final.A:.3f}, H={final.compute_h():.4f}")

print("\n=== 测试完成 ===")