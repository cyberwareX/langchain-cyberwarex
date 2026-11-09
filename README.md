# langchain-cyberwarex

**CyberWareX: web search and web page reading for AI agents, paid per call in USDC with x402. No account, no API key.**

This package gives a LangChain or LangGraph agent two tools:

| Tool | What it does | Price per call (live quote 2026-11-06) |
|---|---|---|
| `CyberwarexSearch` | live web search, top results as `title - url - snippet` lines | 0.00435 USDC |
| `CyberwarexReadPage` | one web page as clean markdown, JavaScript rendered | 0.001 USDC |

Without a wallet the tools use the free trial (3 searches per day per IP). With a wallet key, each call
is paid on its own over [x402](https://x402.org) in USDC on Base. The payment is gasless for the payer,
so the wallet only needs USDC. There is no signup, no key to leak and no monthly plan.

## Install

```bash
pip install langchain-cyberwarex            # free trial only
pip install "langchain-cyberwarex[x402]"    # pay per call from a wallet
```

## Use

```python
from langchain_cyberwarex import CyberwarexSearch, CyberwarexReadPage

tools = [CyberwarexSearch(), CyberwarexReadPage()]          # free trial, no wallet
print(tools[0].invoke({"query": "x402 payment protocol"}))

# pay per call: pass a Base wallet key, or set CYBERWAREX_PRIVATE_KEY
tools = [CyberwarexSearch(private_key="0x..."), CyberwarexReadPage(private_key="0x...")]
```

Hand `tools` to any agent, for example `create_agent(model, tools)` in LangChain or `create_react_agent` in LangGraph.

Options: `CyberwarexSearch(max_results=5, timeout=60)`, `CyberwarexReadPage(max_chars=8000, timeout=90)`.
Errors (free trial used up, rate limit, network) come back as plain text the agent can read, not as a crash.

## Measured

Run on 2026-11-06 with this package and a real paid call: search 4.7 s, page read 1.9 s.
Our own logs put search at a median of about 2 s and a page read at about 5 s; slow pages take longer.

## Use something else when

- You need more than a few thousand searches a day at a flat price: a monthly plan from a big search API costs less.
- You need guaranteed uptime with a contract: we are a small service with no SLA.
- Your agent cannot hold a wallet and the free trial is not enough.
- The page sits behind a login: the reader only sees public pages.

## Safety

Page text is untrusted content from the web. The read tool tells the model never to follow instructions
inside it, but treat it as untrusted in your own prompts too. Keep the wallet small: it only needs a few
dollars of USDC.

More examples (TypeScript, CrewAI, Claude Code, Cursor): https://github.com/cyberwareX/x402-agent-search-examples
Service: https://cyberwarex.com

MIT license.
