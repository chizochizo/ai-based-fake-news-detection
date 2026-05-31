# test_calibrator.py

from analysis.nli_analyzer import calibrate_nli_label

tests = [

    ("CONTRADICTION", 0.99, 0.0, 0.0),

    ("CONTRADICTION", 0.65, 0.0, 0.0),

    ("NEUTRAL", 0.90, 0.80, 20),

    ("NEUTRAL", 0.90, 0.20, 2)

]

for raw, conf, align, fact in tests:

    result = calibrate_nli_label(
        raw,
        conf,
        align,
        fact
    )

    print(
        raw,
        conf,
        align,
        fact,
        "=>",
        result
    )
