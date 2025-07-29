"""
DATAQ DI-2008 Interface
Adapted from original DATAQ Instruments Python Interface under the MIT License

Provides an interface for configuring and reading from DI-2008 Data Acquisition Devices (DAQs)

This file is part of DI2008_Python, https://github.com/Computational-Mechanics-Materials-Lab/DI-2008-Driver

MIT License
"""

import time
import serial
import serial.tools.list_ports

import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
import json

# Typing
from typing import Callable, TypeAlias, BinaryIO, TextIO, Any, Final

import weakref

# Enumerations for DAQ Settings
from .di2008_layout_settings import (
    DI2008Layout,
    DI2008TCType,
    DI2008ADCRange,
    DI2008Channels,
    _DI2008AllChannels,
    DI2008AllChannels,
    DI2008DigitalChannel,
    DI2008UseDigital,
    DI2008ScanRateSettings,
    DI2008FilterModes,
    DI2008PSOption,
    DI2008PSSettings,
)

DI2008ChannelsAlias: TypeAlias = DI2008Channels | DI2008DigitalChannel


class DI2008Port:
    """
    Structure Class
    Stores a single port with:
    channel number (channel: int)
    port layout (layout: int)
    type of connected device (connected_type: int)
    sclaing function (rescalar: Callable[[int], float])
    """

    def __init__(
        self,
        channel: DI2008Channels | DI2008DigitalChannel,
        layout: int,
        connected_type: int,
        rescalar: Callable[[int], float],
    ) -> None:
        """
        DI2008Port Init Signature:
        channel: int
        layout: int
        connected_type: int
        rescalar: Callable[[int], float]
        """
        self.channel: int = channel
        self.layout: int = layout
        self.connected_type: int = connected_type
        self.rescalar: Callable[[int], float] = rescalar


class SerialConnectionWrapper:
    """
    Wraps around a pyserial serial connection
    Automatically encodes and decodes communication.
    Stores:
    the connected DAQ's hardware map location (location: str)
    the actual connection (conn: serial.Serial)
    """

    def __init__(self, location: str, connection: serial.Serial) -> None:
        """
        SerialConnectionWrapper Signature:
        location: str
        connection: serial.Serial
        """
        self.location: str = location
        self.conn: serial.Serial = connection
        self.serial_num: int | None = None
        self.ports: list[DI2008Port] | None = None

    def send_command(self, command: str) -> None:
        """Send a command without echoing"""
        self._send_command(command)

    def echo(self, command: str) -> str | None:
        """Send a command and echo the result"""
        return self._send_command(command)

    def close(self) -> None:
        """Close the serial connection"""
        self.conn.close()

    def _send_command(self, command: str) -> str | None:
        """Internal method for formatting, sending, and receiving DI2008 communication"""
        formatted_command: str = f"{command}\r"
        self.conn.write(formatted_command.encode())
        time.sleep(0.1)
        final: str = ""
        # If the `start` command was sent, the DI-2008 will immediately start sending data, which this method should not handle
        if command == "start":
            return None
        # If we haven't started, clear the buffer and potentially return it
        else:
            while self.conn.in_waiting > 0:
                res_b: bytes = self.conn.readline()
                res: str = res_b.decode()
                # Replace newlines and non-printable characters
                res = res.replace("\n", "")
                res = res.replace("\r", "")
                res = res.replace(chr(0), "")
                final += res

            return final


