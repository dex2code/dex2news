from loguru import logger
import asyncio
from signal import SIGINT, SIGTERM

from app_config import app_config
from globals import shutdown_event, sleep_event, sigint_handler, sigterm_handler
from tg_bot import tg_bot_shutdown, tg_send_news
from wrappers import in_out_debug
from news import get_news_by_category


@in_out_debug
async def main() -> None:
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(SIGINT, sigint_handler)
    loop.add_signal_handler(SIGTERM, sigterm_handler)

    logger.info(f"Entering main loop with {app_config.news_period_hours*60*60:,} seconds timeout...")
    while not shutdown_event.is_set():
        logger.info(f"Main loop executing")
        news_ids = []

        for news_category in app_config.news_categories:
            logger.info(f"Processing {news_category=}...")

            news = await get_news_by_category(category=news_category)

            if news is not None:
                for news_article in news.articles:
                    if news_article.id in news_ids:
                        logger.info(f"Article with {news_article.id=} is a clone. Skipping...")
                    else:
                        logger.info(f"A new article with {news_article.id=} found")
                        news_ids.append(news_article.id)
                        await asyncio.sleep(delay=2.1)
                        if not await tg_send_news(article=news_article):
                            logger.error(f"Cannot send Article with {news_article.id=} to TG chat")
                        else:
                            logger.info(f"Successfully sent article with {news_article.id=} to TG chat")

        try:
            logger.info(f"Main loop is going to sleep for {app_config.news_period_hours*60*60:,} seconds...")
            await asyncio.wait_for(
                fut=sleep_event.wait(),
                timeout=app_config.news_period_hours*60*60
            )
        except asyncio.TimeoutError:
            pass

    logger.info(f"Exiting main loop...")

    await tg_bot_shutdown()

    return None


if __name__ == "__main__":
    logger.add(
        app_config.log_path,
        level=app_config.log_level,
        enqueue=app_config.log_enqueue,
        rotation=app_config.log_rotation,
        retention=app_config.log_retention
    )
    logger.info(f" >>> Starting service...")

    asyncio.run(main=main())

    logger.warning(f" <<< Quitting service")
