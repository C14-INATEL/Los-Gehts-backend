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


# ---------------------- NEW TESTS (8 extra) ----------------------

# teste 1: create_task passa os campos corretos para o banco
@pytest.mark.asyncio
async def test_create_task_correct_payload(service, mock_db):
    mock_db.task.create = AsyncMock(return_value={"id": 1})

    data = MagicMock(title="Buy milk", description="2% please", priority=MagicMock(value="HIGH"), due_date=None)

    await service.create_task(user_id=99, data=data)

    call_data = mock_db.task.create.call_args[1]["data"]
    assert call_data["title"] == "Buy milk"
    assert call_data["userId"] == 99
    assert call_data["priority"] == "HIGH"


# teste 2: create_task lança HTTPException 500 com mensagem correta
@pytest.mark.asyncio
async def test_create_task_error_status_code(service, mock_db):
    from prisma.errors import PrismaError
    mock_db.task.create = AsyncMock(side_effect=PrismaError("connection failed"))

    data = MagicMock(title="t", description="d", priority=MagicMock(value=1), due_date=None)

    with pytest.raises(HTTPException) as exc:
        await service.create_task(1, data)

    assert exc.value.status_code == 500


# teste 3: get_pending_tasks filtra pelo userId e completed=False corretos
@pytest.mark.asyncio
async def test_get_pending_tasks_correct_filter(service, mock_db):
    mock_db.task.find_many = AsyncMock(return_value=[])

    await service.get_pending_tasks(user_id=42)

    call_where = mock_db.task.find_many.call_args[1]["where"]
    assert call_where["userId"] == 42
    assert call_where["completed"] is False


# teste 4: get_completed_tasks filtra pelo userId e completed=True corretos
@pytest.mark.asyncio
async def test_get_completed_tasks_correct_filter(service, mock_db):
    mock_db.task.find_many = AsyncMock(return_value=[])

    await service.get_completed_tasks(user_id=7)

    call_where = mock_db.task.find_many.call_args[1]["where"]
    assert call_where["userId"] == 7
    assert call_where["completed"] is True


# teste 5: _get_task_or_404 busca pela combinação correta de task_id e user_id
@pytest.mark.asyncio
async def test_get_task_or_404_correct_query(service, mock_db):
    mock_db.task.find_first = AsyncMock(return_value={"id": 5})

    await service._get_task_or_404(task_id=5, user_id=10)

    call_where = mock_db.task.find_first.call_args[1]["where"]
    assert call_where["id"] == 5
    assert call_where["userId"] == 10


# teste 6: _get_task_or_404 lança HTTPException 404 (não 500) quando não encontrado
@pytest.mark.asyncio
async def test_get_task_or_404_raises_404(service, mock_db):
    mock_db.task.find_first = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc:
        await service._get_task_or_404(1, 1)

    assert exc.value.status_code == 404


# teste 7: complete_task chama update com completed=True
@pytest.mark.asyncio
async def test_complete_task_sets_completed_true(service, mock_db):
    mock_db.task.find_first = AsyncMock(return_value={"id": 3})
    mock_db.task.update = AsyncMock(return_value={"id": 3, "completed": True})

    await service.complete_task(task_id=3, user_id=1)

    call_data = mock_db.task.update.call_args[1]["data"]
    assert call_data["completed"] is True


# teste 8: delete_task chama delete com o task_id correto
@pytest.mark.asyncio
async def test_delete_task_correct_id(service, mock_db):
    mock_db.task.find_first = AsyncMock(return_value={"id": 8})
    mock_db.task.delete = AsyncMock(return_value=None)

    await service.delete_task(task_id=8, user_id=1)

    call_where = mock_db.task.delete.call_args[1]["where"]
    assert call_where["id"] == 8