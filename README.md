# Site Clusters

## Commands

- `streamlit run app.py` to run the app locally

## Package management

This project uses [Poetry](https://python-poetry.org/) for package management. Don't edit the `requirements.txt` file directly, it is generated from the `pyproject.toml` file by using the following command:

```bash
poetry export -f requirements.txt --output requirements.txt
```
