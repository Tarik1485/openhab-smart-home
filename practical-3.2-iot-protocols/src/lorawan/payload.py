"""Educational LoRaWAN payload simulation for agricultural sensors.

This module encodes five soil-moisture readings and weather/water/GPS data
into a compact binary payload. It does not implement real LoRaWAN radio,
OTAA cryptography, or TTN connectivity.
"""
import struct
from dataclasses import dataclass


@dataclass
class FarmReading:
    soil_moisture: tuple[int, int, int, int, int]
    temperature_c: float
    humidity_pct: float
    pressure_hpa: float
    wind_mps: float
    tank_level_pct: int
    latitude: float
    longitude: float
    battery_mv: int


# Format:
# 5 x uint8 soil %, int16 temperature in centi-degrees,
# uint8 humidity %, uint16 pressure in tenths of hPa,
# uint8 wind in tenths of m/s, uint8 tank %, int32 lat/lon in 1e-5 degrees,
# uint16 battery mV.
PAYLOAD_FORMAT = ">5BhBHB BiiH".replace(" ", "")
PAYLOAD_SIZE = struct.calcsize(PAYLOAD_FORMAT)


def encode_payload(reading: FarmReading) -> bytes:
    """Encode a sensor reading into a fixed-size binary payload."""
    if len(reading.soil_moisture) != 5:
        raise ValueError("Exactly five soil-moisture readings are required")
    if any(not 0 <= value <= 100 for value in reading.soil_moisture):
        raise ValueError("Soil moisture must be between 0 and 100 percent")
    if not 0 <= reading.humidity_pct <= 100:
        raise ValueError("Humidity must be between 0 and 100 percent")
    if not 0 <= reading.tank_level_pct <= 100:
        raise ValueError("Tank level must be between 0 and 100 percent")
    if not -90 <= reading.latitude <= 90:
        raise ValueError("Latitude must be between -90 and 90")
    if not -180 <= reading.longitude <= 180:
        raise ValueError("Longitude must be between -180 and 180")

    return struct.pack(
        PAYLOAD_FORMAT,
        *reading.soil_moisture,
        round(reading.temperature_c * 100),
        round(reading.humidity_pct),
        round(reading.pressure_hpa * 10),
        round(reading.wind_mps * 10),
        reading.tank_level_pct,
        round(reading.latitude * 100000),
        round(reading.longitude * 100000),
        reading.battery_mv,
    )


def decode_payload(payload: bytes) -> FarmReading:
    """Decode a payload produced by encode_payload."""
    if len(payload) != PAYLOAD_SIZE:
        raise ValueError(f"Expected {PAYLOAD_SIZE} bytes, got {len(payload)}")
    values = struct.unpack(PAYLOAD_FORMAT, payload)
    return FarmReading(
        soil_moisture=tuple(values[:5]),
        temperature_c=values[5] / 100,
        humidity_pct=float(values[6]),
        pressure_hpa=values[7] / 10,
        wind_mps=values[8] / 10,
        tank_level_pct=values[9],
        latitude=values[10] / 100000,
        longitude=values[11] / 100000,
        battery_mv=values[12],
    )


if __name__ == "__main__":
    sample = FarmReading(
        soil_moisture=(42, 39, 45, 51, 47),
        temperature_c=23.75,
        humidity_pct=61,
        pressure_hpa=1013.2,
        wind_mps=3.4,
        tank_level_pct=76,
        latitude=50.4501,
        longitude=30.5234,
        battery_mv=3850,
    )
    packet = encode_payload(sample)
    print(f"Payload size: {len(packet)} bytes")
    print(f"Decoded: {decode_payload(packet)}")
