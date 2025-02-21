#Добавление нужных модулей
from aiogram.dispatcher.router import Router
from model import init,get_placement,get_string_words
from aiogram.filters import Command,CommandStart,StateFilter,CommandObject
from aiogram.types import Message,CallbackQuery,FSInputFile
from datetime import datetime,timedelta
import asyncio
from database import reset_parameter,fetch_data,insert_data, get_top10, create_chats_db,create_chat_db,insert_data_from_table
from model import init,word_hint
from aiogram.client.bot import Bot
from aiogram import F,exceptions
import buttons
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import string
from promo import process_promo
from logs import logger_handlers
from api_token import ADMINISTRATORS
from load_config import *
from random import randint
from guess_word import g_word
from games import handle_game,handle_crash
from help_texts import*
#-------------------------------------------------------------
GAMES_EMOJI = {
    "кубик": "🎲",
    "футбол": "⚽",
    "баскетбол": "🏀",
    "боулинг": "🎳",
    "дартс": "🎯"
}
CHATS = ["group","supergroup"]
class Word(StatesGroup):
   is_guessing = State()

class Game(StatesGroup):
   bid = State()
   multiplier = State()

all_word_dicts = dict()
similarities = dict()
async def generate_words(bot: Bot,all_word_dict,similarities,bc):

   for id in fetch_data("users","telegram_id"):
         init_word,word_dict = init() #подгрузка слов
         all_word_dict[id[0]] = word_dict
         similarities[id[0]] = list()
         reset_parameter("users","word",f"'{init_word}'",condition=f"WHERE telegram_id = {id[0]}")
         if bc == True:
            notifications_enabled = fetch_data("users","notifications_enabled",condition = f"WHERE telegram_id = {id[0]}")
            if notifications_enabled[0][0]==1:
               try:
                  await bot.send_message(id[0],"<b>Ваше ежедневное слово было обновлено.</b>")
               except exceptions.TelegramForbiddenError:
                  logger_handlers.warning(f"Не удалось отправить уведомление пользователю {id[0]} - у него заблокирован бот.")
               except exceptions.TelegramBadRequest:
                  pass
   return all_word_dict,similarities
async def schedule_daily_task(bot: Bot,bc: bool = True):
   global all_word_dicts
   global similarities 
   while True:
      with open("data/word_data.json","r",encoding="utf-8") as f:
         all_word_dicts = json.load(f)
      similarities = dict()
      for id in fetch_data("users","telegram_id"):
         similarities[id[0]] = list()
      if all_word_dicts == {}:
         all_word_dicts,similarities = await generate_words(bot,all_word_dicts,similarities,bc)
      else:
         now = datetime.now()
         next_day = datetime(now.year, now.month, now.day, 0, 0, 0) + timedelta(days=1)
         delay = (next_day - now).total_seconds()
         await asyncio.sleep(delay)
         
         reset_parameter("users","attempts",0)
         reset_parameter("users","guessed_word",0)  
         all_word_dicts,similarities = await generate_words(bot,all_word_dicts,similarities,bc)   
         
         logger_handlers.info("Ежедневные слова игроков были сброшены.")
      with open("data/word_data.json","w",encoding="utf-8") as f:
         json.dump(all_word_dicts,f,ensure_ascii=False)

async def reset_word(bot: Bot,id_sender: int,id_receiver: int):
   global similarities
   global all_word_dicts
   init_word,word_dict = init()
   all_word_dicts[id_receiver] = word_dict
   similarities[id_receiver] = list()
   reset_parameter("users","word",f"'{init_word}'",condition=f"WHERE telegram_id = {id_receiver}")
   reset_parameter("users","attempts",0,condition=f"WHERE telegram_id = {id_receiver}")
   reset_parameter("users","guessed_word",0,condition=f"WHERE telegram_id = {id_receiver}")
   await bot.send_message(id_sender,f"Сброс слова для 🆔{id_receiver} прошел успешно.")
   await bot.send_message(id_receiver,"Администратор сбросил ваше слово.")
   logger_handlers.info(f"Сброс слова для ID {id_receiver} прошел успешно.")

router = Router() # Добавление роутера

new_init_word,new_init_dict = init()

