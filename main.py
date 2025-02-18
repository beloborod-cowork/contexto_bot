#Добавление нужных модулей
import asyncio
from api_token import API_TOKEN
from aiogram import Bot,Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
import handlers
from logs import logger_main
import database
from load_config import load_config
#------------------------------------------------------------------

session = AiohttpSession() #Создание сессии
# Создание бота
async def main():
    with open('data\\latest.log', 'w') as file:
        pass
    bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML,session=session)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(handlers.router)
    task = asyncio.create_task(handlers.schedule_daily_task(bot,bc=load_config()["broadcast_when_restarted"]))   
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    await task
    logger_main.info("Бот запущен.")
 

    
if __name__ == "__main__":
    database.create_user_db()
    asyncio.run(main())
    
database.close_conn()