# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["BrandRetrieveParams"]


class BrandRetrieveParams(TypedDict, total=False):
    domain: Required[str]
    """Domain name to retrieve brand data for"""

    force_language: Literal[
        "albanian",
        "arabic",
        "azeri",
        "bengali",
        "bulgarian",
        "cebuano",
        "croatian",
        "czech",
        "danish",
        "dutch",
        "english",
        "estonian",
        "farsi",
        "finnish",
        "french",
        "german",
        "hausa",
        "hawaiian",
        "hindi",
        "hungarian",
        "icelandic",
        "indonesian",
        "italian",
        "kazakh",
        "kyrgyz",
        "latin",
        "latvian",
        "lithuanian",
        "macedonian",
        "mongolian",
        "nepali",
        "norwegian",
        "pashto",
        "pidgin",
        "polish",
        "portuguese",
        "romanian",
        "russian",
        "serbian",
        "slovak",
        "slovene",
        "somali",
        "spanish",
        "swahili",
        "swedish",
        "tagalog",
        "turkish",
        "ukrainian",
        "urdu",
        "uzbek",
        "vietnamese",
        "welsh",
    ]
    """Optional parameter to force the language of the retrieved brand data"""
