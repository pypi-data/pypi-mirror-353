import matplotlib.pyplot as plt
import numpy as np


def get_all_dataset_names(data):
    """Extracts all dataset names from the Experiment data."""
    return list(data.keys())


def get_all_model_method_names(data):
    """Extract unique model names across all datasets"""
    models = set()
    for dataset_data in data.values():
        for key in dataset_data.keys():
            if key not in ["metrics", "original_metrics"]:
                models.add(key)
    return sorted(models)


def get_all_numeric_metric_names(data):
    """
    Extracts all unique numeric metric names present in model/method results
    or in 'original_metrics'.
    """
    all_metrics = set()
    utility_keys_to_ignore = [
        "test_name",
        "test_size",
        "test_index",
        "test_runtime",
        "test_samples_per_second",
        "test_steps_per_second",
        "epoch",
        "Accuracy",  # Accuracy is often NaN
    ]
    for dataset_name, dataset_data in data.items():
        # Check original_metrics
        if "original_metrics" in dataset_data and isinstance(
            dataset_data["original_metrics"], dict
        ):
            for metric_key, metric_value in dataset_data["original_metrics"].items():
                if metric_key not in utility_keys_to_ignore and isinstance(
                    metric_value, (int, float)
                ):
                    all_metrics.add(metric_key)

        # Check each model/method
        for model_or_method_key, model_or_method_data in dataset_data.items():
            if model_or_method_key not in [
                "metrics",
                "original_metrics",
            ] and isinstance(model_or_method_data, dict):
                for metric_key, metric_value in model_or_method_data.items():
                    if metric_key not in utility_keys_to_ignore and isinstance(
                        metric_value, (int, float)
                    ):
                        all_metrics.add(metric_key)
    return sorted(all_metrics)


def _shorten_dataset_name(d_name):
    """Helper to shorten dataset names for display."""
    return d_name.split("/")[0].replace("___", "\n").replace("_", " ").title()[:30]


def _shorten_model_name(m_name, max_len=25):
    """Helper to shorten model names for display."""
    if len(m_name) > max_len:
        return m_name[: max_len - 3] + "..."
    return m_name


# Visualization Functions


def plot_metric_comparison_across_datasets(
    data, metric_name, specific_models=None, show_original=True
):
    """
    Compares a specific metric for selected models/methods across all datasets.

    Args:
        data (dict): The parsed JSON data.
        metric_name (str): The metric to compare (e.g., 'bertscore_f1', 'test_accuracy').
        specific_models (list, optional): A list of model/method names to include.
                                          If None, includes all found models/methods.
        show_original (bool): If True, includes 'Original Model' performance for the metric.
    """
    datasets = get_all_dataset_names(data)
    all_model_methods = get_all_model_method_names(data)

    if specific_models:
        models_to_plot = [m for m in all_model_methods if m in specific_models]
        if show_original and "Original Model" not in models_to_plot:
            models_to_plot.append("Original Model")
    else:
        models_to_plot = [
            m for m in all_model_methods if m != "metrics" and m != "original_metrics"
        ]
        if not show_original and "Original Model" in models_to_plot:
            models_to_plot.remove("Original Model")

    if not models_to_plot:
        print("No models/methods selected or found for plotting.")
        return

    metric_values = {}  # {model_name: [val_ds1, val_ds2, ...]}

    for model_name in models_to_plot:
        metric_values[model_name] = []
        for dataset_name in datasets:
            dataset_info = data.get(dataset_name, {})
            score = np.nan
            if model_name == "Original Model":
                model_info = dataset_info.get("original_metrics", {})
                val = model_info.get(metric_name)
                if isinstance(val, (int, float)):
                    score = val
            else:
                model_info = dataset_info.get(model_name, {})
                val = model_info.get(metric_name)
                if isinstance(val, (int, float)):
                    score = val
            metric_values[model_name].append(score)

    # Filter out models that have no scores at all for this metric
    models_with_data = [
        m for m in models_to_plot if not all(np.isnan(s) for s in metric_values[m])
    ]
    if not models_with_data:
        print(
            f"No data found for metric '{metric_name}' for the selected models across datasets."
        )
        return
    models_to_plot = models_with_data

    num_datasets = len(datasets)
    num_models_plotted = len(models_to_plot)

    fig, ax = plt.subplots(
        figsize=(max(15, num_datasets * 1.5 * (num_models_plotted / 5)), 8)
    )

    index = np.arange(num_datasets)
    # Adjust bar width based on number of models to avoid excessive crowding/sparseness
    total_group_width = 0.8
    bar_width = total_group_width / num_models_plotted

    for i, model_name in enumerate(models_to_plot):
        scores = np.array(metric_values[model_name], dtype=float)
        ax.bar(
            index + i * bar_width - (total_group_width - bar_width) / 2,
            scores,
            bar_width,
            label=_shorten_model_name(model_name),
        )

    ax.set_xlabel("Dataset", fontsize=12)
    ax.set_ylabel(metric_name, fontsize=12)
    ax.set_title(f"{metric_name} by Model/Method Across Datasets", fontsize=14)
    ax.set_xticks(index)
    ax.set_xticklabels(
        [_shorten_dataset_name(d) for d in datasets],
        rotation=45,
        ha="right",
        fontsize=10,
    )
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5), fontsize=10)
    ax.grid(True, axis="y", linestyle="--", alpha=0.7)

    plt.tight_layout(rect=[0, 0, 0.85, 1])  # Adjust layout for legend
    plt.show()


