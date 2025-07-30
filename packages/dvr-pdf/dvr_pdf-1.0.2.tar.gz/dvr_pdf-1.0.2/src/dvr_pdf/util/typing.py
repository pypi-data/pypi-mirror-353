from io import BufferedReader
from typing import BinaryIO, Any

from pydantic import BaseModel, Field

from dvr_pdf.util.enums import PaginationPosition, ElementType, PageBehavior, ElementAlignment, Font, AlignSetting
from dvr_pdf.util.util import px_to_pt


class PDFElement(BaseModel):
    x: int
    y: int
    width: int
    height: int
    element_type: ElementType = Field(alias='elementType')
    page_behaviour: PageBehavior = Field(alias='pageBehavior')
    alignment: ElementAlignment | None = None

    @property
    def x_pt(self):
        return px_to_pt(self.x)

    @property
    def y_pt(self):
        return px_to_pt(self.y)

    @property
    def width_pt(self):
        return px_to_pt(self.width)

    @property
    def height_pt(self):
        return px_to_pt(self.height)


class PDFTextElement(PDFElement):
    text: str
    font_size: int | None = Field(alias='fontSize', default=None)
    font: Font | None = None
    color: str | None = None


class PDFImageElement(PDFElement):
    model_config = {
        'arbitrary_types_allowed': True
    }
    image: BinaryIO | BufferedReader | str


class PDFBackgroundElement(PDFElement):
    color: str


class ConfigurableTableElement(BaseModel):
    bold: bool | None = False
    italic: bool | None = False
    background_color: str | None = Field(alias='backgroundColor', default=None)
    color: str | None = None
    border_bottom_color: str | None = Field(alias='borderBottomColor', default=None)
    border_top_color: str | None = Field(alias='borderTopColor', default=None)


class PDFCellElement(ConfigurableTableElement):
    text: str | float | int
    text_alignment: AlignSetting | None = Field(alias='textAlignment', default=None)


class PDFRowElement(ConfigurableTableElement):
    columns: list[PDFCellElement]
    key: str


class PDFTableElement(PDFElement):
    rows: list[PDFRowElement]
    column_widths: list[int] = Field(alias='columnWidths')
    font: Font | None = None
    font_size: int | None = Field(alias='fontSize', default=None)
    background_color: str | None = Field(alias='backgroundColor', default=None)
    color: str | None = None
    border_color: str | None = Field(alias='borderColor', default=None)


class Pagination(BaseModel):
    position: PaginationPosition
    render_total_pages: bool = Field(alias='renderTotalPages')


class PDFTemplate(BaseModel):
    font: Font
    font_size: int = Field(alias='fontSize')
    pagination: Pagination
    elements: list[dict]
    background_color: str | None = Field(alias='backgroundColor', default=None)


type TableStyleProp = tuple[str, tuple[int, int], tuple[int, int], Any] | tuple[
    str, tuple[int, int], tuple[int, int], int, Any]
