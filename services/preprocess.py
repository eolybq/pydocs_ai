from bs4 import BeautifulSoup
from pathlib import Path


# vytvoreni dict chunks s contents a titles chunku
def is_h_tag(tag):
    return tag.name and tag.name.startswith("h") and tag.name[1].isdigit()  # and tag.name[1] != "1"


def get_chunk(h_tag, main_title, max_len=4000, overlap=500):
    chunk = {
        "title": h_tag.get_text(strip=True),
        # pridavam main title / title i do content -> ktery se prevede pak na embdedding aby byl title v nem
        "content": h_tag.get_text(strip=True) + main_title,
    }

    for tag in h_tag.find_next_siblings():
        if is_h_tag(tag):
            break
        chunk["content"] = chunk["content"] + tag.get_text(strip=True)

    # overlap contetnu delsi nez max_len
    if len(chunk["content"]) <= max_len:
        yield chunk
        return

    step = max_len - overlap
    for i, start in enumerate(range(0, len(chunk["content"]), step)):
        yield {
            "title": f"{chunk["title"]} ({i + 1})",
            "content": chunk["content"][start:start + max_len]
        }


def get_pages(path):
    files_list = []
    base_path = Path("html") / path
    for file in base_path.rglob("*.html"):
        if str(file) not in ("index.html", "whatsnew.html", "genindex.html", "release.html"):
            files_list.append(str(file))

    pages_list = []
    for file in files_list:
        with open(file, "r", encoding="utf8") as f:
            html = f.read()

        soup = BeautifulSoup(html, "lxml")

        for script in soup(["script", "style"]):
            script.decompose()

        if not soup.find("h1"):
            continue

        main_title = soup.find("h1").get_text()
        h_tags = soup.find_all(is_h_tag)

        page = {
            "main_title": main_title,
            "chunks": []
        }

        for h_tag in h_tags:
            if len(h_tags) > 1 and h_tag.name != "h1":
                page["chunks"].extend(get_chunk(h_tag, main_title=main_title))
            elif len(h_tags) == 1 and h_tag.name == "h1":
                page["chunks"].extend(get_chunk(h_tag, main_title=main_title))
        print(page["chunks"])

        pages_list.append(page)

    return pages_list