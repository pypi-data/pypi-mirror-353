import os
import platform
import shlex
import subprocess

from rich.console import Console
from rich.markdown import Markdown

console = Console()

base_env_dict: dict[str, str] = {
    "PYTORCH_NPU_ALLOC_CONF": "expandable_segments:True",
    "OMP_PROC_BIND": "false",
    "OMP_NUM_THREADS": 100,
    "TASK_QUEUE_ENABLE": 2,
    "CPU_AFFINITY_CONF": 2,  # 0: no affinity, 1: cpu affinity, 2: cpu affinity + numa
    "HCCL_OP_EXPANSION_MODE": "AIV",
    "HCCL_DETERMINISTIC": "false",  # 关闭确定性计算
    "HCCL_CONNECT_TIMEOUT": 7200,  # 建链等待时间
    "HCCL_EXEC_TIMEOUT": 0,  # 设备间执行等待时间
    "ASCEND_LAUNCH_BLOCKING": 0,  # 非阻塞模式
    "NPU_MEMORY_FRACTION": 0.96,
    "INF_NAN_MODE_FORCE_DISABLE": 1,
}


def check_env(env_dict: dict[str, str], cmd: str = None):
    print("machine info:")
    system_info = {
        "操作系统名称及版本号": platform.platform(),
        "操作系统的位数": platform.architecture(),
        "处理器信息": platform.processor(),
        "Python版本": platform.python_version(),
    }
    for k, v in system_info.items():
        print(f"\t{k}: {v}")

    if platform.system() == "Linux":
        cmd_res = subprocess.run(
            shlex.split("cat /sys/kernel/mm/transparent_hugepage/enabled"), capture_output=True
        ).stdout.decode()
        if cmd_res.split()[0] == "[always]":
            print("Transparent Hugepages is enabled")
        else:
            print("Transparent Hugepages is disabled")

    #     console.print(
    #         Markdown("""
    # `yum install kernel-tools` or `apt install cpufrequtils`
    # 成功后执行 `cpupower -c all frequency-set -g performance`
    # """)
    #     )

    print("environment check:")
    env_suggest_str = "#!/bin/bash"
    for environment in env_dict:
        expected_env_value = str(env_dict[environment])
        if (env_value := os.getenv(environment)) == expected_env_value:
            console.print(f"\t[√] {environment}={env_value}", style="green")
        else:
            console.print(
                f'\t[X] {environment}={env_value}, expected="{expected_env_value}"', style="red"
            )
            os.environ[environment] = expected_env_value
            env_suggest_str += f'\nexport {environment}="{expected_env_value}"'

    # console.print("[Tip] Following cmd to set the environment variables:", style="blue")
    # console.print(cmd_str)
    # res 保存到文件中
    save_file = "set_env_for_performance.sh"
    with open(save_file, "w") as f:
        f.write(env_suggest_str)
    console.print(f"{save_file} saved, run it to set the environment variables")

    if cmd:
        return subprocess.run(shlex.split(cmd), shell=True, check=True)


def check_mindie_high_preformance_env(cmd: str = None):
    env_dict: dict[str, str] = {
        **base_env_dict,
        "MINDIE_LOG_TO_STDOUT": 0,
        "MINDIE_LOG_TO_FILE": 1,
        "MINDIE_LOG_LEVEL": "info; llm:error; server:error",
        "MINDIE_ASYNC_SCHEDULING_ENABLE": 1,  # 异步双发射
        "ATB_LLM_HCCL_ENABLE": 1,
        "ATB_LLM_COMM_BACKEND": "hccl",
        "ATB_WORKSPACE_MEM_ALLOC_ALG_TYPE": 3,
        "ATB_WORKSPACE_MEM_ALLOC_GLOBAL": 1,
        "ATB_LLM_ENABLE_AUTO_TRANSPOSE": 0,
        "ATB_LAYER_INTERNAL_TENSOR_REUSE": 1,
        "ATB_OPERATION_EXECUTE_ASYNC": 1,
        "ATB_CONVERT_NCHW_TO_ND": 1,
        "ATB_CONTEXT_WORKSPACE_SIZE": 0,
        "ATB_LAUNCH_KERNEL_WITH_TILING": 1,
    }
    check_env(env_dict, cmd)


def check_vllm_high_preformance_env(cmd: str = None):
    env_dict: dict[str, str] = {
        **base_env_dict,
        "VLLM_USE_V1": 1,
        "VLLM_OPTIMIZATION_LEVEL": 3,
        "USING_LCCL_COM": 1,
        "USING_SAMPLING_TENSOR_CACHE": 1,
    }
    check_env(env_dict, cmd)
