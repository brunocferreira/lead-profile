# # leadprofile/tools/page_summary_tool.py
# from crewai.tools import BaseTool
# from pydantic import BaseModel, Field
# import requests
# import json
# from bs4 import BeautifulSoup
# from readability import Document
# from fake_useragent import UserAgent


# class PageInput(BaseModel):
#     url: str = Field(...)


# class PageSummaryTool(BaseTool):
#     name: str = "page_summary"
#     description: str = ("Extrai <title> e resumo (1–2 frases) da página")
#     args_schema: type = PageInput

#     def _run(self, url: str) -> str:
#         html = requests.get(
#             url, headers={"User-Agent": UserAgent().chrome}, timeout=15).text
#         doc = Document(html)
#         title = doc.short_title()
#         soup = BeautifulSoup(doc.summary(), "html.parser")
#         text = " ".join(p.get_text(" ", strip=True)
#                         for p in soup.find_all("p")[:5])
#         summary = text[:350] + "…" if len(text) > 350 else text
#         return json.dumps({"title": title, "summary": summary}, ensure_ascii=False)
