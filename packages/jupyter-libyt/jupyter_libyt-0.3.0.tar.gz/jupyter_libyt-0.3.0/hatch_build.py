import json
import os.path
import sys
from tempfile import TemporaryDirectory

from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from jupyter_client.kernelspec import KernelSpecManager

kernel_json = {
    "display_name": "Libyt",
    "language": "python",
    "metadata": {"kernel_provisioner": {"provisioner_name": "libyt-kernel-provisioner"}},
}


class CustomHook(BuildHookInterface):
    def initialize(self, version, build_data) -> None:
        here = os.path.abspath(os.path.dirname(__file__))
        sys.path.insert(0, here)

        with TemporaryDirectory() as td:
            os.chmod(td, 0o755)
            with open(os.path.join(td, "kernel.json"), "w") as f:
                json.dump(kernel_json, f, sort_keys=False)
            print("Installing libyt kernel spec")

            # TODO: logos?
            # cur_path = os.path.dirname(os.path.realpath(__file__))
            # for logo in ["logo-32x32.png", "logo-64x64.png"]:
            #     try:
            #         shutil.copy(os.path.join(cur_path, logo), td)
            #     except FileNotFoundError:
            #         print("Custom logo files not found.",
            #               "Default logos will be used.")

            KernelSpecManager().install_kernel_spec(
                td, "libyt_kernel", user=False, prefix=sys.prefix
            )
