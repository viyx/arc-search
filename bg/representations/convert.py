from bg.representations.base_classes import Figure

# begin(model(1)).
# pos.
# point(p1).
# point(p2).
# point(p5).
# point(p6).
# i(p1).
# i(p2).
# o(p5).
# o(p6).
# x(p1,0).
# x(p2,1).
# x(p5,0).
# x(p6,1).
# y(p1,0).
# y(p2,1).
# y(p5,1).
# y(p6,1).
# end(model(1)).


def convert_model(x: set[Figure], y: set[Figure], pic_num: int, pos: bool) -> str:
    atoms = []

    atoms.append(f"begin(model({pic_num})).")
    atoms.append("pos." if pos else "neg.")

    for f in x:
        assert f.level == 1
        name = f"p1_{f.x}_{f.y}"
        atoms.append(f"point({name}).")
        atoms.append(f"i({name}).")
        atoms.append(f"x({name},{f.x}).")
        atoms.append(f"y({name},{f.y}).")
        atoms.append(f"color({name},{f.color}).")

    for f in y:
        assert f.level == 1
        name = f"p2_{f.x}_{f.y}"
        atoms.append(f"point({name}).")
        atoms.append(f"o({name}).")
        atoms.append(f"x({name},{f.x}).")
        atoms.append(f"y({name},{f.y}).")
        atoms.append(f"color({name},{f.color}).")

    atoms.append(f"end(model({pic_num})).")
    res = "\n".join(atoms)
    return res


# puzzle(1, pos).
# point(1,1,inp,0,0).
# point(1,2,inp,1,1).
# point(1,3,outp,0,1).
# point(1,4,outp,1,1).

# puzzle(2, neg).
# point(2,1,inp,0,0).
# point(3,2,inp,1,1).
# point(4,3,outp,1,1).
# # point(5,4,outp,1,1).


def convert_key(x: set[Figure], y: set[Figure], pic_num: int, pos: bool) -> str:
    atoms = []

    class_name = "pos" if pos else "neg"
    atoms.append(f"puzzle({pic_num}, {class_name}).")

    for f in sorted(x, key=lambda _x: (_x.x, _x.y)):
        assert f.level == 1
        name = f"px_{f.x}_{f.y}"
        atoms.append(f"point({pic_num}, {name}, inp, {f.x}, {f.y}, {f.color}).")

    for f in sorted(y, key=lambda _x: (_x.x, _x.y)):
        assert f.level == 1
        name = f"py_{f.x}_{f.y}"
        atoms.append(f"point({pic_num}, {name}, outp, {f.x}, {f.y}, {f.color}).")

    res = "\n".join(atoms)
    return res
