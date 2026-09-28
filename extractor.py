import os
from typing import List, Literal

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


class Entity(BaseModel):
    id: str = Field(
        description="Unique normalized name, e.g., 'United States', 'Emmanuel Macron'"
    )

    label: Literal[
        "Country",
        "Leader",
        "Organization",
        "Treaty",
        "MilitaryBloc"
    ] = Field(
        description="Category of the entity"
    )


class Relationship(BaseModel):
    source: str = Field(
        description="Normalized ID of source entity"
    )

    target: str = Field(
        description="Normalized ID of target entity"
    )

    relation_type: str = Field(
        description="UPPERCASE relationship type, e.g. SANCTIONED, ALLIED_WITH, SIGNED_PACT"
    )

    timestamp: str = Field(
        description="Event date in YYYY-MM-DD format, or CURRENT"
    )

    summary: str = Field(
        description="One-sentence description of the geopolitical action"
    )


class GeopoliticalKnowledgeGraph(BaseModel):
    entities: List[Entity] = Field(
        description="List of all detected entities"
    )

    relationships: List[Relationship] = Field(
        description="List of directed relationships"
    )


def extract_graph_from_news(news_text: str) -> GeopoliticalKnowledgeGraph:

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    )

    structured_llm = llm.with_structured_output(
        GeopoliticalKnowledgeGraph
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            Extract all geopolitical entities and their directed
            relationships from the news text.

            Identify countries, leaders, organizations, treaties,
            and military blocs.

            Extract meaningful geopolitical relationships such as:
            SANCTIONED
            ALLIED_WITH
            SIGNED_PACT
            EXPELLED_DIPLOMATS
            TRADED_WITH
            ATTACKED
            MET_WITH

            Return only information supported by the provided text.
            """
        ),
        (
            "human",
            "{news_text}"
        )
    ])

    chain = prompt | structured_llm

    return chain.invoke({
        "news_text": news_text
    })