from src import pipeline, resource, source


@resource(
    name="player",
    table_name="player",
    primary_key="id",
    columns=["username", "country", "followers"],
)
def chess_players(players: list[str]):
    for idx, player in enumerate(players, start=1):
        yield {
            "id": idx,
            "username": player,
            "country": "unknown",
            "followers": 0,
        }


@source(name="chess")
def chess_source(players: list[str]):
    return [chess_players(players)]


p = pipeline(
    pipeline_name="chess_pipeline",
    destination="postgres",
    dataset_name="player_data",
    credentials={
        "host": "localhost",
        "port": 5432,
        "database": "world",
        "user": "postgres",
        "password": "postgres",
    },
    profile="historized_snapshot",
    primary_key="id",
    hash_columns=["username", "country", "followers"],
    extract_chunk_size=1000,
    write_chunk_size=500,
)

p.run(chess_source(players=["magnuscarlsen", "rpragchess"]))
