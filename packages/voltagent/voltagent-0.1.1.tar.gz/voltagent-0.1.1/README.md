# VoltAgent Python SDK

Modern, type-safe, and async-ready Python SDK for AI agent observability and tracing. Track your LLM workflows, agent interactions, and tool usage with comprehensive telemetry.

## 🚀 Quick Start

```bash
pip install voltagent
```

### Context Manager Usage (Recommended)

```python
import asyncio
from voltagent import VoltAgentSDK

async def main():
    sdk = VoltAgentSDK(
        base_url="https://api.voltagent.dev",
        public_key="your-public-key",
        secret_key="your-secret-key",
        auto_flush=True,
        flush_interval=5
    )

    # Start a trace (conversation/session) with automatic resource management
    async with sdk.trace(
        agentId="customer-support-v1",
        input={"query": "How to reset my password?"},
        userId="user-123",
        conversationId="conv-456",
        tags=["support", "password-reset"]
    ) as trace:

        # Add an agent with automatic completion
        async with trace.add_agent({
            "name": "Support Agent",
            "input": {"task": "Handle password reset request"},
            "instructions": "You are a helpful customer support agent.",
            "metadata": {
                "model_parameters": {"model": "gpt-4"}
            }
        }) as agent:

            # Use a tool
            tool = await agent.add_tool({
                "name": "knowledge-base-search",
                "input": {"query": "password reset procedure"}
            })

            await tool.success(
                output={
                    "results": ["Reset via email", "Reset via SMS"],
                    "relevance_score": 0.89
                }
            )

            # Complete the workflow - agent auto-completes when exiting context
            await agent.success(
                output={"response": "Password reset link sent!"},
                usage={"prompt_tokens": 150, "completion_tokens": 85, "total_tokens": 235}
            )

        # Trace auto-completes when exiting context

asyncio.run(main())
```

### Manual Usage (For Advanced Control)

```python
import asyncio
from voltagent import VoltAgentSDK, TraceStatus

async def manual_example():
    sdk = VoltAgentSDK(
        base_url="https://api.voltagent.dev",
        public_key="your-public-key",
        secret_key="your-secret-key"
    )

    trace = None
    agent = None

    try:
        # Manually create trace
        trace = await sdk.create_trace(
            agentId="customer-support-v1",
            input={"query": "How to reset my password?"},
            userId="user-123",
            conversationId="conv-456",
            tags=["support", "password-reset"]
        )

        # Manually add agent
        agent = await trace.add_agent({
            "name": "Support Agent",
            "input": {"task": "Handle password reset request"},
            "instructions": "You are a helpful customer support agent.",
            "metadata": {
                "model_parameters": {"model": "gpt-4"}
            }
        })

        # Use a tool
        tool = await agent.add_tool({
            "name": "knowledge-base-search",
            "input": {"query": "password reset procedure"}
        })

        await tool.success(
            output={
                "results": ["Reset via email", "Reset via SMS"],
                "relevance_score": 0.89
            }
        )

        # Manually complete agent
        await agent.success(
            output={"response": "Password reset link sent!"},
            usage={"prompt_tokens": 150, "completion_tokens": 85, "total_tokens": 235}
        )

        # Manually end trace
        await trace.end(
            output={"support_completed": True},
            status=TraceStatus.COMPLETED
        )

    except Exception as e:
        # Manual error handling
        if agent:
            await agent.error(status_message=f"Agent failed: {e}")
        if trace:
            await trace.end(status=TraceStatus.ERROR, metadata={"error": str(e)})
    finally:
        await sdk.shutdown()

asyncio.run(manual_example())
```

## 🎯 Usage Patterns: When to Use Which Approach

### Context Manager Usage (Recommended for Most Cases)

**Best for:**
- ✅ Simple workflows and standard use cases
- ✅ Automatic resource cleanup and error handling
- ✅ Cleaner, more Pythonic code
- ✅ Built-in exception handling and trace completion
- ✅ Reduced boilerplate code

**Example scenarios:**
- Standard chat bot interactions
- Simple data processing workflows
- API integrations with straightforward error handling
- Most production applications

### Manual Usage (For Advanced Control)

**Best for:**
- ✅ Long-running processes that need checkpoints
- ✅ Complex error handling and recovery scenarios
- ✅ Custom resource management requirements
- ✅ Integration with existing error handling systems
- ✅ Batch processing with progress tracking
- ✅ When you need granular control over trace lifecycle

