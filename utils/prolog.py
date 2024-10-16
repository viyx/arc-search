from reprs.primitives import Bag


def convert1(data: tuple[Bag], fname: str, name: str, start_enum: int = 1) -> None:
    """s(0/0/'0'/1),s(0/1/'0'/1)"""
    for i, b in enumerate(data.bags, start_enum):
        strs = []
        for r in b.regions:
            if r.mask.shape == (1, 1):
                strs.append(f"{name}({r.x},{r.y},'{next(iter(r.unq_colors))}',{i})")
        with open(fname, "a") as f:
            f.write(".\n".join(strs) + ".\n")
