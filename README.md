# clever-prover
This has the baseline implementation for the CLEVER benchmark [CLEVER: Curated Lean Verified Code Generation Benchmark](https://github.com/trishullab/clever).

# Running the baseline implementation
To run the baseline implementation, follow these steps:
1. **Clone the Repository**: First, clone the repository to your local machine using the following command:
   ```bash
   git clone https://github.com/trishullab/clever-prover.git
   ``` 
2. **Navigate to the Directory**: Change your current directory to the cloned repository:
   ```bash
   cd clever-prover
   ```
3. **Install Dependencies**: Make sure you have all the necessary dependencies installed. You can
install them using pip:
    ```bash
    pip install -e .
    ```
>Note: To run open source models via vLLM, you need to also run `pip install copra-theorem-prover[os_models]`

4. **Run install command to setup clever-bench**:
    ```bash
    clever-bench-install 
    # This will build the clever benchmark and install Lean 4 if not already installed
    # tested on Linux, for other OS please refer to clever-bench README for Lean 4 installation instructions
    ```

5. [Optional] **For running COPRA baselines you would additionally need to install itp-interface**:
    ```bash
    export LEAN_VERSION="4.15.0" # This is the version currently used in clever-bench
    install-lean-repl
    install-itp-interface
    ```

4. **Running the baseline**:
    
    **[Optional]** First need to start the ray cluster so that parallel evaluation can be done:
    ```bash
    python src/clever_prover/main/init_ray.py &
    # ^ NOTE: Make sure to run this in background so that we can schedule that actual evaluation jobs next
    ```

    Then run the evaluation script with the desired experiment config file. For example:

    ```bash
    python src/clever_prover/main/eval.py --config-name few_shot_impl_copra_proof_gpt5_mini
    ```
    OR
    ```bash
    export CUDA_VISIBLE_DEVICES="0,1,2,3"  # Set this if you are using GPUs for local models via vLLM
    python src/clever_prover/main/eval.py --config-name few_shot_impl_few_shot_proof_gpt_oss_20b
    ```
    >NOTE: Make sure to read the [Config](#config) and [Secrets](#secrets) sections below to set up the config files and secrets properly before running the above command.
    
    >NOTE: The eval script will start the ray cluster automatically if not already started with 8 CPUs and 150GB object store memory. To customize the ray cluster settings, please use the `init_ray.py` script as shown above.

    The above command runs implementation generation using few-shot prompting of GPT-5 Mini model and proof generation using few-shot prompting of CoPRA prover.

# Config files

The config files are located in the `src/clever_prover/configs` folder. You can change the config file to run different models or different settings.
For example, the contents of `src/clever_prover/main/configs/few_shot_impl_few_shot_proof_deepseek_r1.yaml`:
```yaml
task_type: IMPL_CORRECTNESS # The certification task type, can be IMPL_CORRECTNESS or SPEC_ISOMORPHISM
log_dir: ".logs/eval_few_shot_impl_few_shot_proof_deepseek_r1"
exp_name: "few_shot_impl_few_shot_proof_deepseek_r1"
impl_generation_strategy: "ImplGenerator"
problems_to_solve: "*"
k: 1
timeout_in_secs: 600 # Timeout for each problem, the evaluation will keep trying to regenrate implementation/proof until this timeout is reached
params:
proof_dump_file_path: "proofs.txt"
num_implementation_samples: 1000 # Max number of implementation samples within the timeout (usually it won't reach this number before timeout)
num_proof_plan_samples: 1000
uses_copra_prover: false # Set to true to use CoPRA prover for proof generation, remember to change the prompt and model settings accordingly
impl_prompt_settings: # Model which will be used for implementation generation
    system_prompt_path: 
    # ......
    # ......
impl_model_settings:
    model_name: "deepseek.r1-v1:0"
    secret_path: ".secrets/bedrock_key.json" # Path to your AWS Bedrock secret key
    temperature: 0.75
prover_prompt_settings:
    system_prompt_path: # ....
    # ......
    # ......
prover_model_settings: # Model which will be used for proof generation
    model_name: "deepseek.r1-v1:0"
    secret_path: ".secrets/bedrock_key.json" # Path to your AWS Bedrock secret key
    # the json file should contain at least
    # {
    #     "region_name": "<something like us-east-1>",
    #     "aws_access_key_id": "<aws-access-key-id>",
    #     "aws_secret_access_key": "<aws-secret-access-key>"
    # }
    temperature: 0.75
# These settings are experimental planning based approaches and are not used in the baseline implementation
proof_planner_prompt_settings: null
proof_planner_model_settings: null
impl_planner_model_settings: null
impl_planner_prompt_settings: null
```

Similarly, you can run experiments for specification correctness by changing the config file name. Take a look at the config file `src/clever_prover/main/configs/few_shot_spec_few_shot_proof_claude_3_7.yaml` for an example.

# Running models locally on GPUs via VLLM:
To run open source models locally on GPUs via vLLM, you need to first install the required packages:
```bash
pip install copra-theorem-prover[os_models]
```

Then, you can change the model settings in the config file to use local models. For example, to use GPT-OSS 20B (open source model), you can modify the config file as follows:
```yaml
# @package _global_
defaults:
  - override hydra/job_logging: 'disabled'

task_type: SPEC_ISOMORPHISM
log_dir: ".logs/eval_few_shot_spec_few_shot_proof_gpt_oss_20b"
exp_name: "few_shot_spec_few_shot_proof_gpt_oss_20b"
spec_generation_strategy: "IsoGenerator"
problems_to_solve: "*"
k: 1
timeout_in_secs: 600
params:
  proof_dump_file_path: "proofs.txt"
  num_spec_samples: 1000
  num_proof_plan_samples: 1000
  uses_copra_prover: false
  spec_prompt_settings:
    system_prompt_path: "src/clever_prover/prompts/baselines/system/FewShotSpecGeneration.md"
    example_prompt_path: "src/clever_prover/prompts/baselines/examples/FewShotSpecGeneration.md"
    max_tokens_per_action: 5000
    max_history_messages: 0
    end_tokens: ["[END]"]
  spec_model_settings:
    model_name: "vllm:openai/gpt-oss-20b" # The pattern is vllm:<huggingface-model-identifier>
    secret_path: "<some-valid-json-path>" # Even though we are not using any secret here, just any existing path is needed to satisfy the config structure. Can use "./secret_template.json"
    temperature: 0.75
  prover_prompt_settings:
    system_prompt_path: "src/clever_prover/prompts/baselines/system/FewShotSpecProofGeneration.md"
    example_prompt_path: "src/clever_prover/prompts/baselines/examples/FewShotSpecProofGeneration.md"
    max_tokens_per_action: 7500
    max_history_messages: 0
    end_tokens: ["[END]"]
  prover_model_settings:
    model_name: "vllm:openai/gpt-oss-20b" # The pattern is vllm:<huggingface-model-identifier>
    secret_path: "<some-valid-json-path>" # Even though we are not using any secret here, just any existing path is needed to satisfy the config structure. Can use "./secret_template.json"
    temperature: 0.75
  proof_planner_prompt_settings: null
  proof_planner_model_settings: null
  spec_planner_model_settings: null
  spec_planner_prompt_settings: null
```
See `src/clever_prover/main/configs/few_shot_impl_few_shot_proof_gpt_oss_20b.yaml` and `src/clever_prover/main/configs/few_shot_spec_few_shot_proof_gpt_oss_20b.yaml`.

# Running on server hosting OpenAI compatible APIs:

To run models hosted on servers that provide OpenAI compatible APIs (like vLLM server), you need to set the `VLLM_BASE_URL` environment variable to point to the server URL before running the eval script. For example:
```bash
export VLLM_BASE_URL="http://localhost:48000"

```
If there is a key required for authentication, you can also set the `VLLM_API_KEY` environment variable:
```bash
export VLLM_API_KEY="<your-api-key>"
```

Then, you can use the `vllm:<model-identifier>` pattern in the config file to specify the model hosted on the server. For example:
```yaml
spec_model_settings:
    model_name: "vllm:<your-model-identifier>" # The pattern is vllm:<model-identifier>, even though we do NOT start the vLLM server here, we are just using the OpenAI compatible API it provides
    secret_path: "<some-valid-json-path>" # Even though we are not using any secret here, just any existing path is needed to satisfy the config structure. Can use "./secret_template.json"
```

# Secrets

For now we support AWS Bedrock models (Anthropic, DeepSeek), and OpenAI models, and for that you need to create a secret json file with the following structure (make sure that it doesn't get committed to any repository). In this repo, `.secrets` is already added to `.gitignore`, so you can create your secret files there (or somewhere else outside the repo if you prefer).

For AWS Bedrock models, the secret json file should contain at least the following fields:
```json
{
    "region_name": "<something like us-east-1>",
    "aws_access_key_id": "<aws-access-key-id>",
    "aws_secret_access_key": "<aws-secret-access-key>"
}
```

For OpenAI models, the secret json file should contain at least the following field:
```json
{
    "organization": "<your-openai-organization-id>",
    "api_key": "<your-openai-api-key>"
}
```

For open source models via vLLM, no secret file is needed, but you still need to provide some existing path in the config to satisfy the config structure.

# Additional Information

For more complicated evaluation startegy, like running specific number of samples first and then trying proof or retrying code generation based on failure to find proof, please use the underlying `clever-bench` (https://pypi.org/project/clever-bench/) APIs directly as mentioned in the [clever-bench README](https://github.com/trishullab/clever/blob/main/README.md#-submitting-your-solutions-to-clever). You can use that link to customize your evaluation approach then just test for the final correctness of your generated implementations/proofs using the `clever-bench` APIs.

To evaluate your LLM-generated solutions against the CLEVER benchmark, use the Python API to package and submit them as `LeanProblemView` objects. Each submission is compiled and verified using Lean 4, and results are returned as structured `ValidationResult` objects.

### 🔧 Steps

0. **Installing the python package**:
   You can simply use `pip install clever-bench` to install the package from PyPi. 
   
   After installing the package, run the command `clever-bench-install` (this will work on Linux, no prerequisite of installing Lean 4).

   If you are not on Linux, then you will have install the Lean 4 dependency by yourself. After Lean 4 installation, you can run `cd <path-to-clever-package-installation/lean4-dir> && lake exe cache get && lake build` (or equivalent command) to build the Lean 4 environment (This is a one time step only).

1. **Load the benchmark**:
   ```python
   from clever_bench.benchmark import Benchmark
   benchmark = Benchmark(is_sample=True)  # or is_sample=False for actual HumanEval problems in `src/lean4/human_eval`
   benchmark.load_all()
   ```

2. **Select a task** (e.g., proof generation):
   ```python
   from clever_bench.task import ProblemViewTask, TaskComponent
   task = ProblemViewTask(benchmark, TaskComponent.PROOF_GENERATION)
   ```

3. **Get a problem and fill in your solution**:
   ```python
   problem = task.get_view(3) # Abstraction to hide the staged problem details and only show relevant fields for the selected task for problem with id 3
   problem.implementation = "<your Lean implementation>"
   problem.correctness_proof = "<your proof>"
   ```

4. **Submit the solution**:
   ```python
   import asyncio
   result = asyncio.run(task.submit_async(problem, timeout_in_ms=30000))
   print(result.correctness_ok, result.error_message)
   ```