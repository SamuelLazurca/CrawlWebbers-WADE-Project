from collections import defaultdict

import pandas as pd
import datetime
import os

# ================= CONFIGURATION =================
TOP_N_MOVIES = 2000
MAX_RATINGS_PER_MOVIE = 1000
GENOME_THRESHOLD = 0.5
INPUT_DIR = "data"
OUTPUT_DIR = "output_ttl_final"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# NAMESPACES & PREFIXES
PREFIXES = """@prefix schema: <http://schema.org/> .
@prefix davi-mov: <https://purl.org/davi/vocab/movielens#> .
@prefix imdb: <https://www.imdb.com/title/tt> .
@prefix genre: <https://www.imdb.com/search/title/?genres=> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
"""

# GLOBAL STORAGE
MOVIE_ID_TO_IMDB = {}  # Internal ID -> IMDB Suffix (e.g., "1" -> "0114709")

# GENRE MAPPING (MovieLens -> IMDB Search Slug)
GENRE_MAP = {
    "Action": "action", "Adventure": "adventure", "Animation": "animation",
    "Children": "family", "Comedy": "comedy", "Crime": "crime",
    "Documentary": "documentary", "Drama": "drama", "Fantasy": "fantasy",
    "Film-Noir": "film-noir", "Horror": "horror", "Musical": "musical",
    "Mystery": "mystery", "Romance": "romance", "Sci-Fi": "sci-fi",
    "Thriller": "thriller", "War": "war", "Western": "western"
}


def clean_text(text):
    """Escapes special characters for Turtle strings."""
    if pd.isna(text): return ""
    return str(text).replace('\\', '\\\\').replace('"', '\\"')


def format_date(timestamp):
    """Converts Unix timestamp to ISO 8601 XSD DateTime."""
    try:
        dt = datetime.datetime.fromtimestamp(int(timestamp), tz=datetime.timezone.utc)
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    except:
        return ""


def write_header(f):
    f.write(PREFIXES + "\n")


# ================= STEP 1: MAPPING IDs =================
def setup_movie_mapping():
    print("Step 1: Finding top movies and mapping IDs...")

    # 1. Count ratings to find top movies
    counts = pd.Series(dtype=int)
    chunk_size = 1000000
    reader = pd.read_csv(f"{INPUT_DIR}/ratings.csv", usecols=['movieId'], chunksize=chunk_size)

    for chunk in reader:
        counts = counts.add(chunk['movieId'].value_counts(), fill_value=0)

    top_ids = set(counts.sort_values(ascending=False).head(TOP_N_MOVIES).index.astype(str))

    # 2. Map internal ID to IMDB ID using links.csv
    links_df = pd.read_csv(f"{INPUT_DIR}/links.csv", dtype=str)
    mapped_count = 0

    for _, row in links_df.iterrows():
        m_id = row['movieId']
        imdb_raw = row['imdbId']

        if m_id in top_ids and pd.notna(imdb_raw):
            # Pad with zeros to ensure 7 digits (e.g., "114709" -> "0114709")
            imdb_clean = str(imdb_raw).zfill(7)
            MOVIE_ID_TO_IMDB[m_id] = imdb_clean
            mapped_count += 1

    print(f"   Mapped {mapped_count} movies to valid IMDB IDs.")


# ================= STEP 2: MOVIES (Schema.org) =================
def process_movies():
    print("Step 2: Processing Movies...")
    movies_df = pd.read_csv(f"{INPUT_DIR}/movies.csv", dtype=str)

    with open(f"{OUTPUT_DIR}/movies.ttl", "w", encoding="utf-8") as f:
        write_header(f)

        for _, row in movies_df.iterrows():
            m_id = row['movieId']
            if m_id not in MOVIE_ID_TO_IMDB: continue

            # CURIE: imdb:0114709
            imdb_suffix = MOVIE_ID_TO_IMDB[m_id]
            movie_node = f"imdb:{imdb_suffix}"

            title = clean_text(row['title'])

            # Process Genres into CURIE (e.g., genre:comedy)
            genre_uris = []
            if pd.notna(row['genres']):
                for g in row['genres'].split('|'):
                    slug = GENRE_MAP.get(g)
                    if slug:
                        genre_uris.append(f"genre:{slug}")

            genre_ttl = f"    schema:genre {', '.join(genre_uris)} ;" if genre_uris else ""

            f.write(f"""
{movie_node} a schema:Movie ;
    schema:name "{title}" ;
    dcterms:identifier "{m_id}" ;
{genre_ttl}
    .
""")


