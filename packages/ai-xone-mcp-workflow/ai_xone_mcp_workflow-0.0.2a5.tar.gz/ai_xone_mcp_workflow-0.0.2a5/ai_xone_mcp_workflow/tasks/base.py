from workflow_model import Task, TaskType

class TaskHandler:
    def __init__(self, task: Task):
        self.task = task

    def run(self, input_data=None):
        raise NotImplementedError

    def gen_instruction(self):
        """生成指令，指导大模型如何完成该task。"""
        raise NotImplementedError

class TaskFactory:
    @staticmethod
    def create(task: Task):
        if task.type == TaskType.ai:
            from .ai_task import AITaskHandler
            return AITaskHandler(task)
        elif task.type == TaskType.mcp:
            from .mcp_task import MCPTaskHandler
            return MCPTaskHandler(task)
        else:
            raise ValueError(f"未知的Task类型: {task.type}")
