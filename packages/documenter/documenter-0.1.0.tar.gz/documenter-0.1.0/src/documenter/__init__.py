from typing_extensions import Literal, Any, Union, Dict
from toml import load, dump
from os import makedirs
from pathlib import Path

__version__ = "0.1.0"
__all__ = ["init", "initsettings", "Path"
           "LOCAL", "GLOBAL", "ALL", "HOME", "CWD"
        ]
__author__ = "xystudio"

initsettings = {}
lang_alias = {}

ALL = "all"

HOME = Path.home()
CWD = Path.cwd()

def init(**kwargs):
    global initsettings

    initsettings.update(kwargs)

__init__ = init

def get_alias(lang: str = ALL):
    if initsettings.get("have_alias", False) == False: raise AttributeError("init settings is not enabled alias.")
    print()
    match_alias = None
    for k, v in lang_alias.items():
        if lang.lower() in v:
            match_alias = k
            break

    if lang == ALL:
        for k, v in lang_alias.items():
            print(f"alias {k} -> {', '.join(v)}")
    elif match_alias is not None:
        print(f"alias {match_alias} -> {lang}")
    else:
        print(f"alias {lang} -> {', '.join(lang_alias.get(lang, ["Not found."]))}")

def open_doc(doc_name: str, lang: str = ALL):
    if initsettings.get("have_alias", False) == False:
        pass
    else:
        from markdown import markdown
        from os import remove
        from webbrowser import open as op
        from time import sleep

        doc_html_path = Path(initsettings.get("cache_path", Path.cwd() / ".xystudio" / "documenter" / "cache" / "doc.html"))
        doc_name = doc_name.lower()

        makedirs(doc_html_path.parent, exist_ok=True)

        if initsettings.get("use_alias", False):
            if initsettings.get("have_lang", False):
                for key, values in lang_alias.items():
                    if lang.lower() in values:
                        lang = key
                lang = lang.lower()

                if doc_name == "index" and initsettings.get("use_index_path", False):
                    op(Path(initsettings.get("index_path", Path.cwd()  / ".xystudio" / "documenter" / "webs") / lang / "index.html"))
                else:
                    with open(Path(initsettings.get("doc_path", Path.cwd()  / ".xystudio" / "documenter" / "markdown") / lang / f"{doc_name}.md"), "r", encoding="utf-8") as f:
                        html = markdown(f.read())

                    with open(doc_html_path, "w", encoding="utf-8") as f:
                        f.write(html)

                    op(doc_html_path)
                    sleep(1)
                    remove(doc_html_path)
            else:
                if doc_name == "index" and initsettings.get("use_index_path", False):
                    op(Path(initsettings.get("index_path", Path.cwd()  / ".xystudio" / "documenter" / "webs") / "index.html"))
                else:
                    with open(Path(initsettings.get("doc_path", Path.cwd()  / ".xystudio" / "documenter" / "markdown") / f"{doc_name}.md"), "r", encoding="utf-8") as f:
                        html = markdown(f.read())

                    with open(doc_html_path, "w", encoding="utf-8") as f:
                        f.write(html)

                    op(doc_html_path)
                    sleep(1)
                    remove(doc_html_path)
        else:
            if initsettings.get("have_lang", False):
                if doc_name == "index" and initsettings.get("use_index_path", False):
                    op(Path(initsettings.get("index_path", Path.cwd()  / ".xystudio" / "documenter" / "webs") / lang / "index.html"))
                else:
                    with open(Path(initsettings.get("doc_path", Path.cwd()  / ".xystudio" / "documenter" / "markdown") / lang / f"{doc_name}.md"), "r", encoding="utf-8") as f:
                        html = markdown(f.read())

                    with open(doc_html_path, "w", encoding="utf-8") as f:
                        f.write(html)

                    op(doc_html_path)
                    sleep(1)
                    remove(doc_html_path)
            else:
                if doc_name == "index" and initsettings.get("use_index_path", False):
                    op(Path(initsettings.get("index_path", Path.cwd()  / ".xystudio" / "documenter" / "webs") / "index.html"))
                else:
                    with open(Path(initsettings.get("doc_path", Path.cwd()  / ".xystudio" / "documenter" / "markdown") / f"{doc_name}.md"), "r", encoding="utf-8") as f:
                        html = markdown(f.read())

                    with open(doc_html_path, "w", encoding="utf-8") as f:
                        f.write(html)

                    op(doc_html_path)
                    sleep(1)
                    remove(doc_html_path)

def _write_init_settings():
    with open(initsettings.get("local_config_path", Path.home() / ".xystudio" / "configurer" / "init_settings.xys"), "init_settings.xys", "w") as f:
        dump(initsettings, f)

def _read_init_settings():
    global initsettings
    try:
        with open(initsettings.get("local_config_path", Path.home() / ".xystudio" / "configurer" / "init_settings.xys"), "r") as f:
            initsettings = load(f)
    except FileNotFoundError:
        pass

def main():
    pass

if __name__ == "__main__":
    main()