import os
import logging
from copra.tools.vllm_tools import start_server
from copra.tools.misc import is_vllm_model

# Global variable to track vLLM server process
_vllm_server_process = None


def _initialize_services(
    model_name: str,
    logger: logging.Logger,
    log_dir: str
) -> None:
    """
    Initialize required services (vLLM) based on configuration.
    """
    # Check if the vLLM server base URL is already set
    # Then don't start another server
    if "VLLM_BASE_URL" in os.environ:
        logger.info("vLLM_BASE_URL is already set. Skipping vLLM server initialization.")
        logger.info(f"VLLM_BASE_URL: {os.environ['VLLM_BASE_URL']}")
        return

    global _vllm_server_process

    # Initialize vLLM service if using vLLM model
    if model_name is not None and \
       len(model_name) != 0 and \
       is_vllm_model(model_name):
        logger.info(f"Starting vLLM server for model: {model_name}")

        # Extract actual model name without vllm: prefix
        actual_model_name = model_name.replace("vllm:", "", 1)

        # Get vLLM configuration from environment variables or use defaults
        vllm_port = int(os.environ.get("VLLM_PORT", "48000"))
        vllm_host = os.environ.get("VLLM_HOST", "127.0.0.1")
        vllm_api_key = os.environ.get("VLLM_API_KEY", "EMPTY")
        vllm_max_model_len = None #eval_settings.model_params.get("max_model_len", None)
        if vllm_max_model_len is None and "VLLM_MAX_MODEL_LEN" in os.environ:
            vllm_max_model_len = int(os.environ.get("VLLM_MAX_MODEL_LEN"))

        try:
            base_url, proc = start_server(
                model=actual_model_name,
                host=vllm_host,
                port=vllm_port,
                api_key=vllm_api_key,
                max_model_len=vllm_max_model_len,
                max_num_seqs=4,
                wait_seconds=600,  # Give it 10 minutes to start
                logger=logger,
                log_file=os.path.join(log_dir, "vllm_server.log")
            )
            _vllm_server_process = proc
            os.environ["VLLM_BASE_URL"] = base_url
            logger.info(f"vLLM server started successfully at {base_url}")
        except Exception as e:
            logger.error(f"Failed to start vLLM server: {e}")
            raise