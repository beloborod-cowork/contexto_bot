from aiogram.types import Message
from database import reset_parameter
import random
import math
import asyncio

def count_crash():

    values = [i for i in range(100,500,1)]
    weights = [i for i in range(500,100,-1)]
    result = random.choices(values,weights)
    return result[0]


async def handle_game(game: str, dice: Message, chat_id: int,bid: int) -> str:
    """
    Обрабатывает результат игры и возвращает текстовое сообщение.

    :param game: Название игры (кубик, футбол, баскетбол, боулинг, дартс).
    :param dice: Объект сообщения с результатом броска (dice_message).
    :param chat_id: ID чата, куда нужно отправить результат.
    :return: Текстовое сообщение с результатом.
    """
    
    reset_parameter("users","coins",f"coins-{bid}",condition=f"WHERE telegram_id = {chat_id}")
    await asyncio.sleep(5)
    result = dice.dice.value
    mult_football = [0, 0, 0.5, 1, 2]
    mult_bowling = [0, 0.5, 1, 1.5, 2, 2.5]
    if game == "кубик":
        multipliers = [0, 0.5, 1, 1.5, 2, 2.5]
        random.shuffle(multipliers)
        reset_parameter("users","coins",f"coins+{bid*multipliers[result-1]}",condition=f"WHERE telegram_id = {chat_id}")
        return f"🎲 Вы бросили кубик и выпало: {result}\nВы получили: {int(bid*multipliers[result-1])} монет"
    elif game == "футбол":
        reset_parameter("users","coins",f"coins+{bid*mult_football[result-1]}",condition=f"WHERE telegram_id = {chat_id}")
        return f"⚽ Вы ударили по мячу и забили {result} голов!\nВы получили: {int(bid*mult_football[result-1])} монет"
    elif game == "баскетбол":
        reset_parameter("users","coins",f"coins+{bid*mult_football[result-1]}",condition=f"WHERE telegram_id = {chat_id}")
        return f"🏀 Вы забросили {result} мячей в корзину!\nВы получили: {int(bid*mult_football[result-1])} монет"
    elif game == "боулинг":
        reset_parameter("users","coins",f"coins+{bid*mult_bowling[result-1]}",condition=f"WHERE telegram_id = {chat_id}")
        return f"🎳 Вы сбили {result} кеглей!\nВы получили: {int(bid*mult_bowling[result-1])} монет"
    elif game == "дартс":
        reset_parameter("users","coins",f"coins+{bid*mult_bowling[result-1]}",condition=f"WHERE telegram_id = {chat_id}")
        return f"🎯 Вы попали в {result} очков!\nВы получили: {int(bid*mult_bowling[result-1])} монет"
    else:
        return "Неизвестная игра."

async def handle_crash(msg: Message,bid: int, multiplier: float,id: int):

    multiplier_game = 1.0
    reset_parameter("users","coins",f"coins-{bid}",condition=f"WHERE telegram_id = {msg.chat.id}")
    first_try = False
    while True:
        multiplier_temp = count_crash() / 100
        leave = random.choice([True,False])
        
        if leave == True and first_try != False:
            break
        else:
            if multiplier_temp >= multiplier_game:
                await msg.edit_text("<b>📈График поднялся!</b>\n"
                                    f"<b>🔥Текущий множитель: {multiplier_temp}x</b>")
            else:
                await msg.edit_text("<b>📉График опустился.\n</b>"
                                    f"🔥Текущий множитель: {multiplier_temp}x")
            multiplier_game = multiplier_temp
            if first_try == False:
                first_try = True
        await asyncio.sleep(0.75)
    if multiplier_game >= multiplier:
        reward = int(bid*multiplier)
        await msg.answer("<b>🔥Вы победили!</b>\n"
                         f"<b>Ваш множитель: {multiplier}x</b>\n"
                         f"<b>Финальный множитель: {multiplier_game}x.</b>\n"
                         f"<b>Вы получили: {reward}(+{reward-bid}) монет</b>")
        reset_parameter("users","coins",f"coins + {reward}",condition=f"WHERE telegram_id = {id}")
    else:
        await msg.answer("<b>Увы, Вы проиграли.</b>\n"
                         f"<b>Ваш множитель: {multiplier}x\n</b>"
                         f"<b>Финальный множитель: {multiplier_game}x.</b>\n"
                         f"<b>Вы потеряли: {bid} монет</b>")

    return
        
        
