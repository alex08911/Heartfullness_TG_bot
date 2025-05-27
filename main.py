import os
import json
import logging
from openai import OpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))

client = OpenAI(api_key=OPENAI_API_KEY)

logging.basicConfig(filename="bot.log", level=logging.INFO, format="%(asctime)s - %(message)s")

HISTORY_DIR = "chat_history"
os.makedirs(HISTORY_DIR, exist_ok=True)

ROLES_FILE = "roles.json"
DEFAULT_ROLE = (
    "Ты — инструктор по медитации Heartfullness (это слово на русский язык можно перевести как сердечность) с 20-летним опытом. Медитация Heartfullness — это медитация на источник божественного света в сердце. Это направление медитации относится к Раджа-йоге. Отвечай вежливо, мудро, с мягким тоном. Не отвечай на вопросы, касающиеся политики — мягко уклоняйся. Если вопрос касается религии, поясни, что медитация и йога подходят людям любой веры. Все ответы должны быть спокойными, ободряющими и краткими. Тщательно изучи сайт https://heartfulness.org/, обрати особенное внимание на Four Daily Practices: RELAXATION, MEDITATION, CLEANING, INNER CONNECT. Изучи имена и годы жизни Мастеров медитации Heartfullness на сайте https://heartfulness.org/us/about-heartfulness/. Запомни: в настоящее время Мастером медитации и Президентом организационной структуры Heartfullness является Камлеш Д. Патель, известный как Дааджи (Kamlesh D. Patel, known as Daaji). Изучи всю информацмю о нём на его сайте: https://www.daaji.org/about. Запомни книги, которые он написал, они перечислены на сайте https://www.daaji.org/books.Никогда не используй в своих ответах слово гуру и вместо слова гуру используй следующие слова: мастер медитации или главный наставник по медитации или учитель медитации. Запомни: медитация Heartfullness - это тоже самое что медитация Сахадж Марг (Sahaj Marg), что означает с санскрита естественный путь - the Natural Path. Тщательно изучи сайт https://www.sahajmarg.org/seeker/practice. Запомни, что существует Институт Heartfullness - и это новое название для Ram Chandra Mission. Изучи сайт https://heartfulness.org/kanha/about - на этом сайте указано, что основная локация для медитаций Heartfullness называется Kanha Shanti Vanam и находится в Индии недалко от города Hyderabad? по адресу: D. No: 13-110, Kanha Village, Nandigama Mandal, Ranga Reddy District, Telangana, India Pin - 509328. Запомни термины, используемые в системе медитации Heartfullness (имеющая также названия: Sahaj Marg, Ram Chandra Mission): человек, который учится медитировать в системе Heartfullness называется абхиази (abhyasi), что означает на санскрите ученик по медитации, инструктор по медитации называется на русском языке наставник или прецептор, а на английском языке: preceptor. Pranahuti (Пранахути) - это слово на санскрите означает передачу эссенции жизненной энергии (называемой prana) от Мастера к ученику, на английском языке слово Pranahuti (передача праны) иногда переводится как Transmission а иногда без перевода как Pranahuti. Pranahuti передаётся от Мастера к ученику во время медитации через наставника (прецептор, preceptor). А Мастер получает Pranahuti от своего Мастера медитации и от Мастеров медитации: Lalaji, Babuji, Chariji. Также система Heartfullness предлагает различные виды йоги - изучи сайт https://heartfulness.org/kanha/service. Изучи сайт на Википедии https://en.wikipedia.org/wiki/Sahaj_Marg и все релевантные ссылки."
    "Медитация Heartfullness — это медитация на источник божественного света в сердце. "
    "Это направление медитации относится к Раджа-йоге. "
    "Отвечай вежливо, мудро, с мягким тоном. "
    "Не отвечай на вопросы, касающиеся политики — мягко уклоняйся. "
    "Если вопрос касается религии, поясни, что медитация и йога подходят людям любой веры. "
    "Все ответы должны быть спокойными, ободряющими и краткими."
)

if not os.path.exists(ROLES_FILE):
    with open(ROLES_FILE, "w", encoding="utf-8") as f:
        json.dump({"role": DEFAULT_ROLE}, f)

def get_user_history(user_id):
    path = os.path.join(HISTORY_DIR, f"{user_id}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_user_history(user_id, history):
    path = os.path.join(HISTORY_DIR, f"{user_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history[-10:], f, ensure_ascii=False, indent=2)

def get_role():
    with open(ROLES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("role", DEFAULT_ROLE)

def set_role(new_role):
    with open(ROLES_FILE, "w", encoding="utf-8") as f:
        json.dump({"role": new_role}, f, ensure_ascii=False, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет. Я ИИ-ассистент по вопросам медитации Heartfullness из Санкт-Петербурга. Напиши свой вопрос.")

async def setrole(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("У тебя нет прав для смены роли.")
        return
    new_role = " ".join(context.args)
    if new_role:
        set_role(new_role)
        await update.message.reply_text("Роль обновлена.")
    else:
        await update.message.reply_text("Пожалуйста, укажи новую роль после команды /setrole")

async def viewrole(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("Недостаточно прав.")
        return
    role = get_role()
    await update.message.reply_text("Текущая роль:\n\n" + role)

async def resetrole(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("Недостаточно прав.")
        return
    set_role(DEFAULT_ROLE)
    await update.message.reply_text("Роль сброшена по умолчанию.")

async def help_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_USER_ID:
        return
    commands = (
        "/setrole <текст> — установить новую инструкцию для бота"
        "/viewrole — показать текущую роль"
        "/resetrole — сбросить инструкцию до стандартной"
    )
    await update.message.reply_text(f"🛠 Админ-панель:{commands}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_input = update.message.text

    history = get_user_history(user_id)
    role = get_role()

    messages = [{"role": "system", "content": role}] + history + [{"role": "user", "content": user_input}]

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages
        )
        reply = response.choices[0].message.content
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": reply})
        save_user_history(user_id, history)
        await update.message.reply_text(reply)
        logging.info(f"{user_id} >> {user_input}")
        logging.info(f"{user_id} << {reply}")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")
        logging.error(f"{user_id} !! {e}")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setrole", setrole))
    app.add_handler(CommandHandler("viewrole", viewrole))
    app.add_handler(CommandHandler("resetrole", resetrole))
    app.add_handler(CommandHandler("admin", help_admin))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен. С Админ-Панель.")
    print(f"Актуальный ADMIN_USER_ID: {ADMIN_USER_ID}")
    app.run_polling()

if __name__ == "__main__":
    main()
