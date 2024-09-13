VAR_CONST = "VAR"


def lgg_dict(data: list[dict]) -> dict:
    first = data[0]
    for d in data:
        for k in first:
            if first[k] == d[k]:
                continue
            first[k] = VAR_CONST
    return first


# def lgg_region(data: tuple[Region]) -> dict:
#     return lgg_dict([r.dump_main_props() for r in data])

# def lgg_prim(data: list[Bag | Region]) -> list[dict]:
#     _l = lgg_dict([r.model_dump() for r in data])
#     if isinstance(data[0], Bag):
#         _l["regions"] = lgg_dict(list(lgg_prim(b.regions) for b in data))
#     return _l