def plot_all_metrics_for_model_on_dataset(data, dataset_name, model_or_method_name):
    """
    Plots all numeric metrics for a specific model/method on a specific dataset.

    Args:
        data (dict): The parsed JSON data.
        dataset_name (str): The name of the dataset.
        model_or_method_name (str): The name of the model/method (e.g., 'google/gemini-flash-1.5-8b/pii').
                                    Use "Original Model" to see metrics from "original_metrics".
    """
    dataset_info = data.get(dataset_name)
    if not dataset_info:
        print(f"Dataset '{dataset_name}' not found.")
        return

    metrics_source_dict = None
    if model_or_method_name == "Original Model":
        metrics_source_dict = dataset_info.get("original_metrics")
        plot_title = f"Original Model Metrics on {_shorten_dataset_name(dataset_name)}"
    else:
        metrics_source_dict = dataset_info.get(model_or_method_name)
        plot_title = f"Metrics for {_shorten_model_name(model_or_method_name)} on {_shorten_dataset_name(dataset_name)}"

    if not metrics_source_dict or not isinstance(metrics_source_dict, dict):
        print(
            f"Model/Method '{model_or_method_name}' not found or has no metric data in dataset '{dataset_name}'."
        )
        return

    utility_keys_to_ignore = [
        "test_name",
        "test_size",
        "test_index",
        "test_runtime",
        "test_samples_per_second",
        "test_steps_per_second",
        "epoch",
        "Accuracy",
    ]

    metrics_data = {
        k: v
        for k, v in metrics_source_dict.items()
        if isinstance(v, (int, float))
        and not np.isnan(v)
        and k not in utility_keys_to_ignore
    }

    if not metrics_data:
        print(
            f"No numeric metrics found for '{model_or_method_name}' in dataset '{dataset_name}'."
        )
        return

    sorted_metrics = sorted(
        metrics_data.items(), key=lambda item: item[0]
    )  # Sort by metric name
    metric_names = [item[0] for item in sorted_metrics]
    metric_values = [item[1] for item in sorted_metrics]

    fig, ax = plt.subplots(figsize=(max(10, len(metric_names) * 0.7), 6))
    bars = ax.bar(metric_names, metric_values, color="cornflowerblue")

    ax.set_xlabel("Metric", fontsize=12)
    ax.set_ylabel("Score", fontsize=12)
    ax.set_title(plot_title, fontsize=14)
    plt.xticks(rotation=45, ha="right", fontsize=10)
    ax.grid(True, axis="y", linestyle="--", alpha=0.7)

    for bar in bars:
        yval = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            yval,
            f"{yval:.3f}",
            va="bottom",
            ha="center",
            fontsize=9,
        )

    plt.tight_layout()
    plt.show()


