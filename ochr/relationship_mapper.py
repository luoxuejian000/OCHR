"""
关系测绘器 —— 关系本体论的工程实现
安装即场域测绘：扫描环境，生成系统拓扑图

核心理念（关系本体论）：
存在即被关系网络定位。龙虾不是"下载"来的，而是"接入"一个关系场域。
安装的第一步不是配置API密钥，而是让系统感知自己的"关系拓扑"：
- 我能访问哪些文件？
- 我能连接哪些网络？
- 我有哪些工具可用？
- 我的边界在哪里？

此模块将传统"安装配置"转化为"关系测绘"，
让龙虾像田新民在沙漠中先摸清沙、风、温差的脾气一样，
先看清自己的环境，再决定如何行动。

解决痛点：不好装
"""

import os
import socket
import time
import logging
from pathlib import Path
from typing import Dict, Any


class RelationshipMapper:
    """
    关系场域测绘器
    
    启动时自动扫描并生成完整的关系拓扑图，
    替代传统的手动配置安装流程。
    
    测绘内容：
    1. 文件系统访问域（可读/可写/敏感文件过滤）
    2. 网络拓扑（关键服务可达性）
    3. 运行环境依赖（Python版本、已安装包）
    4. 可用工具/Skill接口
    """
    
    def __init__(self, workspace_root: str = "."):
        self.root = Path(workspace_root).resolve()
        self.env_map: Dict[str, Any] = {}
        # 敏感文件模式，扫描时自动跳过
        self.sensitive_patterns = [
            ".env", "credentials", ".pem", ".key", "secret", "token", "password"
        ]

    async def map_environment(self) -> Dict[str, Any]:
        """
        执行完整关系测绘，生成系统拓扑
        
        Returns:
            Dict: 关系地图，包含:
                - workspace: 工作区根目录
                - filesystem: 可访问文件列表及权限
                - network: 网络可达性
                - dependencies: Python依赖环境
                - tools: 已发现工具/Skill
                - timestamp: 测绘时间戳
        """
        logging.info(f"关系测绘启动，根目录：{self.root}")
        
        topology = {
            "workspace": str(self.root),
            "filesystem": await self._scan_filesystem(),
            "network": await self._scan_network(),
            "dependencies": await self._scan_dependencies(),
            "tools": await self._discover_tools(),
            "timestamp": time.time()
        }
        
        self.env_map = topology
        logging.info(f"关系测绘完成：发现 {len(topology['filesystem'])} 个文件, "
                    f"{len(topology['tools'])} 个工具, "
                    f"{len(topology['network'])} 个网络端点")
        return topology

    async def _scan_filesystem(self, max_depth: int = 4) -> Dict:
        """
        扫描文件系统，构建访问树
        
        自动跳过：
        - 隐藏文件（以.开头）
        - 敏感文件（密钥、凭证、token等）
        
        Args:
            max_depth: 最大扫描深度
        Returns:
            Dict: {文件路径: {"readable": bool, "writable": bool}}
        """
        access_tree = {}
        base_depth = len(self.root.parts)
        
        for current_root, dirs, files in os.walk(self.root):
            depth = len(Path(current_root).parts) - base_depth
            if depth > max_depth:
                continue
            
            for f in files:
                # 安全过滤
                if f.startswith('.') or any(p in f for p in self.sensitive_patterns):
                    continue
                
                full_path = os.path.join(current_root, f)
                access_tree[full_path] = {
                    "readable": os.access(full_path, os.R_OK),
                    "writable": os.access(full_path, os.W_OK)
                }
        
        return access_tree

    async def _scan_network(self) -> Dict:
        """
        网络拓扑探测
        
        检测关键服务的可达性，为后续边界声明提供依据
        """
        network = {}
        try:
            network["hostname"] = socket.gethostname()
            
            # 测试关键服务
            test_targets = [
                ("api.openai.com", 443),   # LLM API
                ("localhost", 8080),        # 本地服务
                ("google.com", 80)          # 互联网连通性
            ]
            
            for host, port in test_targets:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    result = sock.connect_ex((host, port))
                    network[f"{host}:{port}"] = "reachable" if result == 0 else "blocked"
                    sock.close()
                except Exception:
                    network[f"{host}:{port}"] = "error"
                    
        except Exception as e:
            network["error"] = str(e)
        
        return network

    async def _scan_dependencies(self) -> Dict:
        """探测Python运行环境与关键依赖"""
        deps = {"python_version": __import__('sys').version}
        try:
            import pkg_resources
            installed = [str(p) for p in pkg_resources.working_set]
            deps["packages"] = installed[:50]
        except ImportError:
            deps["packages"] = "pkg_resources not available"
        return deps

    async def _discover_tools(self) -> Dict[str, str]:
        """
        发现已注册的工具或Skill
        
        在实际集成中，此处应调用OpenClaw的插件接口
        """
        return {
            "file_reader": "内置文件读取",
            "web_search": "需配置API Key",
            "code_interpreter": "已连接Python环境",
            "shell_executor": "受限执行"
        }