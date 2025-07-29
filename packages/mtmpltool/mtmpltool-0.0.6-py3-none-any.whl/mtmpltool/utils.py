import json
from argparse import ArgumentTypeError


def get_single_lightning_gpu_device_from_torch_gpu_string(torch_gpu_string: str) -> dict:
    """
    从torch字符串中获取单个GPU设备
    """
    if torch_gpu_string.startswith("cuda"):
        device_id = torch_gpu_string.split(":")[1]
        if device_id.isdigit():
            return {"accelerator": "gpu", "devices": [int(device_id)]}
        else:
            raise ValueError(f"不支持的设备: {torch_gpu_string}")
    else:
        raise ValueError(f"不支持的设备: {torch_gpu_string}")


def parse_json(value):
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        raise ArgumentTypeError("Invalid JSON format for dictionary")
