from fastmcp import FastMCP

import logging
from typing import List, Optional, Dict, Any
from ai_xone_mcp_workflow.workflow_model import Workflow, Step, WorkflowStatus, Task, TaskType
from ai_xone_mcp_workflow.workflow_repository import load_workflows, save_workflows
import uuid
from datetime import datetime


mcp = FastMCP(
    'ai-xone-mcp-workflow',
    instructions='Workflow management and execution',
    dependencies=[
        'pydantic',
        'pyyaml',
    ],
)

@mcp.tool()
def workflow_list(random_string: Optional[str] = None) -> List[Workflow]:
    """
    获取所有已保存的工作流列表。

    Args:
        random_string: 兼容参数（可忽略，通常无需传递）

    Returns:
        List[Workflow]: 当前系统中所有已保存的工作流对象列表。
    """
    return load_workflows(random_string)

@mcp.tool()
def workflow_add(workflow: Workflow) -> Dict[str, Any]:
    """
    添加一个新的工作流。

    Args:
        workflow: Workflow 领域模型对象，包含如下结构：
            - name: 工作流名称
            - steps: List[Step]，每个步骤包含：
                - name: 步骤名称
                - order: 步骤顺序
                - context: 上下文，提供背景信息、约束、场景说明，帮助模型理解任务目标
                - instruction: 指令，明确需要模型执行的具体操作
                - input: 输入，模型需要处理的具体数据或信息
                - output: 输出，规定模型返回结果的格式或结构
                - params: 其他参数（可选）
            - status: WorkflowStatus，工作流状态（active/inactive/archived）
            - description: 工作流描述
            - created_at: 创建时间
            - updated_at: 更新时间

    Returns:
        dict: 新增工作流的详细内容和操作结果。
    """
    workflows = load_workflows()
    workflow_id = str(uuid.uuid4())
    workflow_dict = workflow.model_dump(mode='json')
    workflow_dict['id'] = workflow_id
    new_workflow = Workflow(**workflow_dict)
    workflows.append(new_workflow)
    save_workflows(workflows)
    return {"workflow": new_workflow.model_dump(mode='json'), "result": "success"}

@mcp.tool()
def workflow_update(workflow: Workflow) -> Dict[str, Any]:
    """更新 workflow"""
    workflows = load_workflows()
    found = False
    for idx, wf in enumerate(workflows):
        if wf.id == workflow.id:
            # 保持created_at不变，更新updated_at
            updated_workflow_dict = workflow.model_dump(mode='json')
            updated_workflow_dict['created_at'] = wf.created_at
            updated_workflow_dict['updated_at'] = str(datetime.now())
            workflows[idx] = Workflow(**updated_workflow_dict)
            found = True
            break
    if found:
        save_workflows(workflows)
        return {"workflow": workflows[idx].model_dump(mode='json'), "result": "updated"}
    else:
        return {"workflow": workflow.model_dump(mode='json'), "result": "not_found"}

@mcp.tool()
def workflow_delete(workflow_id: str) -> Dict[str, Any]:
    """删除 workflow"""
    workflows = load_workflows()
    initial_count = len(workflows)
    workflows = [wf for wf in workflows if wf.id != workflow_id]
    if len(workflows) == initial_count:
        return {"workflow_id": workflow_id, "result": "not_found"}
    save_workflows(workflows)
    return {"workflow_id": workflow_id, "result": "deleted"}

