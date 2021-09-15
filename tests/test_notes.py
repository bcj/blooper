import pytest


def test_dynamic():
    from blooper.notes import Dynamic

    assert Dynamic(0).step == 10
    assert Dynamic(10).step == 10

    assert Dynamic(-40).name == "pianissississimo"
    assert Dynamic(-39).name == "pianississimo"
    assert Dynamic(-30).name == "pianississimo"
    assert Dynamic(-20).name == "pianissimo"
    assert Dynamic(-16).name == "piano"
    assert Dynamic(-10).name == "piano"
    assert Dynamic(-5).name == "mezzo-piano"
    assert Dynamic(0).name == "mezzo-piano"
    assert Dynamic(1).name == "mezzo-forte"
    assert Dynamic(10).name == "forte"
    assert Dynamic(19).name == "forte"
    assert Dynamic(20).name == "fortissimo"
    assert Dynamic(32).name == "fortississimo"
    assert Dynamic(40).name == "fortissississimo"

    assert Dynamic(-40).symbol == "pppp"
    assert Dynamic(-39).symbol == "ppp"
    assert Dynamic(-30).symbol == "ppp"
    assert Dynamic(-20).symbol == "pp"
    assert Dynamic(-16).symbol == "p"
    assert Dynamic(-10).symbol == "p"
    assert Dynamic(-5).symbol == "mp"
    assert Dynamic(0).symbol == "mp"
    assert Dynamic(1).symbol == "mf"
    assert Dynamic(10).symbol == "f"
    assert Dynamic(19).symbol == "f"
    assert Dynamic(20).symbol == "ff"
    assert Dynamic(32).symbol == "fff"
    assert Dynamic(40).symbol == "ffff"

    assert Dynamic.from_name("pianissississimo").value == -40
    assert Dynamic.from_name("pianississimo").value == -30
    assert Dynamic.from_name("pianissimo").value == -20
    assert Dynamic.from_name("piano").value == -10
    assert Dynamic.from_name("mezzo-piano").value == -5
    assert Dynamic.from_name("mezzo-forte").value == 5
    assert Dynamic.from_name("forte").value == 10
    assert Dynamic.from_name("fortissimo").value == 20
    assert Dynamic.from_name("fortississimo").value == 30
    assert Dynamic.from_name("fortissississimo").value == 40

    for name in (
        "pianiss",
        "pianimo",
        "mezzo-pianissimo",
        "mezzo-",
        "mezzo",
        "mezzo-fortissimo",
        "fortimo",
        "fortiss",
        "very loud",
    ):
        with pytest.raises(ValueError):
            Dynamic.from_name(name)

    assert Dynamic.from_symbol("pppp").value == -40
    assert Dynamic.from_symbol("ppp").value == -30
    assert Dynamic.from_symbol("pp").value == -20
    assert Dynamic.from_symbol("p").value == -10
    assert Dynamic.from_symbol("mp").value == -5
    assert Dynamic.from_symbol("mf").value == 5
    assert Dynamic.from_symbol("f").value == 10
    assert Dynamic.from_symbol("ff").value == 20
    assert Dynamic.from_symbol("fff").value == 30
    assert Dynamic.from_symbol("ffff").value == 40

    for symbol in ("mpp", "fp", "mff", "forte", "fm", "n"):
        with pytest.raises(ValueError):
            Dynamic.from_symbol(symbol)
