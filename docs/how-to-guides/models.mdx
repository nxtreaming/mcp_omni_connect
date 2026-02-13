# Model Support

OmniCoreAgent uses **LiteLLM** under the hood, giving you unified access to over 100+ AI models from all major providers. You can switch between providers simply by changing the `model_config`.

---

## Supported Providers

| Provider | Prefix | Example Model |
|----------|--------|---------------|
| **OpenAI** | (none) | `gpt-4o`, `gpt-4-turbo` |
| **Anthropic** | `anthropic/` | `anthropic/claude-3-5-sonnet-20240620` |
| **Google** | `gemini/` | `gemini/gemini-pro`, `gemini/gemini-1.5-flash` |
| **Groq** | `groq/` | `groq/llama3-70b-8192` |
| **DeepSeek** | `deepseek/` | `deepseek/deepseek-chat` |
| **Azure OpenAI** | `azure/` | `azure/your-deployment-name` |
| **Bedrock** | `bedrock/` | `bedrock/anthropic.claude-3-sonnet-20240229-v1:0` |
| **Local (Ollama)**| `ollama/` | `ollama/llama3` |

---

## Configuration

To use a specific model, pass its configuration to the `OmniCoreAgent`.

### Example: Anthropic Claude

```python
agent = OmniCoreAgent(
    ...
    model_config={
        "provider": "anthropic",
        "model": "claude-3-5-sonnet-20240620",
        "temperature": 0.7
    }
)
```

### Example: Google Gemini

```python
agent = OmniCoreAgent(
    ...
    model_config={
        "provider": "google",
        "model": "gemini-1.5-pro",
        "max_tokens": 8000
    }
)
```

---

## Authentication

Each provider requires its own API key, typically set as an environment variable.

| Provider | Environment Variable |
|----------|----------------------|
| OpenAI | `OPENAI_API_KEY` |
| Anthropic | `ANTHROPIC_API_KEY` |
| Google | `GEMINI_API_KEY` |
| Groq | `GROQ_API_KEY` |
| DeepSeek | `DEEPSEEK_API_KEY` |

---

## Advanced Model Settings

You can pass any [LiteLLM-supported parameter](https://docs.litellm.ai/docs/completion/input) in the `model_config` dictionary:

- `temperature`: controls randomness (0.0 to 1.0).
- `max_tokens`: limits the length of the response.
- `top_p`: nucleus sampling.
- `frequency_penalty` & `presence_penalty`.
- `api_base`: for custom endpoints (e.g., self-hosted vLLM).

---

## Best Practices

- **Reliability**: Use a provider like OpenAI or Anthropic for complex ReAct tasks that require high-quality tool calling.
- **Cost Efficiency**: Use models like `gpt-4o-mini` or `gemini-1.5-flash` for background processing or simple classification.
- **Local Development**: Use **Ollama** during development to test agent logic without incurring API costs.
