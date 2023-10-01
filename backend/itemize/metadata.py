import httpx
import extruct
import w3lib.html
import pprint
import pathlib
import fake_useragent
import pyppeteer
import pyppeteer.browser

from itemize import schemas
from itemize import models
from itemize import errors

from itemize.db import DB
from itemize.config import CONFIG

from datetime import datetime
from functools import reduce

from sqlalchemy import select
from sqlalchemy.orm import selectinload


URL_CACHE: dict[str, schemas.DBPageMetadata] = {}

class MetadataParser:
    def __init__(self, data: str, url: str) -> None:
        self._data = data
        self._url = url
        self._metadata = extruct.extract(data, base_url=w3lib.html.get_base_url(data, str(url)), uniform=True)

        # fields
        self.title: str | None = None
        self.site_name: str | None = None
        self.description: str | None = None
        self.image_url: str | None = None
        self.price: str | None = None
        self.currency: str | None = None

    def parse(self) -> None:
        if CONFIG.PARSER_LOG_PAGEDATA:
            pathlib.Path('pagedata').mkdir(exist_ok=True)
            with open(f'pagedata/{datetime.utcnow().isoformat()}.html', 'w') as f:
                f.write(self._data)

        pprint.pprint(self._metadata)
        
        parer_get_methods = {
            'dublincore': self._dublincore_get,
            'json-ld': self._json_ld_get,
            # 'microdata': self._microdata_get,
            # 'microformat': self._microformat_get,
            'opengraph': self._opengraph_get,
            'rdfa': self._rdfa_get
        }
        format_rank = [
            'opengraph',
            'rdfa',
            'json-ld',
            'dublincore',
            'microdata',
            'microformat'
        ]
        fields = [
            'title',
            'site_name',
            'description',
            'image_url',
            'price',
            'currency'
        ]

        for format in format_rank:
            if format not in parer_get_methods:
                continue
            get = parer_get_methods[format]
            for field in fields:
                if getattr(self, field) is not None:
                    continue
                value = get(field)
                if value is not None:
                    setattr(self, field, value)
            
    def _dublincore_get(self, key: str) -> str | None:
        """
        Parse dublincore metadata.

        Schema approx:
        [
            {
                '@context': ...,
                'elements': [
                    {
                        'URI': ...,
                        'name': ...,
                        'content': ...
                    },
                    ...
                ]
            },
            ...
        ]
        """
        key_translations = {}
        if key in key_translations:
            key = key_translations[key]

        content = next(map(
            lambda x: x['content'],
            filter(
                lambda x: x['name'] == key,
                reduce(
                    lambda x, y: x + y,
                    map(
                        lambda x: x['elements'],
                        self._metadata['dublincore']
                    ),
                    []
                )
            )
        ), None)
        
        if content is None:
            return None
        return str(content)

    def _json_ld_get(self, key: str) -> str | None:
        """
        Parse json-ld metadata.

        Schema approx:
        [
            {
                '@context': ...,
                '@id': ...,
                '@type': ..., // Organization/Product/etc.
                'name': ... // not title
            }
        ]
        """
        key_translations = {
            'title': 'name',
            'image_url': 'image',
        }
        key_types = {
            'title': 'Product',
            'description': 'Product',
            'image_url': 'Product',
            'price': 'Product',
            'currency': 'Product',
            'site_name': 'Organization'
        }
        properties = next(filter(
            lambda x: x['@type'] == key_types.get(key, 'Product'),
            self._metadata['json-ld']
        ), None)
        if properties is None:
            return None
        
        if key in key_translations:
            key = key_translations[key]
        
        value = properties.get(key, None)
        if value is None:
            return None
        return str(value)

    def _microdata_get(self, key: str) -> str | None:
        """
        Parse microdata metadata.

        TODO: I do not know what the microdata is structured like.
        """
        raise NotImplementedError()

    def _microformat_get(self, key: str) -> str | None:
        """
        Parse microformat metadata.

        TODO: I do not know what the microformat is structured like.
        """
        raise NotImplementedError()

    def _opengraph_get(self, key: str) -> str | None:
        """
        Parse opengraph metadata.

        Schema approx:
        [
            {
                '@context': ...,
                'og:title': ...,
                ...
            },
            ...
        ]
        """
        key_translations = {
            'title': 'og:title',
            'site_name': 'og:site_name',
            'description': 'og:description',
            'image_url': 'og:image',
            'price': 'product:price:amount',
            'currency': 'product:price:currency'
        }
        if key in key_translations:
            key = key_translations[key]

        properties = reduce(
            lambda x, y: y | x,
            self._metadata['opengraph'],
            {}
        )

        value = properties.get(key, None)
        if value is None:
            return None
        return str(value)

    def _rdfa_get(self, key: str) -> str | None:
        """
        Parse rfda metadata.

        Schema approx:
        [
            {
                '@id': ...., // provided url for the page
                'http://ogp.me/ns#title': [
                    {
                        '@value': ...
                    }
                ],
                'http://ogp.me/ns#site_name': ...,
                ....,
                'product:price:amount': ...,
            }
        ]
        """
        key_translations = {
            'title': 'http://ogp.me/ns#title',
            'site_name': 'http://ogp.me/ns#site_name',
            'description': 'http://ogp.me/ns#description',
            'image_url': 'http://ogp.me/ns#image',
            'price': 'product:price:amount',
            'currency': 'product:price:currency'
        }
        if key in key_translations:
            key = key_translations[key]

        page_properties = next(filter(
            lambda x: x['@id'] == self._url,
            self._metadata['rdfa']
        ), None)

        if page_properties is None:
            return None
        
        value = page_properties.get(key, None)
        if value is None:
            return None

        grouped_values = reduce(
            lambda x, y: y | x,
            value,
            {}
        )
        if '@value' not in grouped_values:
            return None
        
        return str(grouped_values['@value'])


