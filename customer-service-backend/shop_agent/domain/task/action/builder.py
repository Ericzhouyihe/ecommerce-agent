from shop_agent.domain.task.action.registry import ActionRegistry
from shop_agent.domain.task.action.runner import ActionRunner


def register_builtin_actions(action_runner: ActionRunner) -> None:
    action_runner.register_builtin_actions()


def register_custom_actions(action_runner: ActionRunner) -> None:
    action_runner.register_custom_actions()


def build_action_runner() -> ActionRunner:
    action_runner = ActionRunner(ActionRegistry())
    register_builtin_actions(action_runner)
    register_custom_actions(action_runner)
    return action_runner
