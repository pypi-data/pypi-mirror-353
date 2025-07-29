"""
Delta codecs for the [`numcodecs`][numcodecs] buffer compression API.
"""

__all__ = ["BinaryDeltaCodec"]

from typing import Any, TypeVar

import numcodecs.compat
import numcodecs.registry
import numpy as np
from numcodecs.abc import Codec
from typing_extensions import Buffer  # MSPV 3.12

S = TypeVar("S", bound=tuple[int, ...])
""" Any array shape. """


class BinaryDeltaCodec(Codec):
    """
    Codec to encode the data as the binary difference between adjacent values.

    The encoded data has the same data type as the input, but its bits
    represent the binary difference between values. If the input data is
    floating point, these difference values may have weird values that are of
    little use arithmetically. Despite this weird representation, this codec is
    able to losslessly reconstruct all values.

    It is recommended to only use lossless encodings after this codec.

    Please refer to the [`numcodecs.delta.Delta`][numcodecs.delta.Delta] codec
    for a delta codec that computes the difference in the data type as the
    input.
    """

    __slots__ = ()

    codec_id: str = "delta.binary"  # type: ignore

    def encode(self, buf: Buffer) -> Buffer:
        """Encode the data in `buf`.

        Parameters
        ----------
        buf : Buffer
            Data to be encoded. May be any object supporting the new-style
            buffer protocol.

        Returns
        -------
        enc : Buffer
            Encoded data. May be any object supporting the new-style buffer
            protocol.
        """

        a = numcodecs.compat.ensure_ndarray(buf)
        a_bits = _as_bits(a.flatten())

        a_bits_delta = a_bits.copy()
        a_bits_delta[1:] = np.diff(a_bits)

        a_delta = a_bits_delta.view(a.dtype).reshape(a.shape)

        return a_delta

    def decode(self, buf: Buffer, out: None | Buffer = None) -> Buffer:
        """
        Decode the data in `buf`.

        Parameters
        ----------
        buf : Buffer
            Encoded data. May be any object supporting the new-style buffer
            protocol.
        out : Buffer, optional
            Writeable buffer to store decoded data. N.B. if provided, this buffer must
            be exactly the right size to store the decoded data.

        Returns
        -------
        dec : Buffer
            Decoded data. May be any object supporting the new-style buffer
            protocol.
        """

        a_delta = numcodecs.compat.ensure_ndarray(buf)
        a_bits_delta = _as_bits(a_delta.flatten())

        # use explicit out to keep dtype byteorder
        a_bits = np.empty_like(a_bits_delta)
        np.cumsum(a_bits_delta, dtype=a_bits_delta.dtype, out=a_bits)

        a = a_bits.view(a_delta.dtype).reshape(a_delta.shape)

        return numcodecs.compat.ndarray_copy(a, out)  # type: ignore


numcodecs.registry.register_codec(BinaryDeltaCodec)


def _as_bits(a: np.ndarray[S, np.dtype[Any]], /) -> np.ndarray[S, np.dtype[Any]]:
    """
    Reinterprets the array `a` to its binary (unsigned integer) representation.

    Parameters
    ----------
    a : np.ndarray[S, np.dtype[Any]]
        The array to reinterpret as binary.

    Returns
    -------
    binary : np.ndarray[S, np.dtype[Any]]
        The binary representation of the array `a`.
    """

    return a.view(_dtype_bits(a.dtype))  # type: ignore


def _dtype_bits(dtype: np.dtype) -> np.dtype:
    """
    Converts the `dtype` to its binary (unsigned integer) representation.

    Parameters
    ----------
    dtype : np.dtype
        The dtype to convert.

    Returns
    -------
    binary : np.dtype
        The binary dtype with equivalent size and alignment but unsigned
        integer kind.
    """

    return np.dtype(dtype.str.replace("f", "u").replace("i", "u"))
