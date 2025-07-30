from __future__ import annotations

__all__ = [
    "FontFace",
    "FontFaceSize",
    "layout_text",
    "PrimaryAxisTextAlign",
    "RichText",
    "RenderedGlyph",
    "RenderedGlyphFormat",
    "SecondaryAxisTextAlign",
    "TextLayout",
    "TextLine",
    "TextGlyph",
]


from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from enum import StrEnum
from typing import BinaryIO
from typing import Callable
from typing import Generator
from typing import Generic
from typing import NamedTuple
from typing import Sequence
from typing import TypeVar

from egeometry import FBoundingBox2d
from emath import FVector2
from emath import UVector2
from freetype import FT_ENCODING_UNICODE  # type: ignore
from freetype import FT_RENDER_MODE_LCD  # type: ignore
from freetype import FT_RENDER_MODE_LCD_V  # type: ignore
from freetype import FT_RENDER_MODE_LIGHT  # type: ignore
from freetype import FT_RENDER_MODE_SDF  # type: ignore
from freetype import Face as FtFace  # type: ignore
from freetype import FT_Exception  # type: ignore
from uharfbuzz import Buffer as HbBuffer  # type: ignore
from uharfbuzz import Face as HbFace  # type: ignore
from uharfbuzz import Font as HbFont  # type: ignore
from uharfbuzz import shape as hb_shape  # type: ignore

from ._break_text import BreakText
from ._break_text import BreakTextChunk
from ._break_text import break_text_never
from ._unicode import character_is_normally_rendered

_T = TypeVar("_T")


class RenderedGlyphFormat(Enum):
    ALPHA = FT_RENDER_MODE_LIGHT
    SDF = FT_RENDER_MODE_SDF
    LCD = FT_RENDER_MODE_LCD
    LCD_V = FT_RENDER_MODE_LCD_V


@dataclass(slots=True, frozen=True)
class RichText(Generic[_T]):
    text: str
    size: FontFaceSize
    user_data: _T


class RichTextRange(NamedTuple):
    i: int
    start: int
    end: int


