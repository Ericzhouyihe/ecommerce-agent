from shop_agent.domain.dialogue.messages import BotMessage
from shop_agent.domain.dialogue.state import DialogueState
from shop_agent.domain.task.action.runner import ActionRunner
from shop_agent.domain.task.command.commands import Command
from shop_agent.domain.task.command.processor import CommandProcessor
from shop_agent.domain.task.flow.executor import FlowExecutor
from shop_agent.domain.task.flow.models import FlowsList


class TaskHandler:
    def __init__(
        self,
        command_processor: CommandProcessor,
        flows: FlowsList,
        flow_executor: FlowExecutor,
        action_runner: ActionRunner,
    ):
        self.command_processor: CommandProcessor = command_processor
        self.flows: FlowsList = flows
        self.flow_executor: FlowExecutor = flow_executor
        self.action_runner: ActionRunner = action_runner

    async def handle(
        self, commands: list[Command], state: DialogueState
    ) -> list[BotMessage]:
        self.command_processor.run(commands, state, self.flows)
        messages: list[BotMessage] = await self.flow_executor.run_task(
            state, self.flows, self.action_runner
        )
        return messages
