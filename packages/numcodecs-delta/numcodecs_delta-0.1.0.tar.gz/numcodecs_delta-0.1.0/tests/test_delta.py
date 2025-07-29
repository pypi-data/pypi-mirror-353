import numcodecs
import numcodecs.registry
import numpy as np


def test_from_config():
    codec = numcodecs.registry.get_codec(dict(id="delta.binary"))
    assert codec.__class__.__name__ == "BinaryDeltaCodec"
    assert codec.__class__.__module__ == "numcodecs_delta"


def check_roundtrip(data: np.ndarray):
    codec = numcodecs.registry.get_codec(dict(id="delta.binary"))

    encoded = codec.encode(data)
    decoded = codec.decode(encoded)

    assert decoded.dtype == data.dtype
    assert decoded.shape == data.shape
    assert np.all(_as_bits(decoded) == _as_bits(data))


def test_roundtrip():
    check_roundtrip(np.zeros(tuple()))
    check_roundtrip(np.zeros((0,)))
    check_roundtrip(np.arange(1000).reshape(10, 10, 10))
    check_roundtrip(np.array([np.inf, -np.inf, np.nan, -np.nan, 0.0, -0.0]))
    check_roundtrip(
        np.array(
            [np.inf, -np.inf, np.nan, -np.nan, 0.0, -0.0],
            dtype=np.dtype(np.float64).newbyteorder("<"),
        )
    )
    check_roundtrip(
        np.array(
            [np.inf, -np.inf, np.nan, -np.nan, 0.0, -0.0],
            dtype=np.dtype(np.float64).newbyteorder(">"),
        )
    )


def _as_bits(a: np.ndarray) -> np.ndarray:
    return a.view(a.dtype.str.replace("f", "u").replace("i", "u"))
