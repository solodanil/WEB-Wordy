# Example of sending and receiving an event after pressing the Callback button
# Documentation: https://vk.cc/aC9JG2

import logging
import os

from vkbottle import Callback, GroupEventType, GroupTypes, Keyboard
from vkbottle.bot import Bot, Message
from vkbottle.modules import json
from config import TOKEN

from requests import get

bot = Bot(TOKEN)
logging.basicConfig(level=logging.INFO)

#KEYBOARD = (
#    Keyboard(one_time=False)
#    .add(Callback("Callback-кнопка", payload={"cmd": "callback"}))
#    .get_json()
#)


#@bot.on.private_message(text="/callback")
#async def send_callback_button(message: Message):
#    await message.answer("Лови!", keyboard=KEYBOARD)


@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=GroupTypes.MessageEvent)
async def handle_message_event(event: GroupTypes.MessageEvent):
    # event_data parameter accepts three object types
    # "show_snackbar" type

    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
        event_data=json.dumps({"type": "show_snackbar", "text": "Сейчас я исчезну"}),
    )

@bot.on.private_message(text="/start")
async def send_message(message: Message):
    if 'user' not in get(f'http://127.0.0.1:8080/api/v1/user/{message.peer_id}').json():
        await message.answer('''Привет!
Кажется, ты не зарегистрирован на сайте под этим аккаунтом
Ссылка на сайт: http://127.0.0.1:8080''', keyboard=KEYBOARD)

bot.run_forever()