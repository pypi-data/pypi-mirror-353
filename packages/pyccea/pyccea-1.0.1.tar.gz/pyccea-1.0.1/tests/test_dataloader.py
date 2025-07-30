import pytest
import logging
import numpy as np
import pandas as pd
from unittest.mock import patch
from pyccea.utils.datasets import DataLoader
from sklearn.model_selection import GroupKFold, KFold, LeaveOneOut, StratifiedKFold


# Disable logging output during tests
logging.disable(logging.CRITICAL)


def test_init_valid_data_conf(complete_data_conf: dict) -> None:
    """Test DataLoader initialization with a valid configuration."""
    DataLoader("dummy_dataset", complete_data_conf)


def test_init_asserts_missing_data_conf_sections(complete_data_conf: dict) -> None:
    """Test DataLoader initialization with configurations missing required sections."""
    for primary_key in complete_data_conf.keys():
        with pytest.raises(AssertionError):
            incomplete_data_conf = complete_data_conf.copy()
            incomplete_data_conf.pop(primary_key)
            DataLoader("dummy_dataset", incomplete_data_conf)


def test_parse_general_parameters_missing_splitter_type(complete_data_conf: dict) -> None:
    """Test DataLoader initialization with missing splitter_type."""
    complete_data_conf["general"].pop("splitter_type")
    with pytest.raises(AssertionError):
        DataLoader("dummy_dataset", complete_data_conf)


def test_parse_general_parameters_invalid_splitter_type(complete_data_conf: dict) -> None:
    """Test DataLoader initialization with invalid splitter_type."""
    complete_data_conf["general"]["splitter_type"] = "invalid_type"
    with pytest.raises(NotImplementedError):
        DataLoader("dummy_dataset", complete_data_conf)


def test_parse_splitter_parameters_missing_kfolds(complete_data_conf: dict) -> None:
    """Test DataLoader initialization with missing kfolds."""
    complete_data_conf["splitter_type"] = "k_fold"
    del complete_data_conf["splitter"]["kfolds"]
    with pytest.raises(AssertionError):
        DataLoader("dummy_dataset", complete_data_conf)


def test_parse_splitter_parameters_preset_true_and_test_ratio(complete_data_conf: dict) -> None:
    """Test DataLoader initialization with preset and test ratio."""
    complete_data_conf["splitter"]["preset"] = True
    complete_data_conf["splitter"]["test_ratio"] = 0.2
    dl = DataLoader("dummy_dataset", complete_data_conf)
    assert dl.test_ratio is None


def test_parse_splitter_parameters_missing_test_ratio_and_preset_false(complete_data_conf: dict) -> None:
    """Test DataLoader initialization with missing test ratio when preset is false."""
    complete_data_conf["splitter"]["preset"] = False
    with pytest.raises(ValueError):
        DataLoader("dummy_dataset", complete_data_conf)


def test_parse_splitter_parameters_test_ratio_out_of_bounds(complete_data_conf: dict) -> None:
    """Test DataLoader initialization with test ratio out of bounds."""
    complete_data_conf["splitter"]["preset"] = False
    for test_ratio in [-0.5, 1.5]:
        complete_data_conf["splitter"]["test_ratio"] = test_ratio
        with pytest.raises(ValueError):
            DataLoader("dummy_dataset", complete_data_conf)


def test_parse_normalization_parameters_missing_method(complete_data_conf: dict) -> None:
    """Test DataLoader initialization with missing normalization method."""
    complete_data_conf["normalization"]["normalize"] = True
    complete_data_conf["normalization"].pop("method")
    with pytest.raises(AssertionError):
        DataLoader("dummy_dataset", complete_data_conf)


def test_parse_normalization_parameters_invalid_method(complete_data_conf: dict) -> None:
    """Test DataLoader initialization with invalid normalization method."""
    complete_data_conf["normalization"]["normalize"] = True
    complete_data_conf["normalization"]["method"] = "invalid_method"
    with pytest.raises(NotImplementedError):
        DataLoader("dummy_dataset", complete_data_conf)


def test_parse_normalization_parameters_method_and_normalize_false(complete_data_conf: dict) -> None:
    """Test DataLoader initialization with normalization method when normalize is false."""
    complete_data_conf["normalization"]["normalize"] = False
    complete_data_conf["normalization"]["method"] = "min_max"
    with pytest.raises(ValueError):
        DataLoader("dummy_dataset", complete_data_conf)


