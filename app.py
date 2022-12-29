from pathlib import Path

import pandas as pd
import folium
import streamlit as st

from streamlit_folium import st_folium


APP_TITLE = "NOS Site clusters"
APP_SUBTITLE = "Show the location of B1 Zone sites in the network."
COLOR_PALETTE = [
    "black",
    "red",
    "blue",
    "green",
    "purple",
    "orange",
    "darkred",
    "lightred",
    "beige",
    "darkblue",
    "darkgreen",
    "cadetblue",
    "darkpurple",
    "lightblue",
    "pink",
    "gray",
]


@st.cache
def load_data() -> pd.DataFrame:
    file_names = ["cluster_coords.csv"]
    data_dir = Path("data")
    dfs: list[pd.DataFrame] = []
    for file_name in file_names:
        data_path = data_dir / file_name
        if data_path.exists():
            dfs.append(pd.read_csv(data_path))
    return pd.concat(dfs, ignore_index=True)


@st.cache
def _get_sorted_cluster_ids(df: pd.DataFrame, cluster_type: str) -> pd.DataFrame:
    """Sort cluster ids based on the cluster rank."""
    _df = df.copy()
    _df = _df[["cluster_type", "cluster_id", "cluster_rank"]].drop_duplicates()
    _df = _df.sort_values(by=["cluster_type", "cluster_rank"])
    return _df[_df["cluster_type"] == cluster_type]["cluster_id"].unique()


def display_cluster_type(df: pd.DataFrame) -> None:
    """Display cluster type selection."""
    cluster_type = st.sidebar.selectbox(
        "Select cluster type",
        df["cluster_type"].unique(),
        help=(
            "Normalized time-series kmeans: clusters that priorize the shape of "
            " behavior of the power consumption, in lieu of their amount.\n"
            "Non-normalized time-series kmeans: clusters that priorize the amount of"
            " the power consumption in lieu of their trends and sazonalities."
        ),
    )
    return cluster_type


def display_legend(df: pd.DataFrame, cluster_type: str) -> None:
    """Display legend."""
    options = _get_sorted_cluster_ids(df, cluster_type)
    st.sidebar.markdown(
        """
        **Legend**

        Clusters are ordered by the average hourly power consumption of the sites in
        the cluster.
        """
    )
    # Display legend where the color of the marker is based on the series index
    for i, cluster_id in enumerate(options):
        st.sidebar.markdown(
            f"""
            <span style="color:{COLOR_PALETTE[i]};">●</span>
            <span style="color:black;">Cluster {cluster_id}</span>
            """,
            unsafe_allow_html=True,
        )


def display_cluster_id(df: pd.DataFrame, cluster_type: str) -> None:
    """Display cluster id selection."""
    options = _get_sorted_cluster_ids(df, cluster_type)
    cluster_id = st.sidebar.multiselect(
        label="Select cluster id",
        options=options,
        default=None,
        help=(
            "Select one or more cluster ids to display on the map.\n"
            "Cluster IDs are sorted by the average hourly power consumption of the"
            "sites in the cluster."
        ),
    )
    return cluster_id


def display_resumes(cluster_type: str) -> None:
    img_mapping = {
        "normalized time-series kmeans": "cluster_plots.png",
    }
    img_dir = Path("img")
    st.image(str(img_dir / img_mapping[cluster_type]))


def display_map(df: pd.DataFrame, cluster_type: str, cluster_id: int = None) -> None:
    """Display sites clusters on a map."""

    # Remove sites with no geolocation
    df = df.loc[~df["longitude"].isna()]

    # Add filters
    df = df[(df["cluster_type"] == cluster_type)]
    if cluster_id:
        df = df[df["cluster_id"].isin(cluster_id)]

    # Diplay map
    map = folium.Map(
        location=[df["latitude"].mean(), df["longitude"].mean()],
        zoom_start=9,
        control_scale=True,
    )
    for row in df.iterrows():
        # The color of the marker is based on the cluster rank, which is a
        # number between 0 and 14 that is assigned to each cluster based on
        # the average hourly power consumption of the sites in the cluster.
        icon_color = COLOR_PALETTE[row[1]["cluster_rank"]]
        folium.CircleMarker(
            location=[row[1]["latitude"], row[1]["longitude"]],
            color=icon_color,
            popup=f"""{row[1]['site_code']},
                    {row[1]['zone_name']}, 
                    {row[1]['cluster_name']},
                    Cluster {row[1]['cluster_id']}""",
            fill=True,
            radius=3,
        ).add_to(map)

    st_folium(map)


def main():
    st.set_page_config(APP_TITLE)
    st.title(APP_TITLE)
    st.caption(APP_SUBTITLE)

    data_load_state = st.text("Loading data...")
    data = load_data()
    data_load_state.text("Loading data...done!")

    # Side bar
    cluster_type = display_cluster_type(data)
    cluster_id = display_cluster_id(data, cluster_type)
    display_legend(data, cluster_type)

    col1, col2 = st.columns(2)
    with col1:
        display_map(data, cluster_type, cluster_id)
    with col2:
        display_resumes(cluster_type)


if __name__ == "__main__":
    main()
