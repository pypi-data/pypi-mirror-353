from pae_toolkit.gen_dataset_by_gsm8k import gen_dataset_by_gsm8k


def test_gen():
    return gen_dataset_by_gsm8k(10, 10, "gsm8k.jsonl", "Qwen2.5-0.5B-Instruct")