def plot_specific_metric_on_dataset_for_all_models(
    data, dataset_name, metric_name, show_original=True
):
    """
    Compares a specific metric across all models/methods for a given dataset.

    Args:
        data (dict): The parsed JSON data.
        dataset_name (str): The name of the dataset.
        metric_name (str): The metric to compare.
        show_original (bool): If True, includes 'Original Model' performance.
    """
    dataset_info = data.get(dataset_name)
    if not dataset_info:
        print(f"Dataset '{dataset_name}' not found.")
        return

    models_scores = {}

    if show_original:
        original_metrics_data = dataset_info.get("original_metrics", {})
        val = original_metrics_data.get(metric_name)
        if isinstance(val, (int, float)) and not np.isnan(val):
            models_scores["Original Model"] = val

    for model_key, model_data in dataset_info.items():
        if model_key not in ["metrics", "original_metrics"] and isinstance(
            model_data, dict
        ):
            val = model_data.get(metric_name)
            if isinstance(val, (int, float)) and not np.isnan(val):
                models_scores[model_key] = val

    if not models_scores:
        print(
            f"No data found for metric '{metric_name}' in dataset '{_shorten_dataset_name(dataset_name)}'."
        )
        return

    sorted_models_scores = dict(
        sorted(models_scores.items(), key=lambda item: item[1], reverse=True)
    )

    model_names_plot = [_shorten_model_name(m) for m in sorted_models_scores.keys()]
    metric_values_plot = list(sorted_models_scores.values())

    fig, ax = plt.subplots(figsize=(max(12, len(model_names_plot) * 0.5), 7))
    bars = ax.bar(model_names_plot, metric_values_plot, color="mediumseagreen")

    ax.set_xlabel("Model / Method", fontsize=12)
    ax.set_ylabel(metric_name, fontsize=12)
    ax.set_title(f"{metric_name} on {_shorten_dataset_name(dataset_name)}", fontsize=14)
    plt.xticks(rotation=45, ha="right", fontsize=10)
    ax.grid(True, axis="y", linestyle="--", alpha=0.7)

    for bar in bars:
        yval = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            yval,
            f"{yval:.3f}",
            va="bottom",
            ha="center",
            fontsize=9,
        )

    plt.tight_layout()
    plt.show()


