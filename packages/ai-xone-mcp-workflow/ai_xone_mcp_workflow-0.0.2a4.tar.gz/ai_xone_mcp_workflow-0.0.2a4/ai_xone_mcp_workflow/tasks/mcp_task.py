from .base import TaskHandler

class MCPTaskHandler(TaskHandler):
    def run(self, input_data=None):
        # 这里可以实现本地自动化任务
        return {"status": "mcp_executed", "result": "本地任务执行逻辑待实现"}

    def gen_instruction(self):
        return f"本地任务：{self.task.name}，无需大模型参与。"
