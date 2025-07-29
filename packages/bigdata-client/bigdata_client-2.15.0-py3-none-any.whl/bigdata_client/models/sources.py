from functools import cache
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.alias_generators import to_camel

from bigdata_client.enum_utils import StrEnum
from bigdata_client.models.advanced_search_query import QueryComponent
from bigdata_client.models.advanced_search_query import Source as SourceQuery
from bigdata_client.models.search import Expression


class SourceRetentionPeriod(StrEnum):
    """Retention periods used for filtering Knowledge Graph results"""

    TWO_WEEKS = "2W"
    TWO_YEARS = "2Y"
    FIVE_YEARS = "5Y"
    FULL_HISTORY = "99Y"


class SourceRank(StrEnum):
    """Source ranks used for filtering Knowledge Graph results"""

    RANK_1 = "1"
    """Fully accountable, reputable, and balanced"""
    RANK_2 = "2"
    """Official, reliable, and honest"""
    RANK_3 = "3"
    """Acknowledged, formal, and credible"""
    RANK_4 = "4"
    """Known and reasonable credibility"""
    RANK_5 = "5"
    """Satisfactory credibility"""


class Source(BaseModel):
    """A source of news and information for RavenPack"""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)
    id: str
    name: str
    volume: Optional[int] = None
    description: Optional[str] = None
    entity_type: Literal["SRCE"] = Field(default="SRCE")
    publication_type: str
    language: Optional[str] = Field(default=None)
    country: Optional[str] = None
    source_rank: Optional[str] = Field(default=None)
    retention: Optional[SourceRetentionPeriod] = Field(default=None)
    provider_id: str
    url: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def apply_second_alias_generator(cls, values):
        """
        Applied before validating to replace some alias in the input @values so
        we can make the model in 3 ways: snake_case/camel_case/alias. This is required because not
        all endpoints are resolving the groupN into the correct field name.
        """
        values = values.copy()  # keep original input unmutated for Unions
        autosuggest_validation_alias_map = {
            "key": "id",
            "group1": "publicationType",
            "group2": "language",
            "group3": "country",
            "group4": "sourceRank",
            "group5": "retention",
            "metadata1": "providerId",
            "metadata2": "url",
        }
        for key in autosuggest_validation_alias_map:
            if key in values:
                values[autosuggest_validation_alias_map[key]] = values.pop(key)
        return values

    def replace_country_by_iso3166(self):
        if self.country is not None:
            self.country = SourceCountry.get_reverse_mapping().get(
                self.country, self.country
            )

    # QueryComponent methods

    @property
    def _query_proxy(self):
        return SourceQuery(self.id)

    def to_expression(self) -> Expression:
        return self._query_proxy.to_expression()

    def __or__(self, other: QueryComponent) -> QueryComponent:
        return self._query_proxy | other

    def __and__(self, other: QueryComponent) -> QueryComponent:
        return self._query_proxy & other

    def __invert__(self) -> QueryComponent:
        return ~self._query_proxy

    def make_copy(self) -> QueryComponent:
        return self._query_proxy.make_copy()


