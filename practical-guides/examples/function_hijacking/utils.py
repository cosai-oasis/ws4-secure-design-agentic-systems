import logging
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_model_and_tokenizer(model_path, dtype="float16"):
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=getattr(torch, dtype),
    ).to("cuda" if torch.cuda.is_available() else "cpu")
    return tokenizer, model


def prepare_prompt(template, optim_str, jailbreak=False):
    return template.replace("{optim_str}", optim_str) if jailbreak else template

def extract_response_block(raw_output):
    try:
        return raw_output.split("<|python_tag|>")[1].split("<|eom_id|>")[0].strip()
    except IndexError:
        try:
            return raw_output.split("<|eom_id|>")[0].strip()
        except IndexError:
            logger.error("Failed to extract function call from model output.")
            return ""

def display_tools(tools):
    logger.info("\nAvailable Tools:")
    for tool in tools:
        logger.info(f"- {tool['name']}: {tool['description']}")
