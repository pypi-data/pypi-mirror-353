import torch


def test_torch():
    a = torch.zeros(3, 4)
    aa = torch.add(a, a)
    print(aa)


def test_npu():
    import torch_npu  # type: ignore  # noqa: F401

    device = "npu:0"
    a = torch.zeros(3, 4).to(device)
    aa = torch.add(a, a)
    print(aa)
