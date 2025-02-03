from database import reset_parameter,create_promo_db,fetch_data
from logs import logger_promo
create_promo_db()

def process_promo(promo: str,id: int) -> str:
    try:
        exists = fetch_data("promos","*",condition=f"WHERE name = '{promo}'")[0] if not list() else fetch_data("promos","*",condition=f"WHERE name = '{promo}'")
        if exists == list():
            logger_promo.info(f"Пользователь {id} ввел промокод {promo}, однако его не существует.")
            return "<b>Такого промокода не существует</b>"
        user_id_raw = exists[3]
        if user_id_raw != None:
            user_ids_activated = [int(i) for i in user_id_raw.split(",")[:-1]]
        else: user_ids_activated = None
        if user_ids_activated != None:
            if id in user_ids_activated:
                logger_promo.info(f"Пользователь {id} ввел промокод {promo}, однако он уже активирован.")
                return "<b>Вы уже активировали данный промокод.</b>"
        activations = exists[1]
        if activations == 0:
            logger_promo.info(f"Пользователь {id} ввел промокод {promo}, однако у этого промокода закончились активации.")
            return "<b>У данного промокода закончились активации.</b>"

        hints = exists[2]
        if user_id_raw !=None:
            user_id_raw += f"{id},"
        else:
            user_id_raw = f"{id},"

        reset_parameter("users","hints",f"hints + {hints}",condition=f"WHERE telegram_id = {id}")
        reset_parameter("promos","activations","activations - 1",condition=f"WHERE name = '{promo}'")
        reset_parameter("promos","users_activated",f"'{user_id_raw}'",condition=f"WHERE name = '{promo}'")
        logger_promo.info(f"Пользователь {id} ввел промокод {promo}. Ему начислено {hints} подсказок")
        return f"<b>Вы активировали промокод.\nВам начислено {hints}💡Подсказок.</b>"
    except Exception as e:
        logger_promo.error(f"Возникла ошибка при вводе промокода {promo} для пользователя {id}. Ошибка: {e}")
        return "Возникла непредвиденная ошибка при вводе промокода. Проверьте правильность ввода команды и попробуйте еще раз."
