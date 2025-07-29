import logging
import os
import platform
import time
from pathlib import Path
from typing import Literal

import psutil
import requests
from docker import DockerClient
from docker.models.containers import Container
from filelock import FileLock
from pydantic import BaseModel, model_validator

from screensuite.agents.remote_env.provider import IPAddr, Provider

logger = logging.getLogger()
logger.setLevel(logging.INFO)

WAIT_TIME = 3
RETRY_INTERVAL = 10
LOCK_TIMEOUT = 10


class PortAllocationError(Exception):
    pass


class DockerProviderConfig(BaseModel):
    PROVIDER_NAME: Literal["docker"] = "docker"
    ports_to_forward: set[int]
    healthcheck_endpoint: str | None
    healthcheck_port: int | None
    environment: dict[str, str] = {"DISK_SIZE": "32G", "RAM_SIZE": "4G", "CPU_CORES": "4"}  # Modify if needed
    image: str
    volumes: list[str] = []  # list of volumes to mount
    lock_file: Path = (
        Path(os.getenv("TEMP", "TEMP_DIR") if platform.system() == "Windows" else "/tmp") / "docker_port_allocation.lck"
    )
    privileged: bool = False
    cap_add: list[str] | None = None  # set to ["NET_ADMIN"] for using
    devices: list[str] | None = None  # set to ["/dev/kvm"] for enabling nested virtualization - only for linux
    user: str | None = None  # set to the user to run the container as


class DockerProvider(Provider):
    client: DockerClient = DockerClient.from_env()
    container: Container | None = None
    config: DockerProviderConfig
    ports: dict[int, int] = {}

    @model_validator(mode="after")
    def post_init(self):
        self.config.lock_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.config.ports_to_forward:
            raise ValueError("Ports to forward must be provided")
        self.ports = {port: port for port in self.config.ports_to_forward}
        return self

    def _get_used_ports(self):
        """Get all currently used ports (both system and Docker)."""
        # Get system ports
        system_ports = set(conn.laddr.port for conn in psutil.net_connections() if conn.laddr)

        # Get Docker container ports
        docker_ports: set[int] = set()
        for container in self.client.containers.list():
            ports = container.attrs["NetworkSettings"]["Ports"]
            if ports:
                for port_mappings in ports.values():
                    if port_mappings:
                        docker_ports.update(int(p["HostPort"]) for p in port_mappings)

        return system_ports | docker_ports

    def _get_available_port(self, start_port: int) -> int:
        """Find next available port starting from start_port."""
        used_ports = self._get_used_ports()
        port = start_port
        while port < 65354:
            if port not in used_ports:
                return port
            port += 1
        raise PortAllocationError(f"No available ports found starting from {start_port}")

    def _wait_for_vm_ready(self, timeout: int = 1000):
        """Wait for VM to be ready by checking screenshot endpoint."""
        start_time = time.time()

        def check_health():
            if self.config.healthcheck_endpoint is None or self.config.healthcheck_port is None:
                logger.warning(
                    "Healthcheck endpoint or port not set, skipping healthcheck: \n"
                    "healthcheck_endpoint: %s, \n"
                    "healthcheck_port: %s",
                    self.config.healthcheck_endpoint,
                    self.config.healthcheck_port,
                )
                return True
            try:
                response = requests.get(
                    f"http://localhost:{self.ports[self.config.healthcheck_port]}/{self.config.healthcheck_endpoint.lstrip('/')}",
                    timeout=(10, 10),
                )
                return response.status_code == 200
            except Exception:
                return False

        while time.time() - start_time < timeout:
            if check_health():
                return True
            logger.info(
                "🔄 Initializing virtual machine... %s seconds elapsed (this process may take a few minutes)",
                int(time.time() - start_time),
            )
            time.sleep(RETRY_INTERVAL)

        raise TimeoutError("VM failed to become ready within timeout period")

    def start_emulator(self):
        # Use a single lock for all port allocation and container startup
        lock = FileLock(str(self.config.lock_file), timeout=LOCK_TIMEOUT)

        try:
            with lock:
                # Allocate all required ports
                for port in self.ports:
                    self.ports[port] = self._get_available_port(port)

                # Start container while still holding the lock
                logger.info(
                    "🔄 Starting container with settings: %s",
                    {
                        "image": self.config.image,
                        "environment": self.config.environment,
                        "cap_add": self.config.cap_add,
                        "devices": self.config.devices,
                        "volumes": self.config.volumes,
                        "ports": self.ports,
                        "privileged": self.config.privileged,
                    },
                )
                self.container = self.client.containers.run(
                    image=self.config.image,
                    environment=self.config.environment,
                    cap_add=self.config.cap_add,
                    devices=self.config.devices,
                    volumes=self.config.volumes if self.config.volumes else None,
                    ports={str(port): self.ports[port] for port in self.ports},
                    detach=True,
                    privileged=self.config.privileged,
                    user=self.config.user,
                )

            logger.info(f"Started container with ports: {self.ports} ")

            # Wait for VM to be ready
            self._wait_for_vm_ready()

        except Exception as e:
            # Clean up if anything goes wrong
            if self.container:
                try:
                    self.container.stop()
                    self.container.remove()
                except Exception:
                    pass
            raise e

    def get_ip_address(self) -> IPAddr:
        if not all([self.ports]):
            raise RuntimeError("VM not started - ports not allocated")
        return IPAddr(
            ip_address="localhost",
            host_port={port: self.ports[port] for port in self.ports},
        )

    def save_state(self, snapshot_name: str):
        raise NotImplementedError("Snapshots not available for Docker provider")

    def revert_to_snapshot(self, snapshot_name: str):
        raise NotImplementedError("Snapshots not available for Docker provider")

    def reset(self):
        logger.info("Resetting environment...")
        self.stop_emulator()
        self.start_emulator()
        logger.info("Environment reset.")

    def stop_emulator(self):
        if self.container:
            logger.info("Stopping VM...")
            try:
                self.container.stop()
                self.container.remove()
                time.sleep(WAIT_TIME)
            except Exception as e:
                logger.error(f"Error stopping container: {e}")
            finally:
                self.container = None
