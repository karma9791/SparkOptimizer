import pytest

from app import create_app, recommend_spark_config


@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    with app.test_client() as client:
        yield client


def test_index_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Spark Parameter Advisor" in response.data


def test_calculate_with_valid_input_returns_results(client):
    response = client.post(
        "/calculate",
        data={"nodes": "4", "cores_per_node": "16", "ram_per_node_gb": "64"},
    )
    assert response.status_code == 200
    assert b"spark.executor.instances" in response.data


def test_calculate_with_invalid_input_shows_error(client):
    response = client.post(
        "/calculate",
        data={"nodes": "abc", "cores_per_node": "16", "ram_per_node_gb": "64"},
    )
    assert response.status_code == 400
    assert b"valid whole numbers" in response.data


def test_recommend_spark_config_basic_case():
    config = recommend_spark_config(nodes=4, cores_per_node=16, ram_per_node_gb=64)
    assert config["spark.executor.cores"] == 5
    assert config["spark.executor.instances"] > 0
    assert config["spark.default.parallelism"] > 0
