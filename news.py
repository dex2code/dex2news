from pydantic import BaseModel, ConfigDict, Field, AnyHttpUrl
from typing import List, Optional
from tools import in_out_debug, get_dates
from app_config import app_config
from loguru import logger
import httpx


class SourceModel(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra='ignore'
    )

    id: str = Field(default="")
    name: str = Field(default="")
    url: str = Field(default="")
    country: str = Field(default="")


class ArticlesModel(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra='ignore'
    )

    id: str = Field(default="")
    title: str = Field()
    description: str = Field()
    content: str = Field(default="")
    url: AnyHttpUrl = Field()
    image: AnyHttpUrl = Field()
    publishedAt: str = Field()
    lang: str = Field(default="")
    source: SourceModel = Field(default_factory=SourceModel)


class NewsModel(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra='ignore'
    )

    totalArticles: int = Field(default=0)
    articles: List[ArticlesModel] = Field(default_factory=List)


@in_out_debug
async def get_news_by_category(category: str = "general") -> Optional[NewsModel]:
    news_dates = get_dates()

    request_params = {
        'lang': app_config.news_lang,
        'category': category,
        'max': app_config.news_max_articles,
        'from': news_dates.get("from"),
        'to': news_dates.get("to"),
        'apikey': app_config.news_api_token.get_secret_value()
    }
    log_params = request_params.copy()
    log_params['apikey'] = app_config.news_api_token
    logger.info(f"Sending request to {app_config.news_api_endpoint} with {log_params=}")

    try:
        async with httpx.AsyncClient() as httpx_client:
            r = await httpx_client.get(
                url=app_config.news_api_endpoint,
                params=request_params,
                follow_redirects=True,
                timeout=app_config.news_api_timeout_sec
            )
            if not r.is_success:
                raise httpx.RequestError(message=f"HTTP {r.status_code}")
    except (httpx.TimeoutException, httpx.ConnectError, httpx.ConnectTimeout, httpx.RequestError) as e:
        logger.error(f"HTTP request error: {e}")
        return None
    except BaseException as e:
        logger.error(f"Unexpected HTTP request error: {e}")
        return None
    else:
        logger.info(f"Successfully requested API with HTTP {r.status_code}")
    
    try:
        r_json: dict = r.json()
        result_news = NewsModel(**r_json)
    except BaseException as e:
        logger.error(f"Cannot process news: {e}")
        return None
    else:
        logger.info(f"Successfully processed {len(result_news.articles)} article(s)")

    return result_news
