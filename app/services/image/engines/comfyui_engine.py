"""
ComfyUI Engine
负责调用本地 ComfyUI 工作流
"""
import json
import requests
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Optional, Callable

from app.services.image.engines.base import EngineBase, EngineType


class ComfyUIEngine(EngineBase):
    """ComfyUI Engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化 ComfyUI Engine
        
        Args:
            config: ComfyUI 配置（包含 comfyui_url, workflow_path 等）
        """
        super().__init__(config)
        self.engine_type = EngineType.COMFYUI
        
        # 从配置中获取 ComfyUI 信息
        self.comfyui_url = self.get_config("comfyui_url", "http://localhost:8188")
        self.workflow_path = self.get_config("workflow_path")
        self.timeout = self.get_config("timeout", 300)
        self.poll_interval = self.get_config("poll_interval", 2)  # 轮询间隔（秒）
        
        # 客户端 ID（用于识别）
        self.client_id = str(uuid.uuid4())
    
    def execute(self, input_data: Any, **kwargs) -> Any:
        """
        执行 ComfyUI 工作流
        
        Args:
            input_data: 输入数据
            **kwargs: 其他参数
            
        Returns:
            Any: 工作流执行结果
        """
        self._log(f"执行 ComfyUI 工作流: {self.workflow_path}")
        
        # 1. 验证输入
        if not self.validate_input(input_data):
            raise ValueError("输入数据验证失败")
        
        # 2. 加载工作流定义
        workflow = self._load_workflow()
        
        # 3. 注入输入数据
        workflow_with_input = self._inject_input(workflow, input_data, **kwargs)
        
        # 4. 提交工作流
        prompt_id = self._submit_workflow(workflow_with_input)
        
        # 5. 等待执行完成
        result = self._wait_for_completion(prompt_id)
        
        self._log("ComfyUI 工作流执行成功")
        
        return result
    
    def validate_input(self, input_data: Any) -> bool:
        """
        验证输入数据
        
        Args:
            input_data: 输入数据
            
        Returns:
            bool: 是否有效
        """
        # 检查工作流文件是否存在
        if self.workflow_path and not Path(self.workflow_path).exists():
            self._log(f"工作流文件不存在: {self.workflow_path}", "ERROR")
            return False
        
        return True
    
    def _load_workflow(self) -> Dict:
        """
        加载工作流定义
        
        Returns:
            Dict: 工作流 JSON
        """
        try:
            with open(self.workflow_path, 'r', encoding='utf-8') as f:
                workflow = json.load(f)
            
            self._log(f"工作流加载成功: {self.workflow_path}")
            return workflow
            
        except Exception as e:
            raise Exception(f"加载工作流失败: {e}")
    
    def _inject_input(self, workflow: Dict, input_data: Any, **kwargs) -> Dict:
        """
        注入输入数据到工作流
        
        Args:
            workflow: 工作流定义
            input_data: 输入数据
            **kwargs: 其他参数
            
        Returns:
            Dict: 注入后的工作流
        """
        # 复制工作流，避免修改原始数据
        workflow = workflow.copy()
        
        # 从配置中获取节点映射
        node_mappings = self.get_config("node_mappings", {})
        
        # 如果输入是字典，根据映射注入
        if isinstance(input_data, dict):
            for key, value in input_data.items():
                if key in node_mappings:
                    node_id, field = node_mappings[key].split(".")
                    if node_id in workflow:
                        workflow[node_id]["inputs"][field] = value
        
        # 注入额外参数
        for key, value in kwargs.items():
            if key in node_mappings:
                node_id, field = node_mappings[key].split(".")
                if node_id in workflow:
                    workflow[node_id]["inputs"][field] = value
        
        return workflow
    
    def _submit_workflow(self, workflow: Dict) -> str:
        """
        提交工作流到 ComfyUI
        
        Args:
            workflow: 工作流定义
            
        Returns:
            str: Prompt ID
        """
        try:
            # 构建提交数据
            payload = {
                "prompt": workflow,
                "client_id": self.client_id
            }
            
            # 发送请求
            url = f"{self.comfyui_url}/prompt"
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            prompt_id = result.get("prompt_id")
            
            if not prompt_id:
                raise Exception("未获取到 prompt_id")
            
            self._log(f"工作流已提交，Prompt ID: {prompt_id}")
            
            return prompt_id
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"提交工作流失败: {e}")
        except Exception as e:
            raise Exception(f"提交工作流异常: {e}")
    
    def _wait_for_completion(self, prompt_id: str) -> Any:
        """
        等待工作流执行完成
        
        Args:
            prompt_id: Prompt ID
            
        Returns:
            Any: 执行结果
        """
        start_time = time.time()
        
        while True:
            # 检查超时
            if time.time() - start_time > self.timeout:
                raise TimeoutError(f"工作流执行超时: {self.timeout}秒")
            
            # 查询执行状态
            status = self._get_prompt_status(prompt_id)
            
            if status == "completed":
                # 获取输出结果
                result = self._get_output(prompt_id)
                return result
            
            elif status == "failed":
                raise Exception("工作流执行失败")
            
            elif status == "executing":
                # 继续等待
                time.sleep(self.poll_interval)
            
            else:
                # 未知状态
                time.sleep(self.poll_interval)
    
    def _get_prompt_status(self, prompt_id: str) -> str:
        """
        获取 Prompt 执行状态
        
        Args:
            prompt_id: Prompt ID
            
        Returns:
            str: 状态（executing / completed / failed）
        """
        try:
            # 查询历史记录
            url = f"{self.comfyui_url}/history/{prompt_id}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                history = response.json()
                
                if prompt_id in history:
                    prompt_history = history[prompt_id]
                    
                    # 检查是否有输出
                    if "outputs" in prompt_history:
                        return "completed"
                    
                    # 检查是否有错误
                    if "status" in prompt_history:
                        status_info = prompt_history["status"]
                        if status_info.get("status_str") == "error":
                            return "failed"
                    
                    return "executing"
            
            return "executing"
            
        except Exception as e:
            self._log(f"查询状态失败: {e}", "WARNING")
            return "executing"
    
    def _get_output(self, prompt_id: str) -> Any:
        """
        获取工作流输出
        
        Args:
            prompt_id: Prompt ID
            
        Returns:
            Any: 输出数据
        """
        try:
            # 查询历史记录
            url = f"{self.comfyui_url}/history/{prompt_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            history = response.json()
            
            if prompt_id not in history:
                raise Exception("未找到执行历史")
            
            prompt_history = history[prompt_id]
            outputs = prompt_history.get("outputs", {})
            
            # 提取输出图片
            output_images = self._extract_output_images(outputs)
            
            return {
                "images": output_images,
                "outputs": outputs
            }
            
        except Exception as e:
            raise Exception(f"获取输出失败: {e}")
    
    def _extract_output_images(self, outputs: Dict) -> list:
        """
        从输出中提取图片信息
        
        Args:
            outputs: 输出数据
            
        Returns:
            list: 图片信息列表
        """
        images = []
        
        # 遍历所有输出节点
        for node_id, node_output in outputs.items():
            if "images" in node_output:
                for image_info in node_output["images"]:
                    # 构建图片 URL
                    filename = image_info.get("filename")
                    subfolder = image_info.get("subfolder", "")
                    image_type = image_info.get("type", "output")
                    
                    if filename:
                        image_url = f"{self.comfyui_url}/view"
                        params = {
                            "filename": filename,
                            "type": image_type
                        }
                        if subfolder:
                            params["subfolder"] = subfolder
                        
                        # 构建完整 URL
                        param_str = "&".join([f"{k}={v}" for k, v in params.items()])
                        full_url = f"{image_url}?{param_str}"
                        
                        images.append({
                            "filename": filename,
                            "url": full_url,
                            "subfolder": subfolder,
                            "type": image_type
                        })
        
        return images
    
    def download_image(self, image_info: Dict, save_path: str) -> str:
        """
        下载 ComfyUI 生成的图片
        
        Args:
            image_info: 图片信息
            save_path: 保存路径
            
        Returns:
            str: 保存路径
        """
        try:
            url = image_info.get("url")
            if not url:
                raise ValueError("图片信息中没有 URL")
            
            # 下载图片
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # 保存图片
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            self._log(f"图片已下载: {save_path}")
            
            return save_path
            
        except Exception as e:
            raise Exception(f"下载图片失败: {e}")
    
    def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            bool: ComfyUI 是否可用
        """
        try:
            # 检查配置
            if not self.comfyui_url:
                return False
            
            # 尝试访问 ComfyUI
            url = f"{self.comfyui_url}/system_stats"
            response = requests.get(url, timeout=5)
            
            return response.status_code == 200
            
        except Exception:
            return False
