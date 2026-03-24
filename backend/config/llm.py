from groq import Groq
import os

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Primary model configuration (Llama 3 70B)
PRIMARY_MODEL = "llama3-70b-8192"

# Fallback model configuration (Mixtral)
FALLBACK_MODEL = "mixtral-8x7b-32768"

# Model temperature settings
DEFAULT_TEMPERATURE = 0.3
LOW_TEMPERATURE = 0.1




# Model instances for agno compatibility
from agno.models.groq import Groq as GroqModel

model = GroqModel(
    id=PRIMARY_MODEL,
    api_key=os.getenv("GROQ_API_KEY")
)

model2 = GroqModel(
    id=FALLBACK_MODEL,
    api_key=os.getenv("GROQ_API_KEY")
)

def get_groq_completion(
    messages,
    model=PRIMARY_MODEL,
    temperature=DEFAULT_TEMPERATURE,
    max_tokens=8096
):
    """
    Get completion from Groq API
    
    Args:
        messages: List of message dictionaries with 'role' and 'content'
        model: Model ID (default: llama3-70b-8192)
        temperature: Sampling temperature
        max_tokens: Maximum tokens in response
        
    Returns:
        Response content string
    """
    try:
        response = groq_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        # Try fallback model if primary fails
        if model == PRIMARY_MODEL:
            print(f"Primary model failed, trying fallback: {str(e)}")
            response = groq_client.chat.completions.create(
                model=FALLBACK_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        raise