**Example scenarios:**
- Data pipeline processing with checkpoints
- Multi-stage workflows with custom retry logic
- Integration with enterprise error handling systems
- Real-time streaming applications
- Background job processing

### Event Hierarchy

```
Trace
├── Agent 1
│   ├── Tool 1 → success/error
│   ├── Memory 1 → success/error
│   ├── Sub-Agent 1.1
│   │   └── Tool 1.1.1 → success/error
│   └── Agent 1 → success/error
└── Agent 2
    └── Retriever 1 → success/error
```


### Environment Variables

Set these environment variables for easy configuration:

```bash
export VOLTAGENT_BASE_URL="https://api.voltagent.dev"
export VOLTAGENT_PUBLIC_KEY="your-public-key"
export VOLTAGENT_SECRET_KEY="your-secret-key"
```

## 📚 Step-by-Step Guide

### 1. Initialize the SDK

```python
from voltagent import VoltAgentSDK

sdk = VoltAgentSDK(
    base_url="https://api.voltagent.dev",
    public_key="your-public-key",
    secret_key="your-secret-key",
    auto_flush=True,
    flush_interval=5,
    timeout=30
)
```

> **Prerequisites**: Create an account at [https://console.voltagent.dev/](https://console.voltagent.dev/) and set up an organization and project to get your API keys.

### 2. Create a Trace

A trace represents one complete agent execution session. Every agent operation must happen within a trace.

```python
async with sdk.trace(
    agentId="customer-support-v1",
    input={"query": "How to reset password?"},
    userId="user-123",
    conversationId="conv-456",
    tags=["support", "password-reset"],
    metadata={
        "priority": "high",
        "source": "web-chat"
    }
) as trace:
    # Your agent operations here
    pass
```

### 3. Add an Agent to the Trace

```python
async with trace.add_agent({
    "name": "Support Agent",
    "input": {"query": "User needs password reset help"},
    "instructions": "You are a customer support agent specialized in helping users with account issues.",
    "metadata": {
        "model_parameters": {
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 1000
        },
        "role": "customer-support",
        "specialization": "account-issues"
    }
}) as agent:
    # Agent operations here
    pass
```

### 4. Add Tools, Memory, and Retrievers

#### Tools (External API calls)

```python
search_tool = await agent.add_tool({
    "name": "knowledge-base-search",
    "input": {
        "query": "password reset procedure",
        "max_results": 5
    },
    "metadata": {
        "search_type": "semantic",
        "database": "support-kb"
    }
})

# Tool success
await search_tool.success(
    output={
        "results": ["Reset via email", "Reset via SMS", "Contact support"],
        "count": 3,
        "relevance_score": 0.89
    },
    metadata={
        "search_time": "0.2s",
        "index_used": "support-kb-v2"
    }
)

# Tool error (if needed)
await search_tool.error(
    status_message=Exception("Database connection timeout"),
    metadata={
        "database": "support-kb",
        "timeout_ms": 5000
    }
)
```

#### Memory Operations

```python
memory_op = await agent.add_memory({
    "name": "user-context-storage",
    "input": {
        "key": "user_123_context",
        "value": {
            "last_login": "2024-01-15",
            "account_type": "premium"
        },
        "ttl": 3600
    },
    "metadata": {
        "type": "redis",
        "region": "us-east-1"
    }
})

await memory_op.success(
    output={
        "stored": True,
        "key": "user_123_context",
        "expires_at": "2024-01-15T15:00:00Z"
    },
    metadata={
        "cache_hit": False,
        "storage_latency": "2ms"
    }
)
```

#### Retrieval Operations

```python
retriever = await agent.add_retriever({
    "name": "policy-document-retriever",
    "input": {
        "query": "password reset policy for premium users",
        "max_documents": 3,
        "threshold": 0.8
    },
    "metadata": {
        "vector_store": "pinecone",
        "embedding_model": "text-embedding-ada-002"
    }
})

await retriever.success(
    output={
        "documents": [
            "Premium users can reset passwords instantly via email",
            "Password reset requires 2FA verification for premium accounts"
        ],
        "relevance_scores": [0.95, 0.88]
    },
    metadata={
        "search_time": "0.3s",
        "documents_scanned": 1500
    }
)
```

### 5. Working with Sub-Agents

Create hierarchical agent structures for complex workflows:

```python
# Create a sub-agent under the main agent
async with agent.add_agent({
    "name": "Policy Checker",
    "input": {
        "user_id": "user-123",
        "request_type": "password-reset"
    },
    "instructions": "You verify customer requests against company policies.",
    "metadata": {
        "role": "policy-verification",
        "parent_agent": agent.id,
        "model_parameters": {"model": "gpt-4"}
    }
}) as policy_checker:

    # Add a tool to the sub-agent
    verification_tool = await policy_checker.add_tool({
        "name": "policy-verification",
        "input": {"user_id": "user-123", "action": "password-reset"}
    })

    await verification_tool.success(
        output={"policy_compliant": True, "required_verification": "2fa-sms"}
    )

    # Complete the sub-agent
    await policy_checker.success(
        output={
            "policy_compliant": True,
            "approval_granted": True
        },
        usage={
            "prompt_tokens": 85,
            "completion_tokens": 45,
            "total_tokens": 130
        },
        metadata={
            "policies_checked": ["password-policy", "premium-user-policy"],
            "compliance_score": 0.95
        }
    )
```

### 6. Complete the Agent and Trace

```python
# Complete the main agent
await agent.success(
    output={
        "response": "Password reset link sent to user's email",
        "action_taken": "email-reset-link",
        "user_satisfied": True
    },
    usage={
        "prompt_tokens": 150,
        "completion_tokens": 85,
        "total_tokens": 235
    },
    metadata={
        "response_time": "2.1s",
        "confidence_score": 0.95
    }
)

# Trace automatically completes when exiting context manager
```

## 📚 API Reference

### SDK Initialization

```python
sdk = VoltAgentSDK(
    base_url: str,
    public_key: str,
    secret_key: str,
    auto_flush: bool = True,        # Enable automatic event flushing
    flush_interval: int = 5,        # Flush every 5 seconds
    timeout: int = 30,              # Request timeout in seconds
    max_retries: int = 3,           # Maximum retries for failed requests
    retry_delay: float = 1.0        # Delay between retries
)
```

### Creating Traces

```python
async with sdk.trace(
    agentId: str,                   # The main agent identifier
    input: Optional[Dict] = None,   # Input data for the trace
    userId: Optional[str] = None,   # User identifier
    conversationId: Optional[str] = None,  # Conversation identifier
    metadata: Optional[Dict] = None,       # Additional metadata
    tags: Optional[List[str]] = None       # Tags for filtering
) as trace:
    # Your trace operations
    pass
```

### Trace Operations

```python
# Update trace metadata
await trace.update(
    status: Optional[str] = None,
    metadata: Optional[Dict] = None
)

# End trace manually (usually not needed with context managers)
await trace.end(
    output: Optional[Dict] = None,
    status: str = "completed",
    usage: Optional[Dict] = None,
    metadata: Optional[Dict] = None
)

# Add agents to trace
async with trace.add_agent({
    "name": str,
    "input": Optional[Dict],
    "instructions": Optional[str],
    "metadata": Optional[Dict]
}) as agent:
    pass
```

### Agent Operations

```python
# Add sub-agents
async with agent.add_agent(options) as sub_agent:
    pass

# Add tools
tool = await agent.add_tool({
    "name": str,
    "input": Optional[Dict],
    "metadata": Optional[Dict]
})

# Add memory operations
memory = await agent.add_memory({
    "name": str,
    "input": Optional[Dict],
    "metadata": Optional[Dict]
})

# Add retrieval operations
retriever = await agent.add_retriever({
    "name": str,
    "input": Optional[Dict],
    "metadata": Optional[Dict]
})

# Complete agent - Success
await agent.success(
    output: Optional[Dict] = None,
    usage: Optional[Dict] = None,  # {prompt_tokens, completion_tokens, total_tokens}
    metadata: Optional[Dict] = None
)

# Complete agent - Error
await agent.error(
    status_message: Union[str, Exception, Dict],
    metadata: Optional[Dict] = None
)
```

### Tool/Memory/Retriever Operations

```python
# Success completion
await tool.success(
    output: Optional[Dict] = None,
    metadata: Optional[Dict] = None
)

await memory.success(
    output: Optional[Dict] = None,
    metadata: Optional[Dict] = None
)

await retriever.success(
    output: Optional[Dict] = None,
    metadata: Optional[Dict] = None
)

# Error handling
await tool.error(
    status_message: Union[str, Exception, Dict],
    metadata: Optional[Dict] = None
)

await memory.error(
    status_message: Union[str, Exception, Dict],
    metadata: Optional[Dict] = None
)

await retriever.error(
    status_message: Union[str, Exception, Dict],
    metadata: Optional[Dict] = None
)
```

## 🔧 Usage Examples

### Simple Weather Agent (Context Manager)

```python
import asyncio
from voltagent import VoltAgentSDK

async def weather_example():
    sdk = VoltAgentSDK(
        base_url="https://api.voltagent.dev",
        public_key="your-public-key",
        secret_key="your-secret-key"
    )

    async with sdk.trace(
        agentId="weather-agent-v1",
        input={"query": "Weather in Istanbul?"},
        tags=["weather", "query"]
    ) as trace:

        async with trace.add_agent({
            "name": "Weather Agent",
            "instructions": "You provide accurate weather information.",
            "metadata": {"model_parameters": {"model": "gpt-4"}}
        }) as agent:

            # Call weather API
            weather_tool = await agent.add_tool({
                "name": "weather_api",
                "input": {"city": "Istanbul"}
            })

            await weather_tool.success(
                output={
                    "temperature": 22,
                    "condition": "sunny",
                    "humidity": 65
                }
            )

            # Save to memory
            memory = await agent.add_memory({
                "name": "cache_weather",
                "input": {
                    "key": "istanbul_weather",
                    "value": {"temp": 22, "condition": "sunny"}
                }
            })

            await memory.success(
                output={"cached": True, "expires_in": 3600}
            )

            await agent.success(
                output={"response": "It's 22°C and sunny in Istanbul!"},
                usage={"prompt_tokens": 50, "completion_tokens": 25, "total_tokens": 75}
            )

asyncio.run(weather_example())
```

### Simple Weather Agent (Manual Control)

```python
import asyncio
from voltagent import VoltAgentSDK, TraceStatus

async def manual_weather_example():
    sdk = VoltAgentSDK(
        base_url="https://api.voltagent.dev",
        public_key="your-public-key",
        secret_key="your-secret-key"
    )

    trace = None
    agent = None

    try:
        # Manually create trace
        trace = await sdk.create_trace(
            agentId="weather-agent-manual",
            input={"query": "Weather in Istanbul?"},
            tags=["weather", "manual"]
        )

        # Manually add agent
        agent = await trace.add_agent({
            "name": "Weather Agent Manual",
            "instructions": "You provide accurate weather information.",
            "metadata": {"model_parameters": {"model": "gpt-4"}}
        })

        # Call weather API
        weather_tool = await agent.add_tool({
            "name": "weather_api",
            "input": {"city": "Istanbul"}
        })

        await weather_tool.success(
            output={
                "temperature": 22,
                "condition": "sunny",
                "humidity": 65
            }
        )

        # Save to memory
        memory = await agent.add_memory({
            "name": "cache_weather",
            "input": {
                "key": "istanbul_weather",
                "value": {"temp": 22, "condition": "sunny"}
            }
        })

        await memory.success(
            output={"cached": True, "expires_in": 3600}
        )

        # Manually complete agent
        await agent.success(
            output={"response": "It's 22°C and sunny in Istanbul!"},
            usage={"prompt_tokens": 50, "completion_tokens": 25, "total_tokens": 75}
        )

        # Manually end trace
        await trace.end(
            output={"weather_provided": True, "city": "Istanbul"},
            status=TraceStatus.COMPLETED
        )

    except Exception as e:
        if agent:
            await agent.error(status_message=f"Weather agent failed: {e}")
        if trace:
            await trace.end(status=TraceStatus.ERROR, metadata={"error": str(e)})
    finally:
        await sdk.shutdown()

asyncio.run(manual_weather_example())
```

### Multi-Agent Research Workflow (Context Manager)

```python
async def research_workflow():
    sdk = VoltAgentSDK(
        base_url="https://api.voltagent.dev",
        public_key="your-public-key",
        secret_key="your-secret-key"
    )

    async with sdk.trace(
        agentId="research-orchestrator",
        input={"topic": "AI trends 2024"},
        tags=["research", "ai-trends"]
    ) as trace:

        # Research agent
        async with trace.add_agent({
            "name": "Research Agent",
            "instructions": "You research and gather information on given topics.",
            "metadata": {"model_parameters": {"model": "gpt-4"}}
        }) as researcher:

            search = await researcher.add_retriever({
                "name": "web_search",
                "input": {"query": "AI trends 2024", "max_results": 10}
            })

            await search.success(
                output={
                    "documents": ["AI trend doc 1", "AI trend doc 2"],
                    "relevance_scores": [0.9, 0.8],
                    "total_results": 10
                }
            )

            await researcher.success(
                output={"research_complete": True, "documents_found": 10},
                usage={"prompt_tokens": 200, "completion_tokens": 150, "total_tokens": 350}
            )

        # Summary agent
        async with trace.add_agent({
            "name": "Summary Agent",
            "instructions": "You create comprehensive summaries from research data.",
            "metadata": {"model_parameters": {"model": "gpt-4"}}
        }) as summarizer:

            # Translation sub-agent
            async with summarizer.add_agent({
                "name": "Translation Agent",
                "instructions": "You translate content to different languages.",
                "metadata": {"model_parameters": {"model": "gpt-3.5-turbo"}}
            }) as translator:

                translate_tool = await translator.add_tool({
                    "name": "translate_api",
                    "input": {"text": "AI trends summary", "target_language": "tr"}
                })

                await translate_tool.success(
                    output={"translated_text": "AI eğilimleri özeti..."}
                )

                await translator.success(
                    output={"translation": "Turkish translation completed"},
                    usage={"prompt_tokens": 100, "completion_tokens": 80, "total_tokens": 180}
                )

            await summarizer.success(
                output={"summary": "Comprehensive AI trends summary with translation"},
                usage={"prompt_tokens": 300, "completion_tokens": 200, "total_tokens": 500}
            )

asyncio.run(research_workflow())
```

### Multi-Agent Research Workflow (Manual Control)

```python
async def manual_research_workflow():
    sdk = VoltAgentSDK(
        base_url="https://api.voltagent.dev",
        public_key="your-public-key",
        secret_key="your-secret-key"
    )

    trace = None
    researcher = None
    summarizer = None
    translator = None

    try:
        # Manually create trace
        trace = await sdk.create_trace(
            agentId="research-orchestrator-manual",
            input={"topic": "AI trends 2024"},
            tags=["research", "ai-trends", "manual"]
        )

        # Manually create research agent
        researcher = await trace.add_agent({
            "name": "Research Agent Manual",
            "instructions": "You research and gather information on given topics.",
            "metadata": {"model_parameters": {"model": "gpt-4"}}
        })

        search = await researcher.add_retriever({
            "name": "web_search",
            "input": {"query": "AI trends 2024", "max_results": 10}
        })

        await search.success(
            output={
                "documents": ["AI trend doc 1", "AI trend doc 2"],
                "relevance_scores": [0.9, 0.8],
                "total_results": 10
            }
        )

        # Manually complete research agent
        await researcher.success(
            output={"research_complete": True, "documents_found": 10},
            usage={"prompt_tokens": 200, "completion_tokens": 150, "total_tokens": 350}
        )

        # Manually create summary agent
        summarizer = await trace.add_agent({
            "name": "Summary Agent Manual",
            "instructions": "You create comprehensive summaries from research data.",
            "metadata": {"model_parameters": {"model": "gpt-4"}}
        })

        # Manually create translation sub-agent
        translator = await summarizer.add_agent({
            "name": "Translation Agent Manual",
            "instructions": "You translate content to different languages.",
            "metadata": {"model_parameters": {"model": "gpt-3.5-turbo"}}
        })

        translate_tool = await translator.add_tool({
            "name": "translate_api",
            "input": {"text": "AI trends summary", "target_language": "tr"}
        })

        await translate_tool.success(
            output={"translated_text": "AI eğilimleri özeti..."}
        )

        # Manually complete translation agent
        await translator.success(
            output={"translation": "Turkish translation completed"},
            usage={"prompt_tokens": 100, "completion_tokens": 80, "total_tokens": 180}
        )

        # Manually complete summary agent
        await summarizer.success(
            output={"summary": "Comprehensive AI trends summary with translation"},
            usage={"prompt_tokens": 300, "completion_tokens": 200, "total_tokens": 500}
        )

        # Manually end trace
        await trace.end(
            output={
                "research_completed": True,
                "agents_used": 3,
                "total_documents": 10,
                "translation_completed": True
            },
            status=TraceStatus.COMPLETED,
            usage={"prompt_tokens": 600, "completion_tokens": 430, "total_tokens": 1030}
        )

    except Exception as e:
        # Manual cascade error handling
        if translator:
            await translator.error(status_message=f"Translation failed: {e}")
        if summarizer:
            await summarizer.error(status_message=f"Summary failed: {e}")
        if researcher:
            await researcher.error(status_message=f"Research failed: {e}")
        if trace:
            await trace.end(status=TraceStatus.ERROR, metadata={"error": str(e)})
    finally:
        await sdk.shutdown()

asyncio.run(manual_research_workflow())
```

### Error Handling

```python
async def error_handling_example():
    sdk = VoltAgentSDK(
        base_url="https://api.voltagent.dev",
        public_key="your-public-key",
        secret_key="your-secret-key"
    )

    async with sdk.trace(
        agentId="test-agent",
        input={"task": "risky operation"}
    ) as trace:

        async with trace.add_agent({
            "name": "Risky Agent",
            "instructions": "You handle operations that might fail."
        }) as agent:

            risky_tool = await agent.add_tool({
                "name": "external_api",
                "input": {"endpoint": "https://unreliable-api.com"}
            })

            try:
                # Simulate API call that might fail
                result = await call_external_api()
                await risky_tool.success(
                    output=result,
                    metadata={"response_time": "1.2s"}
                )

                await agent.success(
                    output={"result": "Operation completed successfully"}
                )

            except Exception as error:
                # Handle tool error
                await risky_tool.error(
                    status_message=error,
                    metadata={
                        "error_code": "API_TIMEOUT",
                        "retry_attempts": 3
                    }
                )

                # Handle agent error
                await agent.error(
                    status_message="Agent failed due to tool error",
                    metadata={
                        "failed_tool": "external_api",
                        "error_type": "TIMEOUT"
                    }
                )

asyncio.run(error_handling_example())
```

## 💡 Best Practices

### General Guidelines

1. **Use meaningful names** for traces, agents, tools, and operations to improve debugging
2. **Include relevant metadata** for debugging and analytics, but avoid sensitive data
3. **Track token usage** in the `usage` parameter for proper cost tracking
4. **Handle errors properly** with descriptive error messages and relevant context
5. **Use hierarchical agents** for complex workflows to maintain clear operation flow
6. **Set appropriate tags** on traces for easy filtering and search in the dashboard
7. **Use structured error objects** instead of plain strings for better error analysis
8. **Include timing metadata** for performance monitoring and optimization
9. **Group related operations** under the same agent for logical organization
10. **Use snake_case in Python** - the SDK automatically converts to camelCase for the API
11. **Call `await sdk.shutdown()`** before your application exits to ensure all events are sent

### Error Handling Patterns

**Context Manager Error Handling:**
```python
async with sdk.trace(agentId="error-prone") as trace:
    async with trace.add_agent({"name": "Worker"}) as agent:
        try:
            # Risky operation
            result = await risky_api_call()
            await tool.success(output=result)
        except Exception as e:
            # Handle specific tool errors
            await tool.error(status_message=e)
            # Context manager will handle agent/trace errors automatically
```

**Manual Error Handling:**
```python
trace = None
agent = None
try:
    trace = await sdk.create_trace(agentId="error-prone")
    agent = await trace.add_agent({"name": "Worker"})

    result = await risky_api_call()
    await agent.success(output=result)
    await trace.end(status=TraceStatus.COMPLETED)

except Exception as e:
    # Cascade error handling
    if agent:
        await agent.error(status_message=f"Agent failed: {e}")
    if trace:
        await trace.end(
            status=TraceStatus.ERROR,
            metadata={"error": str(e), "error_type": type(e).__name__}
        )
finally:
    await sdk.shutdown()
```

## 🧪 Testing & Development

### Running Tests

```bash
# Install development dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=voltagent --cov-report=html
```

### Running Examples

```bash
cd voltagent-python

# Context manager examples (recommended for most users)
python examples/comprehensive_trace_example.py

# Manual usage examples (for advanced control scenarios)
python examples/manual_usage_examples.py
```

### Code Quality

```bash
# Format code
black .
isort .

# Type checking
mypy .

# Linting
flake8 .
```

## 🏗️ Project Structure

```
voltagent-python/
├── voltagent/
│   ├── __init__.py          # Main package exports
│   ├── types.py             # Pydantic models and types
│   ├── client.py            # HTTP client (VoltAgentCoreAPI)
│   └── sdk.py               # High-level SDK (VoltAgentSDK)
├── tests/                   # Comprehensive test suite
├── examples/                # Usage examples
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Run linting and type checking
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 🔗 Links

- [VoltAgent Platform](https://voltagent.dev)
- [Console Dashboard](https://console.voltagent.dev)
- [Documentation](https://docs.voltagent.dev)

## 📄 License

MIT License - see LICENSE file for details.