#инлайн кнопки
@router.callback_query(F.data.startswith("top")) #рейтинги
async def tops(call: CallbackQuery):
   name = call.data.split("_")[1]
   if name == "guessed":
      top_10 = get_top10('username,guessed_words','guessed_words')
      text = "🏆<b>Топ-10 по количеству угаданных слов:</b>\n\n"
      for i,data in enumerate(top_10,0):
        username = data[0]
        guessed_words = data[1]
        text += f"<i>{i+1}. {username} - {guessed_words} раз</i>\n"
      await call.message.answer(text)
   elif name == "exp":
      top_10 = get_top10('username,exp,level','exp')
      text = "🏆<b>Топ-10 по опыту:</b>\n\n"
      for i,data in enumerate(top_10,0):
        username = data[0]
        exp = data[1]
        level = data[2]
        exp_needed = load_rewards()[str(level+1)]["xp_req"]
        text += f"<i>{i+1}. {username} - {level} lvl({exp}/{exp_needed}) </i>\n"
      await call.message.answer(text)

@router.callback_query(F.data.startswith("levelup"))
async def levelup_menu(call: CallbackQuery):
   if call.message.chat.type in CHATS:
      await call.message.answer("Данная функция пока что недоступна в чатах.")
      return
   info = call.data.split("_")
   exp, level = fetch_data("users","exp,level",condition=f"WHERE telegram_id ={call.message.chat.id}")[0]
   rewards = load_rewards()[str(level+1)]
   exp_needed = rewards["xp_req"]
   hints = rewards["hints"]
   coins = rewards["coins"]
   if len(info)>1:
      if exp >= exp_needed:
         reset_parameter("users","level","level+1",condition = f"WHERE telegram_id = {call.message.chat.id}")
         reset_parameter("users","hints",f"hints+{hints}",condition = f"WHERE telegram_id = {call.message.chat.id}")
         reset_parameter("users","coins",f"coins+{coins}",condition = f"WHERE telegram_id = {call.message.chat.id}")
         exp, level = fetch_data("users","exp,level",condition=f"WHERE telegram_id ={call.message.chat.id}")[0]
         rewards = load_rewards()[str(level+1)]
         exp_needed = rewards["xp_req"]
         hints = rewards["hints"]
         coins = rewards["coins"]
         await call.message.edit_text(f"<b>⏫Добро пожаловать в меню повышения уровня!\n\nВаш текущий уровень: {level}\nВаш опыт: {exp}/{exp_needed}\nЗа повышение уровня вы получите:\n💡{hints} Подсказок\n🪙{coins} монет</b>",reply_markup=buttons.levelup_keyboard_menu)
      else:
         await call.message.answer("<b>У вас недостаточно опыта!</b>")
      return

   await call.message.answer(f"<b>⏫Добро пожаловать в меню повышения уровня!\n\nВаш текущий уровень: {level}\nВаш опыт: {exp}/{exp_needed}\nЗа повышение уровня вы получите:\n💡{hints} Подсказок\n🪙{coins} монет</b>",reply_markup=buttons.levelup_keyboard_menu)

@router.callback_query(F.data.startswith("notifications"))
async def settings(call: CallbackQuery):
   if call.message.chat.type in CHATS:
      await call.message.answer("Данная функция пока что недоступна в чатах.")
      return
   if call.data.split("_")[0] == "notifications" and call.data.split("_")[1] == "set":
      reset_parameter("users","notifications_enabled",int(call.data.split("_")[2]),condition=f"WHERE telegram_id = {call.message.chat.id}")
      if call.data.split("_")[2] == "1":
          buttons.switch_btn(buttons.settings_kb,buttons.btn_notification_enabled)
      else: buttons.switch_btn(buttons.settings_kb,buttons.btn_notification_disabled)
      await call.message.edit_reply_markup(reply_markup=buttons.settings_kb)

@router.callback_query(F.data.startswith("help"))
async def help(call: CallbackQuery):
   if call.data.split("_")[0] == "help":
      if call.data.split("_")[1] == "rules":
         await call.message.answer(rules_text)
      elif call.data.split("_")[1] == "hints":
         await call.message.answer(hints_text)
      elif call.data.split("_")[1] == "minigames":
         await call.message.answer(minigames_text)
      elif call.data.split("_")[1] == "levels":
         await call.message.answer(levels_text)
      elif call.data.split("_")[1] == "chatwork":
         await call.message.answer(chatwork_text)
      elif call.data.split("_")[1] == "chat":
         await call.message.answer(chat_text)

