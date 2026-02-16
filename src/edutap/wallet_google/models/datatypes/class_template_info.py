from ..bases import Model
from .enums import DateFormat
from .enums import PredefinedItem
from .enums import TransitOption
from pydantic import Field
from typing import Annotated
from typing_extensions import deprecated


# Attribute order as in Google's documentation to make future updates easier!
# last check: 2025-01-22


class FieldReference(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#fieldreference
    """

    fieldPath: str
    dateFormat: DateFormat | None = None


class FieldSelector(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#fieldselector
    """

    fields: list[FieldReference]


class TemplateItem(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#templateitem
    """

    firstValue: FieldSelector | None = None
    secondValue: FieldSelector | None = None
    predefinedItem: PredefinedItem | None = None


class BarcodeSectionDetail(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#barcodesectiondetail
    """

    fieldSelector: FieldSelector


class CardBarcodeSectionDetails(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#cardbarcodesectiondetails
    """

    firstTopDetail: BarcodeSectionDetail | None = None
    firstBottomDetail: BarcodeSectionDetail | None = None
    secondTopDetail: BarcodeSectionDetail | None = None


class CardRowOneItem(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#cardrowoneitem
    """

    item: TemplateItem | None = None


class CardRowTwoItems(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#cardrowtwoitems
    """

    startItem: TemplateItem | None = None
    endItem: TemplateItem | None = None


class CardRowThreeItems(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#cardrowthreeitems
    """

    startItem: TemplateItem | None = None
    middleItem: TemplateItem | None = None
    endItem: TemplateItem | None = None


class CardRowTemplateInfo(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#cardrowtemplateinfo
    """

    oneItem: CardRowOneItem | None = None
    twoItems: CardRowTwoItems | None = None
    threeItems: CardRowThreeItems | None = None


class CardTemplateOverride(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#cardtemplateoverride
    """

    cardRowTemplateInfos: list[CardRowTemplateInfo] | None = None


class DetailsItemInfo(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#detailsiteminfo
    """

    item: TemplateItem | None = None


class DetailsTemplateOverride(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#detailstemplateoverride
    """

    detailsItemInfos: list[DetailsItemInfo] | None = None


class FirstRowOption(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#firstrowoption
    """

    transitOption: TransitOption | None = None
    fieldOption: FieldSelector | None = None


class ListTemplateOverride(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#listtemplateoverride
    """

    firstRowOption: FirstRowOption | None = None
    secondRowOption: FieldSelector | None = None
    thirdRowOption: Annotated[
        FieldSelector | None,
        Field(
            deprecated=deprecated(
                'The Attribute "thirdRowOption" is deprecated on "ListTemplateOverride". Setting it will have no effect on what the user sees.'
            ),
            default=None,
            exclude=True,
        ),
    ]


class ClassTemplateInfo(Model):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo
    """

    cardBarcodeSectionDetails: CardBarcodeSectionDetails | None = None
    cardTemplateOverride: CardTemplateOverride | None = None
    detailsTemplateOverride: DetailsTemplateOverride | None = None
    listTemplateOverride: ListTemplateOverride | None = None


# classTemplateInfo/listTemplateOverride/listTemplateOverride/firstRowOption/fieldOption/fields[]/[fieldPath|dateFormat]
