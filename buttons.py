from aiogram.types import ReplyKeyboardMarkup,InlineKeyboardMarkup,InlineKeyboardButton,KeyboardButton


#кнопки в клаве
btn_menu_profile = KeyboardButton(text="👤Профиль")
btn_menu_rating = KeyboardButton(text="🏆Рейтинг")
btn_menu_settings = KeyboardButton(text="⚙️Настройки")

keyboard_menu = ReplyKeyboardMarkup(resize_keyboard=True,keyboard=[[btn_menu_profile,btn_menu_rating],[btn_menu_settings]])


#инлайн кнопки профиля
inl_btn_levelup = InlineKeyboardButton(text="⬆️Уровень",callback_data="levelup")
inl_btn_games = InlineKeyboardButton(text="🎮Мини-игры",callback_data="games")

inline_keyboard_menu = InlineKeyboardMarkup(inline_keyboard=[[inl_btn_levelup],[inl_btn_games]])


#инлайн кнопка уровня
levelup_keyboard = InlineKeyboardButton(text="⏫Повысить уровень",callback_data="levelup_levelup")

levelup_keyboard_menu = InlineKeyboardMarkup(inline_keyboard=[[levelup_keyboard]])

#инлайн кнопки игр
btn_games_crash = InlineKeyboardButton(text="📈📉Краш",callback_data="games_краш")
btn_games_dice = InlineKeyboardButton(text="🎲Кубик",callback_data="games_кубик")
btn_games_football = InlineKeyboardButton(text="⚽️Футбол",callback_data="games_футбол")
btn_games_basketball = InlineKeyboardButton(text="🏀Баскетбол",callback_data="games_баскетбол")
btn_games_darts = InlineKeyboardButton(text="🎯Дартс",callback_data="games_дартс")
btn_games_bowling = InlineKeyboardButton(text="🎳Боулинг",callback_data="games_боулинг")

games_kb = InlineKeyboardMarkup(inline_keyboard=[[btn_games_crash,btn_games_dice],[btn_games_basketball,btn_games_football],[btn_games_darts,btn_games_bowling]])
#инлайн кнопки топов
btn_rating_guessed = InlineKeyboardButton(text="🏆Топ по угаданным словам",callback_data="top_guessed")
btn_rating_exp = InlineKeyboardButton(text="🏆Топ по опыту",callback_data="top_exp")

rating_kb = InlineKeyboardMarkup(inline_keyboard=[[btn_rating_guessed],[btn_rating_exp]])


#инлайн кнопки настроек
btn_notification_enabled = InlineKeyboardButton(text="🔔Уведомления включены", callback_data="notifications_set_0")
btn_notification_disabled = InlineKeyboardButton(text="🔕Уведомления выключены", callback_data="notifications_set_1")

settings_kb = InlineKeyboardMarkup(inline_keyboard=[[btn_notification_enabled]])


#инлайн кнопки /help
btn_help_rules = InlineKeyboardButton(text="📖Правила",callback_data="help_rules")
btn_help_hints = InlineKeyboardButton(text="💡Подсказки",callback_data="help_hints")
btn_help_chatwork = InlineKeyboardButton(text="💬Работа в чатах",callback_data="help_chatwork")
btn_help_minigames = InlineKeyboardButton(text="🎮Мини-игры",callback_data="help_minigames")
btn_help_levels = InlineKeyboardButton(text="⏫Опыт и уровни",callback_data="help_levels")
btn_help_chat = InlineKeyboardButton(text="🤷‍♂️Не нашли нужной информации?",callback_data="help_chat")
help_kb = InlineKeyboardMarkup(inline_keyboard=[[btn_help_rules,btn_help_hints],[btn_help_minigames,btn_help_levels],[btn_help_chatwork],[btn_help_chat]])

def switch_btn(kb: InlineKeyboardMarkup,btn: InlineKeyboardButton) -> InlineKeyboardMarkup:
    kb.inline_keyboard = [[btn]]