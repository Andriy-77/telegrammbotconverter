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
)
from app.commands import CURRENCY, CONVERT_OWN
from app.fsm import ConvertForm
import aiohttp

router = Router()

@router.message(Command(CURRENCY))
@router.message(F.text == BUTTON_LIST_CONVERSION)
async def conversions_list(message: Message):
    conversions = get_all_conversions(DATABASE)
    markup = conversions_keyboard_markup(conversions)
    await message.answer("Усі конвертації:", reply_markup=markup)

@router.callback_query(ConversionCallback.filter())
async def conversion_callback(callback: CallbackQuery, callback_data: ConversionCallback):
    conversion_id = callback_data.id
    conversion = get_conversion(DATABASE, conversion_id)
    text = f"{conversion['amount']} {conversion['from']} = {conversion['result']} {conversion['to']}"
    await callback.message.answer(text)
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
        await message.answer("Введіть валюту з якої конвертуємо (наприклад USD):")
    else:
        await message.answer("Введіть число!")

@router.message(ConvertForm.from_currency)
async def set_from_currency(message: Message, state: FSMContext):
    await state.update_data(from_currency=message.text.upper())
    await state.set_state(ConvertForm.to_currency)
    await message.answer("Введіть валюту в яку конвертуємо (наприклад EUR):")

@router.message(ConvertForm.to_currency)
async def set_to_currency(message: Message, state: FSMContext):
    await state.update_data(to_currency=message.text.upper())
    data = await state.get_data()
    url = f"{CURRENCY_API_URL}/{data['from_currency']}/{data['to_currency']}/{data['amount']}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            result = await response.json()

    if "conversion_result" in result:
        converted = round(float(result["conversion_result"]), 2)
        conversion_data = {
            "amount": data["amount"],
            "from": data["from_currency"],
            "to": data["to_currency"],
            "result": converted,
        }
        add_conversion(DATABASE, conversion_data)
        await message.answer(
            f"{data['amount']} {data['from_currency']} = {converted} {data['to_currency']}",
            reply_markup=menu_keyboards()
        )
        await state.clear()
    else:
        await message.answer("Не вдалося отримати результат.")
