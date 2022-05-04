import os
import traceback

from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler,
    PicklePersistence,
)

from const import (
    MENU_USER,
    MENU_ADMIN,
    SWITCH_USER,
)
from keys import API_KEY, USER_ADMINS
from hero import Hero

from adminbot import (
    admin_menu,
    update_conv,
    give_item_conv,
)
from userbot import (
    main_menu,
    register_conv,
    use_item_conv,
    arena_status_cbh,
    group_status_cbh,
    rules_cbh
)


def menu(update, context):
    chat_id = update.effective_chat.id
    if chat_id in USER_ADMINS:
        return admin_menu(update, context)
    return main_menu(update, context)


def err(update, context):
    """Error handler callback for dispatcher"""
    error = context.error
    traceback.print_exception(error)
    if update is not None and update.effective_user is not None:
        context.bot.send_message(update.effective_user.id,
            "I'm sorry, an error has occurred. The devs have been alerted!")


def temp(update, context):
    query = update.callback_query
    # assert query.message.chat.id == CHAT_ADMINS
    print("Yay")


def start(update, context):
    chat_id = update.effective_chat.id

    if chat_id < 0:  # private message
        text = "Please private message the bot instead!"
        update.message.reply_text(text)
        return

    if 'registered' in context.user_data and context.user_data['registered']:
        return main_menu(update, context)

    # if chat_id in USER_ADMINS:
    #     text = "Welcome to the exclusive ADMINS ONLY page!!!!"
    #     update.message.reply_text(text)
    #     context.user_data['admin_giveitem_group'] = None
    #     context.user_data['admin_manual_group'] = None
    #     context.user_data['admin_delta_health'] = 0
    #     context.user_data['using_item'] = None
    #     return admin_main_menu(update, context)

    # What users will receive
    text = "Welcome to Computing Day Mass Game! "
    update.message.reply_text(text)
    context.user_data['group_name'] = None
    print("Someone started the bot!")
    return main_menu(update, context)


def unrecognized_buttons(update, context):
    """Edit the query so the user knows button is not accepted."""
    query = update.callback_query
    query.answer()
    text = query.message.text
    text += "\n\nSorry, this button has expired. Please send the previous command again."
    query.edit_message_text(text)


def switch_user1(update, context):
    update.message.reply_text(
        "Who would you like to be?",
        reply_markup=ReplyKeyboardMarkup([['User', 'Admin']]))
    return SWITCH_USER


def switch_user2(update, context):
    text = update.message.text
    if text == 'User':
        state = MENU_USER
    elif text == 'Admin':
        state = MENU_ADMIN
    update.message.reply_text(
        f"Alrights you are now a {text}. Send /menu to see what you can do.",
        reply_markup=ReplyKeyboardRemove())
    return state


top_conv = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        MENU_USER: [
            register_conv,
            use_item_conv,
            arena_status_cbh,
            group_status_cbh,
            rules_cbh,
            CommandHandler('menu', callback=main_menu),
        ],
        MENU_ADMIN: [
            update_conv,
            give_item_conv,
            arena_status_cbh,
            CommandHandler('menu', callback=admin_menu)
        ],
        SWITCH_USER: [MessageHandler(Filters.text, switch_user2)]
    },
    # if it is not in entry point or in state
    fallbacks=[
        CommandHandler('switch', callback=switch_user1),
        CallbackQueryHandler(unrecognized_buttons),
    ],
    name='top_conv',
    persistent=True
)


if __name__ == '__main__':
    file_exists = os.path.exists('persistence.pickle')
    persist = PicklePersistence('persistence.pickle')
    updater = Updater(API_KEY, use_context=True, persistence=persist)
    # updater = Updater(API_KEY, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(top_conv)
    # dispatcher.add_error_handler(err)

    if not file_exists:
        # Populate fake data
        group1 = Hero('team doggos', 200)
        group2 = Hero('team cats', 200)
        dispatcher.bot_data['groups'] = {
            group.group_name: group for group in [group1, group2]
        }

    updater.start_polling()
    updater.idle()
    print("Stopping...")