def plot_metric_distribution(data, metric_name, chart_type="hist"):
    """
    Plots the distribution of a specific metric across all models/methods and datasets.

    Args:
        data (dict): The parsed JSON data.
        metric_name (str): The metric whose distribution is to be plotted.
        chart_type (str): Type of chart: 'hist' for histogram, 'box' for box plot.
    """
    all_scores = []
    sources = []  # To potentially color by source if using boxplot per model type later

    for dataset_name, dataset_info in data.items():
        # Original model scores
        original_m_data = dataset_info.get("original_metrics", {})
        score_orig = original_m_data.get(metric_name)
        if isinstance(score_orig, (int, float)) and not np.isnan(score_orig):
            all_scores.append(score_orig)
            sources.append("Original")

        # Other models/methods
        for model_key, model_data_dict in dataset_info.items():
            if model_key not in ["metrics", "original_metrics"] and isinstance(
                model_data_dict, dict
            ):
                score = model_data_dict.get(metric_name)
                if isinstance(score, (int, float)) and not np.isnan(score):
                    all_scores.append(score)
                    sources.append(
                        model_key
                    )  # Could be used for more detailed boxplots

    if not all_scores:
        print(f"No scores found for metric '{metric_name}' to plot distribution.")
        return

    plt.figure(figsize=(10, 6))
    if chart_type == "hist":
        plt.hist(all_scores, bins=20, color="teal", edgecolor="black", alpha=0.7)
        plt.title(f"Distribution of {metric_name} Scores (All Sources)", fontsize=14)
        plt.xlabel(metric_name, fontsize=12)
        plt.ylabel("Frequency", fontsize=12)
    elif chart_type == "box":
        plt.boxplot(
            all_scores,
            vert=False,
            patch_artist=True,
            boxprops=dict(facecolor="lightblue"),
            medianprops=dict(color="red"),
        )
        plt.title(f"Box Plot of {metric_name} Scores (All Sources)", fontsize=14)
        plt.xlabel(metric_name, fontsize=12)
        plt.yticks([])
    else:
        print(f"Unknown chart type: {chart_type}. Use 'hist' or 'box'.")
        return

    plt.grid(True, axis="x" if chart_type == "box" else "y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.show()


def plot_task_vs_anonymization_metric(
    data, task_metric_name, anon_metric_name, model_type_filter=None
):
    """
    Creates a scatter plot of a task performance metric vs. an anonymization/utility metric,
    with a legend for different model/method groups.

    Args:
        data (dict): The parsed JSON data.
        task_metric_name (str): e.g., 'test_f1', 'test_accuracy'.
        anon_metric_name (str): e.g., 'bertscore_f1', 'rougeL', 'sbert'.
        model_type_filter (str, optional): Filter for specific model types or methods
                                          (e.g., 'pii', 'authorship', 'Dummy Model').
                                          If None, automatically groups common model types.
    """
    grouped_data = {}  # {group_name: {'task': [], 'anon': []}}

    for dataset_name, dataset_info in data.items():
        for model_key, model_data_dict in dataset_info.items():
            if model_key in ["metrics", "original_metrics"] or not isinstance(
                model_data_dict, dict
            ):
                continue

            task_val = model_data_dict.get(task_metric_name)
            anon_val = model_data_dict.get(anon_metric_name)

            if not (
                isinstance(task_val, (int, float))
                and not np.isnan(task_val)
                and isinstance(anon_val, (int, float))
                and not np.isnan(anon_val)
            ):
                continue

            current_group = None
            passes_filter = False

            if model_type_filter:
                # Check if the current model_key matches the filter
                if (
                    model_key == model_type_filter
                ):  # Exact match for full model/method names
                    passes_filter = True
                    current_group = _shorten_model_name(
                        model_type_filter, 30
                    )  # Use filter as group name
                elif model_key.endswith(
                    f"/{model_type_filter}"
                ):  # Suffix for methods like 'pii', 'authorship'
                    passes_filter = True
                    current_group = model_type_filter  # Use filter as group name
                # Add more specific filter conditions if needed, e.g., checking a part of the model_key
                elif (
                    model_type_filter.lower() in model_key.lower()
                    and "/" not in model_type_filter
                ):  # general substring if filter is simple (not a path)
                    passes_filter = True
                    current_group = model_type_filter

                if not passes_filter:
                    continue  # Skip if it doesn't match the filter
            else:
                # Automatic grouping if no filter is applied
                if model_key == "Original Model":
                    current_group = "Original Model"
                elif model_key == "Dummy Model":
                    current_group = "Dummy Model"
                elif model_key == "UniquePlaceholderPerEntity":
                    current_group = "Unique Placeholder"
                elif model_key.endswith("/pii"):
                    current_group = "PII Methods"
                elif model_key.endswith("/authorship"):
                    current_group = "Authorship Methods"
                else:
                    current_group = (
                        model_key  # Fallback for models not fitting specific categories
                    )

            if current_group:
                if current_group not in grouped_data:
                    grouped_data[current_group] = {"task": [], "anon": []}
                grouped_data[current_group]["task"].append(task_val)
                grouped_data[current_group]["anon"].append(anon_val)

    if not grouped_data:
        filter_msg = f" (filter: {model_type_filter})" if model_type_filter else ""
        print(
            f"No data points found for {task_metric_name} vs. {anon_metric_name}{filter_msg}."
        )
        return

    plt.figure(figsize=(12, 8))

    # Define a list of colors to cycle through for different groups
    # Using 'tab10' which has 10 distinct colors. Add more if you expect more groups.
    color_map = plt.cm.get_cmap("tab10")
    colors = [color_map(i) for i in range(len(grouped_data))]

    for i, (group_name, scores_dict) in enumerate(grouped_data.items()):
        if scores_dict["task"]:  # Ensure there are points to plot for this group
            plt.scatter(
                scores_dict["anon"],
                scores_dict["task"],
                alpha=0.7,
                label=group_name,
                color=colors[i % len(colors)],
            )

    plt.xlabel(f"{anon_metric_name} (Anonymization/Utility)", fontsize=12)
    plt.ylabel(f"{task_metric_name} (Task Performance)", fontsize=12)
    title_filter_part = (
        f" (Filtered by: {model_type_filter})"
        if model_type_filter
        else " (All Model Types)"
    )
    plt.title(
        f"Task Performance vs. Anonymization Metric{title_filter_part}", fontsize=14
    )

    plt.grid(True, linestyle="--", alpha=0.7)
    # Adjust legend position if it overlaps with data
    plt.legend(loc="best", fontsize=10)  # 'best' tries to find a good spot
    # If legend is consistently problematic, use fixed placement:
    # plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
    # plt.tight_layout(rect=[0, 0, 0.85, 1]) # if legend is outside

    plt.tight_layout()  # Adjust layout to make sure everything fits
    plt.show()


def plot_radar_model_comparison(
    data,
    metric_name,
    model_list,  # List of series (model_key, label, color) for this single radar
    ordered_dataset_keys,
):
    """
    Generates a single radar plot to compare specified model series across datasets for a given metric.

    Args:
        data (dict): The main parsed JSON data.
        metric_name (str): The metric to plot (e.g., 'sbert', 'test_f1').
        model_series_config (list): A list of dictionaries. Each dictionary defines a series
            to plot on this radar and contains:
            - "label" (str): Label for this series in the legend.
            - "model_key" (str): The full key to find this model's data in the `data` object.
                                 This key should directly point to the dictionary containing the metrics.
            - "color" (str): Color for this series.
    ordered_dataset_keys (list): List of dataset keys from the `data` object,
                                 determining the order of axes on the radar.
    ordered_dataset_display_labels (list): List of display labels for the datasets,
                                           corresponding to `ordered_dataset_keys`.
    plot_title (str, optional): Title for the plot.
    y_axis_ticks (list, optional): List of y-axis tick values.
    y_axis_lim (tuple, optional): Tuple (min, max) for y-axis limit.
    default_value_for_missing (float, optional): Value to use if a metric is not found.
    ax (matplotlib.axes.Axes, optional): An existing Axes object to plot on.
                                         If None, a new figure and axes will be created.
    """
    num_vars = len(ordered_dataset_keys)
    if num_vars == 0:
        print("Error: No datasets specified for radar axes.")
        return
    # Prepare angles for radar plot
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]

    # Score Extraction
    extracted_scores_for_plot = {}

    for model_name in model_list:
        # e.g., "google/gemini-flash-1.5-8b/authorship"
        current_series_scores = []

        for dataset_key in ordered_dataset_keys:
            dataset_level_data = data.get(dataset_key, {})
            # The model_key should directly point to the metrics dict
            model_specific_data = dataset_level_data.get(model_name, {})
            score = model_specific_data.get(metric_name, np.nan)

            if not isinstance(score, (int, float)):
                score = np.nan
            current_series_scores.append(score)

        extracted_scores_for_plot[model_name] = current_series_scores

    # --- Plotting ---
    fig, current_ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))

    for model_name in model_list:
        scores_for_radar = extracted_scores_for_plot.get(model_name, [])
        if (
            not scores_for_radar
        ):  # Should not happen if config is correct but good to check
            print(f"Warning: No scores found for series '{model_name}'")
            continue

        plot_values = [
            float(s) if not isinstance(s, str) else np.nan for s in scores_for_radar
        ]
        plot_values += plot_values[:1]  # Close the radar

        current_ax.plot(angles, plot_values, linewidth=2, label=model_name)
        current_ax.fill(angles, plot_values, alpha=0.25)

    current_ax.set_xticks(angles[:-1])
    # Shorten dataset labels if they are full keys
    short_labels = [
        _shorten_dataset_name(lbl) if "/" in lbl else lbl
        for lbl in ordered_dataset_keys
    ]
    current_ax.set_xticklabels(short_labels, fontsize=10)

    all_vals_this_plot = []
    for s_label in extracted_scores_for_plot:
        all_vals_this_plot.extend(
            [v for v in extracted_scores_for_plot[s_label] if not np.isnan(v)]
        )
    if all_vals_this_plot:
        min_val_plot = min(all_vals_this_plot)
        max_val_plot = max(all_vals_this_plot)
        padding = (
            (max_val_plot - min_val_plot) * 0.1
            if (max_val_plot - min_val_plot) > 0
            else 0.1
        )
        current_ax.set_ylim(
            min_val_plot - padding,
            (
                max_val_plot + padding
                if max_val_plot > min_val_plot
                else max_val_plot + 0.2
            ),
        )

    current_ax.grid(True)
    current_ax.legend(
        loc="lower center", bbox_to_anchor=(0.5, -0.2), ncol=len(model_list), fontsize=9
    )

    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    plt.show()