@router.callback_query(F.data.startswith("games"))
async def handle_games(call: CallbackQuery,state: FSMContext):
   #if call.message.chat.type in CHATS:
      #await call.message.answer("Данная функция пока что недоступна в чатах.")
      #return
   if len(call.data.split("_")) > 1:
      await state.set_state(Game.bid)
      await state.set_data({"game": call.data.split("_")[1]})
      await call.message.answer(f"Отлично! Вы выбрали игру {call.data.split("_")[1]}. Введите вашу ставку(0 - отменить):")
   else:
      await call.message.edit_text("Добро пожаловать в меню миниигр! Выбирайте игру вам по душе.",reply_markup=buttons.games_kb)
#Доступные всем команды
@router.message(CommandStart())
async def start(msg: Message,state: FSMContext):
  if msg.chat.type != "private":
     await msg.answer("Регистрация доступна только в личных сообщениях бота.")
     return
  try:
   all_word_dicts[msg.from_user.id] = new_init_dict
   is_user_not_new = fetch_data("users","*",condition=f"WHERE telegram_id = {msg.from_user.id}")
   if not is_user_not_new:
      referrer_id = 'NULL'
      try:
         if (len(msg.text.split(' ')) > 0):
            referrer_id = int(msg.text.split(' ')[1])
      except Exception:
         pass
         
      insert_data("users","telegram_id,username,word,attempts,guessed_words,guessed_word,notifications_enabled,hints,referrer_id",f"{msg.from_user.id},'{msg.from_user.username}','{new_init_word}',0,0,0,1,5,{referrer_id}")
      if referrer_id != 'NULL':
         reset_parameter("users","referrals","referrals + 1",condition=f"WHERE telegram_id = {referrer_id}")
         reset_parameter("users","hints","hints + 3",condition=f"WHERE referrer_id = {referrer_id} AND telegram_id = {msg.from_user.id}")
         reset_parameter("users","hints","hints + 1",condition=f"WHERE telegram_id = {referrer_id}")
         await msg.bot.send_message(referrer_id,f"Пользователь @{msg.from_user.username}(ID: {msg.from_user.id}) присоединился по вашей реферальной ссылке. Награда начислена на ваш аккаунт.")
   similarities[msg.from_user.id] = list()
   await msg.answer(f"Привет,{msg.from_user.first_name}!\nЭто бот, позволяющий играть в Contexto прямо в Telegram!\nДля того, чтобы попытаться угадать слово, используйте команду /word.\nЧтобы посмотреть топ-20 ваших слов, используйте команду /top.",reply_markup=buttons.keyboard_menu)
   await state.set_state(None)
   logger_handlers.info(f"Пользователь с ID {msg.from_user.id} успешно ввёл команду /start.")
  except Exception as e:
     await msg.answer("Произошла непредвиденная ошибка при вводе команды. Обратитесь к создателю бота -> @Nonamych.")
     logger_handlers.error(f"Произошла ошибка при вводе команды /start у пользователя {msg.from_user.id}. Ошибка - {e}")


@router.message(Command("word")) #Обработка команды /word
async def word(message: Message,state: FSMContext):
   if message.chat.type in CHATS:
      await message.answer("Данная функция пока что недоступна в чатах.")
      return
   try:
      await state.set_state(Word.is_guessing)
      await message.answer(f"<b>Теперь вы можете загадывать слова! Удачи вам, {message.from_user.first_name}, в отгадывании слов!</b>")
      logger_handlers.info(f"Пользователь {message.from_user.id} использовал команду /word")
   except Exception as e:
      logger_handlers.error(f"Произошла ошибка при вводе команды /word у пользователя {message.from_user.id}. Ошибка - {e}")
  
