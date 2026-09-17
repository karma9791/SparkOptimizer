# Spark Parameter Advisor

A small Flask web app that recommends Spark configuration parameters
(`spark.executor.instances`, `spark.executor.cores`, `spark.executor.memory`,
`spark.driver.memory`, `spark.default.parallelism`) based on your cluster size.

Enter the number of nodes, cores per node, and RAM per node — the app returns
a recommended config and a ready-to-copy `spark-submit` snippet.

## Tech stack

- **Backend:** Flask
- **Frontend:** Plain HTML/CSS + Jinja2 templates (no JS framework, no build step)
- **Testing:** pytest + Flask test client
- **Containerization:** Docker
- **Deployment:** Render (free web service, deployed from the Dockerfile)

## Project structure

```
spark-param-advisor/
├── app.py               # Flask app factory, routes, calculation engine
├── requirements.txt
├── templates/
│   ├── index.html        # input form
│   └── results.html      # recommended config + spark-submit snippet
├── static/
│   └── style.css
└── tests/
    └── test_app.py
```

## Running locally

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
flask --app app run --debug
```

Then open **http://127.0.0.1:5000** in your browser.

## Running the tests

```bash
pytest tests/
```

## Running with Docker

```bash
# Build the image
docker build -t spark-param-advisor .

# Run the container
docker run -p 5000:5000 spark-param-advisor
```

Then open **http://127.0.0.1:5000**.

## Deploying (Render, free tier)

1. Push this repo to GitHub.
2. On [Render](https://render.com), create a new **Web Service** and select
   "Deploy from Dockerfile."
3. Point it at your GitHub repo.
4. Make sure the app binds to `0.0.0.0` on the `$PORT` environment variable
   Render provides (update the Dockerfile's `CMD`/entrypoint accordingly if
   needed).
5. Deploy and open the public URL Render gives you.

> Free-tier services on Render spin down after inactivity, so the first
> request after idle time may take a few seconds to respond while it wakes up.

## Calculation assumptions

The current calculation engine (`recommend_spark_config` in `app.py`) is a
placeholder using simple heuristics:

- Reserves 1 core per node for the OS/daemons.
- Caps executor cores at 5 (avoids HDFS throughput bottlenecks from too many
  concurrent threads per executor).
- Reserves ~7% of node memory for YARN/overhead.
- Sets `spark.default.parallelism` to roughly 2× total executor cores.

Replace this logic with your own tuning rules as needed — it's kept as a
standalone function so it can be unit tested independently of Flask.

## Roadmap / ideas

- Cluster-manager-specific presets (YARN, Kubernetes, Standalone)
- Cost estimation based on cloud provider instance pricing
- CSV export of the recommended configuration