class FontFace:
    def __init__(self, file: BinaryIO):
        self._ft_face = FtFace(file)
        file.seek(0)
        self._hb_face = HbFace(file.read())
        self._hb_font = HbFont(self._hb_face)

        self._name = repr(file)
        if self._ft_face.family_name:
            self._name = self._ft_face.family_name.decode("ascii")
        if self._ft_face.postscript_name:
            self._name = self._ft_face.postscript_name.decode("ascii")

        self._ft_face.select_charmap(FT_ENCODING_UNICODE)

    def __repr__(self) -> str:
        return f"<FontFace {self._name!r}>"

    def get_glyph_index(self, character: str) -> int:
        if len(character) != 1:
            raise ValueError("only a single character may be entered")

        index = self._ft_face.get_char_index(character)
        assert isinstance(index, int)
        return index

    def request_point_size(
        self,
        *,
        width: float | None = None,
        height: float | None = None,
        dpi: UVector2 = UVector2(72, 72),
    ) -> FontFaceSize:
        if width is None and height is None:
            raise TypeError("width or height must be specified")
        return _PointFontFaceSize(
            self, 0 if width is None else (width * 64), 0 if height is None else (height * 64), dpi
        )

    def request_pixel_size(
        self, *, width: int | None = None, height: int | None = None
    ) -> FontFaceSize:
        if width is None and height is None:
            raise TypeError("width or height must be specified")
        return _PixelFontFaceSize(
            self, 0 if width is None else width, 0 if height is None else height
        )

    def _get_glyph_size(self, character: int, size: FontFaceSize) -> FVector2:
        size._use()
        self._ft_face.load_glyph(character, 0)
        ft_glyph = self._ft_face.glyph
        return FVector2(ft_glyph.metrics.width / 64.0, ft_glyph.metrics.height / 64.0)

    def render_glyph(
        self,
        character: str | int,
        size: FontFaceSize,
        *,
        format: RenderedGlyphFormat | None = None,
    ) -> RenderedGlyph:
        if format is None:
            format = RenderedGlyphFormat.ALPHA
        if isinstance(character, str) and len(character) != 1:
            raise ValueError("only a single character may be rendered")
        if size.face is not self:
            raise ValueError("size is not compatible with this face")

        size._use()
        if isinstance(character, str):
            self._ft_face.load_char(character, 0)
        else:
            try:
                self._ft_face.load_glyph(character, 0)
            except FT_Exception as ex:
                raise ValueError("face does not contain the specified glyph")

        ft_glyph = self._ft_face.glyph
        try:
            ft_glyph.render(format.value)
        except FT_Exception as ex:
            pass
        width = ft_glyph.bitmap.width
        height = ft_glyph.bitmap.rows
        data = bytes(ft_glyph.bitmap.buffer)
        if format == RenderedGlyphFormat.LCD:
            width = width // 3
            data = b"".join(
                (
                    bytes(
                        (
                            data[x * 3 + (y * ft_glyph.bitmap.pitch)],
                            data[x * 3 + 1 + (y * ft_glyph.bitmap.pitch)],
                            data[x * 3 + 2 + (y * ft_glyph.bitmap.pitch)],
                        )
                    )
                    for y in range(height)
                    for x in range(width)
                )
            )
        elif format == RenderedGlyphFormat.LCD_V:
            height = height // 3
            data = b"".join(
                (
                    bytes(
                        (
                            data[x + (y * 3 * ft_glyph.bitmap.pitch)],
                            data[x + ((y * 3 + 1) * ft_glyph.bitmap.pitch)],
                            data[x + ((y * 3 + 2) * ft_glyph.bitmap.pitch)],
                        )
                    )
                    for y in range(height)
                    for x in range(width)
                )
            )

        return RenderedGlyph(
            data,
            UVector2(width, height),
            FVector2(ft_glyph.bitmap_left, -ft_glyph.bitmap_top),
            format,
        )

    @property
    def fixed_sizes(self) -> Sequence[FontFaceSize]:
        return tuple(
            _FixedFontFaceSize(self, i) for i, _ in enumerate(self._ft_face.available_sizes)
        )

    @property
    def name(self) -> str:
        return self._name


def layout_text(
    rich_text: Sequence[RichText[_T]],
    *,
    break_text: BreakText | None = None,
    max_line_size: int | None = None,
    is_character_rendered: Callable[[str], bool] | None = None,
    line_height: int | None = None,
    primary_axis_alignment: PrimaryAxisTextAlign | None = None,
    secondary_axis_alignment: SecondaryAxisTextAlign | None = None,
    origin: FVector2 | None = None,
) -> TextLayout[_T] | None:
    if break_text is None:
        break_text = break_text_never
    if is_character_rendered is None:
        is_character_rendered = character_is_normally_rendered
    if primary_axis_alignment is None:
        primary_axis_alignment = PrimaryAxisTextAlign.BEGIN
    if secondary_axis_alignment is None:
        secondary_axis_alignment = SecondaryAxisTextAlign.BEGIN
    if origin is None:
        origin = FVector2(0)

    return _TextLayout(
        rich_text,
        break_text,
        max_line_size,
        is_character_rendered,
        line_height,
        primary_axis_alignment,
        secondary_axis_alignment,
    ).to_text_layout(origin)


class PrimaryAxisTextAlign(StrEnum):
    BEGIN = "begin"
    END = "end"
    CENTER = "center"


class SecondaryAxisTextAlign(StrEnum):
    BEGIN = "begin"
    END = "end"
    CENTER = "center"
    BASELINE = "baseline"


@dataclass(slots=True)
class _PositionedGlyph:
    character: str
    glyph_index: int
    advance_position: FVector2
    rendered_position: FVector2
    rendered_size: FVector2
    is_rendered: bool
    font_face_size: FontFaceSize
    line_size: float
    text_index: int
    rich_text_index: tuple[int, int]

    @property
    def rendered_extent(self) -> FVector2:
        return self.rendered_position + self.rendered_size


