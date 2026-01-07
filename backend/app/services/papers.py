"""Paper discovery service using Semantic Scholar and OpenAlex."""
from typing import Any, Optional

import httpx


class PaperService:
    """Service for discovering and fetching academic papers."""
    
    def __init__(self):
        self.semantic_scholar_url = "https://api.semanticscholar.org/graph/v1"
        self.openalex_url = "https://api.openalex.org"
    
    async def search_papers(
        self,
        query: str,
        limit: int = 20,
        sources: Optional[list[str]] = None,
    ) -> list[dict[str, Any]]:
        """
        Search for papers across multiple sources.
        
        Args:
            query: The search query
            limit: Maximum number of results
            sources: List of sources to search (default: all)
            
        Returns:
            List of papers
        """
        if sources is None:
            sources = ["semantic_scholar", "openalex"]
        
        papers = []
        
        if "semantic_scholar" in sources:
            ss_papers = await self._search_semantic_scholar(query, limit)
            papers.extend(ss_papers)
        
        if "openalex" in sources:
            oa_papers = await self._search_openalex(query, limit)
            papers.extend(oa_papers)
        
        # Deduplicate by title (simple approach)
        seen_titles = set()
        unique_papers = []
        for paper in papers:
            title_lower = paper.get("title", "").lower()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_papers.append(paper)
        
        return unique_papers[:limit]
    
    async def _search_semantic_scholar(
        self,
        query: str,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Search Semantic Scholar for papers.
        
        Args:
            query: The search query
            limit: Maximum number of results
            
        Returns:
            List of papers in standard format
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.semantic_scholar_url}/paper/search",
                    params={
                        "query": query,
                        "limit": limit,
                        "fields": "paperId,title,authors,year,abstract,venue,url,openAccessPdf",
                    },
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()
                
                papers = []
                for paper in data.get("data", []):
                    papers.append({
                        "id": paper.get("paperId", ""),
                        "title": paper.get("title", ""),
                        "authors": [a.get("name", "") for a in paper.get("authors", [])],
                        "year": paper.get("year"),
                        "abstract": paper.get("abstract"),
                        "venue": paper.get("venue"),
                        "url": paper.get("url") or (
                            paper.get("openAccessPdf", {}).get("url") if paper.get("openAccessPdf") else None
                        ),
                        "source": "semantic_scholar",
                    })
                return papers
        except Exception as e:
            print(f"Semantic Scholar search error: {e}")
            return []
    
    async def _search_openalex(
        self,
        query: str,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Search OpenAlex for papers.
        
        Args:
            query: The search query
            limit: Maximum number of results
            
        Returns:
            List of papers in standard format
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.openalex_url}/works",
                    params={
                        "search": query,
                        "per_page": limit,
                        "filter": "is_oa:true",  # Only open access for MVP
                    },
                    headers={"User-Agent": "Flow/1.0 (https://flow.xyz)"},
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()
                
                papers = []
                for work in data.get("results", []):
                    # Get best available URL
                    url = None
                    if work.get("open_access", {}).get("oa_url"):
                        url = work["open_access"]["oa_url"]
                    elif work.get("doi"):
                        url = f"https://doi.org/{work['doi']}"
                    
                    papers.append({
                        "id": work.get("id", "").replace("https://openalex.org/", ""),
                        "title": work.get("title", ""),
                        "authors": [
                            a.get("author", {}).get("display_name", "")
                            for a in work.get("authorships", [])
                        ],
                        "year": work.get("publication_year"),
                        "abstract": work.get("abstract"),
                        "venue": work.get("primary_location", {}).get("source", {}).get("display_name") if work.get("primary_location") else None,
                        "url": url,
                        "source": "openalex",
                    })
                return papers
        except Exception as e:
            print(f"OpenAlex search error: {e}")
            return []
    
    async def get_paper_by_id(
        self,
        paper_id: str,
        source: str = "semantic_scholar",
    ) -> Optional[dict[str, Any]]:
        """
        Get a specific paper by ID.
        
        Args:
            paper_id: The paper identifier
            source: The source to query
            
        Returns:
            The paper data or None
        """
        if source == "semantic_scholar":
            return await self._get_semantic_scholar_paper(paper_id)
        elif source == "openalex":
            return await self._get_openalex_paper(paper_id)
        return None
    
    async def _get_semantic_scholar_paper(
        self,
        paper_id: str,
    ) -> Optional[dict[str, Any]]:
        """Get a paper from Semantic Scholar by ID."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.semantic_scholar_url}/paper/{paper_id}",
                    params={
                        "fields": "paperId,title,authors,year,abstract,venue,url,openAccessPdf,tldr",
                    },
                    timeout=30.0,
                )
                response.raise_for_status()
                paper = response.json()
                
                return {
                    "id": paper.get("paperId", ""),
                    "title": paper.get("title", ""),
                    "authors": [a.get("name", "") for a in paper.get("authors", [])],
                    "year": paper.get("year"),
                    "abstract": paper.get("abstract"),
                    "venue": paper.get("venue"),
                    "url": paper.get("url") or (
                        paper.get("openAccessPdf", {}).get("url") if paper.get("openAccessPdf") else None
                    ),
                    "source": "semantic_scholar",
                    "tldr": paper.get("tldr", {}).get("text") if paper.get("tldr") else None,
                }
        except Exception:
            return None
    
    async def _get_openalex_paper(
        self,
        paper_id: str,
    ) -> Optional[dict[str, Any]]:
        """Get a paper from OpenAlex by ID."""
        try:
            async with httpx.AsyncClient() as client:
                # OpenAlex IDs are URLs, but we store just the ID
                full_id = f"https://openalex.org/{paper_id}" if not paper_id.startswith("http") else paper_id
                response = await client.get(
                    full_id,
                    headers={"User-Agent": "Flow/1.0 (https://flow.xyz)"},
                    timeout=30.0,
                )
                response.raise_for_status()
                work = response.json()
                
                url = None
                if work.get("open_access", {}).get("oa_url"):
                    url = work["open_access"]["oa_url"]
                elif work.get("doi"):
                    url = f"https://doi.org/{work['doi']}"
                
                return {
                    "id": work.get("id", "").replace("https://openalex.org/", ""),
                    "title": work.get("title", ""),
                    "authors": [
                        a.get("author", {}).get("display_name", "")
                        for a in work.get("authorships", [])
                    ],
                    "year": work.get("publication_year"),
                    "abstract": work.get("abstract"),
                    "venue": work.get("primary_location", {}).get("source", {}).get("display_name") if work.get("primary_location") else None,
                    "url": url,
                    "source": "openalex",
                }
        except Exception:
            return None
