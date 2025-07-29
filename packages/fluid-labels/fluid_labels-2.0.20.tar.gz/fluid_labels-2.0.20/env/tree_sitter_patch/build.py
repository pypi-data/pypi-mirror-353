import os

import tree_sitter

GRAMMARS: dict[str, str] = {
    "swift": os.environ["envTreeSitterSwift"],
}


def main() -> None:
    out: str = os.environ["out"]
    path: str

    os.makedirs(out)

    for grammar, src in GRAMMARS.items():
        path = os.path.join(out, f"{grammar}.so")
        tree_sitter.Language.build_library(path, [src])


if __name__ == "__main__":
    main()
