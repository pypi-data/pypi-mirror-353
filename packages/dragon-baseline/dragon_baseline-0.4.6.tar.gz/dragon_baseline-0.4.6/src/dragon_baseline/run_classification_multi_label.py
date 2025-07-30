#!/usr/bin/env python
# coding=utf-8
# Copyright 2020 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Finetuning the library models for text classification."""
# You can also adapt this script on your own text classification task. Pointers for this are left as comments.

import logging
import os
import random
import sys
from dataclasses import dataclass, field
from typing import List, Optional, NewType, Any

DataClass = NewType("DataClass", Any)

import datasets
import evaluate
import numpy as np
import transformers
from datasets import Value, load_dataset
from transformers import (AutoConfig, AutoModelForSequenceClassification,
                          AutoTokenizer, DataCollatorWithPadding,
                          EvalPrediction, HfArgumentParser, Trainer,
                          TrainingArguments, default_data_collator, set_seed)
from transformers.trainer_utils import get_last_checkpoint
from transformers.utils import check_min_version, send_example_telemetry
from transformers.utils.versions import require_version

from dragon_baseline.architectures.clf_multi_head import \
    AutoModelForMultiHeadSequenceClassification
from dragon_baseline.architectures.reg_multi_head import \
    AutoModelForMultiHeadSequenceRegression

# Will error if the minimal version of Transformers is not installed. Remove at your own risks.
check_min_version("4.48.0.dev0")

require_version("datasets>=1.8.0", "To fix: pip install -r examples/pytorch/text-classification/requirements.txt")


logger = logging.getLogger(__name__)


@dataclass
class DataTrainingArguments:
    """
    Arguments pertaining to what data we are going to input our model for training and eval.

    Using `HfArgumentParser` we can turn this class
    into argparse arguments to be able to specify them on
    the command line.
    """

    dataset_name: Optional[str] = field(
        default=None, metadata={"help": "The name of the dataset to use (via the datasets library)."}
    )
    dataset_config_name: Optional[str] = field(
        default=None, metadata={"help": "The configuration name of the dataset to use (via the datasets library)."}
    )
    problem_type: str = field(
        default=None,
        metadata={
            "help": "Problem type (regression, classification, multi-label regression, multi-label classification). If None, will be inferred from the dataset."
        },
    )
    text_column_names: Optional[str] = field(
        default=None,
        metadata={
            "help": (
                "The name of the text column in the input dataset or a CSV/JSON file. "
                'If not specified, will use the "sentence" column for single/multi-label classification task.'
            )
        },
    )
    text_column_delimiter: Optional[str] = field(
        default=" ", metadata={"help": "The delimiter to use to join text columns into a single sentence."}
    )
    train_split_name: Optional[str] = field(
        default=None,
        metadata={
            "help": 'The name of the train split in the input dataset. If not specified, will use the "train" split when do_train is enabled'
        },
    )
    validation_split_name: Optional[str] = field(
        default=None,
        metadata={
            "help": 'The name of the validation split in the input dataset. If not specified, will use the "validation" split when do_eval is enabled'
        },
    )
    test_split_name: Optional[str] = field(
        default=None,
        metadata={
            "help": 'The name of the test split in the input dataset. If not specified, will use the "test" split when do_predict is enabled'
        },
    )
    remove_splits: Optional[str] = field(
        default=None,
        metadata={"help": "The splits to remove from the dataset. Multiple splits should be separated by commas."},
    )
    remove_columns: Optional[str] = field(
        default=None,
        metadata={"help": "The columns to remove from the dataset. Multiple columns should be separated by commas."},
    )
    label_column_names: Optional[str] = field(
        default=None,
        metadata={
            "help": (
                "The names of the label columns in the input dataset or a CSV/JSON file."
                'If not specified, will use the "label1"/"label2"/etc. columns for multi-label regression/classifcation task'
            )
        },
    )
    max_seq_length: int = field(
        default=128,
        metadata={
            "help": (
                "The maximum total input sequence length after tokenization. Sequences longer "
                "than this will be truncated, sequences shorter will be padded."
            )
        },
    )
    truncation_side: str = field(
        default="right",
        metadata={
            "help": (
                "The direction to truncate the sequences to max_seq_length when truncation is needed. "
                "One of ('left', 'right', 'longest_first', 'only_first'). Default: 'right'"
            )
        },
    )
    preprocessing_num_workers: Optional[int] = field(
        default=None,
        metadata={"help": "The number of processes to use for the preprocessing."},
    )
    overwrite_cache: bool = field(
        default=False, metadata={"help": "Overwrite the cached preprocessed datasets or not."}
    )
    pad_to_max_length: bool = field(
        default=True,
        metadata={
            "help": (
                "Whether to pad all samples to `max_seq_length`. "
                "If False, will pad the samples dynamically when batching to the maximum length in the batch."
            )
        },
    )
    shuffle_train_dataset: bool = field(
        default=False, metadata={"help": "Whether to shuffle the train dataset or not."}
    )
    shuffle_seed: int = field(
        default=42, metadata={"help": "Random seed that will be used to shuffle the train dataset."}
    )
    max_train_samples: Optional[int] = field(
        default=None,
        metadata={
            "help": (
                "For debugging purposes or quicker training, truncate the number of training examples to this "
                "value if set."
            )
        },
    )
    max_eval_samples: Optional[int] = field(
        default=None,
        metadata={
            "help": (
                "For debugging purposes or quicker training, truncate the number of evaluation examples to this "
                "value if set."
            )
        },
    )
    max_predict_samples: Optional[int] = field(
        default=None,
        metadata={
            "help": (
                "For debugging purposes or quicker training, truncate the number of prediction examples to this "
                "value if set."
            )
        },
    )
    metric_name: Optional[str] = field(default=None, metadata={"help": "The metric to use for evaluation."})
    train_file: Optional[str] = field(
        default=None, metadata={"help": "A csv or a json file containing the training data."}
    )
    validation_file: Optional[str] = field(
        default=None, metadata={"help": "A csv or a json file containing the validation data."}
    )
    test_file: Optional[str] = field(default=None, metadata={"help": "A csv or a json file containing the test data."})

    def __post_init__(self):
        if self.dataset_name is None:
            if self.train_file is None or self.validation_file is None:
                raise ValueError(" training/validation file or a dataset name.")

            train_extension = self.train_file.suffix[1:]
            assert train_extension in ["csv", "json"], "`train_file` should be a csv or a json file."
            validation_extension = self.validation_file.suffix[1:]
            assert (
                validation_extension == train_extension
            ), "`validation_file` should have the same extension (csv or json) as `train_file`."


