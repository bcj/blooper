def test_usage_metadata():
    from blooper.filetypes import UsageMetadata
    from blooper.notes import Dynamic

    pianissimo = Dynamic.from_symbol("pp")
    piano = Dynamic.from_symbol("p")
    forte = Dynamic.from_symbol("f")
    fortississimo = Dynamic.from_symbol("fff")

    for dynamic in (None, pianissimo, piano, forte, fortississimo):
        assert UsageMetadata(440).compatible_dynamic(dynamic)

    metadata = UsageMetadata(440, piano)
    assert metadata.compatible_dynamic(None)
    assert not metadata.compatible_dynamic(pianissimo)
    assert metadata.compatible_dynamic(piano)
    assert metadata.compatible_dynamic(forte)
    assert metadata.compatible_dynamic(fortississimo)

    metadata = UsageMetadata(440, forte)
    assert metadata.compatible_dynamic(None)
    assert not metadata.compatible_dynamic(pianissimo)
    assert not metadata.compatible_dynamic(piano)
    assert metadata.compatible_dynamic(forte)
    assert metadata.compatible_dynamic(fortississimo)

    metadata = UsageMetadata(440, None, piano)
    assert metadata.compatible_dynamic(None)
    assert metadata.compatible_dynamic(pianissimo)
    assert metadata.compatible_dynamic(piano)
    assert not metadata.compatible_dynamic(forte)
    assert not metadata.compatible_dynamic(fortississimo)

    metadata = UsageMetadata(440, piano, forte)
    assert metadata.compatible_dynamic(None)
    assert not metadata.compatible_dynamic(pianissimo)
    assert metadata.compatible_dynamic(piano)
    assert metadata.compatible_dynamic(forte)
    assert not metadata.compatible_dynamic(fortississimo)

    metadata = UsageMetadata(440, piano, piano)
    assert metadata.compatible_dynamic(None)
    assert not metadata.compatible_dynamic(pianissimo)
    assert metadata.compatible_dynamic(piano)
    assert not metadata.compatible_dynamic(forte)
    assert not metadata.compatible_dynamic(fortississimo)