class SourceCountry(StrEnum):
    """Countries used for filtering Knowledge Graph results"""

    GR = "Greece"
    CA = "Canada"
    IN = "India"
    TN = "Tunisia"
    MT = "Malta"
    NZ = "New Zealand"
    ES = "Spain"
    AU = "Australia"
    NG = "Nigeria"
    IE = "Ireland"
    YE = "Yemen"
    TR = "Turkey"
    ZW = "Zimbabwe"
    AM = "Armenia"
    NO = "Norway"
    FI = "Finland"
    SE = "Sweden"
    BB = "Barbados"
    KE = "Kenya"
    KR = "South Korea"
    FJ = "Fiji"
    JP = "Japan"
    ZM = "Zambia"
    HR = "Croatia"
    RU = "Russia"
    LB = "Lebanon"
    BS = "Bahamas"
    CR = "Costa Rica"
    VN = "Vietnam"
    JM = "Jamaica"
    BR = "Brazil"
    HU = "Hungary"
    CZ = "Czechia"
    MA = "Morocco"
    JE = "Jersey"
    CO = "Colombia"
    OM = "Oman"
    UZ = "Uzbekistan"
    DZ = "Algeria"
    BW = "Botswana"
    PS = "Palestinian Territory"
    NP = "Nepal"
    LT = "Lithuania"
    VG = "British Virgin Islands"
    CU = "Cuba"
    SZ = "Eswatini"
    US = "United States"
    LU = "Luxembourg"
    BE = "Belgium"
    CH = "Switzerland"
    TH = "Thailand"
    NL = "The Netherlands"
    PL = "Poland"
    IL = "Israel"
    AT = "Austria"
    GI = "Gibraltar"
    GH = "Ghana"
    NI = "Nicaragua"
    LA = "Laos"
    IM = "Isle of Man"
    AF = "Afghanistan"
    MX = "Mexico"
    KY = "Cayman Islands"
    TZ = "Tanzania"
    MK = "North Macedonia"
    SI = "Slovenia"
    BT = "Bhutan"
    BM = "Bermuda"
    CK = "Cook Islands"
    AD = "Andorra"
    MV = "Maldives"
    SD = "Sudan"
    NA = "Namibia"
    MO = "Macau SAR"
    CL = "Chile"
    LK = "Sri Lanka"
    BY = "Belarus"
    GU = "Guam"
    CD = "Democratic Republic of the Congo"
    MN = "Mongolia"
    DO = "Dominican Republic"
    CM = "Cameroon"
    GM = "Gambia"
    LS = "Lesotho"
    TL = "East Timor"
    MC = "Monaco"
    LI = "Liechtenstein"
    NE = "Niger"
    XK = "Kosovo"  # Note: Kosovo does not have an official ISO code, using XK as a placeholder
    VI = "U.S. Virgin Islands"
    VC = "Saint Vincent and the Grenadines"
    MZ = "Mozambique"
    GB = "United Kingdom"
    HK = "Hong Kong SAR"
    AE = "United Arab Emirates"
    BG = "Bulgaria"
    ZA = "South Africa"
    PH = "Philippines"
    MY = "Malaysia"
    SO = "Somalia"
    CN = "China"
    DK = "Denmark"
    BH = "Bahrain"
    ID = "Indonesia"
    EG = "Egypt"
    GE = "Georgia"
    PT = "Portugal"
    BD = "Bangladesh"
    TT = "Trinidad and Tobago"
    IT = "Italy"
    SG = "Singapore"
    SA = "Saudi Arabia"
    PR = "Puerto Rico"
    EE = "Estonia"
    BZ = "Belize"
    UA = "Ukraine"
    AZ = "Azerbaijan"
    PK = "Pakistan"
    UY = "Uruguay"
    RS = "Serbia"
    TW = "Taiwan"
    IS = "Iceland"
    SB = "Solomon Islands"
    SY = "Syria"
    KG = "Kyrgyzstan"
    VA = "Vatican"
    IQ = "Iraq"
    PA = "Panama"
    BN = "Brunei"
    KW = "Kuwait"
    HT = "Haiti"
    TG = "Togo"
    GY = "Guyana"
    FR = "France"
    DE = "Germany"
    KN = "Saint Kitts and Nevis"
    SL = "Sierra Leone"
    CY = "Cyprus"
    MM = "Myanmar"
    QA = "Qatar"
    IR = "Iran"
    SC = "Seychelles"
    RO = "Romania"
    JO = "Jordan"
    MW = "Malawi"
    AR = "Argentina"
    FM = "Micronesia"
    UG = "Uganda"
    KH = "Cambodia"
    PG = "Papua New Guinea"
    CI = "Ivory Coast"
    RW = "Rwanda"
    SM = "San Marino"
    BA = "Bosnia and Herzegovina"
    WS = "Samoa"
    LV = "Latvia"
    LY = "Libya"
    ET = "Ethiopia"
    ML = "Mali"
    KZ = "Kazakhstan"
    MU = "Mauritius"
    SX = "Sint Maarten"
    VE = "Venezuela"
    SN = "Senegal"
    PY = "Paraguay"
    TJ = "Tajikistan"
    MD = "Moldova"
    AL = "Albania"
    LR = "Liberia"
    TO = "Tonga"
    LC = "Saint Lucia"
    MH = "Marshall Islands"

    @classmethod
    @cache
    def get_reverse_mapping(self) -> dict[str, str]:
        """Returns a reverse mapping of the enum values to their names."""
        return {member.value: member.name for member in SourceCountry}
