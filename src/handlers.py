from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from db import User, get_async_session
from scheduler import send_weekly_report

router = Router()
user_api_key_requests: dict[int, bool] = {}


async def get_user_from_db(user_id: int, session: AsyncSession) -> User:
    result = await session.execute(select(User).where(User.user_id == user_id))
    return result.scalars().first()


async def store_api_key(
    user_id: int, api_key: str, session: AsyncSession
) -> None:
    user = await session.get(User, user_id)
    if user:
        user.wakatime_api_key = api_key
    else:
        user = User(user_id=user_id, wakatime_api_key=api_key)
        session.add(user)
    await session.commit()


@router.message(Command('wakatime'))
async def help_command(message: Message) -> None:
    help_text = (
        'ℹ️ Доступные команды:\n'
        '/get - Получить свой отчёт за последние 7 дней.\n'
        '/api - Установить ваш WakaTime API ключ (вызывается в личных сообщениях).'
    )
    await message.reply(help_text, reply_to_message_id=message.message_id)


@router.message(Command('report'))
async def report_command(message: Message) -> None:
    user_id = message.from_user.id
    chat_id = message.chat.id

    async for session in get_async_session():
        user = await get_user_from_db(user_id, session)
        if user and user.wakatime_api_key:
            await send_weekly_report(
                user_id, chat_id, message.bot, message.message_id
            )
        else:
            await message.reply(
                'ℹ️ У вас нет сохраненного API ключа.\nИспользуйте команду /api.',
                reply_to_message_id=message.message_id,
            )


@router.message(Command('api'))
async def api_key_command(message: Message) -> None:
    if message.chat.type != 'private':
        await message.reply(
            'ℹ️ Используйте команду /api в личных сообщениях.',
            reply_to_message_id=message.message_id,
        )
        return
    await message.reply(
        'ℹ️ Введите ваш WakaTime API ключ:',
        reply_to_message_id=message.message_id,
    )
    user_api_key_requests[message.from_user.id] = True


@router.message()
async def handle_api_key_input(message: Message) -> None:
    user_id = message.from_user.id

    if message.chat.type == 'private' and user_id in user_api_key_requests:
        api_key = message.text.strip()
        async for session in get_async_session():
            await store_api_key(user_id, api_key, session)

        await message.reply(
            '✅ API ключ обновлен!', reply_to_message_id=message.message_id
        )
        del user_api_key_requests[user_id]


def get_router() -> Router:
    return router
