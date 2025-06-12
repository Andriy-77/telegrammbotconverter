from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from settings import DATABASE, CURRENCY_API_URL
from app.database import get_all_conversions, get_conversion, add_conversion
from app.keyboards import (
    BUTTON_LIST_CONVERSION,
    BUTTON_CREATE_CONVERSION,
    ConversionCallback,
    conversions_keyboard_markup,
    menu_keyboards,
    currency_inline_keyboard
)
from app.commands import CURRENCY, CONVERT_OWN
from app.fsm import ConvertForm
import aiohttp

router = Router()

@router.message(Command(CURRENCY))
@router.message(F.text == BUTTON_LIST_CONVERSION)
async def conversions_list(message: Message):
    markup = conversions_keyboard_markup(get_all_conversions(DATABASE))
    await message.answer("Усі конвертації:", reply_markup=markup)

@router.callback_query(ConversionCallback.filter())
async def conversion_callback(callback: CallbackQuery, callback_data: ConversionCallback):
    conv = get_conversion(DATABASE, callback_data.id)
    await callback.message.answer(f"{conv['amount']} {conv['from']} = {conv['result']} {conv['to']}")
    await callback.answer()

@router.message(Command(CONVERT_OWN))
@router.message(F.text == BUTTON_CREATE_CONVERSION)
async def create_conversion(message: Message, state: FSMContext):
    await state.set_state(ConvertForm.amount)
    await message.answer("Введіть суму для конвертації:", reply_markup=ReplyKeyboardRemove())

@router.message(ConvertForm.amount)
async def set_amount(message: Message, state: FSMContext):
    if message.text.replace(".", "", 1).isdigit():
        await state.update_data(amount=message.text)
        await state.set_state(ConvertForm.from_currency)
        await message.answer("Виберіть валюту, з якої конвертуємо:", reply_markup=currency_inline_keyboard(0, prefix="from"))
    else:
        await message.answer("Введіть число!")

@router.callback_query(lambda c: c.data.startswith("from:"))
async def currency_from_callback(call: CallbackQuery, state: FSMContext):
    _, value, page = call.data.split(":")
    page = int(page)
    if value == "next":
        await call.message.edit_reply_markup(reply_markup=currency_inline_keyboard(page+1, prefix="from"))
    elif value == "prev":
        await call.message.edit_reply_markup(reply_markup=currency_inline_keyboard(page-1, prefix="from"))
    else:
        await call.message.delete_reply_markup()
        await state.update_data(from_currency=value)
        await state.set_state(ConvertForm.to_currency)
        await call.message.answer("Виберіть валюту, в яку конвертуємо:", reply_markup=currency_inline_keyboard(0, prefix="to"))
    await call.answer()

@router.callback_query(lambda c: c.data.startswith("to:"))
async def currency_to_callback(call: CallbackQuery, state: FSMContext):
    _, value, page = call.data.split(":")
    page = int(page)
    if value == "next":
        await call.message.edit_reply_markup(reply_markup=currency_inline_keyboard(page+1, prefix="to"))
    elif value == "prev":
        await call.message.edit_reply_markup(reply_markup=currency_inline_keyboard(page-1, prefix="to"))
    else:
        await call.message.delete_reply_markup()
        await state.update_data(to_currency=value)
        data = await state.get_data()
        url = f"{CURRENCY_API_URL}/{data['from_currency']}/{data['to_currency']}/{data['amount']}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                result = await response.json()
        if "conversion_result" in result:
            converted = round(float(result["conversion_result"]), 2)
            add_conversion(DATABASE, {
                "amount": data["amount"],
                "from": data["from_currency"],
                "to": data["to_currency"],
                "result": converted,
            })
            await call.message.answer(
                f"{data['amount']} {data['from_currency']} = {converted} {data['to_currency']}",
                reply_markup=menu_keyboards()
            )
            await state.clear()
        else:
            await call.message.answer("Не вдалося отримати результат.")
        await call.answer()