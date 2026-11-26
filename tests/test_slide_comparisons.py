"""The comparison tables of midterm slides 6 and 7 must stay reproducible from the repo's code."""
from experiments.slide_comparisons import compare_intent, compare_retrieval


def test_slide6_retrieval_rows_reproduce_within_tolerance():
    table = compare_retrieval().set_index("method")
    assert len(table) == 8
    lsa = "LSA (TF-IDF + 60-dim SVD)"
    exact = table.drop(index=lsa)
    # Deterministic rows: paraphrase Hit@1 equal to the slide, full MRR within 0.001.
    assert (exact["repo_paraphrase_hit1"] == exact["slide_paraphrase_hit1"]).all()
    assert exact["mrr_diff"].abs().max() <= 0.001
    assert table.loc["TF-IDF char 3-5-grams", "repo_mrr"] == 0.943
    # LSA uses a randomised SVD whose last digits can move with the BLAS build.
    assert abs(table.loc[lsa, "mrr_diff"]) <= 0.01
    assert abs(table.loc[lsa, "repo_paraphrase_hit1"] - table.loc[lsa, "slide_paraphrase_hit1"]) <= 1 / 35 + 1e-9
    # The ranking by MRR is the one shown on the slide.
    assert list(table.sort_values("repo_mrr", ascending=False, kind="stable").index) == list(table.index)


def test_slide7_intent_rows_reproduce_exactly():
    table = compare_intent()
    assert len(table) == 5
    assert (table["train_texts"] == 231).all()
    assert (table["repo_accuracy"] == table["slide_accuracy"]).all()
    assert (table["repo_conf_in_scope"] == table["slide_conf_in_scope"]).all()
    assert (table["repo_conf_ooc"] == table["slide_conf_ooc"]).all()
