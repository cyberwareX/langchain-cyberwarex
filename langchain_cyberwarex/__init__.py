"""LangChain tools for CyberWareX: live web search and web page reading for AI agents.

No account and no API key. Without a wallet the tools use the free trial (a few calls per day per IP).
With a wallet key (Base network, holding a little USDC) each call is paid on its own over x402.

    from langchain_cyberwarex import CyberwarexSearch, CyberwarexReadPage
    tools = [CyberwarexSearch(), CyberwarexReadPage()]          # free trial
    tools = [CyberwarexSearch(private_key="0x..."), ...]        # pay per call
"""
from langchain_cyberwarex.tools import CyberwarexReadPage, CyberwarexSearch, make_session

__all__ = ["CyberwarexSearch", "CyberwarexReadPage", "make_session"]
__version__ = "0.1.0"