class _TextLineLayout:
    def __init__(self, position: FVector2):
        self.position = position
        self.size = FVector2(0)
        self.baseline_offset = FVector2(0)
        self.glyphs: list[_PositionedGlyph] = []

    def add_glyphs(
        self, glyphs: Sequence[_PositionedGlyph], advance: FVector2, max_size: int | None
    ) -> bool:
        if max_size is not None and self.extent.x + advance.x > max_size:
            if self.glyphs:
                return False

        line_size = self.size.y
        for glyph in glyphs:
            glyph.rendered_position += self.size.xo
            if round(glyph.line_size) > line_size:
                line_size = round(glyph.line_size)
                self.baseline_offset = glyph.font_face_size._baseline_offset

        self.size = FVector2(self.size.x + advance.x, line_size)

        self.glyphs.extend(glyphs)
        return True

    @property
    def baseline(self) -> FVector2:
        baseline = self.position + self.size.oy + self.baseline_offset
        return FVector2(int(baseline.x), int(baseline.y))

    @property
    def extent(self) -> FVector2:
        return self.position + self.size

    @property
    def rendered_bounding_box(self) -> FBoundingBox2d:
        position_x = 0.0
        extent_x = 0.0
        for glyph in self.glyphs:
            if glyph.is_rendered:
                position_x = glyph.rendered_position.x
                break
        for glyph in reversed(self.glyphs):
            if glyph.is_rendered:
                extent_x = glyph.rendered_extent.x
                break
        return FBoundingBox2d(
            FVector2(self.position.x + position_x, self.position.y),
            FVector2(extent_x - position_x, self.size.y),
        )


