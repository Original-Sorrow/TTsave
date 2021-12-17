import os, re, configparser, requests
import urllib
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.utils.helper import Helper, HelperMode, ListItem
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton,ContentType
from tiktok import getCookie, getDownloadUrl, getDownloadID, getStatus 
from db.date import new_user,stata,to_all
import urllib.request

ADMINS=['ID']
TOKEN = 'ТОКЕН' 

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class State_t(StatesGroup):
    send_all=State()

def download_video(video_url, name):
    r = requests.get(video_url, allow_redirects=True)
    content_type = r.headers.get('content-type')
    if content_type == 'video/mp4':
        open(f'./videos/video{name}.mp4', 'wb').write(r.content)
    else:
        pass
 
if not os.path.exists('videos'):
    os.makedirs('videos')


@dp.message_handler(content_types=ContentType.all(),state=State_t.send_all)
async def sending_all(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['all'] = message.text
    if data['all'] == 'Отмена':
        await message.answer('<em>Отмена..</em>',parse_mode='html')
        await state.finish()
    else:
        await state.finish()
        nus = await to_all(message,InlineKeyboardMarkup().add(InlineKeyboardButton('❌ Закрыть',callback_data='mes_del')))
        await bot.send_message(message.chat.id,f'<b>Отправлено {nus} пользователям</b>',parse_mode='html')
        
@dp.callback_query_handler(lambda c: c.data == 'mes_del')
async def delete(call):
    await call.message.delete()

@dp.message_handler(commands=['rsl'])
async def do_send(message):
    if message.from_user.id in ADMINS:
        await message.answer('<b>Введи сообщение которое я всем отправлю\n\nДля отмены написать <code>Отмена</code></b>',parse_mode='html')
        await State_t.send_all.set()

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    new_user(message.from_user.id)
    user = await bot.get_chat_member(IDканала,message.from_user.id)
    if user['status']=='left':
        await message.answer('<b>⚠️Для работы с ботом нужно подписаться на канал @вашканал\n\n🔒После подписки отправьте /start</b>',parse_mode='html')
    else:
        await bot.send_message(chat_id=message.chat.id, text=' Привет, я помогу тебе скачать видео с TikTok, пришли мне ссылку на видео:') 
 

 
 
@dp.message_handler(commands=['users'])
async def stat(message: types.Message):
    num = stata()
    await message.answer(f'<b>Пользователей в боте: <code>{num}</code></b>',parse_mode='html')

@dp.message_handler(content_types=['text'])
async def text(message: types.Message):
    if message.text.startswith('https://www.tiktok.com'):
        video_url = message.text
        cookie = getCookie()
        status = getStatus(video_url,cookie)
        if status == False:
            await bot.send_message(chat_id=message.chat.id, text='Неверная ссылка, видео было удалено или я его не нашел.')
        else:
            await bot.send_message(chat_id=message.chat.id, text='Скачиваю видео')
            url = getDownloadUrl(video_url, cookie)
            video_id = getDownloadID(video_url, cookie)
            download_video(url, video_id)
            path = f'./videos/video{video_id}.mp4'
            with open(f'./videos/video{video_id}.mp4', 'rb') as file:
                await bot.send_video(
                    chat_id=message.chat.id,
                    video=file,
                    caption='Держи ролик'
                    )
            os.remove(path)
    elif message.text.startswith('https://vm.tiktok.com'):
        video_url = message.text
        req = urllib.request.Request(
            video_url,
            data=None,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
            } 
                    )
        url_v = urllib.request.urlopen(req).geturl()
        if url_v == 'https://www.tiktok.com/':
            await bot.send_message(chat_id=message.chat.id, text='Неверная ссылка, видео было удалено или я его не нашел.')
        else:
            cookie = getCookie()
            await bot.send_message(chat_id=message.chat.id, text='Скачиваю...')
            url = getDownloadUrl(url_v, cookie)
            video_id = getDownloadID(url_v, cookie)
            download_video(url, video_id)
            path = f'./videos/video{video_id}.mp4'
            with open(f'./videos/video{video_id}.mp4', 'rb') as file:
                await bot.send_video(
                    chat_id=message.chat.id,
                    video=file,
                    caption='Держи ролик'
                    ) 
            os.remove(path)
    else:
        await bot.send_message(chat_id=message.chat.id, text='Я тебя не понял, отправь мне ссылку на видео TikTok.')

if __name__ == "__main__":
    
    executor.start_polling(dp, skip_updates=True)