@router.message(Command("nickname"))
async def set_nickname(msg: Message):
   if len(msg.text) > 29:
      await msg.answer("Вы превысили допустимый лимит символов! Ваш никнейм должен содержать не более 20 символов.")
   else:

      nickname = " ".join(msg.text.split(" ")[1:])
      edited_nickname = " ".join(nickname.split("\n"))
      reset_parameter("users","username",f"'{edited_nickname}'",condition=f"WHERE telegram_id = {msg.from_user.id}")
      await msg.answer("Вы успешно установили свой новый никнейм.")

@router.message(Command("top"))

async def top(msg: Message):
    if msg.chat.type in CHATS:
      await msg.answer("Данная функция пока что недоступна в чатах.")
      return
    try:
      placement = get_string_words(similarities[msg.from_user.id],10)
      await msg.answer(placement)
      logger_handlers.info(f"Пользователь с ID {msg.from_user.id} успешно ввёл команду /top.")
    except Exception as e:
       logger_handlers.error(f"Произошла ошибка при вводе команды /top у пользователя {msg.from_user.id}. Ошибка - {e}")
       

@router.message(Command("hint"))
async def hint(msg: Message):
    if msg.chat.type in CHATS:
      await msg.answer("Данная функция пока что недоступна в чатах.")
      return
    try:
      guessed_word = fetch_data("users","word",condition=f"WHERE telegram_id = {msg.chat.id}")[0][0]
      hints = fetch_data("users","hints",condition=f"WHERE telegram_id = {msg.chat.id}")[0][0]
      if hints >0:
         hint = word_hint(all_word_dicts[msg.chat.id],guessed_word,100)
         reset_parameter("users","hints","hints - 1",condition=f"WHERE telegram_id = {msg.chat.id}")
         await msg.answer(hint["text"])
      else:
         await msg.answer("❌<b>У вас недостаточно подсказок.</b>")
      logger_handlers.info(f"Пользователь с ID {msg.from_user.id} успешно ввёл команду /hint Подсказанное слово - {hint}.")
    except Exception as e:
      logger_handlers.error(f"Произошла ошибка при вводе команды /hint у пользователя {msg.from_user.id}. Ошибка - {e}")

@router.message(Command("help"))
async def help(msg: Message):
   await msg.answer(f"{msg.from_user.first_name}, полезную информацию можно прочитать здесь:",reply_markup=buttons.help_kb)

@router.message(Command("promo"))
async def promo(msg: Message):
   promo_name = msg.text.split(" ")[1]
   output = process_promo(promo_name,msg.from_user.id)
   await msg.answer(output)

@router.message(Command("referral"))
async def referral(msg: Message):
   id = msg.from_user.id
   referral_amount = fetch_data("users","referrals",condition=f"WHERE telegram_id = {id}")[0][0]
   await msg.answer(f"👥<b>Добро пожаловать в реферальную систему бота Contexto!</b>\n\nВами приглашено <b><i>{referral_amount}</i></b> людей.\n\nВаша реферальная ссылка:\nhttps://t.me/ContextoGame_Bot?start={id} \nРеферал получит дополнительные 3 💡Подсказки, а вы - 1💡Подсказку за каждого приглашенного реферала.")

@router.message(Command("игрок",prefix="."))
async def check_player_status(msg: Message):
   if not msg.reply_to_message:
      await msg.answer("Данная команда может быть использована только в ответ на сообщение.")
      return
   player_id = msg.reply_to_message.from_user.id
   user_data = fetch_data("users","*",condition=f"WHERE telegram_id = {player_id}")
   if not user_data:
      await msg.answer("Ошибка: не удалось найти профиль этого игрока. Возможно, он не зарегистрирован в боте.")
      return
   id = user_data[0][0]
   username = user_data[0][1]
   attempts = user_data[0][3]
   guessed_word = "✅" if user_data[0][5] == 1 else "❌"
   level = user_data[0][13]
   await msg.answer(f"👤Профиль {username} | 🆔 {id}\n"
                    f"-------------------------------\n"
                    f"⏫Уровень: {level}\n"
                    f"📖Попыток сегодня: {attempts}\n"
                    f"🏅Угадано сегодняшнее слово: {guessed_word}\n"
                     "-------------------------------")

