import json
import time

from transformers import AutoTokenizer


def gen_dataset_by_gsm8k():
    # 1. 传入模型权重路径
    tokenizer = AutoTokenizer.from_pretrained(
        "/data/weights/DeepSeek-R1-Distill-Qwen-32B/"
    )
    batch_size = 150  # 2. 数据集条数
    input_len = 1000  # 3. 平均输入长度
    dataset_path = "GSM8K.jsonl"  # 4. 原始数据集路径

    dataset = []
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = [json.loads(line)["question"] for line in f]

    # repeat input_len
    dataset_2k = []
    for sentence in dataset:
        words = tokenizer.tokenize(sentence)
        if len(words) == 0:
            continue
        len_num = len(words) // input_len
        if len_num == 0:
            multiplier = (input_len // len(words)) + 1
            # 获取时间戳
            prefix_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            repeated_len = tokenizer.tokenize(prefix_time) + words * multiplier
            words = repeated_len[:input_len]
            decoded_text = tokenizer.convert_tokens_to_string(words)
            dataset_2k.append(decoded_text)
    # repeat to batch_size
    batch_num = len(dataset_2k) // batch_size
    if batch_num == 0:
        multiplier = (batch_size // len(dataset_2k)) + 1
        repeated_batch = dataset_2k * multiplier
        dataset_2k = repeated_batch[:batch_size]
    else:
        dataset_2k = dataset_2k[:batch_size]
    json_str = json.dumps(dataset_2k, ensure_ascii=False, indent=4)
    print("gen start.........")
    with open(f"GSM8K-in{input_len}-bs{batch_size}.jsonl", "w", encoding="utf-8") as f:
        print("open file start.........")
        for i in range(len(dataset_2k)):
            f.write(
                json.dumps(
                    {"question": dataset_2k[i], "answer": "none"}, ensure_ascii=False
                )
            )
            f.write("\n")