# ================= STEP 3: RATINGS =================
def process_ratings():
    print(f"Step 3: Processing Ratings (Max {MAX_RATINGS_PER_MOVIE} per movie)...")

    # Track how many ratings we have saved for each movie
    ratings_per_movie_count = defaultdict(int)

    # Using chunksize for memory efficiency
    reader = pd.read_csv(f"{INPUT_DIR}/ratings.csv", chunksize=500000, dtype=str)

    with open(f"{OUTPUT_DIR}/ratings.ttl", "w", encoding="utf-8") as f:
        write_header(f)
        total_written = 0

        for chunk in reader:
            buffer = []

            # Iterating rows is safer for memory with huge files.
            for _, row in chunk.iterrows():
                m_id = row['movieId']

                if m_id not in MOVIE_ID_TO_IMDB:
                    continue

                # 2. Check if we already have enough ratings for this movie
                if ratings_per_movie_count[m_id] >= MAX_RATINGS_PER_MOVIE:
                    continue

                # Increment counter
                ratings_per_movie_count[m_id] += 1
                total_written += 1

                imdb_suffix = MOVIE_ID_TO_IMDB[m_id]
                u_id = row['userId']
                rating = row['rating']
                ts = format_date(row['timestamp'])

                rating_node = f"davi-mov:rating_{u_id}_{m_id}"
                user_node = f"davi-mov:user_{u_id}"
                movie_node = f"imdb:{imdb_suffix}"

                buffer.append(f"""
{rating_node} a schema:Rating ;
    schema:author {user_node} ;
    schema:itemReviewed {movie_node} ;
    schema:ratingValue {rating} ;
    schema:datePublished "{ts}"^^xsd:dateTime .
""")

            if buffer:
                f.write("".join(buffer))

            print(f"   Processed chunk... Total ratings written: {total_written}")

    print(f"Step 3 Complete. Total Ratings: {total_written}")


# ================= STEP 4: GENOME SCORES =================
def process_genome():
    print("Step 4: Processing Genome Scores (Relevance > 0.5)...")
    reader = pd.read_csv(f"{INPUT_DIR}/genome-scores.csv", chunksize=500000, dtype=str)

    with open(f"{OUTPUT_DIR}/genome_scores.ttl", "w", encoding="utf-8") as f:
        write_header(f)

        for chunk in reader:
            chunk['relevance'] = pd.to_numeric(chunk['relevance'])
            chunk = chunk[chunk['relevance'] > GENOME_THRESHOLD]

            if chunk.empty: continue

            buffer = []
            for _, row in chunk.iterrows():
                m_id = row['movieId']
                if m_id not in MOVIE_ID_TO_IMDB: continue

                imdb_suffix = MOVIE_ID_TO_IMDB[m_id]
                t_id = row['tagId']
                score = row['relevance']

                relevance_node = f"davi-mov:relevance_{m_id}_{t_id}"
                movie_node = f"imdb:{imdb_suffix}"
                tag_node = f"davi-mov:genometag_{t_id}"

                buffer.append(f"""
{relevance_node} a davi-mov:GenomeRelevance ;
    davi-mov:isRelevantTo {movie_node} ;
    davi-mov:hasGenomeTag {tag_node} ;
    davi-mov:relevanceScore {score} .
""")
            f.write("".join(buffer))


# ================= STEP 5: TAG METADATA =================
def process_tags_metadata():
    print("Step 5: Processing Tag Definitions and User Tags...")

    # 1. Genome Tag Definitions
    df_defs = pd.read_csv(f"{INPUT_DIR}/genome-tags.csv", dtype=str)
    with open(f"{OUTPUT_DIR}/genome_defs.ttl", "w", encoding="utf-8") as f:
        write_header(f)
        for _, row in df_defs.iterrows():
            t_id = row['tagId']
            t_name = clean_text(row['tag'])
            f.write(f'davi-mov:genometag_{t_id} a davi-mov:GenomeTag ; rdfs:label "{t_name}" .\n')

    # 2. User Tags (Free text)
    df_user_tags = pd.read_csv(f"{INPUT_DIR}/tags.csv", dtype=str)
    with open(f"{OUTPUT_DIR}/user_tags.ttl", "w", encoding="utf-8") as f:
        write_header(f)
        for _, row in df_user_tags.iterrows():
            m_id = row['movieId']
            if m_id not in MOVIE_ID_TO_IMDB: continue

            imdb_suffix = MOVIE_ID_TO_IMDB[m_id]
            u_id = row['userId']
            ts_raw = row['timestamp']
            ts = format_date(ts_raw)
            content = clean_text(row['tag'])

            # Using davi-mov:TagApplication (subclass of schema:CreateAction)
            tag_app_node = f"davi-mov:tagapp_{u_id}_{m_id}_{ts_raw}"
            movie_node = f"imdb:{imdb_suffix}"
            user_node = f"davi-mov:user_{u_id}"

            f.write(f"""
{tag_app_node} a davi-mov:TagApplication ;
    davi-mov:taggedBy {user_node} ;
    davi-mov:tagsMovie {movie_node} ;
    davi-mov:tagContent "{content}" ;
    schema:startTime "{ts}"^^xsd:dateTime .
""")


if __name__ == "__main__":
    setup_movie_mapping()
    process_movies()
    process_tags_metadata()
    process_genome()
    # process_ratings()
    print("\nConversion Complete! Output is in 'output_ttl_final/'")
