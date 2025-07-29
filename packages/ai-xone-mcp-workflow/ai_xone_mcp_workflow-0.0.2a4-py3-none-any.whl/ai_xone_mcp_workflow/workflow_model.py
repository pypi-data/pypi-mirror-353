from enum import Enum
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class WorkflowStatus(str, Enum):
    active = "active"         # 启用
    inactive = "inactive"     # 停用
    archived = "archived"     # 已归档/删除

class TaskType(str, Enum):
    ai = "ai"         # 由大模型执行
    mcp = "mcp"       # 由 mcp 本地执行

class Task(BaseModel):
    name: str
    type: TaskType = TaskType.ai
    instruction: str
    input: Optional[str] = None
    output: Optional[str] = None
    params: Optional[Dict[str, Any]] = None

class Step(BaseModel):
    name: str
    order: int
    context: Optional[str] = None      # 上下文，背景信息、约束、场景说明
    instruction: Optional[str] = None  # 兼容老数据，若有则自动转为一个 ai 类型的 task
    tasks: Optional[List[Task]] = None # 新增，支持多个 task
    input: Optional[str] = None        # 输入，模型需要处理的数据
    output: Optional[str] = None       # 输出，期望的返回格式或结构
    params: Optional[Dict[str, Any]] = None  # 其他参数（可选）

class Workflow(BaseModel):
    id: Optional[str] = None  # 唯一标识
    name: str
    steps: List[Step]
    status: WorkflowStatus = WorkflowStatus.active
    description: Optional[str] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()