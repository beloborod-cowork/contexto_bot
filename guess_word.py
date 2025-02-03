from database import reset_parameter,fetch_data
from random import randint
import string
from logs import *
from load_config import load_config
from model import get_placement

async def g_word(similarities,state,message,awd):
    try:
      init_word = fetch_data("users","word",condition=f"WHERE telegram_id = {message.from_user.id}")[0][0]
      if len(message.text.split(" ")) >= 2:
         await message.answer("😞<b>В сообщении разрешается не более одного слова.</b>")
         return
      word = message.text.lower()
      if word == init_word:
         
         is_guessed_today = fetch_data("users","guessed_word",condition=f"WHERE telegram_id = {message.from_user.id}")[0][0]
         if is_guessed_today != 1:
            count = fetch_data("users","COUNT(guessed_word)",condition="WHERE guessed_word = 1")[0][0]
            text = f"🎉<b>Ты угадал слово {count+1}-м из игроков!\nСледующее слово будет завтра.</b>\n\n"
            coins_given = randint(1,200)
            hint_given = randint(1,2)
            if load_config()["hints_from_words"] == True:
               if hint_given == 1:
                  reset_parameter("users","hints","hints + 1",condition=f"WHERE telegram_id = {message.from_user.id}")
                  text += f"Вы получили 1 💡Подсказку.\n"
            text +=f"Вы получили 🪙{coins_given} монет."
            reset_parameter("users","guessed_words","guessed_words + 1",condition=f"WHERE telegram_id = {message.from_user.id}")
            reset_parameter("users","guessed_word","1",condition=f"WHERE telegram_id = {message.from_user.id}")
            reset_parameter("users","exp",f"exp + {5000*load_config()["exp_multiplier"]}",condition = f"WHERE telegram_id = {message.from_user.id}")
            
            await message.answer(text)
            await state.set_state(None)
            logger_handlers.info(f"Пользователь {message.from_user.id} отгадал свое слово.")
            return
         else:
            await message.answer(f"<b>Вы уже отгадали сегодняшнее слово.\nСледующее слово будет завтра или при перезагрузке бота.</b>")
            return
      for char in word:
         if (char in string.ascii_lowercase) or (char in string.punctuation and char != "-"):
            await message.answer("❌<b>В вашем слове содержатся латинские символы/знаки пунктуации.</b>")
            return
      place = get_placement(word,awd[message.from_user.id])
      if place == -1:
         await message.answer("❌<b>Слова не найдено в словаре.</b>")
         return
      
      reset_parameter("users","attempts","attempts + 1",condition=f"WHERE telegram_id = {message.from_user.id}")
      if (word,place) not in similarities[message.from_user.id]:
         similarities[message.from_user.id].append((word,place))
         similarities[message.from_user.id].sort(key=lambda tup:tup[1])
         reset_parameter("users","exp",f"exp + {(185-place//1000)*load_config()["exp_multiplier"]}",condition = f"WHERE telegram_id = {message.from_user.id}")

      #msg = get_string_words(similarities,20)
      await message.answer(f"<i>{word}</i> - <b>{place}</b>") 
      logger_handlers.info(f"Пользователь {message.from_user.id} загадал слово '{word}'. Его рейтинг - {place} место.")      
    except Exception as e:
       await message.answer("Случилась непредвиденная ошибка. Отправьте боту команду /start, затем /word и если это не поможет, обратитесь к разработчику -> @Nonamych.")
       logger_handlers.error(f"Случилась ошибка при вводе слова пользователем {message.from_user.id}. Ошибка - {e}")