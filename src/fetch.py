import aiohttp
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from logger import logger


async def make_wakatime_request(
    url: str, api_key: str
) -> Optional[Dict[str, Any]]:
    async with aiohttp.ClientSession() as session:
        headers = {'Authorization': f'Basic {api_key}:'}

        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                logger.error(
                    f'❌ Ошибка при получении данных с {url}: {response.status}'
                )
                return None


async def fetch_wakatime_user(api_key: str) -> Optional[str]:
    url = 'https://wakatime.com/api/v1/users/current'
    user_data = await make_wakatime_request(url, api_key)

    if user_data:
        return user_data.get('data', {}).get('username', '')

    return None


def week_offset(start_day: int = 1) -> tuple[str, str]:
    today = datetime.now(timezone.utc)

    first_start_date = datetime(2024, 10, 18, 0, 0, 0, tzinfo=timezone.utc)
    first_end_date = datetime(2024, 10, 25, 23, 59, 59, tzinfo=timezone.utc)

    if today <= first_end_date:
        start_date = first_start_date
        end_date = first_end_date
    else:
        weeks_passed = (today - first_end_date).days // 8
        start_date = first_start_date + timedelta(weeks=weeks_passed + 1)
        end_date = start_date + timedelta(days=7)

    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    print(f'[DEBUG] Current date: {today}')
    print(f'[DEBUG] Start of week (formatted): {start_date_str}')
    print(f'[DEBUG] End of week (formatted): {end_date_str}')

    return start_date_str, end_date_str


async def fetch_wakatime_data(api_key: str) -> Optional[Dict[str, Any]]:
    start_of_week, end_of_week = week_offset(start_day=1)
    url = (
        f'https://wakatime.com/api/v1/users/current/summaries'
        f'?start={start_of_week}&end={end_of_week}'
    )

    print(f'[DEBUG] Wakatime API URL: {url}')

    return await make_wakatime_request(url, api_key)
