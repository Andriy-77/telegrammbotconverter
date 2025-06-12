from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

BUTTON_LIST_CONVERSION = "Перелік конвертацій"
BUTTON_CREATE_CONVERSION = "Нова конвертація"


def menu_keyboards():
    builder = ReplyKeyboardBuilder()
    builder.button(text=BUTTON_LIST_CONVERSION)
    builder.button(text=BUTTON_CREATE_CONVERSION)

    markup = builder.as_markup()
    markup.resize_keyboard = True
    return markup


class ConversionCallback(CallbackData, prefix="conv", sep=";"):
    id: int


def conversions_keyboard_markup(conversion_list: list[dict]):
    builder = InlineKeyboardBuilder()

    for index, conv in enumerate(conversion_list):
        title = f"{conv['amount']} {conv['from']} → {conv['to']}"
        callback = ConversionCallback(id=index)
        builder.button(text=title, callback_data=callback.pack())

    builder.adjust(1, repeat=True)
    return builder.as_markup()
