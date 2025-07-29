"""Convenient and deterministic packaging. No pyproject.toml, only the __project__ dictionary.

> pip install dundle

License: 0BSD (See end of file)
"""

def format_core_metadata(metadata: dict) -> list:
    """Return core metadata as list of (key, value) tuples.

    metadata: Dictionary conforming to __project__ (see section 2).

    Note: This function assumes metadata has already been validated (see validate_metadata).
    Note: The core metadata format (introduced in PEP 241) is used both in sdist (as PKG-INFO) and wheel (as METADATA).
    """
    tuples = [
        ("Metadata-Version", "2.4"),
        ("Name", metadata["name"]),
        ("Version", metadata["version"]),
    ]

    try: tuples.append(("Summary", metadata["description"]))
    except: pass

    try: tuples.append(("Requires-Python", metadata["requires-python"]))
    except: pass

    try: tuples += [("Requires-Dist", e) for e in metadata["dependencies"]]
    except: pass

    try:
        for label, opt_deps in metadata["optional-dependencies"].items():
            tuples.append(("Provides-Extra", label))
            tuples += [("Requires-Dist", f'{e}; extra == "{label}"') for e in opt_deps]
    except: pass

    try: tuples += [("Project-URL", f"{label}, {url}") for label, url in metadata["urls"].items()]
    except: pass

    try: tuples += [("Classifier", e) for e in metadata["classifiers"]]
    except: pass

    try: tuples.append(("Keywords", ",".join(metadata["keywords"])))
    except: pass

    def format_author(e):
        try:
            name = e["name"]
            if " " in name:
                name = f'"{name}"'
        except: # only email
            return e["email"]
        else:
            try: # name and email
                return f'{name} <{e["email"]}>'
            except: # only name
                return name

    for var in "author", "maintainer":
        try: list = metadata[f"{var}s"]
        except: continue
        Var = var.capitalize()
        Var_email = f"{Var}-email"

        try: tuples.append((Var, ", ".join(format_author(e) for e in list if "email" not in e)))
        except: pass

        try: tuples.append((Var_email, ", ".join(format_author(e) for e in list if "email" in e)))
        except: pass

    try: tuples.append(("License-Expression", metadata["license"]))
    except: pass

    try: tuples += [("License-File", e) for e in metadata["license-files"]]
    except: pass

    try: tuples.append(("Description-Content-Type", metadata["readme"]["content-type"]))
    except: pass

    return tuples

__license__ = """\
The 0BSD license.

Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""
