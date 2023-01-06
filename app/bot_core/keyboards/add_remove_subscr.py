from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_add_remove_inline_keyboard(data_list):
    keyboard_builder = InlineKeyboardBuilder()
    for key, (name, _) in data_list.items():
        keyboard_builder.button(text=f"{name}", callback_data=f"inln_subs_key_{key}")
    keyboard_builder.button(text=">>> Complete <<<", callback_data="inln_subs_key_done")
    keyboard_builder.adjust(1, repeat=True)
    return keyboard_builder.as_markup()