@router.message(Command("register_chat"))#Регистрация чата
async def register_chat(msg: Message):
   admins = await msg.chat.get_administrators()
   owner = next((admin for admin in admins if admin.status == "creator"), None)
   if msg.from_user.id != owner.user.id:
      await msg.answer("Вы не являетесь владельцем чата, чтобы зарегистрировать чат.")
      return
   
   chat_id = msg.chat.id
   chat_exists = fetch_data("chats","*",condition=f"WHERE chat_id = {abs(chat_id)}")
   if not chat_exists:
      create_chats_db()
      create_chat_db(abs(chat_id))
      insert_data_from_table(f"chat_{abs(chat_id)}","user_id,username",f"SELECT telegram_id,username FROM users WHERE telegram_id = {msg.from_user.id}")
      insert_data("chats","chat_id,chat_name",f"{abs(chat_id)},'{msg.chat.full_name}'")
      reset_parameter("users","chat_linked",f"{abs(chat_id)}",condition=f"WHERE telegram_id = {msg.from_user.id}")
      await msg.answer("Вы успешно зарегистрировали чат!\n"
                     "Теперь участники чата могут привязать свой профиль к боту, используя команду /link_chat")
      return
   await msg.answer("Данный чат уже был зарегистрирован.")
   
@router.message(Command("link_chat"))
async def link_chat(msg: Message):
   if msg.chat.type not in CHATS:
      await msg.answer("Данная команда доступна только в чатах.")
      return
   user_id = msg.from_user.id
   chat_id = abs(msg.chat.id)
   chat_info = fetch_data("chats","*",condition=f"WHERE chat_id = {chat_id}")
   if not chat_info:
      await msg.answer("Данный чат еще не был зарегистрирован. ")
      return
   user_info = fetch_data(f"chat_{chat_id}","*",condition=f"WHERE user_id = {user_id}")
   if not user_info:
      insert_data_from_table(f"chat_{chat_id}","user_id,username",f"SELECT telegram_id,username FROM users WHERE telegram_id = {user_id}")
      reset_parameter("users","chat_linked",f"{chat_id}",condition=f"WHERE telegram_id = {msg.from_user.id}")
      await msg.answer("Вы успешно привязали свой профиль!")
      return
   await msg.answer("Вы уже привязали свой профиль к чату. Если вы хотите перепривязать чат, ожидайте будущих обновлений")

#Админские команды
@router.message(Command("grestart",prefix="."))
async def global_restart(msg: Message):
   if msg.chat.type in CHATS:
      await msg.answer("Данная функция пока что недоступна в чатах.")
      return
   if msg.from_user.id in ADMINISTRATORS:
      await schedule_daily_task(msg.bot)

@router.message(Command("restart"))
async def local_restart(msg: Message):
   if msg.chat.type in CHATS:
      await msg.answer("Данная функция пока что недоступна в чатах.")
      return
   try:
      if msg.from_user.id in ADMINISTRATORS:
         id = int(msg.text.split(" ")[1])
         await reset_word(bot=msg.bot,id_receiver=id,id_sender = msg.from_user.id)
         logger_handlers.info(f"Администратор {msg.from_user.id} сбросил слово пользователя {id}.")
   except Exception as e:
      logger_handlers.error(logger_handlers.error(f"Произошла ошибка при вводе команды /restart у пользователя {msg.from_user.id}. Ошибка - {e}"))

@router.message(Command("exp_multiplier"))
async def set_xp_multiplier(msg: Message):
   if msg.from_user.id not in ADMINISTRATORS:
      return
   if msg.chat.type in CHATS:
      await msg.answer("Данная функция пока что недоступна в чатах.")
      return
   multiplier = msg.text.split(" ")[1]
   config = load_config()
   config["exp_multiplier"] = float(multiplier)
   save_config(config)
   await msg.answer("Множитель успешно обновлен.")

@router.message(Command("hfw"))
async def set_xp_multiplier(msg: Message):
   if msg.from_user.id not in ADMINISTRATORS:
      return
   if msg.chat.type in CHATS:
      await msg.answer("Данная функция пока что недоступна в чатах.")
      return
   config = load_config()
   if config["hints_from_words"] == True:
      config["hints_from_words"] = False
      await msg.answer("Теперь подсказки не могут выпасть за угадывание слов")
   elif config["hints_from_words"] == False:
      config["hints_from_words"] = True
      await msg.answer("Теперь подсказки могут выпасть за угадывание слов")
   save_config(config)

   