async def get_image(page_metadata_id: int) -> bytes:
    async with DB.async_session() as session:
        image = await session.scalar(select(models.MetadataImage).where(models.MetadataImage.page_metadata_id == page_metadata_id))
        if image is None:
            raise errors.ImageNotFoundError('Image not found!')
        return image.data


async def get_cached(url: str) -> schemas.DBPageMetadata | None:
    if url in URL_CACHE:
        return URL_CACHE[url]
    async with DB.async_session() as session:
        metadata = await session.scalar(
            select(models.PageMetadata)
            .where(models.PageMetadata.url == url)
            .options(selectinload(models.PageMetadata.images))
        )
        if metadata is None:
            return None
        metadata_schema = schemas.DBPageMetadata(
            id=metadata.id,
            url=metadata.url,
            image_url=metadata.image_url if metadata.image_url != '' else (
                f'{CONFIG.SERVER_URL}/metadata/images/{metadata.images[0].id}' if len(metadata.images) > 0 else ''
            ),
            title=metadata.title,
            description=metadata.description,
            site_name=metadata.site_name
        )
        URL_CACHE[url] = metadata_schema
        return metadata_schema

async def try_write_cache(metadata: schemas.PageMetadata) -> schemas.DBPageMetadata:
    async with DB.async_session() as session:
        cached = await session.scalar(select(models.PageMetadata).where(models.PageMetadata.url == metadata.url))
        if cached is not None:
            cached.image_url = metadata.image_url
            cached.title = metadata.title
            cached.description = metadata.description
            cached.site_name = metadata.site_name
        else:
            cached = models.PageMetadata(
                url=metadata.url,
                image_url=metadata.image_url,
                title=metadata.title,
                description=metadata.description,
                site_name=metadata.site_name
            )
            session.add(cached)
        await session.commit()
        await session.refresh(cached, ['images'])

        # TODO: save all images in future
        if metadata.image_url in (None, '') and len(cached.images) == 0:
            global BROWSER
            browser = await pyppeteer.launch()
            page = await browser.newPage()
            await page.goto(metadata.url)
            ss = await page.screenshot({'type': 'jpeg'})
            if isinstance(ss, str):
                ss = ss.encode('utf-8')
            session.add(models.MetadataImage(
                data=ss,
                page_metadata_id=cached.id
            ))
            await session.commit()
            await session.refresh(cached, ['images'])

        db_schema = schemas.DBPageMetadata(
            id=cached.id,
            url=cached.url,
            image_url=cached.image_url if cached.image_url != '' else (
                f'{CONFIG.SERVER_URL}/metadata/images/{cached.images[0].id}' if len(cached.images) > 0 else ''
            ),
            title=cached.title,
            description=cached.description,
            site_name=cached.site_name
        )
        URL_CACHE[metadata.url] = db_schema
        return db_schema


async def get_metadata(url: str, *, cache_only: bool = False) -> schemas.DBPageMetadata | None:
    # if (cached := await get_cached(url)) is not None:
    #     return cached
    # if cache_only:
    #     return None

    async with httpx.AsyncClient() as client:
        user_agent_header = fake_useragent.UserAgent().random
        response = await client.get(url, headers={'User-Agent': user_agent_header})
        print(len(response.text))

    parser = MetadataParser(response.text, str(response.url))
    parser.parse()

    print(f'{parser.title=} {parser.site_name=} {parser.description=} {parser.image_url=} {parser.price=} {parser.currency=}')
    return await try_write_cache(schemas.PageMetadata(
        url=url,
        image_url=parser.image_url or '',
        title=parser.title or '',
        description=parser.description or '',
        site_name=parser.site_name or '',
    ))