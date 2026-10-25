from shop_agent.domain.dialogue.flow.steps import FlowStep
from pathlib import Path

import yaml

from shop_agent.domain.dialogue.flow.models import Flow, FlowsList, FlowSlot


class FlowLoader:
    def load(self, path: Path) -> FlowsList:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        slots = self._load_slots(data.get("slots", {}))
        print(slots)
        flows = self._load_flows(data.get("flows", {}), slots)
        print(flows)
        # flows = []
        # for flow_id, flow_data in flows_data.items():
        #     steps = [step_from_json(raw_step) for raw_step in flow_data.get("steps", [])]
        #     flows.append(
        #         Flow(
        #             id=str(flow_id),
        #             name=None if flow_data.get("name") is None else str(flow_data.get("name")),
        #             description=str(flow_data.get("description", "")),
        #             steps=steps,
        #             slots=self._collect_flow_slots(steps, slots),
        #         )
        #     )
        # return FlowsList(flows=flows, slots=slots)
        # result = FlowsList(flows=flows, slots=slots)
        # self._cache[file_path] = result
        # return result

    def _load_slots(self, slots_data: dict[str, dict]) -> dict[str, FlowSlot]:
        slots = {}
        for slot_name, slot_data in slots_data.items():
            slots[slot_name] = FlowSlot(**slot_data, name=slot_name)
        return slots

    def _load_flows(self, flows_data: dict[str, dict], slots: dict[str, FlowSlot]) -> list[Flow]:
        flows: list[Flow] = []
        for flow_id, flow_data in flows_data.items():
            steps: list[FlowStep] = [flow_data(**step) for step in flow_data.get("steps", [])]

            flow = Flow(
                id=flow_id,
                name=flow_data.get("name", flow_id),
                description=flow_data.get("description", ""),
                steps=None,
                slots=None,
            )
            flows.append(flow)
        return flows

    def load_all(self, *paths: str | Path) -> FlowsList:
        """合并多个 YAML 文件（例如 system_flows + user_flows）"""
        merged = FlowsList()
        for path in paths:
            loaded = self.load(path)
            merged.flows.extend(loaded.flows)
            merged.slots.update(loaded.slots)
        return merged


if __name__ == "__main__":
    project_root = Path(__file__).parents[2]
    loader = FlowLoader(project_root)
    loader.load(project_root / "flow_config" / "user_flows.yml")
