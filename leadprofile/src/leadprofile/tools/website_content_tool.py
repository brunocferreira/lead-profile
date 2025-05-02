from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import requests
import json
import re
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (LeadProfileHunter/1.0)"}


class WebInput(BaseModel):
    url: str = Field(..., description="URL da página a raspar")


class WebsiteContentTool(BaseTool):
    name: str = "website_content"
    description: str = "Extrai título e resumo simples de uma página web"
    args_schema: type = WebInput

    def _run(self, url: str) -> str:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")

        title = soup.title.string.strip() if soup.title else url

        # pega até 2 parágrafos razoáveis
        paras = [p.get_text(" ", strip=True) for p in soup.find_all("p")
                 if len(p.get_text(strip=True)) > 50][:2]
        summary = " ".join(paras)
        summary = re.sub(r"\s+", " ", summary)[:600]

        return json.dumps({"title": title, "summary": summary}, ensure_ascii=False)