@dataclass
class ModelArguments:
    """
    Arguments pertaining to which model/config/tokenizer we are going to fine-tune from.
    """

    model_name_or_path: str = field(
        metadata={"help": "Path to pretrained model or model identifier from huggingface.co/models"}
    )
    config_name: Optional[str] = field(
        default=None, metadata={"help": "Pretrained config name or path if not the same as model_name"}
    )
    tokenizer_name: Optional[str] = field(
        default=None, metadata={"help": "Pretrained tokenizer name or path if not the same as model_name"}
    )
    cache_dir: Optional[str] = field(
        default=None,
        metadata={"help": "Where do you want to store the pretrained models downloaded from huggingface.co"},
    )
    use_fast_tokenizer: bool = field(
        default=True,
        metadata={"help": "Whether to use one of the fast tokenizer (backed by the tokenizers library) or not."},
    )
    model_revision: str = field(
        default="main",
        metadata={"help": "The specific model version to use (can be a branch name, tag name or commit id)."},
    )
    token: str = field(
        default=None,
        metadata={
            "help": (
                "The token to use as HTTP bearer authorization for remote files. If not specified, will use the token "
                "generated when running `huggingface-cli login` (stored in `~/.huggingface`)."
            )
        },
    )
    trust_remote_code: bool = field(
        default=False,
        metadata={
            "help": (
                "Whether to trust the execution of code from datasets/models defined on the Hub."
                " This option should only be set to `True` for repositories you trust and in which you have read the"
                " code, as it will execute code present on the Hub on your local machine."
            )
        },
    )
    ignore_mismatched_sizes: bool = field(
        default=False,
        metadata={"help": "Will enable to load a pretrained model whose head dimensions are different."},
    )


def get_label_list(raw_dataset, split="train") -> List[str]:
    """Get the list of labels from a multi-label dataset"""

    if isinstance(raw_dataset[split]["label"][0], list):
        label_list = [label for sample in raw_dataset[split]["label"] for label in sample]
        label_list = list(set(label_list))
    else:
        label_list = raw_dataset[split].unique("label")
    # we will treat the label list as a list of string instead of int, consistent with model.config.label2id
    label_list = [str(label) for label in label_list]
    return label_list

