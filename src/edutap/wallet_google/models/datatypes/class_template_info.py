from .enums import DateFormat
from .enums import PredefinedItem
from .enums import TransitOption
from pydantic import BaseModel
from pydantic import Field


class FieldReference(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#fieldreference
    """

    fieldPath: str
    dateFormat: DateFormat | None = None


class FieldSelector(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#fieldselector
    """

    fields: list[FieldReference]


class TemplateItem(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#templateitem
    """

    firstValue: FieldSelector | None = None
    secondValue: FieldSelector | None = None
    predefinedItem: PredefinedItem | None = None


class BarcodeSectionDetail(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#barcodesectiondetail
    """

    fieldSelector: FieldSelector


class CardBarcodeSectionDetails(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#cardbarcodesectiondetails
    """

    firstTopDetail: BarcodeSectionDetail | None = None
    firstBottomDetail: BarcodeSectionDetail | None = None
    secondTopDetail: BarcodeSectionDetail | None = None


class CardRowOneItem(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#cardrowoneitem
    """

    item: TemplateItem | None = None


class CardRowTwoItems(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#cardrowtwoitems
    """

    startItem: TemplateItem | None = None
    endItem: TemplateItem | None = None


class CardRowThreeItems(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#cardrowthreeitems
    """

    startItem: TemplateItem | None = None
    middleItem: TemplateItem | None = None
    endItem: TemplateItem | None = None


class CardRowTemplateInfo(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#cardrowtemplateinfo
    """

    oneItem: CardRowOneItem | None = None
    twoItems: CardRowTwoItems | None = None
    threeItems: CardRowThreeItems | None = None


class CardTemplateOverride(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#cardtemplateoverride
    """

    cardRowTemplateInfos: list[CardRowTemplateInfo] | None = None


class DetailsItemInfo(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#detailsiteminfo
    """

    item: TemplateItem | None = None


class DetailsTemplateOverride(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#detailstemplateoverride
    """

    detailsItemInfos: list[DetailsItemInfo] | None = None


class FirstRowOption(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#firstrowoption
    """

    transitOption: TransitOption | None = None
    fieldOption: FieldSelector | None = None


class ListTemplateOverride(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo#listtemplateoverride
    """

    firstRowOption: FirstRowOption | None = None
    secondRowOption: FieldSelector | None = None
    thirdRowOption: FieldSelector | None = Field(
        description="deprecated", exclude=True, default=None
    )


class ClassTemplateInfo(BaseModel):
    """
    see: https://developers.google.com/wallet/generic/rest/v1/ClassTemplateInfo
    """

    cardBarcodeSectionDetails: CardBarcodeSectionDetails | None = None
    cardTemplateOverride: CardTemplateOverride | None = None
    detailsTemplateOverride: DetailsTemplateOverride | None = None
    listTemplateOverride: ListTemplateOverride | None = None


# classTemplateInfo/listTemplateOverride/listTemplateOverride/firstRowOption/fieldOption/fields[]/[fieldPath|dateFormat]
