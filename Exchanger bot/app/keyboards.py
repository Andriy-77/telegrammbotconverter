from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
BUTTON_LIST_CONVERSION = "Перелік конвертацій"
BUTTON_CREATE_CONVERSION = "Нова конвертація"
CURRENCIES = [
    "USD", "EUR", "UAH", "GBP", "PLN", "CHF", "JPY", "CNY", "CAD", "AUD",
]


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

def currency_inline_keyboard(page=0, per_page=5, prefix="cur"):
    builder = InlineKeyboardBuilder()
    start = page * per_page
    end = start + per_page
    for cur in CURRENCIES[start:end]:
        builder.button(text=cur, callback_data=f"{prefix}:{cur}:{page}")
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"{prefix}:prev:{page}"))
    if end < len(CURRENCIES):
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"{prefix}:next:{page}"))
    if nav:
        builder.row(*nav)
    builder.adjust(1)
    return builder.as_markup()
