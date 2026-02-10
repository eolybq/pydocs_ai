from bs4 import BeautifulSoup, Tag
from pathlib import Path
from typing import Generator
from loguru import logger

from config import Chunk


def is_h_tag(tag: Tag) -> bool:
    return bool(
        tag.name and tag.name.startswith("h") and tag.name[1].isdigit()
    )  # and tag.name[1] != "1"


# vytvoreni dict chunks s contents a titles chunku
def get_chunk(
    h_tag: Tag, main_title: str, max_len: int = 4000, overlap: int = 500
) -> Generator[Chunk, None, None]:
    chunk = Chunk(
        main_title=main_title, chunk_title=h_tag.get_text(strip=True), content=""
    )

    for tag in h_tag.find_next_siblings():
        if is_h_tag(tag):
            break
        chunk.content += "\n" + tag.get_text(strip=True)

    # overlap contetnu delsi nez max_len
    if len(chunk.content) <= max_len:
        yield chunk
        return

    step = max_len - overlap
    for i, start in enumerate(range(0, len(chunk.content), step)):
        yield Chunk(
            main_title=chunk.main_title,
            chunk_title=f"{chunk.chunk_title} ({i + 1})",
            content=chunk.content[start : start + max_len],
        )


def get_chunks_list(path: str) -> list[Chunk]:
    files_list = []
    base_path = Path("data") / path
    for file in sorted(base_path.rglob("*.html")):
        if str(file.name) not in (
            "index.html",
            "whatsnew.html",
            "genindex.html",
            "release.html",
        ):
            files_list.append(file)

    chunks_list = []
    for file in files_list:
        with open(file, "r", encoding="utf8") as f:
            html = f.read()

        soup = BeautifulSoup(html, "lxml")

        for script in soup(["script", "style"]):
            script.decompose()

        first_h1 = soup.find("h1")

        if not first_h1:
            continue

        main_title = first_h1.get_text()
        h_tags = soup.find_all(is_h_tag)

        page_chunks = []

        for h_tag in h_tags:
            if len(h_tags) > 1 and h_tag.name != "h1":
                page_chunks.extend(get_chunk(h_tag, main_title=main_title))
            elif len(h_tags) == 1 and h_tag.name == "h1":
                page_chunks.extend(get_chunk(h_tag, main_title=main_title))
        logger.debug(page_chunks)

        chunks_list.extend(page_chunks)

    return chunks_list
