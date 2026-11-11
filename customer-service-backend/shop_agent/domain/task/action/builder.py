from shop_agent.domain.task.action.builtin.action_listen import ActionListen
from shop_agent.domain.task.action.builtin.action_response import ActionResponse
from shop_agent.domain.task.action.registry import ActionRegistry
from shop_agent.domain.task.action.runner import ActionRunner


def register_builtin_actions(action_runner: ActionRunner) -> None:
    """注册内置操作"""
    action_runner.registry.register(ActionResponse())
    action_runner.registry.register(ActionListen())


def register_custom_actions(action_runner: ActionRunner) -> None:
    """注册自定义操作"""
    action_runner.registry.register(ActionListen())


def build_action_runner() -> ActionRunner:
    action_runner = ActionRunner(ActionRegistry())
    register_builtin_actions(action_runner)
    register_custom_actions(action_runner)
    return action_runner
