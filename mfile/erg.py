# pylint: disable=C0301
"""
This modules implements the reader for the ERG binary file type generate by
IPG CarMaker.

"""

import re
import sys
from collections import OrderedDict
import numpy as np
import pandas as pd
import datetime

from asammdf import Signal, MDF
from asammdf import __version__ as asammdf_version
from asammdf.blocks.v4_blocks import ChannelConversion


PY_VERSION = sys.version_info[0]

SPACES = r"[ \t]"

SEEK_START = 0
SEEK_REL = 1
SEEK_END = 2

CONVERTER = {
    "Float": "f4",
    "Double": "f8",
    "LongLong": "i8",
    "ULongLong": "u8",
    "Long": "i4",
    "ULong": "u4",
    "Int": "i4",
    "UInt": "u4",
    "Short": "i2",
    "UShort": "u2",
    "Char": "i1",
    "UChar": "u1",
    "1 Bytes": "S1",
    "2 Bytes": "S2",
    "3 Bytes": "S3",
    "4 Bytes": "S4",
    "5 Bytes": "S5",
    "6 Bytes": "S6",
    "7 Bytes": "S7",
}

SIZER = {
    "Float": 4,
    "Double": 8,
    "LongLong": 8,
    "ULongLong": 8,
    "Long": 4,
    "ULong": 4,
    "Int": 4,
    "UInt": 4,
    "Short": 2,
    "UShort": 2,
    "Char": 1,
    "UChar": 1,
    "1 Bytes": 1,
    "2 Bytes": 2,
    "3 Bytes": 3,
    "4 Bytes": 4,
    "5 Bytes": 5,
    "6 Bytes": 6,
    "7 Bytes": 7,
}


__all__ = [
    "ERG",
]


class ERGSignal(object):
    """
    This helper class is used to organize the signals read from the ERG file.

    Parameters
    ----------
    name : string
        signal name
    data_type : string
        data type description
    unit : string
    factor : float
        factor used for liniar conversion
    offset : float
        offset used for liniar conversion

    Attributes
    ----------
    name : string
        signal name
    data_type : string
        data type description
    unit : string
    numpy_dtype : string
        numpy data type description
    byte_size : int
        number of bytes of a signal sample
    factor : float
        factor used for liniar conversion
    offset : float
        offset used for liniar conversion
    data : numpy.array
        signal samples

    """

    def __init__(self, name, data_type, unit=None, factor=None, offset=None):

        self.name = name.decode("utf-8") if isinstance(name, bytes) else name
        self.data_type = data_type
        self.numpy_dtype = CONVERTER[data_type]
        self.byte_size = SIZER[data_type]
        self.unit = unit if unit else ""
        self.factor = factor
        self.offset = offset
        self.data = None

    def __str__(self):
        out = []
        out.append("Name = {}".format(self.name))
        out.append("\tData_type = {}".format(self.numpy_dtype))
        return "\n".join(out)


