from typing import Dict, Tuple, Optional, Iterable
from pcf8574_interface import PCF8574Interface, IoPortType, PCF8574InterfaceApi


class PCF8574Pool:
    def __init__(self):
        self._ports: Dict[Tuple[int, int], PCF8574Interface] = {}

    def add_port(self, port: PCF8574Interface) -> None:
        key = (port.bus_no, port.address)
        self._ports[key] = port

    def add_ports(self, ports: Iterable[PCF8574Interface]) -> None:
        for port in ports:
            self.add_port(port)

    def get_port(self, bus: int, address: int) -> Optional[PCF8574Interface]:
        return self._ports.get((bus, address))

    def get_all_ports(self) -> Iterable[PCF8574Interface]:
        return self._ports.values()

    def get_ports_by_type(self, port_type: IoPortType) -> Iterable[PCF8574Interface]:
        return (port for port in self._ports.values() if port.port_type == port_type)

    def remove_port(self, bus: int, address: int) -> None:
        self._ports.pop((bus, address), None)

    def set_api(self, api: PCF8574InterfaceApi) -> None:
        """
        Set the API for all ports in the pool.
        """
        for port in self._ports.values():
            port.api = api
