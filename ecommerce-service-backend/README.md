# atguigu ecommerce service

这是一个配套 `atguigu` 项目使用的电商业务服务示例。

它提供：

- 用户最近订单 / 商品
- 订单状态查询
- 物流查询
- 商品信息查询
- 发货提醒创建
- 退款申请创建

初始化数据覆盖了多种典型状态，便于课堂演示：

- 待发货
- 待揽收
- 运输中
- 已完成
- 已取消
- 已有退款申请
- 已有发货提醒

## 启动方式

1. 在仓库根目录启动 MySQL(会自动建库、建表并写入演示数据):

```powershell
docker compose up -d mysql
```

2. 启动本服务(默认监听 `127.0.0.1:18081`):

```powershell
cd ecommerce-service-backend
uv sync
uv run python main.py
```

如果你想清空数据重新初始化:

```powershell
docker compose down -v
docker compose up -d mysql
```

## 核心接口

- `GET /health`
- `GET /users/{user_id}/orders`
- `GET /users/{user_id}/products`
- `GET /orders/{order_id}`
- `GET /orders/{order_id}/status`
- `GET /orders/{order_id}/logistics`
- `GET /products/{product_id}`
- `POST /orders/{order_id}/shipping-reminders`
- `POST /orders/{order_id}/refund-applications`

## 环境变量

见 `.env.example`。服务启动时会自动加载项目根目录的 `.env`(已存在的环境变量优先)。
