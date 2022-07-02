import asyncio
import logging
from this import d
import aioredis



from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2


from tgbot.config import load_config 
from tgbot.filters.admin import  FilterAdmin
from tgbot.filters.private import FilterPrivate
from tgbot.handlers.admin import register_admin
from tgbot.handlers.menu import register_menu
from tgbot.handlers.inline_menu import register_inline_menu
from tgbot.handlers.echo import register_echo
from tgbot.handlers.test import register_test
from tgbot.handlers.user import register_user
from tgbot.middlewares.db import DbMiddleware
from tgbot.middlewares.bog import BigBog
from tgbot.middlewares.throttling import ThrottlingMiddleware



logger = logging.getLogger(__name__)


def register_all_middlewares(dp):
    dp.setup_middleware(BigBog())
    dp.setup_middleware(DbMiddleware())
    dp.setup_middleware(ThrottlingMiddleware())



def register_all_filters(dp):
    dp.filters_factory.bind(FilterAdmin)
    dp.filters_factory.bind(FilterPrivate)



def register_all_handlers(dp):
    register_admin(dp)
    register_user(dp)
    register_inline_menu(dp)
    register_menu(dp)
    register_test(dp)
    #register_echo(dp)


async def main(): #метод запуска бота
    logging.basicConfig(  #лоигирование ошибок
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config(".env") #импортируем файл с конфигом

    storage = RedisStorage2() if config.tgbot.use_redis else MemoryStorage() #использовать для состояний или редис если подключин или оперативную память пк
    bot = Bot(token=config.tgbot.token, parse_mode='HTML') #отправляем телеграму токен нашего бота
    dp = Dispatcher(bot, storage=storage) #диспетчер запросов

    bot['config'] = config #боту передали конфиг, чтобы его можно было вызывать

    #вызов
    register_all_middlewares(dp) 
    register_all_filters(dp) 
    register_all_handlers(dp) 

    # start
    try:
        await dp.start_polling()
    finally: #если ошибка, бот закрывает все стабильно
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__': #запуск бота
    try:
        asyncio.run(main()) #Запускает метод запуска бота
    except (KeyboardInterrupt, SystemExit): # если бот остановили выдаст сообщение
        logger.error("Bot stopped!")