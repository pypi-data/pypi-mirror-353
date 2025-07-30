#!/usr/bin/env python3
"""
Script to load SNOMED CT RF2 files into Neo4j.
"""

import csv
import logging
import os
import sys
import time
from pathlib import Path

from neo4j import Session
from tqdm import tqdm

from snomed_neo4j_core.client import get_driver
from snomed_neo4j_core.models import Concept, Description, Relationship
from snomed_neo4j_core.utils import env_bool


def find_rf2_files(data_dir: Path) -> dict[str, Path]:
    """Find RF2 files in the data directory."""

    logging.info(f"Searching for RF2 files in: {data_dir}")

    data_path = Path(data_dir)
    snapshot_dirs = list(data_path.glob("**/Snapshot"))

    if not snapshot_dirs:
        logging.error(f"Could not find Snapshot directory in the provided data path: {data_dir}")
        sys.exit(1)

    snapshot_dir = snapshot_dirs[0]

    concept_file = list(snapshot_dir.glob("**/sct2_Concept_Snapshot*.txt"))
    description_file = list(snapshot_dir.glob("**/sct2_Description_Snapshot*.txt"))
    relationship_file = list(snapshot_dir.glob("**/sct2_Relationship_Snapshot*.txt"))

    if not concept_file or not description_file or not relationship_file:
        logging.error("Could not find all required RF2 files.")
        sys.exit(1)

    return {"concept": concept_file[0], "description": description_file[0], "relationship": relationship_file[0]}


def setup_neo4j_schema(session: Session) -> None:
    """Set up Neo4j schema with indexes and constraints."""
    logging.info("Setting up Neo4j schema...")

    # Create constraints
    session.run("""
        CREATE CONSTRAINT concept_id IF NOT EXISTS
        FOR (c:Concept) REQUIRE c.id IS UNIQUE
    """)

    session.run("""
        CREATE CONSTRAINT description_id IF NOT EXISTS
        FOR (d:Description) REQUIRE d.id IS UNIQUE
    """)

    session.run("""
        CREATE CONSTRAINT relationship_id IF NOT EXISTS
        FOR ()-[r:RELATIONSHIP]->() REQUIRE r.id IS UNIQUE
    """)

    # Create indexes
    session.run("""
        CREATE INDEX concept_active IF NOT EXISTS
        FOR (c:Concept) ON (c.active)
    """)

    session.run("""
        CREATE INDEX description_term IF NOT EXISTS
        FOR (d:Description) ON (d.term)
    """)

    session.run("""
        CREATE INDEX relationship_type IF NOT EXISTS
        FOR ()-[r:RELATIONSHIP]->() ON (r.typeId)
    """)


