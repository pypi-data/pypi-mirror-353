import hashlib
from typing import Generic, Protocol, TypeVar

from django.utils.timezone import datetime  # type: ignore[attr-defined]
from django.db.models import QuerySet
from wagtail.models import Page


PageType = TypeVar("PageType", bound=Page)


class PageQuerySetMixin(Protocol[PageType]):
    def not_type(  # noqa: E704
        self, model_class: type[PageType]
    ) -> "PageQuerySet[PageType]": ...


class PageQuerySet(QuerySet[PageType], PageQuerySetMixin[PageType], Generic[PageType]):
    pass


def exclude_page_type(
    queryset: PageQuerySet[PageType], page_models: list[type[PageType]]
) -> PageQuerySet[PageType]:
    qs = queryset.none()
    for model in page_models:
        qs |= queryset.not_type(model)
    return qs


def hash_draft_code(code: str, page_id: int) -> str:
    """sha256 of date + code + page id"""
    date_code = datetime.today().strftime("%Y%m%d")
    combined_code = date_code + code + str(page_id)
    hashed_code = hashlib.sha256(combined_code.encode())
    return hashed_code.hexdigest()
