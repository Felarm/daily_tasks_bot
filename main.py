from contextlib import asynccontextmanager

from aiogram.types import Update
from fastapi import FastAPI, Request
from loguru import logger

from bot.main import start_bot, bot, dp, stop_bot
from config import jobs_scheduler, settings
from db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("starting app...")
    if settings.INIT_DB:
        await init_db()
    await start_bot()
    jobs_scheduler.start()
    yield
    await stop_bot()
    jobs_scheduler.shutdown()
    logger.info(f"stopped everything")


app = FastAPI(lifespan=lifespan)


@app.post("/webhook")
async def webhook(request: Request):
    logger.debug("received request from webhook")
    try:
        update_data = await request.json()
        update = Update.model_validate(update_data, context={"bot": bot})
        await dp.feed_update(bot, update)
        logger.debug("updated processed")
    except Exception as e:
        logger.error(f"error while processing update on webhook:\n{e}\n{e.with_traceback(e.__traceback__)}")
