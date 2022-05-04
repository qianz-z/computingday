# To assign each status to a number
[
    MENU_USER,
    MENU_ADMIN,
    SWITCH_USER,
    USE_ITEMS,
    USE_ITEMS2,
    REG_TYPING_NAME,
    REG_CONFIRMING_NAME,
    REG_TYPING_BASE,
    REG_SENDING_BASE_PHOTO,
    REG_CHOOSING_HERO,
    ADMIN_GIVE_ITEM_NEXT,
    ADMIN_ITEM_CONFIRMATION,
    ADMIN_MANUAL_UPDATE,
    ADMIN_MANUAL_UPDATE2,
    ADMIN_MANUAL_UPDATE3,
    ADMIN_MANUAL_UPDATE4,
    *_
] = range(100)


ITEMS_OFFENSIVE = {
    'hammer':   150,
    'chainsaw':  50,
    'pistol':    20,
    'axe':       30,
    'barrett':   80
}

# defence_mechanism = +100 base health
ITEMS_DEFENSIVE = [
    'potion',
    'base_mover',
    'defence_mechanism',
]

RULES_TEXT = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
"""