def get_multi_label_classification_argument_parser():
    return HfArgumentParser((ModelArguments, DataTrainingArguments, TrainingArguments))

def get_cli_arguments():
    # See all possible arguments in src/transformers/training_args.py
    # or by passing the --help flag to this script.
    # We now keep distinct sets of args, for a cleaner separation of concerns.
    parser = get_multi_label_classification_argument_parser()
    if len(sys.argv) == 2 and sys.argv[1].endswith(".json"):
        # If we pass only one argument to the script and it's the path to a json file,
        # let's parse it to get our arguments.
        model_args, data_args, training_args = parser.parse_json_file(json_file=os.path.abspath(sys.argv[1]))
    else:
        model_args, data_args, training_args = parser.parse_args_into_dataclasses()

    return model_args, data_args, training_args

def run_multi_label_classification(model_args: DataClass, data_args: DataClass, training_args: DataClass):

    # Sending telemetry. Tracking the example usage helps us better allocate resources to maintain them. The
    # information sent is the one passed as arguments along with your Python/PyTorch versions.
    send_example_telemetry("run_classification", model_args, data_args)

    # Setup logging
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    if training_args.should_log:
        # The default of training_args.log_level is passive, so we set log level at info here to have that default.
        transformers.utils.logging.set_verbosity_info()

    log_level = training_args.get_process_log_level()
    logger.setLevel(log_level)
    datasets.utils.logging.set_verbosity(log_level)
    transformers.utils.logging.set_verbosity(log_level)
    transformers.utils.logging.enable_default_handler()
    transformers.utils.logging.enable_explicit_format()

    # Log on each process the small summary:
    logger.warning(
        f"Process rank: {training_args.local_rank}, device: {training_args.device}, n_gpu: {training_args.n_gpu}, "
        + f"distributed training: {training_args.parallel_mode.value == 'distributed'}, 16-bits training: {training_args.fp16}"
    )
    logger.info(f"Training/evaluation parameters {training_args}")

    # Detecting last checkpoint.
    last_checkpoint = None
    if os.path.isdir(training_args.output_dir) and training_args.do_train and not training_args.overwrite_output_dir:
        last_checkpoint = get_last_checkpoint(training_args.output_dir)
        if last_checkpoint is None and len(os.listdir(training_args.output_dir)) > 0:
            raise ValueError(
                f"Output directory ({training_args.output_dir}) already exists and is not empty. "
                "Use --overwrite_output_dir to overcome."
            )
        elif last_checkpoint is not None and training_args.resume_from_checkpoint is None:
            logger.info(
                f"Checkpoint detected, resuming training at {last_checkpoint}. To avoid this behavior, change "
                "the `--output_dir` or add `--overwrite_output_dir` to train from scratch."
            )

    # Set seed before initializing model.
    set_seed(training_args.seed)

    # Get the datasets: you can either provide your own CSV/JSON training and evaluation files, or specify a dataset name
    # to load from huggingface/datasets. In ether case, you can specify a the key of the column(s) containing the text and
    # the key of the column containing the label. If multiple columns are specified for the text, they will be joined together
    # for the actual text value.
    # In distributed training, the load_dataset function guarantee that only one local process can concurrently
    # download the dataset.
    if data_args.dataset_name is not None:
        # Downloading and loading a dataset from the hub.
        raw_datasets = load_dataset(
            data_args.dataset_name,
            data_args.dataset_config_name,
            cache_dir=model_args.cache_dir,
            token=model_args.token,
            trust_remote_code=model_args.trust_remote_code,
        )
        # Try print some info about the dataset
        logger.info(f"Dataset loaded: {raw_datasets}")
        logger.info(raw_datasets)
    else:
        # Loading a dataset from your local files.
        # CSV/JSON training and evaluation files are needed.
        data_files = {"train": str(data_args.train_file), "validation": str(data_args.validation_file)}

        # Get the test dataset: you can provide your own CSV/JSON test file
        if training_args.do_predict:
            if data_args.test_file is not None:
                train_extension = data_args.train_file.suffix[1:]
                test_extension = data_args.test_file.suffix[1:]
                assert (
                    test_extension == train_extension
                ), "`test_file` should have the same extension (csv or json) as `train_file`."
                data_files["test"] = str(data_args.test_file)
            else:
                raise ValueError("Need either a dataset name or a test file for `do_predict`.")

        for key in data_files.keys():
            logger.info(f"load a local file for {key}: {data_files[key]}")

        if data_args.train_file.suffix == ".csv":
            # Loading a dataset from local csv files
            raw_datasets = load_dataset(
                "csv",
                data_files=data_files,
                cache_dir=model_args.cache_dir,
                token=model_args.token,
            )
        else:
            # Loading a dataset from local json files
            raw_datasets = load_dataset(
                "json",
                data_files=data_files,
                cache_dir=model_args.cache_dir,
                token=model_args.token,
            )

    # See more about loading any type of standard or custom dataset at
    # https://huggingface.co/docs/datasets/loading_datasets.

    if data_args.remove_splits is not None:
        for split in data_args.remove_splits.split(","):
            logger.info(f"removing split {split}")
            raw_datasets.pop(split)

    if data_args.train_split_name is not None:
        logger.info(f"using {data_args.train_split_name} as train set")
        raw_datasets["train"] = raw_datasets[data_args.train_split_name]
        raw_datasets.pop(data_args.train_split_name)

    if data_args.validation_split_name is not None:
        logger.info(f"using {data_args.validation_split_name} as validation set")
        raw_datasets["validation"] = raw_datasets[data_args.validation_split_name]
        raw_datasets.pop(data_args.validation_split_name)

    if data_args.test_split_name is not None:
        logger.info(f"using {data_args.test_split_name} as test set")
        raw_datasets["test"] = raw_datasets[data_args.test_split_name]
        raw_datasets.pop(data_args.test_split_name)

    if data_args.remove_columns is not None:
        for split in raw_datasets.keys():
            for column in data_args.remove_columns.split(","):
                logger.info(f"removing column {column} from split {split}")
                raw_datasets[split] = raw_datasets[split].remove_columns(column)

    if data_args.label_column_names is not None:
        logger.info(f"using {data_args.label_column_names} as label columns")
        for i, label_column_name in enumerate(data_args.label_column_names.split(",")):
            logger.info(f"using {label_column_name} as label{i+1} column")
            for key in raw_datasets.keys():
                new_label_column_name = f"label{i+1}"
                if label_column_name != new_label_column_name:
                    raw_datasets[key] = raw_datasets[key].rename_column(label_column_name, new_label_column_name)

    # Trying to have good defaults here, don't hesitate to tweak to your needs.
    if data_args.problem_type is None:
        # Infer problem_type from the high-level structure of the dataset
        if "label1" in raw_datasets["train"].features:
            # Multi-label classification or regression
            if (raw_datasets["train"].features["label1"].dtype in ["float32", "float64"]):
                data_args.problem_type = "multi_label_regression"
            else:
                data_args.problem_type = "multi_label_multi_class_classification"
        else:
            raise ValueError(
                "You are running a fine-tuning task but didn't provide label columns named 'label1'/'label2' in your CSV/JSON dataset."
            )
        logger.info(f"Setting problem type to {data_args.problem_type}.")

    # Verify dataset structure
    if data_args.problem_type in ["multi_label_regression", "multi_label_multi_class_classification"]:
        if "label1" not in raw_datasets["train"].features or "label2" not in raw_datasets["train"].features:
            raise ValueError(
                "You are running a multi-label task but didn't provide label columns named 'label1'/'label2'/etc. in your CSV/JSON dataset."
            )

    # Infer the number of labels and label mapping from the dataset
    label_names = [lbl for lbl in raw_datasets["train"].features if lbl.startswith("label")]
    label_names.sort()  # Let's sort it for determinism
    if data_args.problem_type == "multi_label_regression":
        num_labels = len(label_names)
    elif data_args.problem_type == "multi_label_multi_class_classification":
        # Trying to find the number of labels in a multi-label classification task
        # We have to deal with the scenario that labels appear in the validation/test set but not in the training set.
        # So we build the label list from the union of labels in train/val/test.
        label_lists = [raw_datasets["train"].unique(lbl) for lbl in label_names]
        for split in ["validation", "test"]:
            if split in raw_datasets:
                val_or_test_label_lists = [raw_datasets[split].unique(lbl) for lbl in label_names]
                for label_list, val_or_test_label_list in zip(label_lists, val_or_test_label_lists):
                    diff = set(val_or_test_label_list).difference(set(label_list))
                    if len(diff) > 0:
                        # labels appear in val/test but not in train, throw a warning
                        logger.warning(
                            f"Labels {diff} in {split} set but not in training set, adding them to the label list"
                        )
                        label_list.extend(list(diff))

        num_classes_per_label = [len(lbl_list) for lbl_list in label_lists]
        num_labels = sum(num_classes_per_label)
        for label_list in label_lists:
            label_list.sort()  # Let's sort it for determinism
    else:
        raise ValueError(f"Unrecognized problem type {data_args.problem_type}")

    # Load pretrained model and tokenizer
    # In distributed training, the .from_pretrained methods guarantee that only one local process can concurrently
    # download model & vocab.
    config = AutoConfig.from_pretrained(
        model_args.config_name if model_args.config_name else model_args.model_name_or_path,
        num_labels=num_labels,
        finetuning_task="text-classification",
        cache_dir=model_args.cache_dir,
        revision=model_args.model_revision,
        token=model_args.token,
        trust_remote_code=model_args.trust_remote_code,
    )
    tokenizer = AutoTokenizer.from_pretrained(
        model_args.tokenizer_name if model_args.tokenizer_name else model_args.model_name_or_path,
        cache_dir=model_args.cache_dir,
        use_fast=model_args.use_fast_tokenizer,
        revision=model_args.model_revision,
        token=model_args.token,
        trust_remote_code=model_args.trust_remote_code,
        truncation_side=data_args.truncation_side,
    )
    if data_args.problem_type == "multi_label_multi_class_classification":
        model_config = AutoModelForMultiHeadSequenceClassification.config_class(
            pretrained_model_name_or_path=model_args.model_name_or_path,
            num_classes_per_label=num_classes_per_label,
            from_tf=bool(".ckpt" in model_args.model_name_or_path),
            config=config,
            cache_dir=model_args.cache_dir,
            revision=model_args.model_revision,
            token=model_args.token,
            trust_remote_code=model_args.trust_remote_code,
        )
        model = AutoModelForMultiHeadSequenceClassification(model_config)
    elif data_args.problem_type == "multi_label_regression":
        model_config = AutoModelForMultiHeadSequenceRegression.config_class(
            pretrained_model_name_or_path=model_args.model_name_or_path,
            num_classes_per_label=num_labels,
            from_tf=bool(".ckpt" in model_args.model_name_or_path),
            config=config,
            cache_dir=model_args.cache_dir,
            revision=model_args.model_revision,
            token=model_args.token,
            trust_remote_code=model_args.trust_remote_code,
        )
        model = AutoModelForMultiHeadSequenceRegression(model_config)
    else:
        raise ValueError(f"Unrecognized problem type {data_args.problem_type}")

    # Padding strategy
    if data_args.pad_to_max_length:
        padding = "max_length"
    else:
        # We will pad later, dynamically at batch creation, to the max sequence length in each batch
        padding = False

    label_to_ids = None
    if data_args.problem_type == "multi_label_multi_class_classification":
        label_to_ids = [
            {v: i for i, v in enumerate(label_list)}
            for label_list in label_lists
        ]

    if label_to_ids is not None:
        model.config.label2ids = label_to_ids
        model.config.id2labels = [{id: label for label, id in label2id.items()} for label2id in label_to_ids]

    if data_args.max_seq_length > tokenizer.model_max_length:
        logger.warning(
            f"The max_seq_length passed ({data_args.max_seq_length}) is larger than the maximum length for the "
            f"model ({tokenizer.model_max_length}). Using max_seq_length={tokenizer.model_max_length}."
        )
    max_seq_length = min(data_args.max_seq_length, tokenizer.model_max_length)

    def preprocess_function(examples):
        if data_args.text_column_names is not None:
            text_column_names = data_args.text_column_names.split(",")
            # join together text columns into "sentence" column
            examples["sentence"] = examples[text_column_names[0]]
            for column in text_column_names[1:]:
                for i in range(len(examples[column])):
                    examples["sentence"][i] += data_args.text_column_delimiter + examples[column][i]
        # Tokenize the texts
        result = tokenizer(examples["sentence"], padding=padding, max_length=max_seq_length, truncation=True)
        if label_to_ids is not None:
            result["label"] = np.stack(
                [
                    [(label_to_id[l] if l != -1 else -1) for l in examples[label_name]]
                    for (label_to_id, label_name) in zip(label_to_ids, label_names)
                ], axis=1
            )
        else:
            result["label"] = np.stack(
                [
                    [(l if l is not None else np.nan) for l in examples[label_name]]
                    for label_name in label_names
                ], axis=1
            )
        return result

    # Running the preprocessing pipeline on all the datasets
    with training_args.main_process_first(desc="dataset map pre-processing"):
        raw_datasets = raw_datasets.map(
            preprocess_function,
            batched=True,
            num_proc=data_args.preprocessing_num_workers,
            load_from_cache_file=not data_args.overwrite_cache,
            desc="Running tokenizer on dataset",
        )

    if training_args.do_train:
        if "train" not in raw_datasets:
            raise ValueError("--do_train requires a train dataset.")
        train_dataset = raw_datasets["train"]
        if data_args.shuffle_train_dataset:
            logger.info("Shuffling the training dataset")
            train_dataset = train_dataset.shuffle(seed=data_args.shuffle_seed)
        if data_args.max_train_samples is not None:
            max_train_samples = min(len(train_dataset), data_args.max_train_samples)
            train_dataset = train_dataset.select(range(max_train_samples))

    if training_args.do_eval:
        if "validation" not in raw_datasets and "validation_matched" not in raw_datasets:
            if "test" not in raw_datasets and "test_matched" not in raw_datasets:
                raise ValueError("--do_eval requires a validation or test dataset if validation is not defined.")
            else:
                logger.warning("Validation dataset not found. Falling back to test dataset for validation.")
                eval_dataset = raw_datasets["test"]
        else:
            eval_dataset = raw_datasets["validation"]

        if data_args.max_eval_samples is not None:
            max_eval_samples = min(len(eval_dataset), data_args.max_eval_samples)
            eval_dataset = eval_dataset.select(range(max_eval_samples))

    if training_args.do_predict or data_args.test_file is not None:
        if "test" not in raw_datasets:
            raise ValueError("--do_predict requires a test dataset")
        predict_dataset = raw_datasets["test"]
        # remove label column if it exists
        if data_args.max_predict_samples is not None:
            max_predict_samples = min(len(predict_dataset), data_args.max_predict_samples)
            predict_dataset = predict_dataset.select(range(max_predict_samples))

    # Log a few random samples from the training set:
    if training_args.do_train:
        for index in random.sample(range(len(train_dataset)), 3):
            logger.info(f"Sample {index} of the training set: {train_dataset[index]}.")

    if data_args.metric_name is not None:
        metric = evaluate.load(
            data_args.metric_name,
            config_name="multilabel",
            cache_dir=model_args.cache_dir,
        )
        logger.info(f"Using metric {data_args.metric_name} for evaluation.")
    else:
        if data_args.problem_type == "multi_label_regression":
            metric = evaluate.load(
                "mse",
                config_name="multilabel",
                cache_dir=model_args.cache_dir,
            )
            logger.info(
                "Using mean squared error (mse) as regression score, you can use --metric_name to overwrite."
            )
        elif data_args.problem_type == "multi_label_multi_class_classification":
            metric = evaluate.load("accuracy", cache_dir=model_args.cache_dir)
            logger.info("Using accuracy for multi-label multi-class classification task, you can use --metric_name to overwrite.")
        else:
            raise ValueError(f"Unrecognized problem type {data_args.problem_type}")

    # You can define your custom compute_metrics function. It takes an `EvalPrediction` object (a namedtuple with a
    # predictions and label_ids field) and has to return a dictionary string to float.
    def compute_metrics(p: EvalPrediction):
        if data_args.problem_type == "multi_label_multi_class_classification":
            preds = p.predictions[0] if isinstance(p.predictions, tuple) else p.predictions
            preds = [np.argmax(logits, axis=-1) for logits in preds]
            preds = np.stack(preds, axis=1)
            preds = np.ravel(preds).astype(np.int32)
            labels = np.ravel(p.label_ids).astype(np.int32)
        elif data_args.problem_type == "multi_label_regression":
            preds = p.predictions[0] if isinstance(p.predictions, tuple) else p.predictions
            labels = p.label_ids
            mask = ~np.isnan(labels)
            preds = preds[mask]
            labels = labels[mask]
        result = metric.compute(predictions=preds, references=labels)
        if len(result) > 1:
            result["combined_score"] = np.mean(list(result.values())).item()
        return result

    # Data collator will default to DataCollatorWithPadding when the tokenizer is passed to Trainer, so we change it if
    # we already did the padding.
    if data_args.pad_to_max_length:
        data_collator = default_data_collator
    elif training_args.fp16:
        data_collator = DataCollatorWithPadding(tokenizer, pad_to_multiple_of=8)
    else:
        data_collator = None

    # Initialize our Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset if training_args.do_train else None,
        eval_dataset=eval_dataset if training_args.do_eval else None,
        compute_metrics=compute_metrics,
        processing_class=tokenizer,
        data_collator=data_collator,
    )

    # Training
    if training_args.do_train:
        checkpoint = None
        if training_args.resume_from_checkpoint is not None:
            checkpoint = training_args.resume_from_checkpoint
        elif last_checkpoint is not None:
            checkpoint = last_checkpoint
        train_result = trainer.train(resume_from_checkpoint=checkpoint)
        metrics = train_result.metrics
        max_train_samples = (
            data_args.max_train_samples if data_args.max_train_samples is not None else len(train_dataset)
        )
        metrics["train_samples"] = min(max_train_samples, len(train_dataset))
        trainer.save_model()  # Saves the tokenizer too for easy upload
        trainer.log_metrics("train", metrics)
        trainer.save_metrics("train", metrics)
        trainer.save_state()

    # Evaluation
    if training_args.do_eval:
        logger.info("*** Evaluate ***")
        metrics = trainer.evaluate(eval_dataset=eval_dataset)
        max_eval_samples = data_args.max_eval_samples if data_args.max_eval_samples is not None else len(eval_dataset)
        metrics["eval_samples"] = min(max_eval_samples, len(eval_dataset))
        trainer.log_metrics("eval", metrics)
        trainer.save_metrics("eval", metrics)

    if training_args.do_predict:
        logger.info("*** Predict ***")
        # Removing the `label` columns if exists because it might contains -1 and Trainer won't like that.
        if "label" in predict_dataset.features:
            predict_dataset = predict_dataset.remove_columns("label")
        predictions = trainer.predict(predict_dataset, metric_key_prefix="predict").predictions
        if data_args.problem_type == "multi_label_regression":
            if predictions.shape != (len(predict_dataset), num_labels):
                raise ValueError(
                    f"For regression, the predictions shape ({predictions.shape}) should be the number of samples x number of labels ({len(predict_dataset)}, {num_labels})."
                )
        elif data_args.problem_type == "multi_label_multi_class_classification":
            predictions = [np.argmax(logits, axis=-1) for logits in predictions]
            predictions = np.stack(predictions, axis=1)
            if predictions.shape != (len(predict_dataset), len(num_classes_per_label)):
                raise ValueError(
                    f"For multi-label multi-class classification, the predictions shape ({predictions.shape}) should be the number of samples x number of labels ({len(predict_dataset)}, {len(num_classes_per_label)})."
                )

        output_predict_file = os.path.join(training_args.output_dir, "predict_results.txt")
        if trainer.is_world_process_zero():
            with open(output_predict_file, "w") as writer:
                logger.info("***** Predict results *****")
                prediction_names = [lbl.replace("label", "prediction") for lbl in label_names]
                writer.write("index\t" + "\t".join(prediction_names) + "\n")
                for index, item in enumerate(predictions):
                    if data_args.problem_type == "multi_label_regression":
                        writer.write(f"{index}\t" + "\t".join([f"{i}" for i in item]) + "\n")
                    elif data_args.problem_type == "multi_label_multi_class_classification":
                        # recover from multi-hot encoding
                        model.config.id2labels
                        item = [
                            id2label[p]
                            for p, id2label in zip(item, model.config.id2labels)
                        ]
                        writer.write(f"{index}\t" + "\t".join(item) + "\n")
                    else:
                        raise ValueError(f"Unrecognized problem type {data_args.problem_type}")
        logger.info("Predict results saved at {}".format(output_predict_file))
    kwargs = {"finetuned_from": model_args.model_name_or_path, "tasks": "text-classification"}

    if training_args.push_to_hub:
        trainer.push_to_hub(**kwargs)
    else:
        trainer.create_model_card(**kwargs)

def main():
    model_args, data_args, training_args = get_cli_arguments()
    run_multi_label_classification(model_args, data_args, training_args)

def _mp_fn(index):
    # For xla_spawn (TPUs)
    main()


if __name__ == "__main__":
    main()
