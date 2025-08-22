# Online Wine Club Site (OWC)

## Running Locally

Install the dependencies and run the application on `127.0.0.1:5000`:

```bash
pip install -r requirements.txt
python run.py
```

The app now explicitly binds to `127.0.0.1` on port `5000`, so you can visit
`http://127.0.0.1:5000` in your browser.
## Testing

Run the test suite with:

```bash
pytest
```

Pytest is configured to include the repository root on the PYTHONPATH via `pyproject.toml`.