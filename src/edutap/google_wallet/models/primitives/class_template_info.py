from .enums import DateFormat
from .enums import PredefinedItem
from .enums import TransitOption
from pydantic import BaseModel
from typing import List


class FieldReference(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#fieldreference
    """

    fieldPath: str
    dateFormat: DateFormat | None


class FieldSelector(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#fieldselector
    """

    fields: list[FieldReference]


class TemplateItem(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#templateitem
    """

    firstValue: FieldSelector | None
    secondValue: FieldSelector | None
    predefinedItem: PredefinedItem | None


class BarcodeSectionDetail(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#barcodesectiondetail
    """

    fieldSelector: FieldSelector


class CardBarcodeSectionDetails(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#cardbarcodesectiondetails
    """

    firstTopDetail: BarcodeSectionDetail | None
    firstBottomDetail: BarcodeSectionDetail | None
    secondTopDetail: BarcodeSectionDetail | None


class CardRowOneItem(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#cardrowoneitem
    """

    item: TemplateItem | None


class CardRowTwoItems(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#cardrowtwoitems
    """

    startItem: TemplateItem | None
    endItem: TemplateItem | None


class CardRowThreeItems(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#cardrowthreeitems
    """

    startItem: TemplateItem | None
    middleItem: TemplateItem | None
    endItem: TemplateItem | None


class CardRowTemplateInfo(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#cardrowtemplateinfo
    """

    oneItem: CardRowOneItem | None
    twoItems: CardRowTwoItems | None
    threeItems: CardRowThreeItems | None


class CardTemplateOverride(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#cardtemplateoverride
    """

    cardRowTemplateInfos: List[CardRowTemplateInfo] | None


class DetailsItemInfo(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#detailsiteminfo
    """

    item: TemplateItem | None


class DetailsTemplateOverride(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#detailstemplateoverride
    """

    detailsItemInfos: List[DetailsItemInfo] | None


class FirstRowOption(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#firstrowoption
    """

    transitOption: TransitOption | None
    fieldOption: FieldSelector | None


class ListTemplateOverride(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#listtemplateoverride
    """

    firstRowOption: FirstRowOption | None
    secondRowOption: FieldSelector | None
    thirdRowOption: FieldSelector | None  # deprecated attribute


class ClassTemplateInfo(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo
    """

    cardBarcodeSectionDetails: CardBarcodeSectionDetails | None
    cardTemplateOverride: CardTemplateOverride | None
    detailsTemplateOverride: DetailsTemplateOverride | None
    listTemplateOverride: ListTemplateOverride | None
