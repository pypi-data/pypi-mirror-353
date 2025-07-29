import evaluate

_DESCRIPTION = """\
First Relevant Rank (Rank1) metric measures the rank position where the first relevant item is retrieved.
This is a crucial metric in information retrieval and content-based image retrieval (CBIR) systems.

The metric returns the rank (1-indexed) of the highest-ranked relevant item. Lower values indicate better performance.
If no relevant items are found, it returns the total number of items + 1.

Based on the TREC evaluation methodology as described in:
"Performance Evaluation in Content-Based Image Retrieval: Overview and Proposals"
"""

_KWARGS_DESCRIPTION = """\
Args:
    predictions: List of item IDs or scores in ranked order (highest ranked first)
    references: List of relevant item IDs for the query

    Alternative format:
    predictions: List of (item_id, score) tuples in ranked order  
    references: List of relevance labels (1 for relevant, 0 for not relevant) in same order as predictions

Returns:
    first_relevant_rank: The rank (1-indexed) where the first relevant item appears

Examples:
    >>> first_relevant_rank = evaluate.load("first_relevant_rank")
    >>> predictions = ["item_3", "item_1", "item_5", "item_2", "item_4"]
    >>> references = ["item_1", "item_2"]  # relevant items
    >>> results = first_relevant_rank.compute(predictions=predictions, references=references)
    >>> print(results)
    {'first_relevant_rank': 2}

    >>> # Using relevance labels format
    >>> predictions = ["item_1", "item_2", "item_3", "item_4", "item_5"] 
    >>> references = [0, 1, 0, 1, 0]  # item_2 and item_4 are relevant
    >>> results = first_relevant_rank.compute(predictions=predictions, references=references)
    >>> print(results)
    {'first_relevant_rank': 2}
"""

_CITATION = """\
@article{muller2001performance,
    title={Performance evaluation in content-based image retrieval: overview and proposals},
    author={M{\"u}ller, Henning and M{\"u}ller, Wolfgang and Squire, David McG and Marchand-Maillet, St{\'e}phane and Pun, Thierry},
    journal={Pattern Recognition Letters},
    volume={22},
    number={5},
    pages={593--601},
    year={2001},
    publisher={Elsevier}
}
"""


@evaluate.utils.file_utils.add_start_docstrings(_DESCRIPTION, _KWARGS_DESCRIPTION)
class FirstRelevantRank(evaluate.Metric):

    def _info(self):
        return evaluate.MetricInfo(
            description=_DESCRIPTION,
            citation=_CITATION,
            inputs_description=_KWARGS_DESCRIPTION,
            features=datasets.Features({
                "predictions": datasets.Sequence(datasets.Value("string")),
                "references": datasets.Sequence(datasets.Value("string")),
            }),
            reference_urls=["https://www.sciencedirect.com/science/article/abs/pii/S0167865500001185"]
        )