@mcp.tool()
def workflow_run(
    workflow_id: Optional[str] = None,
    workflow_name: Optional[str] = None,
    input: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    工作流调度：支持通过工作流名称或id查找，获取当前步骤和任务指令。

    step 下可包含多个 task，每个 task 可指定类型（ai/mcp）。
    - ai 类型 task 由大模型执行
    - mcp 类型 task 可由本地后端执行（后续可扩展）
    - 兼容老数据：若 step.tasks 为空但有 instruction，则自动转为一个 ai 类型的 task

    参数:
        workflow_id: 工作流唯一标识（可选）
        workflow_name: 工作流名称（可选，优先）
        input: 传递给当前 task 的输入内容（可选）
        params: 其他上下文参数（如 current_order, current_task_idx）
            - current_order: 当前步骤序号（默认1）
            - current_task_idx: 当前步骤下的 task 序号（默认0）

    返回:
        dict: 当前步骤和任务的指令描述，包括：
            - status: 状态（running/finished/ambiguous/not_found/error）
            - current_step: 当前步骤序号
            - current_task: 当前 task 的详细信息（见下）
                - workflow_id, workflow_name, step_order, step_name
                - task_idx, task_name, task_type
                - context, instruction, input, output, params
                - workflow_description, steps_total, tasks_total
                - continue_instruction: 如何推进到下一个 task/step 的说明
            - 若已全部完成，status=finished
            - 若未找到，status=not_found
            - 若歧义，status=ambiguous
    """
    workflows = load_workflows()
    workflow = None

    # 优先通过名称查找
    if workflow_name:
        matches = [wf for wf in workflows if workflow_name.lower() in wf.name.lower()]
        if len(matches) == 1:
            workflow = matches[0]
        elif len(matches) > 1:
            return {
                "status": "ambiguous",
                "message": f"存在多个名称包含'{workflow_name}'的工作流，请指定id。",
                "candidates": [wf.id for wf in matches]
            }
        else:
            return {"status": "not_found", "message": f"未找到名称包含'{workflow_name}'的工作流"}
    elif workflow_id:
        workflow = next((wf for wf in workflows if wf.id == workflow_id), None)
        if not workflow:
            return {"status": "not_found", "message": f"未找到id为{workflow_id}的工作流"}
    else:
        return {
            "status": "error",
            "message": f"未找到匹配的工作流，请指定工作流。",
            "candidates": [wf.name for wf in workflows]
        }

    # 获取当前步骤序号，默认第一个
    current_order = 1
    if params and "current_order" in params:
        current_order = params["current_order"]

    steps_sorted = sorted(workflow.steps, key=lambda s: s.order)
    current_step = next((s for s in steps_sorted if s.order == current_order), None)
    if not current_step:
        # 所有步骤已完成
        return {
            "workflow_id": workflow.id,
            "status": "finished",
            "message": "工作流已全部执行完毕"
        }

    # 兼容老数据：如果 tasks 为空但有 instruction，则自动转为一个 ai 类型的 task
    tasks = current_step.tasks or []
    if not tasks and current_step.instruction:
        tasks = [Task(name=current_step.name, type=TaskType.ai, instruction=current_step.instruction)]

    # 获取当前 task 序号，默认第一个
    current_task_idx = 0
    if params and "current_task_idx" in params:
        current_task_idx = params["current_task_idx"]
    if current_task_idx >= len(tasks):
        # 当前 step 的所有 task 已完成，推进到下一个 step
        return workflow_run(
            workflow_id=workflow.id,
            input=input,
            params={"current_order": current_order+1, "current_task_idx": 0}
        )
    current_task = tasks[current_task_idx]

    # 指导大模型如何继续执行后续 task/step
    continue_instruction = (
        f"每个 task 执行后自动推进到下一个 task，所有 task 执行完毕后自动进入下一个 step。推进下一个 task 的方法： workflow_run，参数 current_order={current_order}，current_task_idx={current_task_idx+1}。推进下一个 step 的方法： workflow_run，参数 current_order={current_order+1}，current_task_idx=0。"
        if current_task_idx < len(tasks)-1 else
        f"本 step 的所有 task 执行完毕后自动进入下一个 step。推进下一个 step 的方法： workflow_run，参数 current_order={current_order+1}，current_task_idx=0。"
    )

    # 拼接 input，确保 None 安全
    task_input = (current_task.input or "") + ("\n" + input if input else "")

    instruction_payload = {
        "workflow_id": workflow.id,
        "workflow_name": workflow.name,
        "step_order": current_step.order,
        "step_name": current_step.name,
        "task_idx": current_task_idx,
        "task_name": current_task.name,
        "task_type": current_task.type,
        "context": current_step.context,
        "instruction": current_task.instruction,
        "input": task_input,
        "output": current_task.output,
        "params": current_task.params,
        "workflow_description": workflow.description,
        "steps_total": len(steps_sorted),
        "tasks_total": len(tasks),
        "continue_instruction": continue_instruction
    }

    return {
        "status": "running",
        "current_step": current_step.order,
        "current_task": instruction_payload
    }

def main():
    mcp.run()

if __name__ == "__main__":
    main()