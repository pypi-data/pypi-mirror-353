def join_trap_ids_and_daily_status(trap_daily_status, trap_ids):
    trap_daily_status_without_na = trap_daily_status.dropna(axis=0, subset=["Estado_trampa"])
    joined_dataframe = trap_daily_status_without_na.join(
        trap_ids.set_index("ID"), on="ID_de_trampa"
    )
    return joined_dataframe


def add_lat_lon_to_active_traps_of_the_week(active_traps, traps_positions_with_lat_lon):
    joined = active_traps.join(
        traps_positions_with_lat_lon.set_index(["ID", "Linea"]), on=["ID_de_trampa", "line"]
    )
    columns = [
        "date",
        "Tipo_de_trampa",
        "ID_de_trampa",
        "Orden",
        "line",
        "latitude",
        "longitude",
    ]
    return joined[columns]
