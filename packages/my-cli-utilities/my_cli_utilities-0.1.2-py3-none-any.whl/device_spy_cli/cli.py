# -*- coding: utf-8 -*-


import json
import fire
import logger
from my_cli_utilities_common.http_helpers import make_sync_request

BASE_URL = "https://device-spy-mthor.int.rclabenv.com"
HOSTS_ENDPOINT = BASE_URL + "/api/v1/hosts"
ALL_DEVICES_ENDPOINT = BASE_URL + "/api/v1/hosts/get_all_devices"
LABELS_ENDPOINT = BASE_URL + "/api/v1/labels/"
DEVICE_ASSETS_ENDPOINT = BASE_URL + "/api/v1/device_assets/"


class DeviceSpyCli:
    """A CLI tool to interact with the Device Spy service.

    This tool allows you to query various details about devices and hosts
    managed by the Device Spy system.
    """

    def __init__(self):
        self.logger = logger.setup_logger()

    def _get_device_location_from_assets(self, udid):
        self.logger.debug(f"Fetching device location from assets for UDID: {udid}")
        response_data = make_sync_request(DEVICE_ASSETS_ENDPOINT)
        if response_data:
            device_assets = response_data.get("data", [])
            for device_asset in device_assets:
                if device_asset.get("udid") == udid:
                    location = device_asset.get("location")
                    self.logger.debug(f"Found location for {udid}: {location}")
                    return location
        self.logger.warning(f"No location found for UDID: {udid}")
        return None

    def _get_host_alias(self, host_ip):
        self.logger.debug(f"Fetching host alias for IP: {host_ip}")
        response_data = make_sync_request(HOSTS_ENDPOINT)
        if response_data:
            hosts = response_data.get("data", [])
            for host in hosts:
                if host.get("hostname") == host_ip:
                    alias = host.get("alias")
                    self.logger.debug(f"Found alias for {host_ip}: {alias}")
                    return alias
        self.logger.warning(f"No alias found for host IP: {host_ip}")
        return None

    def info(self, udid: str):
        """Queries and displays detailed information for a specific device.

        Args:
            udid (str): The Unique Device Identifier (UDID) of the device to query.
        """
        self.logger.info(f"Querying device info for UDID: {udid}")
        response_data = make_sync_request(ALL_DEVICES_ENDPOINT)
        if not response_data:
            self.logger.error("Failed to fetch device data from API")
            return

        devices = response_data.get("data", [])
        for device_data in devices:
            if udid == device_data.get("udid"):
                self.logger.debug(f"Found device with UDID: {udid}")
                device_info = device_data.copy()
                original_hostname = device_info.get("hostname")

                device_info["hostname"] = self._get_host_alias(original_hostname)

                if device_info.get("platform") == "android":
                    device_info["ip_port"] = (
                        f"{original_hostname}:{device_info.get('adb_port')}"
                    )

                location = self._get_device_location_from_assets(udid)
                if location:
                    device_info["location"] = location

                keys_to_delete = ["is_simulator", "remote_control", "adb_port"]

                for key in keys_to_delete:
                    if key in device_info:
                        del device_info[key]

                print(json.dumps(device_info, indent=2, ensure_ascii=False))
                return
        
        self.logger.warning(f"Device with UDID '{udid}' not found")
        print(f"Device with UDID '{udid}' not found or error in fetching data.")

    def available_devices(self, platform: str):
        """Lists available (not locked, not simulator) devices for a given platform.

        Args:
            platform (str): The platform to filter by (e.g., "android", "ios").
        """
        self.logger.info(f"Fetching available devices for platform: {platform}")
        response_data = make_sync_request(ALL_DEVICES_ENDPOINT)
        if not response_data:
            self.logger.error("Failed to fetch device data from API")
            return

        all_devices = response_data.get("data", [])
        avail_devices_udids = []

        for device in all_devices:
            if (
                not device.get("is_locked")
                and not device.get("is_simulator")
                and device.get("platform") == platform
            ):
                udid = device.get("udid")
                self.logger.debug(f"Available device found: {udid}")
                avail_devices_udids.append(udid)

        result = {
            "count": len(avail_devices_udids),
            "udids": avail_devices_udids,
        }
        self.logger.info(f"Found {len(avail_devices_udids)} available {platform} devices")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    def get_host_ip(self, query_string: str):
        """Finds host IP address(es) based on a query string.

        The query string is matched against host information fields like alias or hostname.

        Args:
            query_string (str): The string to search for within host information.
        """
        self.logger.info(f"Searching for hosts matching: {query_string}")
        response_data = make_sync_request(HOSTS_ENDPOINT)
        if not response_data:
            self.logger.error("Failed to fetch host data from API")
            return

        hosts = response_data.get("data", [])
        found_host_ips = []
        for host in hosts:
            for value in host.values():
                if query_string.lower() in str(value).lower():
                    hostname = host.get("hostname")
                    self.logger.debug(f"Host match found: {hostname}")
                    found_host_ips.append(hostname)
                    break

        if not found_host_ips:
            self.logger.warning(f"No host found matching '{query_string}'")
            print(f"No host found matching '{query_string}'.")
        elif len(found_host_ips) == 1:
            self.logger.info(f"Single host found: {found_host_ips[0]}")
            print(found_host_ips[0])
        else:
            self.logger.info(f"Multiple hosts found: {len(found_host_ips)} matches")
            print(json.dumps(found_host_ips, indent=2))


def main_ds_function():
    fire.Fire(DeviceSpyCli)


if __name__ == "__main__":
    main_ds_function()