class _TextLayout(Generic[_T]):
    def __init__(
        self,
        rich_text: Sequence[RichText[_T]],
        break_text: BreakText,
        max_line_size: int | None,
        is_character_rendered: Callable[[str], bool],
        line_height: int | None,
        primary_axis_alignment: PrimaryAxisTextAlign,
        secondary_axis_alignment: SecondaryAxisTextAlign,
    ):
        self.is_character_rendered = is_character_rendered

        self.line_height = line_height
        self.max_line_size = max_line_size
        self.lines: list[_TextLineLayout] = [_TextLineLayout(FVector2(0))]

        self.rich_text = rich_text if isinstance(rich_text, tuple) else tuple(rich_text)
        if rich_text:
            full_text = "".join(r.text for r in rich_text)
            rich_text_iter = iter(enumerate(rich_text))
            ni, current_rich_text = next(rich_text_iter)
            ri = 0
            i_offset = 0
            for chunk in break_text(full_text):
                chunk_length = len(chunk.text)
                rich_text_ranges: list[RichTextRange] = []
                while chunk_length > 0:
                    i = ni
                    start = ri
                    end = start + chunk_length
                    chunk_length -= len(current_rich_text.text) - start
                    if chunk_length > 0:
                        end = len(current_rich_text.text)
                        ni, current_rich_text = next(rich_text_iter)
                        ri = 0
                    else:
                        ri = end
                    if start != end:
                        rich_text_ranges.append(RichTextRange(i, start, end))
                self._add_chunk(chunk, rich_text, rich_text_ranges, i_offset)
                i_offset += len(chunk.text)

        self._h_align(primary_axis_alignment)
        self._v_align(secondary_axis_alignment)
        self._fix_last_glyph_per_line_advance_position()

        self.position = FVector2(
            min(line.position.x for line in self.lines), self.lines[0].position.y
        )
        self.size = FVector2(
            max(line.rendered_bounding_box.size.x for line in self.lines),
            self.lines[-1].extent.y - self.position.y,
        )

    def _fix_last_glyph_per_line_advance_position(self) -> None:
        for i, line in enumerate(self.lines):
            try:
                next_line = self.lines[i + 1]
            except IndexError:
                break
            try:
                last_glyph = line.glyphs[-1]
            except IndexError:
                continue
            last_glyph.advance_position = -line.baseline + next_line.baseline

    def _add_chunk(
        self,
        chunk: BreakTextChunk,
        rich_texts: Sequence[RichText[_T]],
        rich_text_ranges: Sequence[RichTextRange],
        text_index: int,
    ) -> None:
        chunk_glyphs: list[_PositionedGlyph] = []
        pen_position = FVector2(0)

        for rich_text_i, rich_text_start, rich_text_end in rich_text_ranges:
            rich_text = rich_texts[rich_text_i]
            size = rich_text.size
            text = rich_text.text[rich_text_start:rich_text_end]

            hb_font = size._face._hb_font
            hb_font.scale = size._scale

            hb_buffer = HbBuffer()
            hb_buffer.direction = "LTR"
            hb_buffer.add_str(text)
            hb_shape(hb_font, hb_buffer, {})

            for i, (info, pos) in enumerate(zip(hb_buffer.glyph_infos, hb_buffer.glyph_positions)):
                c = text[info.cluster]
                chunk_glyphs.append(
                    _PositionedGlyph(
                        c,
                        info.codepoint,
                        pen_position + FVector2(pos.x_advance / 64.0, 0),
                        pen_position + FVector2(pos.x_offset / 64.0, pos.y_offset / 64.0),
                        size._face._get_glyph_size(info.codepoint, size),
                        self.is_character_rendered(c),
                        size,
                        size._line_size.y if self.line_height is None else self.line_height,
                        text_index,
                        (rich_text_i, rich_text_start + i),
                    )
                )
                pen_position += FVector2(pos.x_advance / 64.0, pos.y_advance / 64.0)
                text_index += 1

        self._add_chunk_glyphs(chunk, chunk_glyphs, pen_position)

    def _add_chunk_glyphs(
        self, chunk: BreakTextChunk, chunk_glyphs: Sequence[_PositionedGlyph], advance: FVector2
    ) -> None:
        glyphs_added = self.lines[-1].add_glyphs(chunk_glyphs, advance, self.max_line_size)

        if not glyphs_added or chunk.force_break:
            line = _TextLineLayout(FVector2(0, sum((l.size.y for l in self.lines))))
            self.lines.append(line)

            if not glyphs_added:
                glyphs_added = line.add_glyphs(chunk_glyphs, advance, self.max_line_size)
                assert glyphs_added

    def _h_align(self, align: PrimaryAxisTextAlign) -> None:
        getattr(self, f"_h_align_{align.value}")()

    def _h_align_begin(self) -> None:
        pass

    def _h_align_center(self) -> None:
        for line in self.lines:
            line.position -= line.rendered_bounding_box.size.xo * 0.5

    def _h_align_end(self) -> None:
        for line in self.lines:
            line.position -= line.rendered_bounding_box.size.xo

    def _v_align(self, align: SecondaryAxisTextAlign) -> None:
        getattr(self, f"_v_align_{align.value}")()

    def _v_align_begin(self) -> None:
        pass

    def _v_align_center(self) -> None:
        center = FVector2(0, sum(l.size.y for l in self.lines) * 0.5)
        for line in self.lines:
            line.position -= center

    def _v_align_end(self) -> None:
        end = FVector2(0, sum(l.size.y for l in self.lines))
        for line in self.lines:
            line.position -= end

    def _v_align_baseline(self) -> None:
        if not self.lines:
            return
        baseline = FVector2(0, self.lines[0].size.y)
        for line in self.lines:
            line.position -= baseline

    def to_text_layout(self, origin: FVector2) -> TextLayout[_T] | None:
        if not self.size:
            return None
        return TextLayout(
            self.rich_text,
            FBoundingBox2d(origin + self.position, self.size),
            tuple(
                TextLine(
                    line.rendered_bounding_box.translate(origin),
                    tuple(
                        TextGlyph(
                            origin + line.baseline + glyph.advance_position,
                            FBoundingBox2d(
                                origin + line.baseline + glyph.rendered_position,
                                glyph.rendered_size,
                            ),
                            glyph.character,
                            glyph.glyph_index,
                            glyph.font_face_size,
                            glyph.is_rendered,
                            glyph.text_index,
                            glyph.rich_text_index[0],
                            glyph.rich_text_index[1],
                        )
                        for glyph in line.glyphs
                    ),
                )
                for line in self.lines
                if line.rendered_bounding_box.size
            ),
        )


