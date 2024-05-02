import json
import os
from priv_constants import TOKEN
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from mess import clean_mess_menu, next_meal, next_four_meals

def read_config():
    try:
        with open('mess_constants.json', 'r') as file:
            config_data = json.load(file)
            return config_data.get('mess_menu_location', '')
    except FileNotFoundError:
        return ''

def save_config(mess_menu_location):
    config_data = {'mess_menu_location': mess_menu_location}
    with open('mess_constants.json', 'w') as file:
        json.dump(config_data, file, indent=4)

MESS_MENU_LOCATION = read_config()
try:
    MESS_MENU = clean_mess_menu(MESS_MENU_LOCATION)
except:
    MESS_MENU = None
    MESS_MENU_LOCATION = ''
    save_config('')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
    )

async def next(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not (MESS_MENU is None or MESS_MENU.empty):
        await update.message.reply_text(next_meal(MESS_MENU))
    else:
        await update.message.reply_text("Mess menu is not available.")


async def next_four(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not (MESS_MENU is None or MESS_MENU.empty):
        await update.message.reply_text("\n".join(next_four_meals(MESS_MENU)))
    else:
        await update.message.reply_text("Mess menu is not available.")

async def use_next(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Use /next to get the next meal.\nUse /next_four to get the next four meals.")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global MESS_MENU
    global MESS_MENU_LOCATION
    file = update.message.document
    if file.mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        try:
            os.remove(MESS_MENU_LOCATION)
        except:
            pass
        MESS_MENU_LOCATION = f"mess_menus/{file.file_name}"
        if os.path.exists(MESS_MENU_LOCATION):
            os.remove(MESS_MENU_LOCATION)
        file = await update.message.document.get_file()
        await file.download_to_drive(custom_path=MESS_MENU_LOCATION)
        save_config(MESS_MENU_LOCATION)
        MESS_MENU = clean_mess_menu(MESS_MENU_LOCATION)
        await update.message.reply_text("Mess menu file received and updated successfully.")
    else:
        await update.message.reply_text("Please send an Excel file with the mess menu.")

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", use_next))
    application.add_handler(CommandHandler("next", next))
    application.add_handler(CommandHandler("next_four", next_four))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.CHAT & ~filters.REPLY & ~filters.COMMAND, use_next))
    application.add_handler(MessageHandler(filters.Document.FileExtension("xlsx"), handle_file))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
