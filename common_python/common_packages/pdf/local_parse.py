from itertools import chain

import pymupdf
from pydantic import BaseModel
from pymupdf import Document, Page, Pixmap


# span 结构:
class SpanStruClean(BaseModel):
    text: str
    """
    _span_stru = {
        "size": 10.0,
        "flags": 4,
        "font": "MinionPro-Regular",
        "color": 0,
        "ascender": 0.9890000224113464,
        "descender": -0.36000001430511475,
        "text": "Next, we will glue everything together with webpack.",
        "origin": (81.0, 573.5889892578125),
        "bbox": (81.0, 563.698974609375, 291.9960632324219, 577.18896484375),
    }
    """


# 行结构
class LineStruClean(BaseModel):
    spans: list[SpanStruClean]
    """
    _line_stru = {
        "spans": [
            _span_stru,
        ],
        "wmode": 0,
        "dir": (1.0, 0.0),
        "bbox": (81.0, 563.698974609375, 291.9960632324219, 577.18896484375),
    }
    """


# 块结构
class BlockStruClean(BaseModel):
    lines: list[LineStruClean]
    """raw:
    _block_stru = {
        "number": 10,
        "type": 0,
        "bbox": (81.0, 563.698974609375, 291.9960632324219, 577.18896484375),
        "lines": [_line_stru],
    }
    """

    # 页结构
    # class PageStruClean(BaseModel):
    #     blocks: list[BlockStruClean]

    # """
    # raw页结构
    # _page_stru = {
    #     "width": 549.0,
    #     "height": 684.0,
    #     "blocks": [
    #         _block_stru,
    #     ],
    # }
    # """


# 单个目录信息
class RawCatalogueStru(BaseModel):
    # level: 目录级别,也是目录缩进的空格数
    level: int
    # title: 目录标题
    title: str
    # page_num: 目录页码
    page_num: int


class CatalogueStru(BaseModel):
    """子目录结构(仅有2级目录)"""

    title: str
    page_num: int


class FatherCatalogueStru(BaseModel):
    """根目录结构"""

    title: str
    page_num: int
    children: list[CatalogueStru]


class ParsePDF:
    """
    sample file:
    """

    def __init__(self, file_name: str):
        self.doc: Document = pymupdf.open(file_name)
        self.page_count = self.doc.page_count

    def get_cover_image(self) -> bytes:
        """获取封面图片,返回图片的字节数据"""
        page: Page = self.doc[0]

        pix: Pixmap = page.get_pixmap()

        res: bytes = pix.tobytes()
        return res

    def _get_raw_catalogue(self) -> list[RawCatalogueStru]:
        """获取pdf的目录信息"""
        catalogue_info: list[list] = self.doc.get_toc(simple=False)

        res = [
            RawCatalogueStru(level=item[0], title=item[1], page_num=item[2])
            for item in catalogue_info
        ]

        return res

    def get_catalogue(self) -> list[FatherCatalogueStru]:
        """获取经过处理的目录信息

        返回结果数据sample:
        [
            FatherCatalogueStru(
                title='Preface',
                page_num=14,
                children=[]
            ),
            FatherCatalogueStru(
                title='Chapter 1: Introducing React',
                page_num=22,
                children=[
                    CatalogueStru(title='Technical requirements', page_num=23),
                    CatalogueStru(title='Understanding the benefits of React', page_num=23),
                    CatalogueStru(title='Understanding JSX', page_num=24),
                ]
            )
        ]
        """
        raw_catalogue = self._get_raw_catalogue()

        # 1. 过滤目录层级超过2的目录,只能保留1和2级目录
        raw_catalogue_only = list(filter(lambda x: x.level <= 2, raw_catalogue))

        # 2. 生成目录树
        # 2.1 将level是1的目录作为根目录,level是2的目录作为子目录
        res = []
        for catelogue in raw_catalogue_only:
            if catelogue.level == 1:
                f = FatherCatalogueStru(
                    title=catelogue.title, page_num=catelogue.page_num, children=[]
                )
                res.append(f)

            if catelogue.level == 2:
                # 获取最后一个目录块，就是当前的根目录
                current_fa = res.pop()
                # 获取当前的根目录的子目录
                current_children = current_fa.children

                # 获取新的子目录
                cate = CatalogueStru(title=catelogue.title, page_num=catelogue.page_num)

                # 追加新的子目录
                current_children.append(cate)

                # 重新添加到字典中
                current_fa.children = current_children

                res.append(current_fa)
        return res

    def _get_raw_page_info(self, page_num: int) -> list[BlockStruClean]:
        """获取指定页中的原生页面信息"""
        page: Page = self.doc[page_num]
        # 1. 已文本形式获取页面信息
        page_info: dict = page.get_text("dict")

        # 2. raw blocks
        raw_blocks = page_info["blocks"]
        # print("----", len(raw_blocks), raw_blocks[0], "----")

        # 3. format block
        format_blocks = [BlockStruClean(lines=block["lines"]) for block in raw_blocks]
        return format_blocks

    def _get_block_text(self, block_info: BlockStruClean) -> list[str]:
        """获取指定块中每行文本信息
        返回值:
        [
            "该块的第一行文字",
            "该块的第二行文字",
        ]
        """
        # 1. 获取块中的全部行信息
        lines: list[LineStruClean] = block_info.lines

        # 2. 获取每行的文字信息
        lines_text = []
        for line in lines:
            # 1. 获取每行的span
            spans: list[SpanStruClean] = line.spans
            # 1. 获取每个span的文字
            spans_text = [span.text for span in spans]
            # 2. 合并所有span的文字. 获取指定行的所有文字信息
            line_text = "".join(spans_text)
            lines_text.append(line_text)
        return lines_text

    def get_page_text(self, page_num: int):
        """从页面中获取原生的文本信息
        func 是判断是否合并的函数,默认如果不传入,则不合并，展开二维数组
        """

        # 1. 获取页面中的所有块信息
        raw_page_info = self._get_raw_page_info(page_num)

        # 2. 获取页面的原生文本信息
        raw_page_text: list[list[str]] = [
            self._get_block_text(block) for block in raw_page_info
        ]

        # # 3 使用ai判断,是否将这些块进行合并
        # # 这些行合并到一起是不是普通文本，如果是，则合并，否则不合并
        # for block_text in raw_page_text:
        #     # 1. 合并块中的所有行
        #     block_text_single = " ".join(block_text)

        #     # 2. 使用func判断合并完成后的文本是否是普通文本
        #     msg = f"请判断下面这些文本是代码还是普通文本:\n {block_text_single}"
        #     status = func(msg)

        #     # 3. 确定最终的文本信息
        #     if status:
        #         # 是普通文本
        #     else:
        #         ...
        # 3. 将二维数组展开
        page_text = list(chain(*raw_page_text))
        return page_text


# if __name__ == "__main__":
#     pdf = ParsePDF("/Users/jason/temp/test-pdf.pdf")
#     # blocks = pdf._get_raw_page_info(100)
#     # block = blocks[1]
#     # pdf._get_block_text(block)
#     print(pdf.get_page_text(100))
# import json

# print(json.dumps(pdf.get_top_catalogue(), indent=2))
# print(pdf.get_cover_image())

# with open("/Users/evans/Desktop/cover2.png", "wb") as f:
#     f.write(pdf.get_cover_image())