@router.message(Command("hints_add"))
async def hints_add(msg: Message):
   if msg.chat.type in CHATS:
      await msg.answer("Данная функция пока что недоступна в чатах.")
      return
   try:
      if msg.from_user.id in ADMINISTRATORS:
         info = msg.text.split(" ")
         id = int(info[1])
         amount = int(info[2])
         reset_parameter("users","hints",f"hints + {amount}",condition=f"WHERE telegram_id = {id}")
         await msg.answer("Начисление проведено успешно.")
         await msg.bot.send_message(id,f"<b>Вам зачислено {amount}💡Подсказок.</b>")
         logger_handlers.info(f"Администратор {msg.from_user.id} использовал команду /hints_add. Пользователю {id} добавлено {amount} Подсказок.")
      else: await msg.answer("У вас нет доступа к данной команде.")
   except Exception as e:
      logger_handlers.error(logger_handlers.error(f"Произошла ошибка при вводе команды /hints_add у пользователя {msg.from_user.id}. Ошибка - {e}"))

@router.message(Command("add_promo"))
async def add_promo(msg: Message):
   if msg.chat.type in CHATS:
      await msg.answer("Данная функция пока что недоступна в чатах.")
      return
   try:
      if msg.from_user.id in ADMINISTRATORS:
         info = msg.text.split(" ")[1:]
         name = info[0]
         activations = int(info[1])
         rewards = int(info[2])
         insert_data("promos","name,activations,hints",f"'{name}',{activations},{rewards}")
         await msg.answer("Промокод успешно добавлен.")
         logger_handlers.info(f"Администратор {msg.from_user.id} использовал команду /add_promo. Добавленный промокод - {name};кол-во активаций = {activations}; кол-во подсказок: {rewards}")
   except Exception as e:
      logger_handlers.error(logger_handlers.error(f"Произошла ошибка при вводе команды /add_promo у пользователя {msg.from_user.id}. Ошибка - {e}"))

@router.message(Command("load_log"))
async def load_log(msg: Message):
   if msg.chat.type in CHATS:
      await msg.answer("Данная функция пока что недоступна в чатах.")
      return
   if msg.from_user.id in ADMINISTRATORS:
      try:
         logger_handlers.info("Лог сохранен.")
         await msg.bot.send_document(chat_id=msg.from_user.id,document=FSInputFile(path="data/latest.log"))
         with open('data/latest.log', 'w') as file:
            pass
      except Exception as e:
         logger_handlers.error(f"Произошла ошибка при сохранении лога: {e}")
         await msg.answer("Произошла неизвестная ошибка.")

@router.message(Command("bc"))
async def change_broadcast(msg: Message):
   if msg.chat.type in CHATS:
      await msg.answer("Данная функция пока что недоступна в чатах.")
      return
   if msg.from_user.id not in ADMINISTRATORS:
      return
   config = load_config()
   if config["broadcast_when_restarted"] == True:
      config["broadcast_when_restarted"] = False
      await msg.answer("Обновление слов отключено")
   elif config["broadcast_when_restarted"] == False:
      config["broadcast_when_restarted"] = True
      await msg.answer("Обновление слов включено")
   save_config(config)

@router.message(Command("broadcast"))
async def broadcast(msg:Message):
   if msg.chat.type in CHATS:
      await msg.answer("Данная функция пока что недоступна в чатах.")
      return
   broadcasted_msg = " ".join(msg.text.split(" ")[1:])
   for id in fetch_data("users","telegram_id"):
      notifications_enabled = fetch_data("users","notifications_enabled",condition = f"WHERE telegram_id = {id[0]}")
      if notifications_enabled[0][0]==1:
         try:
            await msg.bot.send_message(id[0],broadcasted_msg)
         except exceptions.TelegramForbiddenError:
            logger_handlers.warning(f"Не удалось отправить уведомление пользователю {id[0]} - у него заблокирован бот.")
   await msg.answer("Рассылка проведена успешно.")
   