def load_concepts(session: Session, concept_file: Path, batch_size: int, keep_inactive: bool = False) -> None:
    """Load concepts from RF2 file into Neo4j."""
    logging.info("Loading concepts...")

    with open(concept_file, encoding="utf-8") as f:
        total_lines = sum(1 for _ in f) - 1  # Subtract header

    batch: list[Concept] = []
    loaded = 0

    with open(concept_file, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")

        with tqdm(total=total_lines) as pbar:
            for row in reader:
                active = row["active"] == "1"

                if not active and not keep_inactive:
                    pbar.update(1)
                    continue

                batch.append(Concept(**row))

                if len(batch) >= batch_size:
                    batch_dicts = [{"properties": c.model_dump(by_alias=True)} for c in batch]
                    session.run(
                        """
                        UNWIND $batch AS row
                        CREATE (c:Concept)
                        SET c = row.properties
                        RETURN count(c) as created_count
                        """,
                        {"batch": batch_dicts},
                    )

                    loaded += len(batch)
                    pbar.update(len(batch))
                    batch = []

            if batch:
                batch_dicts = [{"properties": c.model_dump(by_alias=True)} for c in batch]
                session.run(
                    """
                    UNWIND $batch AS row
                    CREATE (c:Concept)
                    SET c = row.properties
                    RETURN count(c) as created_count
                    """,
                    {"batch": batch_dicts},
                )
                loaded += len(batch)
                pbar.update(len(batch))

    logging.info(f"Loaded {loaded} concepts.")


def load_descriptions(session: Session, description_file: Path, batch_size: int, keep_inactive: bool = False) -> None:
    """Load descriptions from RF2 file into Neo4j."""
    logging.info("Loading descriptions...")

    csv.field_size_limit(sys.maxsize)

    # Count lines for progress bar
    with open(description_file, encoding="utf-8") as f:
        total_lines = sum(1 for _ in f) - 1  # Subtract header

    batch: list[Description] = []
    loaded = 0

    with open(description_file, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)

        with tqdm(total=total_lines) as pbar:
            for row in reader:
                active = row["active"] == "1"

                if not active and not keep_inactive:
                    pbar.update(1)
                    continue

                batch.append(Description(**row))

                if len(batch) >= batch_size:
                    batch_dicts = [{"concept_id": d.concept_id, "properties": d.model_dump(by_alias=True)} for d in batch]

                    session.run(
                        """
                        UNWIND $batch AS row
                        MATCH (c:Concept {id: row.concept_id})
                        CREATE (d:Description)
                        SET d = row.properties
                        CREATE (c)-[:HAS_DESCRIPTION]->(d)
                        """,
                        {"batch": batch_dicts},
                    )

                    loaded += len(batch)
                    pbar.update(len(batch))
                    batch = []

            if batch:
                batch_dicts = [{"concept_id": d.concept_id, "properties": d.model_dump(by_alias=True)} for d in batch]

                session.run(
                    """
                    UNWIND $batch AS row
                    MATCH (c:Concept {id: row.concept_id})
                    CREATE (d:Description)
                    SET d = row.properties
                    CREATE (c)-[:HAS_DESCRIPTION]->(d)
                    """,
                    {"batch": batch_dicts},
                )

                loaded += len(batch)
                pbar.update(len(batch))

    logging.info(f"Loaded {loaded} descriptions.")


def load_relationships(session: Session, relationship_file: Path, batch_size: int, keep_inactive: bool = False) -> None:
    """Load relationships from RF2 file into Neo4j."""
    logging.info("Loading relationships...")

    # Count lines for progress bar
    with open(relationship_file, encoding="utf-8") as f:
        total_lines = sum(1 for _ in f) - 1  # Subtract header

    batch: list[Relationship] = []
    loaded = 0

    with open(relationship_file, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")

        with tqdm(total=total_lines) as pbar:
            for row in reader:
                # Convert active to boolean
                active = row["active"] == "1"

                if not active and not keep_inactive:
                    pbar.update(1)
                    continue

                batch.append(Relationship(**row))

                if len(batch) >= batch_size:
                    batch_dicts = [
                        {
                            "source_id": r.source_id,
                            "destination_id": r.destination_id,
                            "properties": r.model_dump(by_alias=True),
                            "type": r.type.name,
                        }
                        for r in batch
                    ]

                    session.run(
                        """
                        UNWIND $batch AS row
                        MATCH (source:Concept {id: row.source_id})
                        MATCH (destination:Concept {id: row.destination_id})
                        CALL apoc.create.relationship(
                            source,
                            row.type,
                            row.properties,
                            destination
                        ) YIELD rel
                        RETURN count(*) AS relationshipsCreated

                        """,
                        {"batch": batch_dicts},
                    )

                    loaded += len(batch)
                    pbar.update(len(batch))
                    batch = []

            if batch:
                batch_dicts = [
                    {"source_id": r.source_id, "destination_id": r.destination_id, "properties": r.model_dump(by_alias=True)} for r in batch
                ]

                session.run(
                    """
                    UNWIND $batch AS row
                    MATCH (source:Concept {id: row.source_id})
                    MATCH (destination:Concept {id: row.destination_id})
                    CREATE (source)-[rel:RELATIONSHIP]->(destination)
                    SET rel = row.properties
                    """,
                    {"batch": batch_dicts},
                )

                loaded += len(batch)
                pbar.update(len(batch))

    logging.info(f"Loaded {loaded} relationships.")


def add_fsn_to_concepts(session: Session) -> None:
    """Add FSN to concepts based on descriptions."""
    logging.info("Adding FSN to concepts...")

    session.run("""
        CALL apoc.periodic.iterate(
        "MATCH (c:Concept)--(d:Description{typeId:'900000000000003001'})
        RETURN c, d",
        "WITH c, d
        ORDER BY d.term
        WITH c, collect(d)[0] as firstDescription
        SET c.term = firstDescription.term
        RETURN c",
        {batchSize: 1000, parallel: false}
        """)


def main() -> None:
    from dotenv import load_dotenv

    load_dotenv()
    rf2_files = find_rf2_files(Path(os.environ["SNOMED_DIR"]))
    driver = get_driver()

    start_time = time.time()
    with driver.session() as session:
        setup_neo4j_schema(session)
        load_concepts(session, rf2_files["concept"], int(os.environ["SNOMED_IMPORT_BATCH"]), env_bool("SNOMED_KEEP_INACTIVE"))
        load_descriptions(session, rf2_files["description"], int(os.environ["SNOMED_IMPORT_BATCH"]), env_bool("SNOMED_KEEP_INACTIVE"))
        load_relationships(session, rf2_files["relationship"], int(os.environ["SNOMED_IMPORT_BATCH"]), env_bool("SNOMED_KEEP_INACTIVE"))

        if env_bool("SNOMED_ADD_FSN"):
            add_fsn_to_concepts(session)

    end_time = time.time()
    logging.info(f"Data loading completed in {end_time - start_time:.2f} seconds.")

    driver.close()
