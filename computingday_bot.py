from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ParseMode
)

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler,
    InlineQueryHandler
)

from keys import API_KEY


# To assign each status to a number
MAIN_MENU, USE_ITEMS, USE_ITEMS2, REGISTER = range(4)


def start(update, context):
    text = "Welcome to Computing Day Mass Game! "
    update.message.reply_text(text)
    context.user_data["registered"] = False
    print("Someone started the bot!")
    return main_menu(update, context)


def main_menu(update, context):
    keyboard = [
        [InlineKeyboardButton("Arena status", callback_data='arena_status'), ],
        [InlineKeyboardButton("Rules", callback_data='rules'), ],
        [InlineKeyboardButton("Use items", callback_data='use_items'), ],
    ]
    if not context.user_data['registered']:
        keyboard.append(
            [InlineKeyboardButton("Register", callback_data='register'), ],
        )

    text = "Pick an option!"
    update.message.reply_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard))
    return MAIN_MENU


def arena_status(update, context):
    pass


def register(update, context):
    text = 'Please enter your group name below.'
    update.callback_query.message.chat.send_message(text)


if __name__ == '__main__':
    top_conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            # current status: InlineQueryHandler(function to be called, pattern  = 'callback_data')
            MAIN_MENU: [
                InlineQueryHandler(arena_status, pattern='arena_status'),
                InlineQueryHandler(register, pattern='register')
            ]
        },
        fallbacks=[]
    )

    updater = Updater(API_KEY)
    dp = updater.dispatcher
    dp.add_handler(top_conv)
    updater.start_polling()
    updater.idle()
