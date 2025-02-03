import logging

logger_main = logging.getLogger("logger_main")
handler_main = logging.FileHandler(
    filename="data\\latest.log",
    encoding='utf-8'
)
formatter_main = logging.Formatter(fmt='[%(asctime)s][main.%(levelname)s]: %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
handler_main.setFormatter(formatter_main)
logger_main.addHandler(handler_main)
logger_main.setLevel(logging.DEBUG)
#Для main файла


logger_promo = logging.getLogger("logger_promo")
handler_promo = logging.FileHandler(
    filename="data\\latest.log",
    encoding='utf-8'
)
formatter_promo = logging.Formatter(fmt='[%(asctime)s][promo.%(levelname)s]: %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
handler_promo.setFormatter(formatter_promo)
logger_promo.addHandler(handler_promo)
logger_promo.setLevel(logging.DEBUG)
#Для promo файла


logger_handlers = logging.getLogger("logger_handlers")
handler_handlers = logging.FileHandler(
    filename="data\\latest.log",
    encoding='utf-8'
)
formatter_handlers = logging.Formatter(fmt='[%(asctime)s][handlers.%(levelname)s]: %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
handler_handlers.setFormatter(formatter_handlers)
logger_handlers.addHandler(handler_handlers)
logger_handlers.setLevel(logging.DEBUG)
#Для handlers файла


logger_database = logging.getLogger("logger_database")
handler_database = logging.FileHandler(
    filename="data\\latest.log",
    encoding='utf-8'
)
formatter_database = logging.Formatter(fmt='[%(asctime)s][database.%(levelname)s]: %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
handler_database.setFormatter(formatter_database)
logger_database.addHandler(handler_database)
logger_database.setLevel(logging.DEBUG)
#Для database файла