import pandas as pd
from ragas.metrics import discrete_metric
from ragas.metrics.result import MetricResult




@discrete_metric(name="accuracy", allowed_values=["pass", "fail"])
def my_metric(prediction: str, actual: str):
    """Calculate accuracy of the prediction."""
    return MetricResult(value="pass", reason="") if prediction == actual else MetricResult(value="fail", reason="")

@experiment()
async def run_experiment(row, model):
    response = run_prompt(row["text"], model=model)
    score = my_metric.score(
        prediction=response,
        actual=row["label"]
    )

    experiment_view = {
        **row,
        "response": response,
        "score": score.value,
    }
    return experiment_view



if __name__ == '__main__':

    samples = [{"text": "I loved the movie! It was fantastic.", "label": "positive"},
        {"text": "The movie was terrible and boring.", "label": "negative"},
        {"text": "It was an average film, nothing special.", "label": "positive"},
        {"text": "Absolutely amazing! Best movie of the year.", "label": "positive"}]
    pd.DataFrame(samples).to_csv("datasets/test_dataset.csv", index=False)
    print("Sample dataset 'datasets/test_dataset.csv' created.")

    dataset = load_dataset("datasets/test_dataset.csv")

    # Run with specific parameters
    run_experiment.arun(dataset, "gpt-4")

    # Or use keyword arguments
    run_experiment.arun(dataset, model="gpt-4o")


