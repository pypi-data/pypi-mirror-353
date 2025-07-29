"""Property-based tests for monochromatic.

By Zac Hatfield-Dodds, based on my Hypothesmith tool for source code
generation.  You can run this file with `python`, `pytest`, or (soon)
a coverage-guided fuzzer I'm working on.
"""

import hypothesmith
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

import monochromatic


# This test uses the Hypothesis and Hypothesmith libraries to generate random
# syntatically-valid Python source code and run monochromatic in odd modes.
@settings(
    max_examples=1000,  # roughly 1k tests/minute, or half that under coverage
    derandomize=True,  # deterministic mode to avoid CI flakiness
    deadline=None,  # ignore Hypothesis' health checks; we already know that
    suppress_health_check=list(HealthCheck),  # this is slow and filter-heavy.
)
@given(
    # Note that while Hypothesmith might generate code unlike that written by
    # humans, it's a general test that should pass for any *valid* source code.
    # (so e.g. running it against code scraped of the internet might also help)
    src_contents=hypothesmith.from_grammar() | hypothesmith.from_node(),
    # Using randomly-varied modes helps us to exercise less common code paths.
    mode=st.builds(
        monochromatic.FileMode,
        line_length=st.just(88) | st.integers(0, 200),
        string_normalization=st.booleans(),
        preview=st.booleans(),
        is_pyi=st.booleans(),
        magic_trailing_comma=st.booleans(),
    ),
)
def test_idempotent_any_syntatically_valid_python(
    src_contents: str, mode: monochromatic.FileMode
) -> None:
    # Before starting, let's confirm that the input string is valid Python:
    compile(src_contents, "<string>", "exec")  # else the bug is in hypothesmith

    # Then format the code...
    dst_contents = monochromatic.format_str(src_contents, mode=mode)

    # And check that we got equivalent and stable output.
    monochromatic.assert_equivalent(src_contents, dst_contents)
    monochromatic.assert_stable(src_contents, dst_contents, mode=mode)

    # Future test: check that pure-python and mypyc versions of monochromatic
    # give identical output for identical input?


if __name__ == "__main__":
    # Run tests, including shrinking and reporting any known failures.
    test_idempotent_any_syntatically_valid_python()

    # If Atheris is available, run coverage-guided fuzzing.
    # (if you want only bounded fuzzing, just use `pytest fuzz.py`)
    try:
        import sys

        import atheris
    except ImportError:
        pass
    else:
        test = test_idempotent_any_syntatically_valid_python
        atheris.Setup(
            sys.argv,
            test.hypothesis.fuzz_one_input,  # type: ignore[attr-defined]
        )
        atheris.Fuzz()