class DI2008:
    """
    DI2008 Python Interface
    When provided input parameters, automatically contacts and configures all requested DI-2008s
    Can then be used to read from connected DAQs
    """

    def __init__(
        self,
        daq_layout_dict: dict[Any, Any],
        baud_rate: int = 115200,
        timeout: float = 0.0,
        target_hwid: str = "USB VID:PID=0683",
    ) -> None:
        """
        DI2008 Signature:
        daq_layout_dict: dict (Dictionary of DAQ Serial Nums to settings. See README for more details)
        baud_rate: int (default 115200)
        timeout: float (default 0.0)
        Hardware ID for DI-2008 (target_hwid: str, default "USB VID:PID=0683")
        """
        self.daq_layout_dict: dict[Any, Any] = daq_layout_dict
        self.baud_rate: int = baud_rate
        self.timeout: float = timeout
        self.TARGET_HWID: str = target_hwid
        self.serial_connections: list[SerialConnectionWrapper] = []
        self.tc_rescalars: dict[DI2008TCType, Callable[[int], float]] = {
            DI2008TCType.B: self._tc_b,
            DI2008TCType.E: self._tc_e,
            DI2008TCType.J: self._tc_j,
            DI2008TCType.K: self._tc_k,
            DI2008TCType.N: self._tc_n,
            DI2008TCType.R: self._tc_r_s,
            DI2008TCType.S: self._tc_r_s,
            DI2008TCType.T: self._tc_t,
        }

        weakref.finalize(self, self._cleanup)

        # Locate selected DI-2008s
        self.find_di2008s()
        # Set selected DI-2008s
        self.configure_di2008s()
        # Begin scanning on slected DI-2008s
        self.start_di2008s()

    def _cleanup(self) -> None:
        scw: SerialConnectionWrapper
        for scw in self.serial_connections:
            scw.close()

    def find_di2008s(self) -> None:
        """
        Given the list of DI-2008 serial nums in the input dict, find these and generate their correct configurations
        """
        port: serial.tools.list_ports_linux.SysFS
        for port in serial.tools.list_ports.comports():
            # Find All DI-2008s by hardware ID
            if self.TARGET_HWID in port.hwid:
                assert port.location is not None
                scw: SerialConnectionWrapper = SerialConnectionWrapper(
                    port.location,
                    serial.Serial(port.device, self.baud_rate, timeout=self.timeout),
                )
                # Stop DI-2008s first, as they are found
                scw.send_command("stop")

                # Getting Serial numbers is not ideal. Must use string echo interface
                serial_num_str: str | None = scw.echo("info 6")
                if serial_num_str is not None:
                    serial_num: str
                    try:
                        # Split off the command sent
                        serial_num = serial_num_str.split("info 6 ")[1]
                    except IndexError as e:
                        raise IndexError(
                            f"Could not get serial number for this DI-2008, with error {e}"
                        ) from e

                    # If you got the serial num, parse the string and store it in hex
                    serial_num = serial_num[0:8]
                    scw.serial_num = int(serial_num, base=16)
                else:
                    # If there is not Serial Num, likely you'll have to unplug/replug devices and try again
                    raise RuntimeError(
                        "COULD NOT GET DAQ SERIAL NUM! UNPLUG/REPLUG DAQS AND TRY AGAIN!!!"
                    )

                # Now, we check if the serial number was requested and, if so, create the configuration and make the connection.

                layout_input: dict[Any, Any] | None
                if layout_input := self.daq_layout_dict.get(scw.serial_num):
                    # Use the input data to get the configuration and save the connection.
                    scw_ports: list[DI2008Port] = self.get_scw_port_configuration(
                        layout_input
                    )
                    assert scw_ports is not None
                    scw.ports = scw_ports
                    self.serial_connections.append(scw)

                else:
                    # Close the connection if not requested
                    scw.close()

        # If not DAQs were connected to
        if len(self.serial_connections) == 0:
            raise Exception("No DAQs were found!")

    def configure_di2008s(self) -> None:
        """
        Once the configuration for the DI-2008s has been created, input them
        """
        scw: SerialConnectionWrapper
        for scw in self.serial_connections:
            # Get the layout for this specific connection
            individual_layout_dict: dict[Any, Any] = self.daq_layout_dict[
                scw.serial_num
            ]

            # Check for a given ps value. If not, set to 0 (16 bytes)
            ps_value: DI2008PSSettings | None
            if ps_value := individual_layout_dict.get(DI2008PSOption):
                scw.send_command(f"ps {ps_value}")

            else:
                scw.send_command(f"ps {DI2008PSSettings.BYTES16}")

            # Check for an srate value. If not, set to 4
            srate_value: int | None
            if srate_value := individual_layout_dict.get(DI2008ScanRateSettings.SRATE):
                if not (4 <= srate_value <= 2232):
                    raise RuntimeError(
                        f"srate value for DI-2008 with Serial Number {scw.serial_num} was not between 4 and 2232, but was instead {srate_value}"
                    )
                else:
                    scw.send_command(f"srate {srate_value}")

            else:
                scw.send_command("srate 4")

            # Check for a decimation value, if not, set to 1
            dec_value: int | None
            if dec_value := individual_layout_dict.get(DI2008ScanRateSettings.DEC):
                if not (1 <= dec_value <= 32767):
                    raise RuntimeError(
                        f"dec value for DI-2008 with Serial Number {scw.serial_num} was not between 1 and 32767, but was instead {srate_value}"
                    )
                else:
                    scw.send_command(f"dec {dec_value}")

            else:
                scw.send_command("dec 1")

            # See if filter settings are given
            channel_filter_dict: dict[DI2008ChannelsAlias, DI2008FilterModes] | None
            if channel_filter_dict := individual_layout_dict.get(
                DI2008ScanRateSettings.FILTER
            ):
                key: DI2008ChannelsAlias | _DI2008AllChannels
                val: DI2008FilterModes
                for key, val in channel_filter_dict.items():
                    if key is DI2008AllChannels:
                        scw.send_command(f"filter * {val.value}")

                    else:
                        scw.send_command(f"filter {key} {val}")

            # Finally, do the slist settings generated in the last step to this DAQ.
            assert scw.ports is not None
            port: DI2008Port
            for port in scw.ports:
                scw.send_command(f"slist {port.channel} {port.layout}")

    def start_di2008s(self) -> None:
        """Perform the synchronized start for the DI-2008s. See the DI-2008 Protocl for details"""

        # If More than 1 DAQ
        if len(self.serial_connections) > 1:
            # Synchronized Start
            # As taken from the docs (top of page 5)
            syncget_0_vals: list[int] = []
            scw: SerialConnectionWrapper
            for scw in self.serial_connections:
                syncget_0_resp: str | None = scw.echo("syncget 0")
                assert syncget_0_resp is not None
                syncget_0: str | int = syncget_0_resp.split(" ")[-1]
                syncget_0 = int(syncget_0)
                syncget_0_vals.append(syncget_0)

            syncget_0_c: int = sum(syncget_0_vals) // len(syncget_0_vals)
            syncget_3_vals: list[int] = []
            for scw in self.serial_connections:
                syncget_3_resp: str | None = scw.echo("syncget 3")
                assert syncget_3_resp is not None
                syncget_3: str | int = syncget_3_resp.split(" ")[-1]
                syncget_3 = int(syncget_3)
                syncget_3_vals.append(syncget_3)

            s3v0: int = syncget_3_vals[0]
            if any(s != s3v0 for s in syncget_3_vals) or s3v0 != syncget_0_c:
                for scw in self.serial_connections:
                    scw.send_command(f"syncset {syncget_0_c}")

                time.sleep(1.0)

            syncget_f_resp: str | None = self.serial_connections[0].echo("syncget 2")
            assert syncget_f_resp is not None
            syncget_f: int | str = syncget_f_resp.split(" ")[-1]
            syncget_f = int(syncget_f)
            syncget_g: int = syncget_f ^ 0x0400
            if syncget_g == 0:
                syncget_g = 1

            for scw in self.serial_connections:
                scw.send_command(f"syncstart {syncget_g}")

        # Simple start if there's only 1 of them
        else:
            for scw in self.serial_connections:
                scw.send_command("start")

    def get_scw_port_configuration(
        self, layout_input: dict[Any, Any]
    ) -> list[DI2008Port]:
        """
        Given the dict of a desired layout, configure it into the needed values in order
        """
        ports: list[DI2008Port] = []
        layout: DI2008Layout | tuple[DI2008Layout, DI2008TCType | DI2008ADCRange] | None
        channel: DI2008Channels
        # If the same setting is used for all channels
        if layout := layout_input.get(DI2008AllChannels):
            for channel in DI2008Channels:
                ports.append(self.get_di2008_port_layout(channel, layout))
        # If there are different settings given for any channel
        else:
            for channel in DI2008Channels:
                layout = layout_input.get(channel, DI2008Layout.IGNORE)
                assert layout is not None
                ports.append(self.get_di2008_port_layout(channel, layout))

        # See if this DAQ uses the digital channel:
        if layout_input.get(DI2008UseDigital):
            ports.append(
                DI2008Port(
                    DI2008DigitalChannel.DI,
                    DI2008Layout.DI,
                    DI2008Layout.DI,
                    (lambda x: x),
                )
            )

        return ports

    def get_di2008_port_layout(
        self,
        channel: DI2008Channels,
        layout: DI2008Layout | tuple[DI2008Layout, DI2008TCType | DI2008ADCRange],
    ) -> DI2008Port:
        """
        Given some layout and the channel, determine which device is connected, get the correct rescaling factor, and return the port
        """
        connected_type: DI2008Layout
        rescalar: Callable[[int], float]
        final_layout: int

        # The TC and ADC needs 2 values, so it's a 2-tuple. The IGNORE version is not
        if isinstance(layout, tuple):
            if len(layout) != 2:
                raise Exception("DAQ Layout must be 1 enum or tuple of 2!")
            connected_type = layout[0]
        else:
            connected_type = layout

        # For Thermocouple, get the right rescalar and set the layout
        if connected_type is DI2008Layout.TC:
            assert isinstance(layout, tuple)
            assert isinstance(layout[1], DI2008TCType)
            tc_type: DI2008TCType = layout[1]
            final_layout = (DI2008Layout.TC | tc_type) | channel
            rescalar = self.tc_rescalars[tc_type]

        # For ADC, use the acual value to rescale it
        elif connected_type is DI2008Layout.ADC:
            assert isinstance(layout, tuple)
            assert isinstance(layout[1], DI2008ADCRange)
            adc_range: DI2008ADCRange = layout[1]
            final_layout = adc_range.value[0] | channel
            rescalar = lambda x: adc_range.value[1] * (x / 32768.0)

        # Instead of truly ignoring, treat as an empty B-type Thermocouple. Won't be read from, whether or not something is connected
        elif connected_type is DI2008Layout.IGNORE:
            final_layout = DI2008Layout.TC | channel
            rescalar = lambda x: x

        else:
            raise Exception("Not a valid layout!")

        return DI2008Port(channel, final_layout, connected_type, rescalar)

    @classmethod
    def from_config(cls, config: str | dict[Any, Any]):
        """
        Given some configuration file or dictionary, return a configured DI2008 object
        """
        translated_keys: Final[dict[str, Any]] = {
            "di2008channelsch1": DI2008Channels.CH1,
            "di2008channelsch2": DI2008Channels.CH2,
            "di2008channelsch3": DI2008Channels.CH3,
            "di2008channelsch4": DI2008Channels.CH4,
            "di2008channelsch5": DI2008Channels.CH5,
            "di2008channelsch6": DI2008Channels.CH6,
            "di2008channelsch7": DI2008Channels.CH7,
            "di2008channelsch8": DI2008Channels.CH8,
            "di2008allchannels": DI2008AllChannels,
            "di2008usedigital": DI2008UseDigital,
            "di2008scanratesettingssrate": DI2008ScanRateSettings.SRATE,
            "di2008scanratesettingsdec": DI2008ScanRateSettings.DEC,
            "di2008scanratesettingsfilter": DI2008ScanRateSettings.FILTER,
            "di2008psoption": DI2008PSOption,
        }

        translated_vals: Final[dict[str, Any]] = {
            "di2008layouttc": DI2008Layout.TC,
            "di2008layoutdi": DI2008Layout.DI,
            "di2008layoutignore": DI2008Layout.IGNORE,
            "di2008layoutadc": DI2008Layout.ADC,
            "di2008tctypeb": DI2008TCType.B,
            "di2008tctypee": DI2008TCType.E,
            "di2008tctypej": DI2008TCType.J,
            "di2008tctypek": DI2008TCType.K,
            "di2008tctypen": DI2008TCType.N,
            "di2008tctyper": DI2008TCType.R,
            "di2008tctypes": DI2008TCType.S,
            "di2008tctypet": DI2008TCType.T,
            "di2008adcrangemv10": DI2008ADCRange.mV10,
            "di2008adcrangemv25": DI2008ADCRange.mV25,
            "di2008adcrangemv50": DI2008ADCRange.mV50,
            "di2008adcrangemv100": DI2008ADCRange.mV100,
            "di2008adcrangemv250": DI2008ADCRange.mV250,
            "di2008adcrangemv500": DI2008ADCRange.mV500,
            "di2008adcrangev1": DI2008ADCRange.V1,
            "di2008adcrangev2_5": DI2008ADCRange.V2_5,
            "di2008adcrangev5": DI2008ADCRange.V5,
            "di2008adcrangev10": DI2008ADCRange.V10,
            "di2008adcrangev25": DI2008ADCRange.V25,
            "di2008adcrangev50": DI2008ADCRange.V50,
            "di2008filtermodeslast_point": DI2008FilterModes.LAST_POINT,
            "di2008filtermodesaverage": DI2008FilterModes.AVERAGE,
            "di2008filtermodesmaximum": DI2008FilterModes.MAXIMUM,
            "di2008filtermodesminimum": DI2008FilterModes.MINIMUM,
            "di2008pssettingsbytes16": DI2008PSSettings.BYTES16,
            "di2008pssettingsbytes32": DI2008PSSettings.BYTES32,
            "di2008pssettingsbytes64": DI2008PSSettings.BYTES64,
            "di2008pssettingsbytes128": DI2008PSSettings.BYTES128,
        }

        formatted_config: dict[str, dict[Any, Any]]
        if isinstance(config, str):
            # Check for json or toml file path
            try:
                formatted_config = cls._config_from_toml(config)
            except tomllib.TOMLDecodeError:
                try:
                    formatted_config = cls._config_from_json(config)
                except json.decoder.JSONDecodeError:
                    raise ValueError()

        else:
            # Just treat the input dict as if it came from a string otherwise
            formatted_config = config

        final_config: dict[int, dict[Any, Any]] = {}
        initial_sns: dict[str, str] = {str(k): str(k) for k in formatted_config.keys()}
        final_sns: dict[str, int] = {}

        k_k: str
        k_v: str | int
        for k_k, k_v in initial_sns.items():
            if not isinstance(k_v, int):
                new_k_v: int
                try:
                    new_k_v = int(k_v)
                except ValueError:
                    try:
                        new_k_v = int(k_v, base=16)
                    except ValueError as e:
                        raise ValueError(f"invalid SN for DAQ: {k_v}") from e

            final_sns[k_k] = new_k_v

        k: str
        v: dict[Any, Any]
        for k, v in formatted_config.items():
            final_config[final_sns[k]] = {}
            _k: str
            _v: int | float | bool | list[str] | str
            for _k, _v in v.items():
                new_k: Any = translated_keys[cls._format_input_k_v(_k)]

                if isinstance(_v, int | float | bool):
                    final_config[final_sns[k]][new_k] = _v

                elif isinstance(_v, list):
                    assert len(_v) == 2
                    final_config[final_sns[k]][new_k] = (
                        translated_vals[cls._format_input_k_v(_v[0])],
                        translated_vals[cls._format_input_k_v(_v[1])],
                    )

                elif isinstance(_v, dict):
                    # Should only ever be 1 layer deep
                    new_v: dict[Any, Any] = {}
                    filter_key: str
                    filter_val: str
                    for filter_key, filter_val in _v.items():
                        new_v[translated_keys[cls._format_input_k_v(filter_key)]] = (
                            translated_vals[cls._format_input_k_v(filter_val)]
                        )

                else:
                    final_config[final_sns[k]][new_k] = translated_vals[
                        cls._format_input_k_v(_v)
                    ]

        return cls(final_config)

    @staticmethod
    def _config_from_toml(config: str) -> dict[Any, Any]:
        """
        Read and return a .toml file. Error handling within parent method
        """
        fp: BinaryIO
        with open(config, "rb") as fp:
            return tomllib.load(fp)

    @staticmethod
    def _config_from_json(config: str) -> dict[Any, Any]:
        """
        Read and return a .json file. Error handling within parent method
        """
        fp: TextIO
        with open(config, "r") as fp:
            ret: dict[Any, Any] = json.load(fp)
            assert isinstance(ret, dict)
            return ret

    @staticmethod
    def _format_input_k_v(i: str) -> str:
        """
        Strip out all formatting characters and spaces, lowercase all. Used only for these dict translations in reading an input dict
        """
        return (
            i.lower()
            .replace(".", "")
            .replace("_", "")
            .replace("-", "")
            .replace(" ", "")
            .strip()
        )

    def read_daqs(self) -> dict[int, dict[DI2008ChannelsAlias, float | int]]:
        all_res: dict[int, dict[DI2008ChannelsAlias, float | int]] = {}
        scw: SerialConnectionWrapper
        for scw in self.serial_connections:
            assert scw.serial_num is not None
            all_res[scw.serial_num] = {}

            port: DI2008Port
            assert scw.ports is not None
            for port in scw.ports:
                while scw.conn.in_waiting < 2:
                    pass

                raw_byte: bytes = bytes(scw.conn.read(2))

                formatted_byte: int
                # Ignore ports marked as such
                if port.connected_type is DI2008Layout.IGNORE:
                    continue

                # Digital Port (must zero-out upper bits
                elif port.connected_type is DI2008Layout.DI:
                    formatted_byte = (
                        int.from_bytes(raw_byte, byteorder="little", signed=True) & 0x7F
                    )

                # All other types
                else:
                    formatted_byte = int.from_bytes(
                        raw_byte, byteorder="little", signed=True
                    )

                # Rescale as necessary
                final_res: float = port.rescalar(formatted_byte)
                assert isinstance(port.channel, DI2008ChannelsAlias)
                all_res[scw.serial_num][port.channel] = final_res

        return all_res

    def _tc_j(self, x: int) -> float:
        """Rescalar for J-Type Thermocouple"""
        return (0.021515 * x) + 495.0

    def _tc_k(self, x: int) -> float:
        """Rescalar for K-Type Thermocouple"""
        return (0.023987 * x) + 586.0

    def _tc_t(self, x: int) -> float:
        """Rescalar for T-Type Thermocouple"""
        return (0.009155 * x) + 100.0

    def _tc_b(self, x: int) -> float:
        """Rescalar for B-Type Thermocouple"""
        return (0.023956 * x) + 1035.0

    def _tc_r_s(self, x: int) -> float:
        """Rescalar for R-Type and S-Type Thermocouple"""
        return (0.02774 * x) + 859.0

    def _tc_e(self, x: int) -> float:
        """Rescalar for E-Type Thermocouple"""
        return (0.018311 * x) + 400.0

    def _tc_n(self, x: int) -> float:
        """Rescalar for N-Type Thermocouple"""
        return (0.022888 * x) + 550.0