class ERG(object):
    """
    This class implements a reader for the ERG binary file type. ERG files are
    generate by the CarMaker tool.

    A CarMaker measurement is split into two files: an information file (.info)
    that holds information regarding the ERG version, CarMaker version,
    an signal metadata, and the binary file that holds the measurement samples.

    Parameters
    ----------
    file_name : string
        path of the ERG file

    Attributes
    ----------
    signals : dict
        dictionary of ERGSignal objects read from the ERG file
    name : string
        ERG file name
    version : string
        ERG file version
    byteorder : string
        ERG byte order ::

            '<' means little Endian and '>' means big Endian

    """

    def __init__(self, file_name, empty=False):
        self.signals = OrderedDict()
        self.name = file_name
        self.version = None
        self.byteorder = "<"
        self.empty = empty
        self.start_time = None

        if not self.empty:
            self._read()

    def append(self, signals, signal_names, signal_units):
        """ appends new signals to the measurement

        Parameters
        ----------
        signals : list
            list of numpy array samples
        signal_names  : lsit
            list of signal names strings
        signal_units : list
            list of signal units strings

        """
        for sig, name, unit in zip(signals, signal_names, signal_units):
            self.signals[name] = ERGSignal(name, sig.dtype, unit)
            self.signals[name].data = sig

    def save(self):
        """ not implemented """
        pass

    def _read(self):
        with open(str(self.name) + ".info") as info_file:
            info = info_file.read()

        # search for byteorder
        pattern = r"\SPACES*File\.ByteOrder\SPACES*=\SPACES*(?P<byte_order>.+)".replace(
            r"\SPACES", SPACES
        )
        byte_order = re.search(pattern, info).group("byte_order").strip()
        self.byteorder = "<" if byte_order == "LittleEndian" else ">"

        # search for start time
        pattern = r"\SPACES*File\.DateInSeconds\SPACES*=\SPACES*(?P<start_time>.+)".replace(
            r"\SPACES", SPACES
        )
        start_time = int(re.search(pattern, info).group("start_time").strip())
        self.start_time = datetime.datetime.fromtimestamp(start_time)

        # search for signals
        pattern = r"(?P<sig_def>\SPACES*File\.At\.[0-9]+\.Name(.+(\n|$))+)".replace(
            r"\SPACES", SPACES
        )
        for match in re.finditer(pattern, info):
            definition = match.group("sig_def")
            name = re.search(
                r"\SPACES*File\.At\.[0-9]+\.Name\SPACES*=\SPACES*(?P<name>.+)\SPACES*".replace(
                    r"\SPACES", SPACES
                ),
                definition,
            ).group("name")
            data_type = re.search(
                r"\SPACES*File\.At\.[0-9]+\.Type\SPACES*=\SPACES*(?P<data_type>.+)\SPACES*".replace(
                    r"\SPACES", SPACES
                ),
                definition,
            ).group("data_type")

            unit = re.search(
                r"\SPACES*\"?Quantity\.(?!\.Unit).+\.Unit\"?\SPACES*=\SPACES*(?P<unit>.+)\SPACES*".replace(
                    r"\SPACES", SPACES
                ),
                definition,
            )
            if unit:
                unit = unit.group("unit")

            factor = re.search(
                r"\SPACES*\"?Quantity\.(?!\.Factor).+\.Factor\"?\SPACES*=\SPACES*(?P<factor>.+)\SPACES*".replace(
                    r"\SPACES", SPACES
                ),
                definition,
            )
            if factor:
                factor = factor.group("data_type")

            offset = re.search(
                r"\SPACES*\"?Quantity\.(?!\.Offset).+\.Offset\"?\SPACES*=\SPACES*(?P<offset>.+)\SPACES*".replace(
                    r"\SPACES", SPACES
                ),
                definition,
            )
            if offset:
                offset = offset.group("offset")

            self.signals[name] = ERGSignal(name, data_type, unit, factor, offset,)

        if PY_VERSION == 2:
            data_types = np.dtype(
                [(s.name.encode("utf-8"), s.numpy_dtype) for s in self.signals.values()]
            )
        elif PY_VERSION == 3:
            data_types = np.dtype(
                [(s.name, s.numpy_dtype) for s in self.signals.values()]
            )

        with open(self.name, "rb") as erg_file:
            data = erg_file.read()[16:]

        data = np.core.records.fromstring(
            data, dtype=data_types, byteorder=self.byteorder,
        )

        for signal in self.signals.values():
            signal.data = data[signal.name]

    def export_mdf(self):
        mdf = MDF()
        mdf.header.start_time = self.start_time
        sigs = []
        cntr = 0
        for name in self.signals:
            if name == "Time":
                continue
            sigs.append(self.get(name, True))
            if sigs[-1].samples.dtype.kind == "S":
                sigs[-1].encoding = "utf-8"
            cntr += 1
            if cntr == 200:
                cntr = 0
                mdf.append(sigs, common_timebase=True)
                sigs = []
        if sigs:
            mdf.append(sigs, common_timebase=True)
        return mdf

    def to_pd(self):
        df = pd.DataFrame()
        for key in self.signals:
            df[str(key + '_' + self.get(key).unit)] = np.array(self.get(key).samples)
        return df

    def get(self, name, raw=False):
        """
        Gets the signals based on the name

        Parameters
        ----------
        name : string
            signal name

        Returns
        -------
        signal : asammdf.Signal
            Signal object

        Raises
        ------
        KeyError : if the signal is not found

        """
        if name not in self.signals:
            raise Exception('Channel "{}" not found in "{}"'.format(name, self.name,))

        signal = self.signals[name]
        samples = signal.data
        if "Time" in self.signals:
            timestamps = self.signals["Time"].data
        else:
            timestamps = np.array([0.001 * i for i in range(len(samples))])
        if not raw:
            conversion = None
            if signal.factor is not None:
                samples = samples * signal.factor + signal.offset
        else:
            if signal.factor is not None:
                conversion = ChannelConversion(a=signal.factor, b=signal.offset,)
            else:
                conversion = None
                raw = False

        if samples.dtype.kind == "S":
            encoding = "utf-8"
        else:
            encoding = None
        return Signal(
            samples=samples,
            timestamps=timestamps,
            name=name,
            unit=self.signals[name].unit,
            conversion=conversion,
            raw=raw,
            encoding=encoding,
        )

    def close(self):
        pass


if __name__ == "__main__":
    pass
