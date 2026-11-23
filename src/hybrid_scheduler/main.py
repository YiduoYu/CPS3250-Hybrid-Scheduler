# src/hybrid_scheduler/main.py
from __future__ import annotations

import threading
import time
from queue import SimpleQueue
from typing import Any, Dict, List

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .dispatcher.dispatcher import RoundRobinDispatcher, create_mock_nodes
from .monitoring.metrics import (
    metrics_router,
    record_task_completed,
    set_queue_length,
)
from .strategies.hybrid import HybridStrategy
from .utils.models import Task

# ---------------------------------------------------------------------------

app = FastAPI(title="Hybrid Scheduler", version="0.1.0")

# ---- runtime components ---------------------------------------------------
task_queue: SimpleQueue[Task] = SimpleQueue()
strategy = HybridStrategy()
dispatcher = RoundRobinDispatcher(create_mock_nodes(3))  # 三个本地节点

# ---------------------------------------------------------------------------
# 数据模型：解析客户端提交的任务元数据
# ---------------------------------------------------------------------------


# src/hybrid_scheduler/main.py
class TaskPayload(BaseModel):
    id:       str  = Field(..., description="任务唯一 ID")
    category: str  = Field(..., description="CPU / IO …")
    duration: float = Field(..., gt=0, description="预计运行时长（秒）")

    # 以下两个仍然可选
    deadline:  int  | None = Field(None, description="Unix epoch 截止期")
    priority:  int  | None = Field(None, description="数字越小越高")


# ---------------------------------------------------------------------------
# 路由
# ---------------------------------------------------------------------------


@app.get("/health")
def healthcheck() -> Dict[str, str]:
    return {"status": "ok"}


app.include_router(metrics_router)


@app.post("/submit")
async def submit_task(payload: TaskPayload) -> Dict[str, str]:
    task = Task(**payload.model_dump())   # 直接解包
    task_queue.put(task)
    set_queue_length(task_queue.qsize())
    return {"id": task.id, "status": "queued"}

# ---------------------------------------------------------------------------
# 后台调度线程
# ---------------------------------------------------------------------------


def scheduler_worker() -> None:
    """守护线程：批量取出队列 → 调度排序 → 轮转派发（本地模拟运行）"""
    while True:
        if task_queue.empty():
            time.sleep(0.1)
            continue

        batch: List[Task] = []
        while not task_queue.empty():
            batch.append(task_queue.get())
        set_queue_length(0)

        ordered = strategy.schedule(batch)  # type: ignore[arg-type]
        dispatcher.dispatch(ordered)

        for t in ordered:
            record_task_completed(t.category, t.meta.get("duration", 0))
            time.sleep(t.meta.get("duration", 0))  # 用 sleep 模拟真实执行时间


# 启动守护线程（进程退出时自动结束）
threading.Thread(target=scheduler_worker, daemon=True).start()
