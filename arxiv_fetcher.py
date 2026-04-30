import arxiv
from datetime import datetime
from typing import List, Dict
import logging
from config import Config

logger = logging.getLogger(__name__)

class ArxivFetcher:
    def __init__(self):
        self.client = arxiv.Client()
        self.keywords = Config.SEARCH_KEYWORDS
        
    def fetch_recent_papers(self, max_results: int = 50) -> List[Dict]:
        """
        获取最近提交的符合关键词的论文
        
        Args:
            max_results: 一次最多获取的论文数量。
                         如果 config.py 中有 Config.MAX_RESULTS，可以替换这里的 50。
        """
        try:
            # 1. 构建关键词查询 (全局搜索: 标题、摘要、作者)
            # 例如: all:"Rydberg atom" OR all:"optical tweezers"
            keyword_query = " OR ".join([f'all:"{kw.strip()}"' for kw in self.keywords])
            
            # 使用括号包裹，确保逻辑清晰
            query = f"({keyword_query})"
            
            logger.info(f"搜索查询: {query}")
            
            # 2. 搜索论文，按提交时间降序排列 (获取最新的)
            # 使用 getattr 尝试从 Config 获取最大数量，如果没有则使用默认值
            fetch_limit = getattr(Config, 'MAX_RESULTS', max_results)
            
            search = arxiv.Search(
                query=query,
                max_results=fetch_limit,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )
            
            papers = []
            for result in self.client.results(search):
                paper = {
                    'id': result.get_short_id(),
                    'title': result.title,
                    'authors': [author.name for author in result.authors],
                    'abstract': result.summary,
                    'pdf_url': result.pdf_url,
                    # 将 datetime 对象转换为易读的字符串格式
                    'published': result.published.strftime('%Y-%m-%d %H:%M'),
                    'primary_category': result.primary_category,
                    'categories': result.categories,
                    'arxiv_url': result.entry_id,
                }
                papers.append(paper)
                logger.info(f"找到论文: {paper['title'][:50]}...")
            
            logger.info(f"共找到 {len(papers)} 篇相关论文")
            return papers
            
        except Exception as e:
            logger.error(f"获取论文失败: {e}", exc_info=True) # exc_info=True 有助于打印完整的错误堆栈
            return []
    
    def generate_summary(self, paper: Dict) -> str:
        """生成论文的简要摘要"""
        title = paper['title']
        abstract = paper['abstract']
        
        # 简单总结逻辑
        summary_lines = [
            "=" * 60,
            f"📄 标题: {title}",
            "",
            f"👥 作者: {', '.join(paper['authors'][:3])}{' 等' if len(paper['authors']) > 3 else ''}",
            f"📅 发布时间: {paper['published']}",
            f"📚 分类: {paper['primary_category']}",
            "",
            "📝 摘要:",
            self._truncate_text(abstract, 800) + ("..." if len(abstract) > 800 else ""),
            "",
            "🔗 链接:",
            f"PDF: {paper['pdf_url']}",
            f"Arxiv: {paper['arxiv_url']}",
            "=" * 60,
            ""
        ]
        
        return "\n".join(summary_lines)
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """截断过长的文本，尽量在单词边界处截断"""
        # 移除换行符，使摘要更紧凑
        text = text.replace('\n', ' ') 
        
        if len(text) <= max_length:
            return text
            
        # 寻找在 max_length 之前的最后一个空格进行截断
        truncated = text[:max_length]
        last_space = truncated.rfind(' ')
        
        if last_space > 0:
            return truncated[:last_space]
        return truncated # 如果找不到空格，就直接硬截断
