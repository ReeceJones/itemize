import logging
import httpx
import extruct
import w3lib.html
import json
import pathlib
import fake_useragent
import pyppeteer
import pyppeteer.browser

from itemize import schemas
from itemize import models
from itemize import errors

from itemize.config import CONFIG

from datetime import datetime
from functools import reduce

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Any


class MetadataParser:
    def __init__(self, data: str, url: str) -> None:
        self._data = data
        self._url = url


        if CONFIG.PARSER_LOG_PAGEDATA:
            pathlib.Path('pagedata').mkdir(exist_ok=True)
            with open(f'pagedata/{datetime.utcnow().isoformat()}.html', 'w') as f:
                f.write(self._data)

        self._metadata = extruct.extract(data, base_url=w3lib.html.get_base_url(data, str(url)), uniform=True, errors='log')

        # fields
        self.title: str | None = None
        self.site_name: str | None = None
        self.description: str | None = None
        self.image_url: str | None = None
        self.price: str | None = None
        self.currency: str | None = None

    def parse(self) -> None:

        logging.info(json.dumps(self._metadata))
        
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
        if 'dublincore' not in self._metadata:
            return None

        key_translations: dict[str, str] = {}
        if key in key_translations:
            key = key_translations[key]

        elements = map(
            lambda x: x['elements'],
            self._metadata['dublincore']
        )

        combined_elements: list[dict[str, Any]] = reduce(
            lambda x, y: x + y,
            elements,
            []
        )

        filtered_elements = filter(
            lambda x: x['name'] == key,
            combined_elements
        )

        content = next(map(
            lambda x: x['content'],
            filtered_elements
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
        if 'json-ld' not in self._metadata:
            return None

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
        if 'opengraph' not in self._metadata:
            return None

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

        properties: dict[str, Any] = reduce(
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
        if 'rdfa' not in self._metadata:
            return None

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

        grouped_values: dict[str, Any] = reduce(
            lambda x, y: y | x,
            value,
            {}
        )
        if '@value' not in grouped_values:
            return None
        
        return str(grouped_values['@value'])


async def get_metadata_image(session: AsyncSession, metadata_image_id: int) -> schemas.MetadataImage:
    logging.info('hello world')
    image = await session.scalar(select(models.MetadataImage).where(models.MetadataImage.id == metadata_image_id))
    if image is None:
        raise errors.ImageNotFoundError('Image not found!')
    return await image.to_schema()


async def get_metadata_from_db(session: AsyncSession, url: str) -> schemas.PageMetadata | None:
    metadata = await session.scalar(
        select(models.PageMetadata)
        .where(models.PageMetadata.url == url)
        .options(selectinload(models.PageMetadata.image))
    )
    if metadata is None:
        return None
    return await metadata.to_schema()

async def save_metadata(
        session: AsyncSession,
        *,
        url: str,
        title: str | None,
        description: str | None,
        site_name: str | None,
        image_url: str | None,
        price: str | None,
        currency: str | None,
) -> schemas.PageMetadata:
    metadata = await session.scalar(select(models.PageMetadata).where(models.PageMetadata.url == url))
    if metadata is not None:
        metadata.title = title
        metadata.description = description
        metadata.site_name = site_name
        metadata.image_url = image_url
        metadata.price = price
        metadata.currency = currency
    else:
        metadata = models.PageMetadata(
            url=url,
            title=title,
            description=description,
            site_name=site_name,
            image_url=image_url,
            price=price,
            currency=currency
        )
        session.add(metadata)
    await session.commit()
    await session.refresh(metadata)

    # May be useful in the future: https://stackoverflow.com/questions/59270710/python-pyppeteer-proxy-usage
    if metadata.image_url in (None, ''):
        if CONFIG.SCREENSHOT_PAGE:
            browser = await pyppeteer.launch()
            try:
                page = await browser.newPage()
                await page.goto(metadata.url)
                ss = await page.screenshot({'type': 'jpeg'})
            finally:
                await browser.close()
            if isinstance(ss, str):
                ss = ss.encode('utf-8')
            image = models.MetadataImage(
                mime='image/jpeg',
                data=ss,
                source_image_url=metadata.url
            )
            session.add(image)
            await session.commit()
            await session.refresh(image)
            metadata.image_id = image.id
            await session.commit()
            await session.refresh(metadata, ['image'])
    elif metadata.image_url is not None:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            user_agent_header = fake_useragent.UserAgent().random
            response = await client.get(metadata.image_url, headers={'User-Agent': user_agent_header})
            logging.debug(f'Got response for downloading image: {response.status_code=} {response.headers=} {response.content=}')
            if response.status_code == 200:
                image = models.MetadataImage(
                    mime=response.headers.get('Content-Type', None),
                    data=response.content,
                    source_image_url=metadata.image_url
                )
                session.add(image)
                await session.commit()
                await session.refresh(image)
                metadata.image_id = image.id
                await session.commit()
                await session.refresh(metadata, ['image'])

    db_schema = await metadata.to_schema()
    return db_schema


async def get_metadata(session: AsyncSession, url: str, *, cache_only: bool = False) -> schemas.PageMetadata | None:
    if (metadata := await get_metadata_from_db(session, url)) is not None:
        return metadata
    if cache_only:
        return None

    async with httpx.AsyncClient() as client:
        user_agent_header = fake_useragent.UserAgent().random
        response = await client.get(url, headers={'User-Agent': user_agent_header})

    parser = MetadataParser(response.text, str(response.url))
    parser.parse()

    logging.info(f'{parser.title=} {parser.site_name=} {parser.description=} {parser.image_url=} {parser.price=} {parser.currency=}')
    return await save_metadata(
        session,
        url=url,
        title=parser.title,
        description=parser.description,
        site_name=parser.site_name,
        image_url=parser.image_url,
        price=parser.price,
        currency=parser.currency
    )