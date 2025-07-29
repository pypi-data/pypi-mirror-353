from .base import TaskHandler

class AITaskHandler(TaskHandler):
    def run(self, input_data=None):
        # 这里只做占位，实际由大模型执行
        return {"status": "waiting_ai", "instruction": self.gen_instruction()}

    def gen_instruction(self):
        # 生成给大模型的详细指令
        instr = f"请根据如下任务说明完成操作：\n任务名称：{self.task.name}\n任务描述：{self.task.instruction}\n"
        if self.task.input:
            instr += f"输入数据：{self.task.input}\n"
        if self.task.output:
            instr += f"期望输出：{self.task.output}\n"
        if self.task.params:
            instr += f"参数：{self.task.params}\n"
        instr += "请严格按照要求完成，并输出结果。"
        return instr
