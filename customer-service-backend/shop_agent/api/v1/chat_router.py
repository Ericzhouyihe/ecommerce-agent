from fastapi import APIRouter

from shop_agent.api.v1.scheme import (
    ChatBotMessage,
    ChatRequest,
    ChatResponse,
    HistoryMessage,
    HistoryResponse,
)

router = APIRouter(prefix="/chat", tags=["智能客服"])


@router.post("", summary="发送消息并获取回复")
async def chat(message: ChatRequest) -> ChatResponse:
    # message.object 可能为 None，先判空
    if message.object is not None and message.object.type == "order":
        order_id = message.object.id  # "ORDER_10001"
        # source = message.object.attributes.get("source")  # "order_list"\
        # order = await order_service.get_order(order_id) TODO: 实现订单查询服务
        return ChatResponse(
            sender_id=message.sender_id,
            message_id=message.message_id,
            messages=[ChatBotMessage(text=f"订单 {order_id} 的状态是 ")],  # {order.status}
        )

    # 分支二：纯文本、没有订单上下文 → 引导用户补充信息
    return ChatResponse(
        sender_id=message.sender_id,
        message_id=message.message_id,
        messages=[ChatBotMessage(text="请告诉我你的订单号。")],
    )


@router.get("/history", summary="获取聊天历史")
async def chat_history(sender_id: str) -> HistoryResponse:
    # messages = await chat_history.get_chat_history(sender_id) TODO: 实现聊天历史查询服务
    return HistoryResponse(
        sender_id=sender_id,
        messages=[
            HistoryMessage(role="user", text="你好"),
            HistoryMessage(role="bot", text="你好！有什么我可以帮助你的吗？"),
        ],
    )
