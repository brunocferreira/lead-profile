# agents/web_research_agent.py
import asyncio
import time
import json
from typing import Dict, List
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool
from leadprofile.src.leadprofile.tools.website_content_tool import WebsiteContentTool
from leadprofile.utils.google_queries import build_queries
from pydantic import BaseModel

serper = SerperDevTool()
scraper = WebsiteContentTool()


class WebResult(BaseModel):
    employment: str
    lawsuits: str
    media_mentions: str
    social_profiles: Dict[str, str]
    sources: List[str]


async def fetch_serper(tag: str, q: str):
    start = time.perf_counter()
    res = serper._run(query=q)
    if time.perf_counter() - start > 15:
        return tag, []           # timeout
    return tag, json.loads(res)[:10]


def run_web_research(name: str, city: str = "", state: str = "") -> Dict:
    queries = build_queries(name, city, state)
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(
        asyncio.gather(*(fetch_serper(tag, q) for tag, q in queries))
    )

    links_by_tag = {tag: [r["link"] for r in res] for tag, res in results}

    # --- Scrape cada link (máx 10 / 15 s) ---------------------------------
    texts = []
    for urls in links_by_tag.values():
        start = time.perf_counter()
        for url in urls[:10]:
            if time.perf_counter() - start > 15:
                break
            text_json = json.loads(scraper._run(url))
            texts.append(text_json["summary"])

    # --- Síntese via LLM ---------------------------------------------------
    agent = Agent.from_yaml(
        "../leadprofile/src/leadprofile/config/agents.yaml", "web_researcher"
    )
    synthesis_task = Task(
        description=(
            "Com base nos textos a seguir, identifique:\n"
            "• emprego atual\n• processos judiciais\n• menções na mídia\n\n"
            + "\n".join(texts[:40])
        ),
        expected_output="JSON válido com employment, lawsuits, media_mentions",
        agent=agent,
        output_json=WebResult
    )

    crew = Crew([agent], [synthesis_task], verbose=True)
    res = crew.kickoff()

    data = res.to_dict()
    # Social profiles: pegue primeiro link de cada rede se existir
    data["social_profiles"] = {
        tag: urls[0] for tag, urls in links_by_tag.items()
        if tag in ["linkedin", "instagram", "facebook", "x", "telegram", "discord", "youtube"]
        and urls
    }
    data["sources"] = [u for urls in links_by_tag.values() for u in urls][:15]
    return data
