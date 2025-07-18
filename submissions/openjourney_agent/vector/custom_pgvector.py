from agno.vectordb.pgvector import PgVector
from agno.document import Document
from agno.vectordb.distance import Distance
from typing import List, Optional, Dict
from sqlalchemy import select, desc, func, bindparam
from agno.vectordb.search import SearchType
from agno.utils.log import logger

class CustomPgVector(PgVector):
    def hybrid_search(self, query: str, limit: int = 5, filters: Optional[Dict] = None) -> List[Document]:
        try:
            query_embedding = self.embedder.get_embedding(query)
            if query_embedding is None:
                logger.error("Query embedding failed.")
                return []

            # Hybrid scoring: vector + text
            ts_vector = func.to_tsvector(self.content_language, self.table.c.content)
            ts_query = func.websearch_to_tsquery(self.content_language, bindparam("query", value=query))
            text_rank = func.ts_rank_cd(ts_vector, ts_query)

            if self.distance == Distance.cosine:
                vector_distance = self.table.c.embedding.cosine_distance(query_embedding)
                vector_score = 1 / (1 + vector_distance)
            else:
                raise NotImplementedError("Only cosine distance is supported in this CustomPgVector.")

            hybrid_score = (self.vector_score_weight * vector_score) + ((1 - self.vector_score_weight) * text_rank)

            stmt = (
                select(
                    self.table.c.id,
                    self.table.c.name,
                    self.table.c.content,
                    self.table.c.embedding,
                    self.table.c.usage,
                    self.table.c.user_id,
                    self.table.c.profile_name,
                    self.table.c.profile_bio,
                    self.table.c.location,
                    self.table.c.project_title,
                    self.table.c.tech_stack,
                    self.table.c.ai_tools,
                    self.table.c.mrr,
                    hybrid_score.label("hybrid_score")
                )
                .order_by(desc("hybrid_score"))
                .limit(limit)
            )

            with self.Session() as sess, sess.begin():
                results = sess.execute(stmt).fetchall()

            documents = []
            for row in results:
                documents.append(Document(
                    id=row.id,
                    name=row.name,
                    content=row.content,
                    embedding=row.embedding,
                    usage=row.usage,
                    meta_data={
                        "user_id": getattr(row, "user_id", None),
                        "username": getattr(row, "username", None),
                        "profile_name": getattr(row, "profile_name", None),
                        "bio": getattr(row, "profile_bio", None),  # match your view
                        "location": getattr(row, "location", None),
                        "profile_pic": getattr(row, "profile_pic", None),
                        "project_title": getattr(row, "project_title", None),
                        "tech_stack": getattr(row, "tech_stack", None),
                        "ai_tools": getattr(row, "ai_tools", None),
                        "mrr": getattr(row, "mrr", None),
                    },
                    embedder=self.embedder
                ))
            return documents

        except Exception as e:
            logger.error(f"Error in CustomPgVector hybrid_search: {e}")
            return []
