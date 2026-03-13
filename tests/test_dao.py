from datetime import datetime, timedelta

import pytest

from daily_task.dao import DailyTaskDao
from daily_task.models import DTaskState
from user.dao import UserDao


class TestUserDao:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        argnames="new_user_kwargs",
        argvalues=[
            {
                "username": "test_user_99",
                "tg_id": 99,
                "first_name": "test_first_name",
                "last_name": "test_last_name",
            },
            {
                "username": "test_user_67",
                "tg_id": 67,
            },
        ]
    )
    async def test_new_user_success(self, session, new_user_kwargs):
        new_user = await UserDao(session).new_user(**new_user_kwargs)
        assert new_user.tg_id in [67, 99]

    @pytest.mark.asyncio
    @pytest.mark.xfail
    @pytest.mark.parametrize(
        argnames="new_user_kwargs_1, new_user_kwargs_2",
        argvalues=[
            ({"username": "user", "tg_id": 22}, {"username": "user", "tg_id": 23}),
            ({"username": "user_1", "tg_id": 69}, {"username": "user_2", "tg_id": 69}),
        ]
    )
    async def test_new_user_unique_constraints(self, session, new_user_kwargs_1, new_user_kwargs_2):
        await UserDao(session).new_user(**new_user_kwargs_1)
        await UserDao(session).new_user(**new_user_kwargs_2)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        argnames="new_user_kwargs",
        argvalues=[
            {"username": "user"}
        ]
    )
    async def test_get_by_variants(self, session, new_user_kwargs):
        new_user = await UserDao(session).new_user(**new_user_kwargs)
        user_obj = await UserDao(session).get_one_or_none_by_id(69)
        assert user_obj is None
        another_user_obj = await UserDao(session).get_one_or_none_by_id(new_user.id)
        assert another_user_obj is not None
        and_another_user_obj = await UserDao(session).get_by_username(another_user_obj.username)
        assert another_user_obj == and_another_user_obj
        assert another_user_obj is and_another_user_obj


class TestDailyTaskDao:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        argnames="task_params",
        argvalues=[{
            "name": "test_task",
            "description": "test_description",
            "start_dt": datetime.now(),
            "end_dt": datetime.now() + timedelta(seconds=5),
        }]
    )
    async def test_create_user_daily_task(self, session, daily_task_user, task_params):
        result = await DailyTaskDao(session).create_user_daily_task(
            user_id=daily_task_user.id,
            **task_params,
        )
        assert result is not None

    @pytest.mark.asyncio
    @pytest.mark.xfail
    @pytest.mark.parametrize(
        argnames="task_params",
        argvalues=[{
            "name": "test_task",
            "description": "test_description",
            "end_dt": datetime.now(),
            "start_dt": datetime.now() + timedelta(seconds=5),
        }]
    )
    async def test_daily_tasks_constraints(self, session, daily_task_user, task_params):
        await DailyTaskDao(session).create_user_daily_task(user_id=daily_task_user.id, **task_params)

    @pytest.mark.asyncio
    async def test_get_user_daily_tasks_all(self, session, daily_task_user, present_daily_task):
        users_tasks = await DailyTaskDao(session).get_user_daily_tasks(daily_task_user.id)
        assert present_daily_task in users_tasks

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        argnames="past_task_params",
        argvalues=[{
            "name": "task in past",
            "start_dt": datetime.now() - timedelta(days=2),
            "end_dt": datetime.now() - timedelta(days=1),
        }]
    )
    async def test_get_user_daily_tasks_by_date(
            self, session, daily_task_user, present_daily_task, past_task_params
    ):
        task_from_past = await DailyTaskDao(session).create_user_daily_task(daily_task_user.id, **past_task_params)
        tasks_from_past = await DailyTaskDao(session).get_user_daily_tasks(
            user_id=daily_task_user.id,
            tasks_date=datetime.now() - timedelta(days=2)
        )
        assert present_daily_task not in tasks_from_past
        assert task_from_past in tasks_from_past

    @pytest.mark.asyncio
    async def test_delete_daily_task(self, session, daily_task_user, present_daily_task):
        await DailyTaskDao(session).delete_daily_task(task_id=present_daily_task.id)
        present_tasks = await DailyTaskDao(session).get_user_daily_tasks(daily_task_user.id)
        assert present_tasks == []

    @pytest.mark.asyncio
    async def test_change_daily_task_state_success(self, session, present_daily_task):
        await DailyTaskDao(session).change_daily_task_state(present_daily_task.id, DTaskState.done)
        assert present_daily_task.state == DTaskState.done.value

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        argnames="real_start_dt, real_end_dt",
        argvalues=[(datetime.now(), datetime.now() + timedelta(minutes=2))])
    async def test_set_real_start_end_dts(self, session, present_daily_task, real_start_dt, real_end_dt):
        await DailyTaskDao(session).set_daily_task_real_start_dt(present_daily_task.id, real_start_dt)
        assert present_daily_task.real_start_dt is not None
        assert present_daily_task.real_start_dt == real_start_dt
        await DailyTaskDao(session).set_daily_task_real_end_dt(present_daily_task.id, real_end_dt)
        assert present_daily_task.real_end_dt is not None
        assert present_daily_task.real_end_dt == real_end_dt
