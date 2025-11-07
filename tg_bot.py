from aiogram import Bot
from aiogram.enums import ParseMode
from app_config import app_config
from wrappers import in_out_debug
from news import ArticlesModel
from loguru import logger


tg_bot = Bot(
    token=app_config.tg_bot_token.get_secret_value()
)

caption = """
📰 <b>{article_source_name}: {article_title}</b>

<i>{article_description}</i>

🔗 <a href="{article_url}">Читать подробнее</a>
""".strip()


@in_out_debug
async def tg_send_news(article: ArticlesModel) -> bool:
    try:
        await tg_bot.send_photo(
            chat_id=app_config.tg_chat_id.get_secret_value(),
            photo=article.image.unicode_string(),
            caption=caption.format(
                article_source_name=article.source.name,
                article_title=article.title,
                article_description=article.description,
                article_url=article.url
            ),
            parse_mode=ParseMode.HTML
        )
    except BaseException as e:
        logger.error(f"Cannot send TG message: {e}")
        return False

    return True


@in_out_debug
async def tg_bot_shutdown() -> None:
    await tg_bot.session.close()


if __name__ == "__main__":
    pass
