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
        
    def fetch_recent_papers(self, days_back: int = 1, max_results: int = 50) -> List[Dict]:
        """获取符合关键词的论文"""
        try:
            from datetime import timedelta # 确保导入了 timedelta
            
            # 1. 基础关键词查询
            keyword_query = " OR ".join([f'all:"{kw.strip()}"' for kw in self.keywords])
            query = f"({keyword_query})"
            
            # === 新增：动态时间限制逻辑 ===
            if days_back > 0:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days_back)
                date_range = f"[{start_date.strftime('%Y%m%d')} TO {end_date.strftime('%Y%m%d')}]"
                query += f" AND submittedDate:{date_range}"
            
            logger.info(f"搜索查询: {query}")
            
            fetch_limit = getattr(Config, 'MAX_RESULTS', max_results)
            
            search = arxiv.Search(
                query=query,
                max_results=fetch_limit,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )
            
            # ... 下面的解析和返回逻辑保持不变 ...
            
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