@router.message(Command("admin_panel"))
async def admin_panel(msg: Message):
   if msg.chat.type in CHATS:
      await msg.answer("Данная функция пока что недоступна в чатах.")
      return
   if msg.from_user.id not in ADMINISTRATORS:
      return
   await msg.answer("Список команд:\n\n/grestart: Обновить слово у всех\n/restart *id*: Обновить слово у игрока id\n/exp_multiplier *х*: установить множитель х для опыта\n/hfw: включить/выключить получение подсказок за угаданные слова\n/hints_add *id* *x*: начислить x подсказок игроку id\n/add_promo *promo* *x* *y*: добавить промокод promo на x активаций с наградой в y подсказок\n/load_log - выгрузить лог бота\n/bc: включить/выключить сброс слова при рестарте\n/broadcast *msg*: рассылка сообщения msg всем юзерам бота")
#Словесные команды
@router.message(F.text.lower().contains("рейтинг"))
async def rating(msg: Message):
    await msg.answer("Выбери рейтинг, который хочешь посмотреть:",reply_markup=buttons.rating_kb)



@router.message(F.text.lower().contains("профиль"))
async def profile(msg: Message):
   user_data = fetch_data("users","*",condition=f"WHERE telegram_id = {msg.from_user.id}")[0]
   id = user_data[0]
   username = user_data[1]
   attempts = user_data[3]
   guessed_words = user_data[4]
   guessed_word = "✅" if user_data[5] == 1 else "❌"
   hints = user_data[7]
   exp = user_data[10]
   coins = user_data[11]
   level = user_data[13]
   exp_req = load_rewards()[str(level+1)]["xp_req"]
   chat_linked = user_data[14]
   chat_name = fetch_data("chats","chat_name",condition=f"WHERE chat_id = {chat_linked}")[0][0]
   await msg.answer(f"<b>👤Ваш профиль:\n🆔ID: {id}\n✍️Никнейм: {username}\n💡Подсказок: {hints}\n⏫Уровень: {level}\n📖Опыт: {exp}/{exp_req}\n🪙Монет: {coins}\n📖Попыток сегодня: {attempts}\n🥇Угаданных слов: {guessed_words}\n🏅Угадано сегодняшнее слово: {guessed_word}\n\nПривязанный чат: {chat_name}</b>",reply_markup=buttons.inline_keyboard_menu)

@router.message(F.text.lower().contains("настройки"))
async def settings_menu(msg: Message):
   if msg.chat.type in CHATS:
      await msg.answer("Данная функция пока что недоступна в чатах.")
      return
   await msg.answer("<b>⚙️Ваши настройки:</b>",reply_markup=buttons.settings_kb)

@router.message(StateFilter(Word.is_guessing))
async def guess_word(message: Message,state: FSMContext):
    await g_word(similarities,state,message,all_word_dicts)

@router.message(StateFilter(Game.bid))
async def save_bid(msg: Message, state: FSMContext):
   bid = int(msg.text)
   if bid == 0:
      await msg.answer("Ставка была возвращена.")
      await state.set_state(None)
      return
   game = await state.get_data()
   if game["game"] != "краш":
      dice = await msg.answer_dice(emoji=GAMES_EMOJI[game["game"]])
      result = await handle_game(game["game"],dice,msg.from_user.id,bid)
      await msg.answer(result)
      await state.set_state(None)
   else:
      await msg.answer("Введите множитель, на котором вы хотите забрать монеты:")
      await state.set_state(Game.multiplier)
      await state.set_data({"bid": bid,"id": msg.from_user.id})
      
   
@router.message(StateFilter(Game.multiplier))
async def play_crash(msg: Message, state: FSMContext):
   bid_data = await state.get_data()
   bid = bid_data["bid"]
   id = bid_data["id"]
   multiplier = float(msg.text)
   await state.set_state(None)
   message_new = await msg.bot.send_message(msg.chat.id,"Игра началась! Текущий множитель: 1.00x")
   
   #await msg.edit_text("Игра началась! Текущий множитель: 1.00x")
   
   await asyncio.sleep(1)
   await handle_crash(message_new,bid,multiplier,id)
   

@router.message()
async def reminder(msg: Message):
   if msg.chat.type in CHATS:
      return
   await msg.answer("Возможно вы хотели попробовать отгадать слово, но забыли отправить команду /word боту, . Отправьте эту команду и начните отгадывать слова!")   