def test_get_ready_calls_all_methods(mocker, complete_data_conf: dict) -> None:
    """Test get_ready method when normalize is True."""
    loader = DataLoader("dummy", complete_data_conf)

    # Mock _load to assign synthetic data
    def _mock_load():
        loader.data = pd.DataFrame({
            0: [1, 2, 3, 4, 5],
            1: [6, 7, 8, 9, 0],
            2: [0, 1, 0, 1, 1],
            3: ["train", "train", "train", "test", "test"]
        })

    mocker.patch.object(loader, "_load", side_effect=_mock_load)

    # Mock the other methods just to track their calls
    mocker.patch.object(loader, "_preprocess")
    mocker.patch.object(loader, "_split")
    mocker.patch.object(loader, "_normalize_subsets")
    mocker.patch.object(loader, "_model_selection")

    # Act
    loader.get_ready()

    # Assert: all methods called once
    loader._load.assert_called_once()
    loader._preprocess.assert_called_once()
    loader._split.assert_called_once()
    loader._normalize_subsets.assert_called_once()
    loader._model_selection.assert_called_once()


def test_get_ready_without_normalize(mocker, complete_data_conf: dict) -> None:
    """Test get_ready method when normalize is False."""
    complete_data_conf["normalization"]["normalize"] = False
    del complete_data_conf["normalization"]["method"]
    loader = DataLoader("dummy", complete_data_conf)

    # Mock _load to assign synthetic data
    def _mock_load():
        loader.data = pd.DataFrame({
            0: [1, 2, 3, 4, 5],
            1: [6, 7, 8, 9, 0],
            2: [0, 1, 0, 1, 1],
            3: ["train", "train", "train", "test", "test"]
        })

    mocker.patch.object(loader, "_load", side_effect=_mock_load)

    # Mock the other methods just to track their calls
    mocker.patch.object(loader, "_preprocess")
    mocker.patch.object(loader, "_split")
    mocker.patch.object(loader, "_normalize_subsets")
    mocker.patch.object(loader, "_model_selection")

    # Act
    loader.get_ready()

    # Assert: normalization should NOT be called
    loader._load.assert_called_once()
    loader._preprocess.assert_called_once()
    loader._split.assert_called_once()
    loader._normalize_subsets.assert_not_called()
    loader._model_selection.assert_called_once()


def test_load_data_invalid_dataset_name(complete_data_conf: dict) -> None:
    """Test DataLoader initialization with an invalid dataset name."""
    with pytest.raises(ValueError):
        dl = DataLoader("invalid_dataset", complete_data_conf)
        dl._load()


def test_load_dataset(monkeypatch, complete_data_conf: dict) -> None:
    """Test _load reads PARQUET correctly."""

    loader = DataLoader("dummy_dataset", complete_data_conf)

    # Patch os.path.dirname and os.path.join to return a dummy path
    monkeypatch.setattr("os.path.dirname", lambda _: "/dummy_dir")
    monkeypatch.setattr("os.path.join", lambda *args: "/dummy_dir/datasets/dummy.parquet")

    # Patch DataLoader.DATASETS to simulate dataset file mapping
    dummy_dataset_info = {"dummy_dataset": {"file": "dummy.parquet", "task": "regression"}}
    with patch.object(DataLoader, "DATASETS", dummy_dataset_info):

        # Mock pd.read_parquet to return a dummy DataFrame
        dummy_df = pd.DataFrame({
            "A": [1, 2],
            "B": [3, 4]
        })

        with patch("pandas.read_parquet", return_value=dummy_df) as mock_read_parquet:
            loader._load()

            # Assert pd.read_parquet called
            mock_read_parquet.assert_called_once_with("/dummy_dir/datasets/dummy.parquet")

            # Assert the data attribute got assigned
            pd.testing.assert_frame_equal(loader.data, dummy_df)


def test_get_input_and_output(complete_data_conf: dict) -> None:
    """Test _get_input and _get_output extract correct columns."""
    loader = DataLoader("dummy", complete_data_conf)
    loader.data = pd.DataFrame({
        "0": [1, 2],
        "1": [3, 4],
        "label": [5, 6],
        "subset": ["train", "test"]
    })

    X = loader._get_input()
    y = loader._get_output()

    expected_X = pd.DataFrame({"0": [1, 2], "1": [3, 4]})
    expected_y = pd.Series([5, 6], name="label")

    pd.testing.assert_frame_equal(X, expected_X)
    pd.testing.assert_series_equal(y, expected_y)


