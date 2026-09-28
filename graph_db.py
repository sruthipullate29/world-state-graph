from neo4j import GraphDatabase


class Neo4jConnector:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(
            uri,
            auth=(user, password)
        )

    def close(self):
        self.driver.close()

    def ingest_graph_data(self, graph_data):

        with self.driver.session() as session:

            # Insert entities
            for entity in graph_data.entities:

                query = f"""
                MERGE (e:{entity.label} {{id: $id}})
                """

                session.run(
                    query,
                    id=entity.id
                )

            # Insert relationships
            for rel in graph_data.relationships:

                query = f"""
                MATCH (s {{id: $source}})
                MATCH (t {{id: $target}})
                MERGE (s)-[r:{rel.relation_type}]->(t)
                SET r.timestamp = $timestamp,
                    r.summary = $summary
                """

                session.run(
                    query,
                    source=rel.source,
                    target=rel.target,
                    timestamp=rel.timestamp,
                    summary=rel.summary
                )

    def fetch_subgraph(self, limit=100):

        with self.driver.session() as session:

            result = session.run(
                """
                MATCH (s)-[r]->(t)
                RETURN
                    s.id AS source,
                    labels(s)[0] AS source_type,
                    type(r) AS relation,
                    r.summary AS summary,
                    t.id AS target,
                    labels(t)[0] AS target_type
                LIMIT $limit
                """,
                limit=limit
            )

            return [
                record.data()
                for record in result
            ]