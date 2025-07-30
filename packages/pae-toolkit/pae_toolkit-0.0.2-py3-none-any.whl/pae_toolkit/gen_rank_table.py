import re
import subprocess
from typing import Literal

from pydantic import BaseModel
from rich.console import Console

# A3
vnic_cmd = "hccn_tool -i {} -vnic -g"
spod_info_cmd = "npu-smi info -t spod-info -i {} -c {}"


console = Console()


class SuperDevice(BaseModel):
    device_id: str
    device_ip: str
    super_device_id: str
    rank_id: str


class DeviceServer(BaseModel):
    server_id: str
    container_ip: str
    host_ip: str
    device: list[SuperDevice]
    host_nic_ip: str = "reserve"


class Server(BaseModel):
    server_id: str


class SuperPod(BaseModel):
    super_pod_id: str
    server_list: list[Server]


class RankTable(BaseModel):
    super_pod_list: list[SuperPod]
    server_list: list[DeviceServer]
    version: str = "1.2"
    status: Literal["initializing", "completed"] = "initializing"
    server_count: int = 0


def gen_rank_table(host: str = ["127.0.0.1"], n_phy: int = 16):
    rank_table = RankTable(super_pod_list=[], server_list=[])

    for host in host:
        device_server = DeviceServer(
            server_id=host,
            container_ip=host,
            host_ip=host,
            device=[],
        )
        for i in range(n_phy):
            if i == 0:
                res = subprocess.run(
                    spod_info_cmd.format(i // 2, i % 2), shell=True, capture_output=True
                )
                res = res.stdout.decode("utf-8").replace(" ", "")
                supod_pod_id = re.search(r"\tSuperPodID:(\d)\n", res).group(1)
                super_pod = SuperPod(
                    super_pod_id=supod_pod_id,
                    server_list=[Server(server_id=host)],
                )
                rank_table.super_pod_list.append(super_pod)

            res = subprocess.run(vnic_cmd.format(i), shell=True, capture_output=True)
            res = res.stdout.decode("utf-8")
            device_ip = re.search(r"vnic ipaddr: (\d+\.\d+\.\d+\.\d+)", res).group(1)

            res = subprocess.run(
                spod_info_cmd.format(i // 2, i % 2), shell=True, capture_output=True
            )
            res = res.stdout.decode("utf-8").replace(" ", "")
            supod_device_id = re.search(r"\tSDID:(\d+)\n", res).group(1)

            super_device = SuperDevice(
                rank_id=str(i),
                device_id=str(i),
                device_ip=device_ip,
                super_device_id=supod_device_id,
            )
            device_server.device.append(super_device)

        rank_table.server_count += 1
        rank_table.server_list.append(device_server)
    rank_table.status = "completed"
    console.print(rank_table.model_dump())


if __name__ == "__main__":
    gen_rank_table()