def test_preprocess(monkeypatch, complete_data_conf: dict) -> None:
    """Test _preprocess replaces ? with NaN, drops rows if required."""
    loader = DataLoader("dummy", complete_data_conf)
    loader.data = pd.DataFrame({
        "0": [1, "?", 3],
        "1": [4, 5, None],
        "label": [0, 1, 0],
        "subset": ["train", "test", "train"]
    })

    monkeypatch.setitem(DataLoader.DATASETS, "dummy", {"task": "classification"})

    loader._preprocess()

    # Check NaN replaced and rows dropped
    assert not loader.data.isin(["?"]).any().any()
    assert loader.n_examples == 1
    assert loader.n_features == 2
    assert loader.n_classes == 1
    assert loader.classes == [0]


def test_split_preset(monkeypatch, complete_data_conf: dict) -> None:
    """Test _split with preset splits."""
    loader = DataLoader("dummy", complete_data_conf)
    loader.data = pd.DataFrame({
        "0": [1, 2, 3, 4, 5],
        "1": [6, 7, 8, 9, 0],
        "label": [0, 1, 0, 1, 1],
        "subset": ["train", "train", "train", "test", "test"]
    })
    loader.X = loader._get_input()
    loader.y = loader._get_output()

    loader._split()

    assert loader.X_train.shape[0] == 3
    assert loader.X_test.shape[0] == 2


def test_split_without_preset(complete_data_conf: dict) -> None:
    """Test _split without preset splits."""
    complete_data_conf["splitter"]["preset"] = False
    complete_data_conf["splitter"]["test_ratio"] = 0.3
    loader = DataLoader("dummy", complete_data_conf)
    n_samples = 100
    loader.data = pd.DataFrame({
        "0": np.arange(n_samples),
        "1": np.arange(n_samples, 2*n_samples),
        "label": [0, 1] * 50,
        "subset": ["train"] * 70 + ["test"] * 30
    })
    loader.X = loader._get_input()
    loader.y = loader._get_output()

    loader._split()

    # Check sizes
    expected_train_size = int(n_samples * (1 - loader.test_ratio))
    expected_test_size = int(n_samples * loader.test_ratio)

    assert loader.X_train.shape[0] == expected_train_size
    assert loader.X_test.shape[0] == expected_test_size
    assert loader.y_train.shape[0] == expected_train_size
    assert loader.y_test.shape[0] == expected_test_size

    # Check no data loss
    total_samples = loader.X_train.shape[0] + loader.X_test.shape[0]
    assert total_samples == n_samples

    # Check subset size attributes
    assert loader.train_size == expected_train_size
    assert loader.test_size == expected_test_size


def test_min_max_normalization(complete_data_conf: dict) -> None:
    """Test min-max normalization of subsets."""
    # Min max normalization
    complete_data_conf["normalization"]["method"] = "min_max"
    loader = DataLoader("dummy", complete_data_conf)
    loader.data = pd.DataFrame({
        "0": [1, 2, 3, 4, 5],
        "1": [6, 7, 8, 9, 0],
        "label": [0, 1, 0, 1, 1],
        "subset": ["train", "train", "train", "test", "test"]
    })
    loader.X = loader._get_input()
    loader.y = loader._get_output()
    loader._split()

    loader._normalize_subsets()

    assert np.allclose(loader.X_train, np.array([[0., 0.], [0.5, 0.5], [1., 1.]]))


def test_standard_normalization(complete_data_conf: dict) -> None:
    # Standard normalization
    complete_data_conf["normalization"]["method"] = "standard"
    loader = DataLoader("dummy", complete_data_conf)
    loader.data = pd.DataFrame({
        "0": [1, 2, 3, 4, 5],
        "1": [6, 7, 8, 9, 0],
        "label": [0, 1, 0, 1, 1],
        "subset": ["train", "train", "train", "test", "test"]
    })
    loader.X = loader._get_input()
    loader.y = loader._get_output()
    loader._split()
    loader._normalize_subsets()
    # For standard scaler: mean 0, std 1 in training set
    assert np.allclose(loader.X_train.mean(axis=0), np.zeros(loader.X_train.shape[1]))
    assert np.allclose(loader.X_train.std(axis=0), np.ones(loader.X_train.shape[1]))


