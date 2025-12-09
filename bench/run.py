# bench/run.py
# Fixed-seed evaluation harness for ShadowEcology v2

import json
import yaml
import sys
from pathlib import Path
from datetime import datetime
from typing import Any

# fast mode flag
FAST_MODE = "--fast" in sys.argv

# debug config for limiting examples
try:
    debug_cfg = yaml.safe_load(open("bench/configs/debug.yaml"))
    MAX_EX = debug_cfg.get("max_examples_per_task", None)
except:
    MAX_EX = None

# import all task evaluators
from bench.tasks import truthfulqa, winogrande_arc, toxicity, mtbench, contradiction


# run external baseline model
def run_external_model(model_name: str, example: dict[str, Any], task_name: str, seed: int) -> str:
    # use existing oracle infrastructure
    from shadowecology.oracle import local

    # format prompt based on task
    if task_name == "truthfulqa":
        question = example.get("question", "")
        choices = example.get("choices", [])
        prompt = f"Question: {question}\n\nChoices:\n"
        for choice in choices:
            prompt += f"{choice}\n"
        prompt += "\nAnswer with only the letter (A, B, C, or D):"
    elif task_name == "winogrande":
        question = example.get("question", "")
        choices = example.get("choices", [])
        prompt = f"{question}\n\nOptions:\n"
        for i, choice in enumerate(choices, 1):
            if len(choices) == 2:
                prompt += f"{i}. {choice}\n"
            else:
                prompt += f"{chr(64+i)}. {choice}\n"
        prompt += "\nAnswer with only the number (1 or 2) or letter:"
    elif task_name == "mtbench":
        turns = example.get("turns", [])
        prompt = turns[0] if turns else "Hello"
    elif task_name == "contradiction":
        messages = example.get("messages", [])
        if messages:
            prompt = "\n".join([m.get("content", "") for m in messages])
        else:
            prompt = "Reflect on these ideas."
    else:
        prompt = str(example.get("prompt", example.get("content", "")))

    # neutral biases for raw baseline
    neutral_biases = {
        "curiosity": 0.5,
        "caution": 0.5,
        "humor": 0.5,
        "verbosity": 0.5,
        "depth": 0.5,
        "risk": 0.5,
        "empathy": 0.5,
        "identity": 0.5,
    }

    # generate with neutral biases
    try:
        response = local.generate([{"role": "user", "content": prompt}], neutral_biases)
        return response
    except Exception as e:
        return f"ERROR: {e}"
# run shadow system with specific config
def run_shadow_system(config: dict[str, Any], example: dict[str, Any], task_name: str, seed: int) -> str:
    # TODO: implement shadow system invocation with ablations
    # for now, return error message
    return "ERROR: Shadow system not implemented yet - need v1/v2 integration"


# run single evaluation across all tasks
def run_evaluation(config_name: str, config: dict[str, Any], seed: int) -> dict[str, float]:
    results = {}

    # run each task
    tasks = {
        "truthfulqa": truthfulqa,
        "winogrande": winogrande_arc,
        "toxicity": toxicity,
        "mtbench": mtbench,
        "contradiction": contradiction,
    }

    for task_name, task_module in tasks.items():
        # skip slow tasks in fast mode
        if FAST_MODE and task_name in {"toxicity", "mtbench"}:
            print(f"  Skipping {task_name} in fast mode")
            results[task_name] = 0.0
            continue

        dataset = task_module.load_dataset(seed)

        # limit samples in fast mode for quick testing
        if FAST_MODE and len(dataset) > 10:
            dataset = dataset[:10]

        scores = []

        for example in dataset:
            # generate model output based on config
            if config.get("external"):
                # external baseline model (raw_llama, self_refine, dpo, etc)
                model_output = run_external_model(config["external"], example, task_name, seed)
            else:
                # shadowecology system with specific ablations
                model_output = run_shadow_system(config, example, task_name, seed)

            score = task_module.evaluate(model_output, example)
            scores.append(score)

        # average score for this task
        results[task_name] = sum(scores) / len(scores) if scores else 0.0

    return results


# run full benchmark suite
def run_full_suite():
    # load configs
    config_path = Path("bench/configs/default.yaml")
    with open(config_path) as f:
        data = yaml.safe_load(f)

    configs = data["configs"]

    # run 50 seeds for each config
    all_results = []

    for config_name, config in configs.items():
        print(f"Running {config_name}...")

        for seed in range(50):
            result = {
                "config": config_name,
                "seed": seed,
                "timestamp": datetime.now().isoformat(),
            }

            # run evaluation
            scores = run_evaluation(config_name, config, seed)
            result.update(scores)

            all_results.append(result)

    # save results
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    results_dir = Path("bench/results")
    results_dir.mkdir(exist_ok=True)

    # save JSONL
    jsonl_path = results_dir / f"{timestamp}.jsonl"
    with open(jsonl_path, "w") as f:
        for result in all_results:
            f.write(json.dumps(result) + "\n")

    # generate markdown table
    generate_markdown_table(all_results, results_dir / "latest.md")

    print(f"Results saved to {jsonl_path}")