class TextGlyph(NamedTuple):
    advance_position: FVector2
    rendered_bounding_box: FBoundingBox2d
    character: str
    glyph_index: int
    font_face_size: FontFaceSize
    is_rendered: bool
    text_index: int
    rich_text_index: int
    rich_text_text_index: int


class TextLine(NamedTuple):
    rendered_bounding_box: FBoundingBox2d
    glyphs: tuple[TextGlyph, ...]


@dataclass
class TextLayout(Generic[_T]):
    rich_text: tuple[RichText[_T], ...]
    rendered_bounding_box: FBoundingBox2d
    lines: tuple[TextLine, ...]

    @property
    def glyphs(self) -> Generator[TextGlyph, None, None]:
        for line in self.lines:
            yield from line.glyphs


class RenderedGlyph(NamedTuple):
    data: bytes
    size: UVector2
    bearing: FVector2
    format: RenderedGlyphFormat


class FontFaceSize(ABC):
    def __init__(self, face: FontFace):
        self._face = face
        self._use()
        self._nominal_size = UVector2(
            self._face._ft_face.size.x_ppem, self._face._ft_face.size.y_ppem
        )
        self._scale = (
            self._face._ft_face.size.x_scale * self._face._ft_face.units_per_EM + (1 << 15) >> 16,
            self._face._ft_face.size.y_scale * self._face._ft_face.units_per_EM + (1 << 15) >> 16,
        )
        self._line_size = FVector2(
            0.0,  # how
            self._face._ft_face.size.height / 64.0,
        )
        self._baseline_offset = FVector2(0, self._face._ft_face.size.descender / 64.0)  # how

    def __repr__(self) -> str:
        return f"<FontFaceSize for {self._face.name!r} of {self.nominal_size}>"

    @abstractmethod
    def _use(self) -> None: ...

    @property
    def face(self) -> FontFace:
        return self._face

    @property
    def nominal_size(self) -> UVector2:
        return self._nominal_size

    @property
    def line_size(self) -> FVector2:
        return self._line_size

    def layout_text(
        self,
        text: str,
        *,
        break_text: BreakText | None = None,
        max_line_size: int | None = None,
        is_character_rendered: Callable[[str], bool] | None = None,
        line_height: int | None = None,
        primary_axis_alignment: PrimaryAxisTextAlign | None = None,
        secondary_axis_alignment: SecondaryAxisTextAlign | None = None,
        origin: FVector2 | None = None,
    ) -> TextLayout | None:
        return layout_text(
            (RichText(text, self, None),),
            break_text=break_text,
            max_line_size=max_line_size,
            is_character_rendered=is_character_rendered,
            line_height=line_height,
            primary_axis_alignment=primary_axis_alignment,
            secondary_axis_alignment=secondary_axis_alignment,
            origin=origin,
        )


class _PointFontFaceSize(FontFaceSize):
    def __init__(self, face: FontFace, width: float | None, height: float | None, dpi: UVector2):
        self._args = (width, height, dpi.x, dpi.y)
        super().__init__(face)

    def _use(self) -> None:
        self.face._ft_face.set_char_size(*self._args)  # type: ignore


class _PixelFontFaceSize(FontFaceSize):
    def __init__(self, face: FontFace, width: int | None, height: int | None):
        self._args = (width, height)
        super().__init__(face)

    def _use(self) -> None:
        self.face._ft_face.set_pixel_sizes(*self._args)  # type: ignore


class _FixedFontFaceSize(FontFaceSize):
    def __init__(self, face: FontFace, index: int):
        self._index = index
        super().__init__(face)

    def _use(self) -> None:
        self.face._ft_face.select_size(self._index)