def test_kfold_model_selection_prefold_missing_fold_column(monkeypatch, complete_data_conf: dict) -> None:
    """Test k-fold model selection when 'prefold' is True but the dataset lacks the required 'fold' column."""
    complete_data_conf["splitter"]["prefold"] = True
    complete_data_conf["splitter"]["kfolds"] = 3
    loader = DataLoader("dummy", complete_data_conf)
    monkeypatch.setitem(DataLoader.DATASETS, "dummy", {"task": "classification"})
    loader.data = pd.DataFrame({
        "0": [1, 2, 3, 4, 5],
        "1": [6, 7, 8, 9, 0],
        "label": [0, 1, 0, 1, 1],
        "subset": ["train", "train", "train", "test", "test"]
    })
    loader.X = loader._get_input()
    loader.y = loader._get_output()
    loader._split()
    with pytest.raises(AssertionError, match="The 'fold' column should be specified"):
        loader._model_selection()


def test_kfold_model_selection_prefold_mismatched_folds(monkeypatch, complete_data_conf: dict) -> None:
    """Test k-fold model selection with 'prefold' set to True and kfolds specified does not match the number of
    folds in the dataset."""
    complete_data_conf["splitter"]["prefold"] = True
    complete_data_conf["splitter"]["kfolds"] = 4
    loader = DataLoader("dummy", complete_data_conf)
    monkeypatch.setitem(DataLoader.DATASETS, "dummy", {"task": "classification"})
    loader.data = pd.DataFrame({
        "0": [1, 2, 3, 4, 5],
        "1": [6, 7, 8, 9, 0],
        "label": [0, 1, 0, 1, 1],
        "subset": ["train", "train", "train", "test", "test"],
        "fold": [1, 2, 3, 1, 2]
    })
    loader.X = loader._get_input()
    loader.y = loader._get_output()
    loader._split()
    with pytest.raises(AssertionError, match="The number of folds in the training set"):
        loader._model_selection()


def test_stratified_kfold_model_selection(monkeypatch, complete_data_conf: dict) -> None:
    """Test _model_selection with k_fold splitter."""
    complete_data_conf["splitter"]["kfolds"] = 2
    loader = DataLoader("dummy", complete_data_conf)
    monkeypatch.setitem(DataLoader.DATASETS, "dummy", {"task": "classification"})
    loader.X_train = np.array([[1], [2], [3], [4], [5], [6]])
    loader.y_train = np.array([0, 1, 0, 1, 1, 0])

    loader._model_selection()

    assert len(loader.train_folds) == loader.kfolds
    assert len(loader.val_folds) == loader.kfolds
    assert isinstance(loader.splitter, StratifiedKFold)


def test_kfold_model_selection(monkeypatch, complete_data_conf: dict) -> None:
    """Test _model_selection with k_fold splitter."""
    complete_data_conf["splitter"]["kfolds"] = 2
    loader = DataLoader("dummy", complete_data_conf)
    monkeypatch.setitem(DataLoader.DATASETS, "dummy", {"task": "regression"})
    loader.X_train = np.array([[1], [2], [3], [4], [5], [6]])
    loader.y_train = np.array([0, 1, 0, 1, 1, 0])

    loader._model_selection()

    assert len(loader.train_folds) == loader.kfolds
    assert len(loader.val_folds) == loader.kfolds
    assert isinstance(loader.splitter, KFold)


