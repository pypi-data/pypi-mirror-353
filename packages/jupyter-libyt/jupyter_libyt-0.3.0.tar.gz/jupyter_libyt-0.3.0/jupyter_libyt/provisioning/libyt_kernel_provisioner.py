import json
import os
import typing
from typing import Any, Dict, List, Optional

from jupyter_client import KernelConnectionInfo, KernelProvisionerBase


class LibytKernelProvisioner(KernelProvisionerBase):  # type:ignore
    process = None  # kernel process
    pid = None  # pid of the kernel process
    pgid = None
    ip = None

    # It finds these files in directory set through environment variable LIBYT_KERNEL_INFO_DIR
    kernel_pid_filename = "libyt_kernel_pid.txt"
    kernel_connection_filename = "libyt_kernel_connection.json"

    @property
    def has_process(self) -> bool:
        # Find if kernel pid file exist
        return self._get_kernel_state()

    async def poll(self) -> Optional[int]:
        # If running, None is returned, otherwise, always assume success and return 0
        if self._get_kernel_state():
            return None
        else:
            return 0

    async def wait(self) -> Optional[int]:
        # Not sure if I need this, (when closing stdout/stderr/stdin, though currently not supported)
        return 0

    async def send_signal(self, signum: int) -> None:
        # Sends signal to process, but currently libyt kernel don't need that.
        # libyt kernel will get msg from server.
        return

    async def kill(self, restart: bool = False) -> None:
        # libyt kernel still respond to shutdown request and shutdown, we only respond to restart
        # which is to reload the connection
        if restart:
            # Get connection info (ex: port, ip ...), and encode key to byte string
            connection = self._get_kernel_info(self.kernel_connection_filename)
            connection["key"] = connection["key"].encode("utf-8")
            self.connection_info = connection

    async def terminate(self, restart: bool = False) -> None:
        # Same as kill
        if restart:
            # Get connection info (ex: port, ip ...), and encode key to byte string
            connection = self._get_kernel_info(self.kernel_connection_filename)
            connection["key"] = connection["key"].encode("utf-8")
            self.connection_info = connection

    async def pre_launch(self, **kwargs: Any) -> Dict[str, Any]:
        # Get connection info (ex: port, ip ...), and encode key to byte string
        connection = self._get_kernel_info(self.kernel_connection_filename)
        connection["key"] = connection["key"].encode("utf-8")
        self.connection_info = connection

        # have no idea what cmd is for, but it seems jupyter-frontend is complaining.
        return await super().pre_launch(cmd="", **kwargs)

    async def launch_kernel(self, cmd: List[str], **kwargs: Any) -> KernelConnectionInfo:
        pgid = None
        self.pid = self._get_kernel_info(self.kernel_pid_filename)
        self.pgid = pgid
        return self.connection_info

    async def cleanup(self, restart: bool = False) -> None:
        # Don't need this, port is selected and bind through libyt kernel
        pass

    def _get_kernel_info(self, target_file: str) -> typing.Union[int, dict]:
        # Print version info
        from .. import _version

        print(
            f"jupyter_libyt version {_version.__version__} (required libyt version >=0.1.0,<1.0.0)"
        )

        # Get LIBYT_KERNEL_INFO_DIR in environment variable
        libyt_kernel_info_dir = os.getenv("LIBYT_KERNEL_INFO_DIR")
        if libyt_kernel_info_dir is None:
            msg = "Environment variable LIBYT_KERNEL_INFO_DIR not set."
            raise ValueError(msg)

        # Read target file
        try:
            target_file_fullpath = os.path.join(libyt_kernel_info_dir, target_file)
            with open(target_file_fullpath, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            msg = (
                "Unable to open '%s'\n" "(LIBYT_KERNEL_INFO_DIR='%s')"
            ) % target_file_fullpath, libyt_kernel_info_dir
            raise FileNotFoundError(msg)

        return data

    def _get_kernel_state(self) -> bool:
        # Get LIBYT_KERNEL_INFO_DIR in environment variable
        libyt_kernel_info_dir = os.getenv("LIBYT_KERNEL_INFO_DIR")
        if libyt_kernel_info_dir is None:
            msg = "Environment variable LIBYT_KERNEL_INFO_DIR not set."
            raise ValueError(msg)

        # Check if kernel pid file exist
        # kernel pid file is removed by libyt kernel when it shuts down
        target_file_fullpath = os.path.join(libyt_kernel_info_dir, self.kernel_pid_filename)

        return os.path.isfile(target_file_fullpath)
