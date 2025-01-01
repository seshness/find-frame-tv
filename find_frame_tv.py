import socket
import re
import requests
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from urllib.parse import urlparse

SIMPLE_SERVICE_DISCOVERY_PROTOCOL_ADDRESS = "239.255.255.250"
SIMPLE_SERVICE_DISCOVERY_PROTOCOL_PORT = 1900


@dataclass
class TVInfo:
    ip: str
    friendly_name: str
    manufacturer: str
    serial_number: str


def find_upnp_devices(timeout: int = 3) -> set[str]:
    # Finds all UPnP devices and returns their location strings.
    # Increase the timeout value if you're not seeing a device you expect.
    locations = set()
    location_regex = re.compile("location:[ ]*(.+)\r\n", re.IGNORECASE)
    ssdp_discover = "\r\n".join(
        [
            "M-SEARCH * HTTP/1.1",
            "HOST: 239.255.255.250:1900",
            'MAN: "ssdp:discover"',
            "MX: 1",
            "ST: ssdp:all",
            "",
            "",  # We need 2 \r\n terminators to end the message.
        ]
    )

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(
        ssdp_discover.encode("ASCII"),
        (
            SIMPLE_SERVICE_DISCOVERY_PROTOCOL_ADDRESS,
            SIMPLE_SERVICE_DISCOVERY_PROTOCOL_PORT,
        ),
    )
    sock.settimeout(3)
    try:
        while True:
            data, addr = sock.recvfrom(1024)
            location_result = location_regex.search(data.decode("ASCII"))
            if location_result and location_result.group(1) not in locations:
                locations.add(location_result.group(1))
    except socket.error:
        sock.close()

    return locations


def parse_xml(xml_data: str, device_ip: str) -> TVInfo | None:
    namespace = {"": "urn:schemas-upnp-org:device-1-0"}
    try:
        root = ET.fromstring(xml_data)

        friendly_name = root.find(".//friendlyName", namespace).text
        manufacturer = root.find(".//manufacturer", namespace).text
        serial_number = root.find(".//serialNumber", namespace).text

        return TVInfo(
            ip=device_ip,
            friendly_name=friendly_name,
            manufacturer=manufacturer,
            serial_number=serial_number,
        )
    except Exception:
        return None


def find_tvs(locations: set[str]) -> list[TVInfo]:
    tvs: list[TVInfo] = []
    locations_with_dmr = [l for l in locations if "/dmr" in l]
    for l in locations_with_dmr:
        try:
            r = requests.get(l)
            xml_data = r.text
            device_ip = urlparse(l).hostname
            tv_info = parse_xml(xml_data, device_ip)
            if tv_info is not None:
                tvs.append(tv_info)
        except Exception:
            continue
    return tvs


def main():
    locations = find_upnp_devices()
    tvs = find_tvs(locations=locations)
    for tv in tvs:
        print(tv)


if __name__ == "__main__":
    main()
