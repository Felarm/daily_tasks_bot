from datetime import datetime, timedelta

import pytest

from db.dao import UserDao, DailyTaskDao


class TestUserDao:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        argnames="new_user_kwargs",
        argvalues=[
            {
                "username": "test_user_99",
                "id_": 99,
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "language_code": "test_language_code",
            },
            {
                "username": "test_user_67",
                "id_": 67,
            },
        ]
    )
    async def test_new_user_success(self, session, new_user_kwargs):
        new_user_id = await UserDao(session).new_user(**new_user_kwargs)
        assert new_user_id in [67, 99]

    @pytest.mark.asyncio
    @pytest.mark.xfail
    @pytest.mark.parametrize(
        argnames="new_user_kwargs",
        argvalues=[
            {"username": 123, "id_": "id"},
        ],
    )
    async def test_new_user_fail(self, session, new_user_kwargs):
        await UserDao(session).new_user(**new_user_kwargs)

    @pytest.mark.asyncio
    @pytest.mark.xfail
    @pytest.mark.parametrize(
        argnames="new_user_kwargs_1, new_user_kwargs_2",
        argvalues=[
            ({"username": "user", "id_": 22}, {"username": "user", "id_": 23}),
            ({"username": "user_1", "id_": 69}, {"username": "user_2", "id_": 69}),
        ]
    )
    async def test_new_user_unique_constraints(self, session, new_user_kwargs_1, new_user_kwargs_2):
        await UserDao(session).new_user(**new_user_kwargs_1)
        await UserDao(session).new_user(**new_user_kwargs_2)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        argnames="new_user_kwargs",
        argvalues=[
            {"username": "user", "id_": 42}
        ]
    )
    async def test_get_by_variants(self, session, new_user_kwargs):
        new_user_id = await UserDao(session).new_user(**new_user_kwargs)
        user_obj = await UserDao(session).get_one_or_none_by_id(69)
        assert user_obj is None
        another_user_obj = await UserDao(session).get_one_or_none_by_id(new_user_id)
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
    async def test_create_user_daily_task(self, session, daily_task_user_id, task_params):
        result = await DailyTaskDao(session).create_user_daily_task(
            user_id=daily_task_user_id,
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
    async def test_daily_tasks_constraints(self, session, daily_task_user_id, task_params):
        await DailyTaskDao(session).create_user_daily_task(user_id=daily_task_user_id, **task_params)

    @pytest.mark.asyncio
    async def test_get_user_daily_tasks_all(self, session, daily_task_user_id, present_daily_task):
        users_tasks = await DailyTaskDao(session).get_user_daily_tasks(daily_task_user_id)
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
            self, session, daily_task_user_id, present_daily_task, past_task_params
    ):
        task_from_past = await DailyTaskDao(session).create_user_daily_task(daily_task_user_id, **past_task_params)
        tasks_from_past = await DailyTaskDao(session).get_user_daily_tasks(
            user_id=daily_task_user_id,
            tasks_date=datetime.now() - timedelta(days=2)
        )
        assert present_daily_task not in tasks_from_past
        assert task_from_past in tasks_from_past

    @pytest.mark.asyncio
    async def test_delete_daily_task(self, session, daily_task_user_id, present_daily_task):
        await DailyTaskDao(session).delete_daily_task(task_id=present_daily_task.id)
        present_tasks = await DailyTaskDao(session).get_user_daily_tasks(daily_task_user_id)
        assert present_tasks == []