def test_waves():
    from blooper.waveforms import saw_wave, sine_wave, square_wave, triangle_wave

    assert sine_wave(0) == 0
    assert sine_wave(0.25) == 1
    assert sine_wave(0.5) == 0
    assert sine_wave(0.75) == -1
    assert sine_wave(1) == 0
    # thanks wolfram alpha
    sin_pi_3 = 0.8660254037844386467637231707529361834714026269051903140279034897
    assert sine_wave(1 / 6) == sin_pi_3
    # looks like we can trust python to about 14 decimal places once we
    # add some additional multiplication
    assert round(sine_wave(1 / 3), 14) == round(sin_pi_3, 14)
    assert round(sine_wave(2 / 3), 14) == round(-sin_pi_3, 14)
    assert sine_wave(5 / 6) == -sin_pi_3

    assert square_wave(0) == 1
    assert square_wave(0.25) == 1
    assert square_wave(0.5) == -1
    assert square_wave(0.75) == -1
    assert square_wave(1) == 1
    assert square_wave(1 / 6) == 1
    assert square_wave(1 / 3) == 1
    assert square_wave(2 / 3) == -1
    assert square_wave(5 / 6) == -1
    assert square_wave(1 / 8) == 1
    assert square_wave(3 / 8) == 1
    assert square_wave(5 / 8) == -1
    assert square_wave(7 / 8) == -1

    assert saw_wave(0) == 0
    assert saw_wave(0.25) in (-1, 1)
    assert saw_wave(0.5) == 0
    assert saw_wave(0.75) in (-1, 1)
    assert saw_wave(1) == 0
    # sine was good to 14 digits so that's all we'll demand
    assert round(saw_wave(1 / 6), 14) == round(2 / 3, 14)
    assert round(saw_wave(1 / 3), 14) == round(-2 / 3, 14)
    assert round(saw_wave(2 / 3), 14) == round(2 / 3, 14)
    assert round(saw_wave(5 / 6), 14) == round(-2 / 3, 14)
    assert saw_wave(1 / 8) == 0.5
    assert saw_wave(3 / 8) == -0.5
    assert saw_wave(5 / 8) == 0.5
    assert saw_wave(7 / 8) == -0.5

    assert triangle_wave(0) == 0
    assert triangle_wave(0.25) == 1
    assert triangle_wave(0.5) == 0
    assert triangle_wave(0.75) == -1
    assert triangle_wave(1) == 0
    assert round(triangle_wave(1 / 6), 14) == round(2 / 3, 14)
    assert round(triangle_wave(1 / 3), 14) == round(2 / 3, 14)
    assert round(triangle_wave(2 / 3), 14) == round(-2 / 3, 14)
    assert round(triangle_wave(5 / 6), 14) == round(-2 / 3, 14)
    assert triangle_wave(1 / 8) == 0.5
    assert triangle_wave(3 / 8) == 0.5
    assert triangle_wave(5 / 8) == -0.5
    assert triangle_wave(7 / 8) == -0.5


def test_waveform():
    from blooper.waveforms import Waveform

    sine = Waveform(400, 1600)
    assert sine.phase is None
    assert sine.sample() == 0
    assert sine.phase == 0
    assert sine.sample() == 1
    assert sine.phase == 1 / 4
    assert sine.sample() == 0
    assert sine.phase == 1 / 2
    assert sine.sample() == -1
    assert sine.phase == 3 / 4
    assert sine.sample() == 0
    assert sine.phase == 0
    assert sine.sample() == 1
    assert sine.phase == 1 / 4

    # passing a phase
    sine = Waveform(400, 1600, phase=0)
    assert sine.phase == 0
    assert sine.sample() == 1
    assert sine.phase == 1 / 4
    assert sine.sample() == 0
    assert sine.phase == 1 / 2

    # passed-in phase doesn't need to align with produced phases
    sine = Waveform(400, 800, phase=3 / 4)
    assert sine.phase == 3 / 4
    assert sine.sample() == 1
    assert sine.phase == 1 / 4
    assert sine.sample() == -1
    assert sine.phase == 3 / 4

    square = Waveform(400, 6_000, wave="square")
    assert square.phase is None
    assert square.sample() == 1
    assert square.phase == 0 / 15
    assert square.sample() == 1
    assert square.phase == 1 / 15
    assert square.sample() == 1
    assert square.phase == 2 / 15
    assert square.sample() == 1
    assert square.phase == 3 / 15
    assert square.sample() == 1
    assert square.phase == 4 / 15
    assert square.sample() == 1
    assert square.phase == 5 / 15
    assert square.sample() == 1
    assert square.phase == 6 / 15
    assert square.sample() == 1
    assert square.phase == 7 / 15
    assert square.sample() == -1
    assert square.phase == 8 / 15
