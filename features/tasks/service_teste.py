import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from features.tasks.service import TaskService


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.task = MagicMock()
    return db


@pytest.fixture
def service(mock_db):
    return TaskService(mock_db)


# ---------------------- create_task ---------------------

@pytest.mark.asyncio
async def test_create_task_success(service, mock_db):
    mock_db.task.create = AsyncMock(return_value={"id": 1})

    data = MagicMock(title="t", description="d", priority=MagicMock(value=1), due_date=None)

    result = await service.create_task(1, data)
    assert result["id"] == 1


@pytest.mark.asyncio
async def test_create_task_error(service, mock_db):
    mock_db.task.create = AsyncMock(side_effect=Exception("db error"))

    data = MagicMock(title="t", description="d", priority=MagicMock(value=1), due_date=None)

    with pytest.raises(HTTPException):
        await service.create_task(1, data)


# ---------------------- get_pending_tasks ----------------------

@pytest.mark.asyncio
async def test_get_pending_tasks_success(service, mock_db):
    mock_db.task.find_many = AsyncMock(return_value=[{"id": 1}])

    result = await service.get_pending_tasks(1)
    assert len(result) == 1


@pytest.mark.asyncio
async def test_get_pending_tasks_empty(service, mock_db):
    mock_db.task.find_many = AsyncMock(return_value=[])

    result = await service.get_pending_tasks(1)
    assert result == []


@pytest.mark.asyncio
async def test_get_pending_tasks_error(service, mock_db):
    mock_db.task.find_many = AsyncMock(side_effect=Exception())

    with pytest.raises(HTTPException):
        await service.get_pending_tasks(1)


# ---------------------- get_completed_tasks ---------------------

@pytest.mark.asyncio
async def test_get_completed_tasks_success(service, mock_db):
    mock_db.task.find_many = AsyncMock(return_value=[{"id": 2}])

    result = await service.get_completed_tasks(1)
    assert len(result) == 1


@pytest.mark.asyncio
async def test_get_completed_tasks_empty(service, mock_db):
    mock_db.task.find_many = AsyncMock(return_value=[])

    result = await service.get_completed_tasks(1)
    assert result == []


@pytest.mark.asyncio
async def test_get_completed_tasks_error(service, mock_db):
    mock_db.task.find_many = AsyncMock(side_effect=Exception())

    with pytest.raises(HTTPException):
        await service.get_completed_tasks(1)


# ---------------------- _get_task_or_404 ----------------------

@pytest.mark.asyncio
async def test_get_task_or_404_found(service, mock_db):
    mock_db.task.find_first = AsyncMock(return_value={"id": 1})

    result = await service._get_task_or_404(1, 1)
    assert result["id"] == 1


@pytest.mark.asyncio
async def test_get_task_or_404_not_found(service, mock_db):
    mock_db.task.find_first = AsyncMock(return_value=None)

    with pytest.raises(HTTPException):
        await service._get_task_or_404(1, 1)


# ---------------------- update_task ---------------------

@pytest.mark.asyncio
async def test_update_task_success(service, mock_db):
    mock_db.task.find_first = AsyncMock(return_value={"id": 1})
    mock_db.task.update = AsyncMock(return_value={"id": 1})

    data = MagicMock()
    data.model_dump = MagicMock(return_value={})

    result = await service.update_task(1, 1, data)
    assert result["id"] == 1


@pytest.mark.asyncio
async def test_update_task_not_found(service, mock_db):
    mock_db.task.find_first = AsyncMock(return_value=None)

    data = MagicMock()
    data.model_dump = MagicMock(return_value={})

    with pytest.raises(HTTPException):
        await service.update_task(1, 1, data)


@pytest.mark.asyncio
async def test_update_task_due_date_mapping(service, mock_db):
    mock_db.task.find_first = AsyncMock(return_value={"id": 1})
    mock_db.task.update = AsyncMock(return_value={"id": 1})

    data = MagicMock()
    data.model_dump = MagicMock(return_value={"due_date": "x"})

    await service.update_task(1, 1, data)

    args = mock_db.task.update.call_args[1]["data"]
    assert "dueDate" in args


@pytest.mark.asyncio
async def test_update_task_priority_mapping(service, mock_db):
    mock_db.task.find_first = AsyncMock(return_value={"id": 1})
    mock_db.task.update = AsyncMock(return_value={"id": 1})

    priority = MagicMock(value=2)
    data = MagicMock()
    data.model_dump = MagicMock(return_value={"priority": priority})

    await service.update_task(1, 1, data)

    args = mock_db.task.update.call_args[1]["data"]
    assert args["priority"] == 2


@pytest.mark.asyncio
async def test_update_task_error(service, mock_db):
    mock_db.task.find_first = AsyncMock(return_value={"id": 1})
    mock_db.task.update = AsyncMock(side_effect=Exception())

    data = MagicMock()
    data.model_dump = MagicMock(return_value={})

    with pytest.raises(HTTPException):
        await service.update_task(1, 1, data)


# ---------------------- complete_task ---------------------

@pytest.mark.asyncio
async def test_complete_task_success(service, mock_db):
    mock_db.task.find_first = AsyncMock(return_value={"id": 1})
    mock_db.task.update = AsyncMock(return_value={"completed": True})

    result = await service.complete_task(1, 1)
    assert result["completed"] is True


@pytest.mark.asyncio
async def test_complete_task_not_found(service, mock_db):
    mock_db.task.find_first = AsyncMock(return_value=None)

    with pytest.raises(HTTPException):
        await service.complete_task(1, 1)


@pytest.mark.asyncio
async def test_complete_task_error(service, mock_db):
    mock_db.task.find_first = AsyncMock(return_value={"id": 1})
    mock_db.task.update = AsyncMock(side_effect=Exception())

    with pytest.raises(HTTPException):
        await service.complete_task(1, 1)


# ---------------------- delete_task ----------------------

@pytest.mark.asyncio
async def test_delete_task_success(service, mock_db):
    mock_db.task.find_first = AsyncMock(return_value={"id": 1})
    mock_db.task.delete = AsyncMock(return_value=None)

    await service.delete_task(1, 1)


@pytest.mark.asyncio
async def test_delete_task_not_found(service, mock_db):
    mock_db.task.find_first = AsyncMock(return_value=None)

    with pytest.raises(HTTPException):
        await service.delete_task(1, 1)


@pytest.mark.asyncio
async def test_delete_task_error(service, mock_db):
    mock_db.task.find_first = AsyncMock(return_value={"id": 1})
    mock_db.task.delete = AsyncMock(side_effect=Exception())

    with pytest.raises(HTTPException):
        await service.delete_task(1, 1)