def test_group_kfold_model_selection(monkeypatch, complete_data_conf: dict) -> None:
    """Test k-fold model selection when 'prefold' is True."""
    complete_data_conf["splitter"]["prefold"] = True
    del complete_data_conf["splitter"]["stratified"]
    del complete_data_conf["splitter"]["kfolds"]
    loader = DataLoader("dummy", complete_data_conf)
    monkeypatch.setitem(DataLoader.DATASETS, "dummy", {"task": "classification"})
    loader.data = pd.DataFrame({
        "0": [1, 2, 3, 4, 5, 6, 7, 8, 9, 0],
        "1": [6, 7, 8, 9, 0, 1, 2, 3, 4, 5],
        "label": [0, 1, 0, 1, 1, 0, 1, 0, 1, 0],
        "subset": ["train"] * 7 + ["test"] * 3,
        "fold": [1, 2, 3, 1, 2, 3, 1, 4, 4, 5]
    })
    loader.X = loader._get_input()
    loader.y = loader._get_output()
    loader._split()
    loader._model_selection()

    assert len(loader.train_folds) == loader.kfolds
    assert len(loader.val_folds) == loader.kfolds
    assert isinstance(loader.splitter, GroupKFold)

    # Original group counts by fold (only for training subset)
    original_group_counts = (
        loader.data.query("subset == 'train'").groupby("fold")["fold"].count()
    )

    for i, _ in enumerate(zip(loader.train_folds, loader.val_folds)):
        val_indices = loader.val_indices[i]
        train_indices = loader.train_indices[i]

        # Folds present in the training and validation sets
        train_folds_present = loader.data.iloc[train_indices]["fold"].unique()
        val_folds_present = loader.data.iloc[val_indices]["fold"].unique()

        # Ensure that the union of training and validation folds equals the full set of original folds
        total_folds_seen = set(train_folds_present).union(set(val_folds_present))
        assert total_folds_seen == set(original_group_counts.index)

        # Ensure that no fold is present in both training and validation sets
        intersection = set(train_folds_present).intersection(set(val_folds_present))
        assert not intersection

        # Ensure that all samples from each training fold are correctly included in train_indices
        for train_fold in train_folds_present:
            expected_train_indices = loader.data.query(f"fold == {train_fold} and subset == 'train'").index.tolist()
            actual_train_indices = loader.data.iloc[train_indices].query(f"fold == {train_fold}").index.tolist()
            assert set(actual_train_indices) == set(expected_train_indices)
        # Ensure that all samples from the validation fold are correctly included in val_indices
        for val_fold in val_folds_present:
            expected_val_indices = loader.data.query(f"fold == {val_fold} and subset == 'train'").index.tolist()
            actual_val_indices = loader.data.iloc[val_indices].query(f"fold == {val_fold}").index.tolist()
            assert set(actual_val_indices) == set(expected_val_indices)


def test_leave_one_out_model_selection_prefold(monkeypatch, complete_data_conf: dict) -> None:
    """Test leave one out model selection when 'prefold' is True."""
    complete_data_conf["splitter"]["prefold"] = True
    complete_data_conf["general"]["splitter_type"] = "leave_one_out"
    del complete_data_conf["splitter"]["kfolds"]
    del complete_data_conf["splitter"]["stratified"]
    with pytest.warns(UserWarning, match="You specified the 'prefold' parameter"):
        _ = DataLoader("dummy", complete_data_conf)


def test_leave_one_out_model_selection_kfolds(monkeypatch, complete_data_conf: dict) -> None:
    """Test leave one out model selection when kfolds is specified."""
    complete_data_conf["general"]["splitter_type"] = "leave_one_out"
    complete_data_conf["splitter"]["kfolds"] = 3
    del complete_data_conf["splitter"]["stratified"]
    with pytest.warns(UserWarning, match="You specified the number of folds using Leave-One-Out"):
        _ = DataLoader("dummy", complete_data_conf)


def test_leave_one_out_model_selection_stratified(monkeypatch, complete_data_conf: dict) -> None:
    """Test leave one out model selection when stratified is True."""
    complete_data_conf["general"]["splitter_type"] = "leave_one_out"
    complete_data_conf["splitter"]["stratified"] = True
    del complete_data_conf["splitter"]["kfolds"]
    with pytest.warns(UserWarning, match="You specified the 'stratified' parameter using Leave-One-Out"):
        _ = DataLoader("dummy", complete_data_conf)


def test_leave_one_out_model_selection(complete_data_conf: dict) -> None:
    """Test _model_selection with leave_one_out splitter."""
    del complete_data_conf["splitter"]["kfolds"]
    del complete_data_conf["splitter"]["stratified"]
    complete_data_conf["general"]["splitter_type"] = "leave_one_out"
    loader = DataLoader("dummy", complete_data_conf)
    loader.data = pd.DataFrame({
        "0": [1, 2, 3, 4, 5],
        "1": [6, 7, 8, 9, 0],
        "label": [0, 1, 0, 1, 1],
        "subset": ["train", "train", "train", "test", "test"]
    })
    loader.X = loader._get_input()
    loader.y = loader._get_output()
    loader._split()

    loader._model_selection()

    assert len(loader.train_folds) == len(loader.X_train)
    assert len(loader.val_folds) == len(loader.X_train)
    assert isinstance(loader.splitter, LeaveOneOut)
