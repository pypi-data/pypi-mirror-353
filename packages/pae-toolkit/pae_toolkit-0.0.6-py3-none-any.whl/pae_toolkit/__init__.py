import time
import typer
from typer import prompt

from pae_toolkit.check_env import check_mindie_high_preformance_env as check_mindie_env
from pae_toolkit.check_env import check_vllm_high_preformance_env as check_vllm_env
from pae_toolkit.pd import Config, start_pd

app = typer.Typer(
    add_completion=True,
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
    pretty_exceptions_enable=False,
    pretty_exceptions_short=False,
)


@app.command(help="检查 MindIE 高性能所需环境变量配置")
def check_mindie_high_preformance_env():
    check_mindie_env()


@app.command(help="检查 vLLM-ascend 高性能所需环境变量配置")
def check_vllm_high_preformance_env():
    check_vllm_env()



# @app.command(help="启动单机P&D服务")
def start_single_machine_pd_server(
    start_npu_id: int = typer.Option(-1),
    p_node_num: int = typer.Option(-1),
    npu_num_per_p_node: int = typer.Option(-1),
    d_node_num: int = typer.Option(-1),
    npu_num_per_d_node: int = typer.Option(-1),
    docker_image: str = typer.Option(""),
    model_path: str = typer.Option(""),
):
    config = Config()
    config.start_npu_id = int(prompt("起始的NPU ID")) if start_npu_id < 0 else start_npu_id
    config.p_node_num = int(prompt("P节点数量")) if p_node_num < 0 else p_node_num
    config.npu_num_per_p_node = (
        int(prompt("每个P节点NPU数量")) if npu_num_per_p_node < 0 else npu_num_per_p_node
    )
    config.d_node_num = int(prompt("D节点数量")) if d_node_num < 0 else d_node_num
    config.npu_num_per_d_node = (
        int(prompt("每个D节点NPU数量")) if npu_num_per_d_node < 0 else npu_num_per_d_node
    )
    config.docker_image = str(prompt("Docker镜像")) if docker_image == "" else docker_image
    config.model_path = str(prompt("模型路径")) if model_path == "" else model_path
    return start_pd(config)


def main() -> None:
    app()
