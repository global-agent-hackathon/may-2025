from agno.vectordb.pgvector import PgVector
from typing import Any, Dict, List, Optional
from sqlalchemy.sql.expression import bindparam, desc, func, select, text
from agno.document import Document
from agno.utils.log import log_debug, logger
from agno.vectordb.distance import Distance
from agno.vectordb.pgvector.index import HNSW, Ivfflat


class CustomPgVector(PgVector):
    """
    Uses modified query to search
    """

    def hybrid_search(
        self,
        query: str,
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        try:
            # Get embedding
            query_embedding = self.embedder.get_embedding(query)
            if query_embedding is None:
                return []

            # Columns to retrieve, must include what's used in `meta_data`
            columns = [
                self.table.c.id,
                self.table.c.name,
                self.table.c.meta_data,
                self.table.c.content,
                self.table.c.embedding,
                self.table.c.usage,
            ]

            # ts_rank
            ts_vector = func.to_tsvector(self.content_language, self.table.c.content)
            ts_query = func.websearch_to_tsquery(self.content_language, bindparam("query", value=query))
            text_rank = func.ts_rank_cd(ts_vector, ts_query)

            # vector distance + score
            vector_distance = self.table.c.embedding.cosine_distance(query_embedding)
            vector_score = 1 / (1 + vector_distance)

            # combine score
            hybrid_score = (
                self.vector_score_weight * vector_score +
                (1 - self.vector_score_weight) * text_rank
            )

            stmt = select(*columns, hybrid_score.label("hybrid_score")).order_by(desc("hybrid_score")).limit(limit)

            log_debug(f"Custom Hybrid Search Query: {stmt}")

            with self.Session() as sess, sess.begin():
                results = sess.execute(stmt).fetchall()

            return [
                Document(
                    id=row.id,
                    name=row.name,
                    content=row.content,
                    embedding=row.embedding,
                    meta_data=row.meta_data or {},
                    embedder=self.embedder,
                    usage=row.usage,
                )
                for row in results
            ]

        except Exception as e:
            logger.error(f"Custom hybrid_search failed: {e}")
            return []