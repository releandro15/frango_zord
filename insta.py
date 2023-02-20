from telegram import Bot
from asyncio import run

async def main():
    # your code

    bot = Bot(token='5620155598:AAECYDQbpOLE9rcgVFUZ3ZoUkcNjnYSXQ_w')

    chat_id = -1001845830961

    photo_path = "C:/Users/ran_l/Downloads/background.png"

    media_1 = InputMediaDocument(media=open(photo_path, 'rb'))

    await bot.send_media_group(chat_id=chat_id, media=[media_1])

if __name__ == "__main__":
    run(main())
