from aiogram.types import Message
from database import reset_parameter
import random
import math
import asyncio

def sigmoid_p(x, epsilon=0.01, k=0.5, x0=5):
    """
    Вычисляет вероятность выхода p(x) с использованием сигмоиды.
    
    Параметры:
        x (float): Текущее значение x.
        epsilon (float): Постоянный шанс не выйти из цикла (по умолчанию 1%).
        k (float): Крутизна сигмоиды (по умолчанию 0.5).
        x0 (float): Точка перегиба сигмоиды (по умолчанию 5).
    
    Возвращает:
        float: Вероятность выхода p(x).
    """
    sigmoid = 1 / (1 + math.exp(-k * (x - x0)))  # Логистическая функция
    p = (1 - epsilon) * sigmoid  # Учитываем epsilon
    return p


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

async def handle_crash(msg: Message,bid: int, multiplier: float):

    won = False
    x = 1.0
    reset_parameter("users","coins",f"coins-{bid}",condition=f"WHERE telegram_id = {msg.chat.id}")
    while True:
        p = sigmoid_p(x=x,x0=5,k=0.7)
    
        # Проверяем, сработал ли выход
        
        x += 0.01
        if x >= multiplier:
            won = True
        if random.random() < p:
            if won == False:
                await msg.answer(f"Увы, но вы проиграли.\nФинальный коэффицент: {x:.2f}")
            break
    if won:
        reset_parameter("users","coins",f"coins+{int(bid*multiplier)}",condition=f"WHERE telegram_id = {msg.from_user.id}")
        await msg.answer(f"Поздравляю вас, вы победили! \nФинальный коэффицент: {x:.2f}\nВы выиграли: {int(bid*multiplier)} монет")
