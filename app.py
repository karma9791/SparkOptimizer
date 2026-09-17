"""
Spark Parameter Advisor - Flask app entry point.

Run locally with:
    flask --app app run --debug
or:
    python app.py
"""
from flask import Flask, render_template, request, flash


def create_app():
    app = Flask(__name__)
    app.secret_key = "dev-secret-key"  # replace with a real secret before deploying

    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")

    @app.route("/calculate", methods=["POST"])
    def calculate():
        try:
            nodes = int(request.form.get("nodes", ""))
            cores_per_node = int(request.form.get("cores_per_node", ""))
            ram_per_node_gb = int(request.form.get("ram_per_node_gb", ""))
        except (TypeError, ValueError):
            flash("Please enter valid whole numbers for all fields.")
            return render_template("index.html"), 400

        if nodes <= 0 or cores_per_node <= 0 or ram_per_node_gb <= 0:
            flash("Nodes, cores per node, and RAM per node must all be positive.")
            return render_template("index.html"), 400

        config = recommend_spark_config(nodes, cores_per_node, ram_per_node_gb)
        return render_template(
            "results.html",
            nodes=nodes,
            cores_per_node=cores_per_node,
            ram_per_node_gb=ram_per_node_gb,
            config=config,
        )

    return app


def recommend_spark_config(nodes: int, cores_per_node: int, ram_per_node_gb: int) -> dict:
    """
    Placeholder calculation engine.

    Replace with the real heuristics from backlog item 3.5 (reserve 1 core/node
    for OS, ~7% memory overhead, etc). Kept here as a plain function so it's
    easy to unit test independently of Flask (see tests/test_calculations.py).
    """
    usable_cores_per_node = max(cores_per_node - 1, 1)
    executor_cores = min(5, usable_cores_per_node)
    executors_per_node = max(usable_cores_per_node // executor_cores, 1)
    total_executors = executors_per_node * nodes

    memory_per_executor_gb = max(
        int((ram_per_node_gb * 0.93) / executors_per_node), 1
    )
    driver_memory_gb = max(int(ram_per_node_gb * 0.1), 1)
    default_parallelism = total_executors * executor_cores * 2

    return {
        "spark.executor.instances": total_executors,
        "spark.executor.cores": executor_cores,
        "spark.executor.memory": f"{memory_per_executor_gb}g",
        "spark.driver.memory": f"{driver_memory_gb}g",
        "spark.default.parallelism": default_parallelism,
    }


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
