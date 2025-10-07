import os
import openai
from src.util import get_selected_model 
openai.api_key = os.getenv("OPENAI_API_KEY")

"""
# ==================================================================================================================================================================================
# OpenAI Model Quick Reference Table
#
# A comprehensive guide to OpenAI's model portfolio, including API identifiers, capabilities, pricing, and primary use cases.
# All pricing is per 1 million tokens unless otherwise specified.
# Data is based on the latest available information as of ** September 2025 **.
# ==================================================================================================================================================================================

# | Model Name     | API Model Identifier | Input Modalities        | Input Price ($/1M)              | Output Price ($/1M)             | Context Window | Max Output  | Knowledge Cutoff | Primary Use Case                                                    |
# |----------------|----------------------|-------------------------|---------------------------------|---------------------------------|----------------|-------------|------------------|---------------------------------------------------------------------|
# | gpt-image-1    | `gpt-image-1`        | Text, Image [3]         | $5.00 (Text), $10.00 (Image)    | Priced per image                | N/A            | N/A         | N/A              | Text-to-image and Image-to-image generation/editing.[3]             |
# | gpt-realtime   | `gpt-realtime`       | Text, Audio [3]         | $4.00 (Text), $32.00 (Audio)    | $16.00 (Text), $64.00 (Audio)   | N/A            | N/A         | N/A              | Realtime text and audio processing.[3]                              |
# | o1             | `o1`                 | Text, Image [6]         | $15.00                          | $60.00                          | 200,000 [7]    | 100,000 [7] | Oct 2023         | Specialized, deep STEM and logic reasoning.[6]                      |
# | o3-pro         | `o3-pro`             | Text, Image             | $8.00                           | $32.00                          | 200,000        | 64,000      | Oct 2023         | High-performance STEM and complex problem-solving.                  |
# | o3             | `o3`                 | Text, Image             | $5.00                           | $20.00                          | 200,000        | 64,000      | Oct 2023         | Advanced STEM reasoning and analysis.                               |
# | GPT-4o         | `gpt-4o`             | Text, Image, Audio [1]  | $2.50                           | $10.00                          | 128,000 [1]    | 16,384 [4]  | Oct 2023         | Real-time, native multimodal (text, image, audio) interaction.[1]   |
# | GPT-5          | `gpt-5`              | Text, Image [1]         | $1.25                           | $10.00                          | 400,000 [2]    | 128,000 [2] | Oct 2024         | State-of-the-art reasoning, coding, and agentic tasks.[2]           |
# | GPT-4.1        | `gpt-4.1`            | Text, Image [4]         | $2.00                           | $8.00                           | 1,000,000 [5]  | 16,384      | Jun 2024         | Long-context analysis, high-throughput chat, and coding.[5]         |
# | o3-mini        | `o3-mini`            | Text [8]                | $1.10                           | $4.40                           | 128,000 [8]    | 32,000 [8]  | Oct 2023         | Cost-efficient STEM reasoning.[8]                                   |
# | o4-mini        | `o4-mini`            | Text, Image [1]         | $1.10                           | $4.40                           | 200,000 [1]    | N/A         | Jun 2024         | Fast, cost-efficient reasoning for math and coding.[9]              |
# | GPT-5 mini     | `gpt-5-mini`         | Text, Image [1]         | $0.25                           | $2.00                           | 400,000 [2]    | 128,000 [2] | May 2024         | Faster, cost-efficient reasoning for well-defined tasks.[3]         |
# | GPT-4.1 mini   | `gpt-4.1-mini`       | Text, Image [1]         | $0.40                           | $1.60                           | 1,047,576 [1]  | 16,384      | Jun 2024         | Optimal balance of power, performance, and price.[1]                |
# | GPT-4o mini    | `gpt-4o-mini`        | Text, Image, Audio [1]  | $0.15                           | $0.60                           | 128,000 [1]    | 16,384      | Oct 2023         | Budget-friendly multimodality and chat.[1]                          |
# | GPT-4.1 nano   | `gpt-4.1-nano`       | Text, Image             | $0.10                           | $0.40                           | 1,047,576 [1]  | 16,384      | Jun 2024         | Fastest and cheapest general-purpose model.[1]                      |
# | GPT-5 nano     | `gpt-5-nano`         | Text, Image [1]         | $0.05                           | $0.40                           | 400,000 [2]    | 128,000 [2] | May 2024         | Fastest reasoning for summarization and classification.[3]          |

"""

model_dict = {
    # "img" : "gpt-image-1",
    # "realtime" : "gpt-realtime",
    # "o1" : "o1",
    "o3" : "o3",
    # "o3-p" : "o3-pro",
    "o3-m" : "o3-mini",
    "o4-m" : "o4-mini",
    "4o" : "gpt-4o",
    "4o-m" : "gpt-4o-mini",
    "4.1" : "gpt-4.1",
    "4.1-m" : "gpt-4.1-mini",
    "4.1-n" : "gpt-4.1-nano",
    "5" : "gpt-5",
    "5-m" : "gpt-5-mini",
    "5-n" : "gpt-5-nano"
}

def get_openai_response(prompt, max_completion_tokens=3500):
    return get_openai_multi_response(prompt, max_completion_tokens, n=1)[0]

# Create a single OpenAI client instance to be reused
openai_client = openai.OpenAI()

def get_openai_multi_response(prompt, max_completion_tokens=3500, n=3):
    try:
        model = get_selected_model(model_dict)  # Dynamically fetch the selected model
        response = openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a professional instructional design assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_completion_tokens,
            n=n,
            stop=None
        )
        return [choice.message.content.strip() for choice in response.choices]
    except Exception as e:
        raise RuntimeError(f"An error occurred while communicating with OpenAI: {e}")