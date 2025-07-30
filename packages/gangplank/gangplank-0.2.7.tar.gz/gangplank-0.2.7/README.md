# Gangplank
## Export Keras metrics to Prometheus
[Prometheus](https://prometheus.io/) is a monitoring system that pulls metrics from applications and infrastructure.
While polling works for applications that are continuously running, scraping metrics does not work well with batch jobs such as
machine learning training or evaluation jobs. The Prometheus [Pushgateway](https://prometheus.io/docs/instrumenting/pushing/)
is middleware that connects batch jobs to Prometheus.

Gangplank is a Keras [callback](https://keras.io/api/callbacks/) for pushing Keras training and testing metrics to Prometheus via a
pushgateway.

### What metrics are exported?
During training, the following metrics are exported:
 * The number of completed training epochs
 * The time spent training
 * The number of model weights (both trainable and non-trainable)
 * The model's loss
 * All metrics configured for the model (e.g. accuracy for a classification model or mean absolute error for a regression model)
 * (Optionally) A histogram of the model's trainable weights at the end of the training run

For testing (i.e. evaluation), the following metrics are exported:
 * The time spent testing
 * The model's loss
 * All metrics configured for the model (accuracy, mean absolute error, etc.)
 * (Optionally) A histogram of the model's trainable weights

## Installing Gangplank
Gangplank can be installed from PyPI

```
pip install gangplank
```

The installation will also install Keras. Keras needs a tensor arithmetic backend like TensorFlow, JAX or PyTorch. You can install a
backend at the same time as installing Gangplank by running one of the following

```
pip install gangplank[tensorflow]
pip install gangplank[jax]
pip install gangplank[torch]
```

Note: Running, e.g., `pip install gangplank[jax]` will install a CPU-only version of JAX. If you want, say, CUDA support you should install JAX separately

```
pip install gangplank
pip install jax[cuda12]
```

Similar comments apply to TensorFlow and PyTorch.

## Examples
Examples of using Gangplank can be found [here](https://github.com/hammingweight/gangplank/tree/main/examples).

