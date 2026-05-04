"""
OCHR 全局配置与λ权重初始值

设计原则（谐振调谐论）：
- 所有权重都可以通过 WeightNegotiation 模块重新协商
- 初始值是"协商起点"，而非"最终真理"
- 杜绝价值黑箱：每个参数的取值都有明确的哲学依据和工程理由
"""

class Config:
    """可协商的全局配置，对应社会协商产生的λ权重"""
    
    # ============ 和谐度权重系数 ============
    # H = λ_U·U + λ_D·D - λ_A·A - λ_C·C
    # 初始取值依据：在AI Agent场景中，统一性(稳定输出)最为重要(0.4)，
    # 发展性(探索新路径)与对抗性(冲突惩罚)同等次之(各0.3)，
    # 成本系数初始较小(0.1)，随系统运行可动态调高
    LAMBDA_U: float = 0.4       # 统一性权重
    LAMBDA_D: float = 0.3       # 发展性权重
    LAMBDA_A: float = 0.3       # 对抗性权重
    LAMBDA_C: float = 0.1       # 成本权重
    
    # ============ 系统运行参数 ============
    SNI_UPDATE_INTERVAL: float = 3600.0    # SNI 自我陈述更新间隔(秒)，默认1小时
    REFLECTION_INTERVAL: float = 1.0       # 映照腔采样间隔(秒)，每秒快照一次
    MAX_BOUNDARY_VIOLATIONS: int = 3       # 越界容忍次数，超过触发降权
    SHORT_TERM_WINDOW: int = 100           # 短期记忆轮次，用于局部趋势分析
    
    # ============ 矛盾捕获器参数 ============
    EXPLORATION_NOISE_BASE: float = 0.2    # 基础探索噪声幅度
    # 噪声动态范围：[0.05, 0.8]
    # 高A时噪声增大(帮助逃脱局部最优)，低A高U时噪声减小(节省成本)
    
    # ============ 行为模式阈值 ============
    # 信心 = U - 0.5*A
    HARMONY_THRESHOLD_CAUTIOUS: float = 0.4   # 低于此值进入审慎模式
    HARMONY_THRESHOLD_NORMAL: float = 0.7     # 高于此值进入正常自主模式
    # 介于两者之间 → cautious模式(增加验证步骤)
    # 低于cautious → delegate模式(建议转交人类)
    
    # ============ 工作区配置 ============
    WORKSPACE_ROOT: str = "."