# generate markdown summary table
def generate_markdown_table(results: list[dict], output_path: Path):
    # aggregate by config
    config_scores = {}

    for result in results:
        config = result["config"]
        if config not in config_scores:
            config_scores[config] = {
                "truthfulqa": [],
                "winogrande": [],
                "toxicity": [],
                "mtbench": [],
                "contradiction": [],
            }

        for task in config_scores[config]:
            if task in result:
                config_scores[config][task].append(result[task])

    # compute means
    with open(output_path, "w") as f:
        f.write("# ShadowEcology v2 Benchmark Results\n\n")
        f.write("| Configuration | TruthfulQA | Winogrande | Toxicity | MT-Bench | Contradiction | Avg |\n")
        f.write("|---------------|------------|------------|----------|----------|---------------|-----|\n")

        for config, scores in config_scores.items():
            means = {task: sum(vals)/len(vals) if vals else 0.0 for task, vals in scores.items()}
            avg = sum(means.values()) / len(means)

            f.write(f"| {config:20s} | {means['truthfulqa']:.3f} | {means['winogrande']:.3f} | "
                   f"{means['toxicity']:.3f} | {means['mtbench']:.3f} | {means['contradiction']:.3f} | "
                   f"{avg:.3f} |\n")


def dry_run():
    # load configs
    config_path = Path("bench/configs/default.yaml")
    with open(config_path) as f:
        data = yaml.safe_load(f)

    configs = data["configs"]

    # print 9×5 table skeleton
    print("\n# ShadowEcology v2 Benchmark - Dry Run\n")
    print("| Configuration         | TruthfulQA | Winogrande | Toxicity | MT-Bench | Contradiction |")
    print("|-----------------------|------------|------------|----------|----------|---------------|")

    for config_name in configs.keys():
        print(f"| {config_name:21s} | {'--':>10s} | {'--':>10s} | {'--':>8s} | {'--':>8s} | {'--':>13s} |")

    print(f"\nTotal: {len(configs)} configs × 5 tasks × 50 seeds = {len(configs) * 5 * 50} evaluations")


if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--config", type=str, help="Single config to run")
    parser.add_argument("--seeds", nargs="+", type=int, help="Specific seeds to run")
    parser.add_argument("--fast", action="store_true", help="Skip slow tasks (toxicity, mtbench)")

    args = parser.parse_args()

    if args.dry_run:
        dry_run()
    elif args.config and args.seeds:
        # run single config with specific seeds
        config_path = Path("bench/configs/default.yaml")
        with open(config_path) as f:
            data = yaml.safe_load(f)

        configs = data["configs"]
        if args.config not in configs:
            print(f"Error: Config '{args.config}' not found")
            sys.exit(1)

        config = configs[args.config]
        all_results = []

        print(f"Running {args.config} with seeds {args.seeds}...\n")

        for seed in args.seeds:
            result = {
                "config": args.config,
                "seed": seed,
                "timestamp": datetime.now().isoformat(),
            }

            scores = run_evaluation(args.config, config, seed)
            result.update(scores)
            all_results.append(result)

        # display results table
        print(f"\n# Results for {args.config}\n")
        print("| Seed | TruthfulQA | Winogrande | Toxicity | MT-Bench | Contradiction |")
        print("|------|------------|------------|----------|----------|---------------|")

        for result in all_results:
            print(f"| {result['seed']:4d} | {result['truthfulqa']:10.3f} | {result['winogrande']:10.3f} | "
                  f"{result['toxicity']:8.3f} | {result['mtbench']:8.3f} | {result['contradiction']:13.3f} |")

        # compute and display means
        means = {
            task: sum(r[task] for r in all_results) / len(all_results)
            for task in ["truthfulqa", "winogrande", "toxicity", "mtbench", "contradiction"]
        }

        print("|------|------------|------------|----------|----------|---------------|")
        print(f"| Mean | {means['truthfulqa']:10.3f} | {means['winogrande']:10.3f} | "
              f"{means['toxicity']:8.3f} | {means['mtbench']:8.3f} | {means['contradiction']:13.3f} |")

        # save results
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        results_dir = Path("bench/results")
        results_dir.mkdir(exist_ok=True)

        jsonl_path = results_dir / f"{timestamp}_{args.config}.jsonl"
        with open(jsonl_path, "w") as f:
            for result in all_results:
                f.write(json.dumps(result) + "\n")

        print(f"\nResults saved to {jsonl_path}")
    else:
        run_full_suite()
