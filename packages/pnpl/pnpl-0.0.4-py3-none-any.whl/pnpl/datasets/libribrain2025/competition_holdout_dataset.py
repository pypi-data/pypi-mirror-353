import os
from torch.utils.data import Dataset
import torch

from pnpl.datasets import LibriBrainSpeech
from pnpl.datasets.libribrain2025.constants import PHONEME_CLASSES, SPEECH_OUTPUT_DIM, PHONEME_HOLDOUT_PREDICTIONS, SPEECH_HOLDOUT_PREDICTIONS
import csv
import torch
import warnings
from torch.utils.data import DataLoader
from pnpl.datasets.libribrain2025.speech_dataset_holdout import LibriBrainSpeechHoldout
from tqdm import tqdm
import pandas as pd
import numpy as np

class LibriBrainCompetitionHoldout(Dataset):
    def __init__(self, data_path,
                 tmin: float = 0.0,
                 tmax: float = 0.8,
                 standardize=True,
                 clipping_boundary=10,
                 stride=1,
                 task: str = "speech",
                 download: bool = True):
        """
        LibriBrain 2025 Competition Holdout Dataset.

        This dataset provides access to the holdout data used for the LibriBrain 2025 competition.
        It loads the specific holdout session and prepares it for generating competition submissions.

        Args:
            data_path: Path where you wish to store the dataset. The local dataset structure 
                      will follow the same BIDS-like structure as the HuggingFace repo:
                      ```
                      data_path/
                      ├── {task}/                    # e.g., "Sherlock1", "COMPETITION_HOLDOUT"  
                      │   └── derivatives/
                      │       ├── serialised/       # MEG data files
                      │       │   └── sub-{subject}_ses-{session}_task-{task}_run-{run}_proc-{preprocessing_str}_meg.h5
                      │       └── events/            # Event files  
                      │           └── sub-{subject}_ses-{session}_task-{task}_run-{run}_events.tsv
                      ```
            tmin: Start time of the sample in seconds relative to the sliding window start. 
                 Together with tmax, defines the time window size for each sample.
            tmax: End time of the sample in seconds relative to the sliding window start. 
                 The number of timepoints per sample = int((tmax - tmin) * sfreq) where sfreq=250Hz.
                 E.g., tmin=0, tmax=0.8 yields 200 timepoints per sample.
            standardize: Whether to z-score normalize each channel's MEG data using mean and std 
                        computed across the holdout data.
            clipping_boundary: If specified, clips all values to [-clipping_boundary, clipping_boundary]. 
                             This can help with outliers. Set to None for no clipping.
            stride: Controls how far (in time) you move the sliding window between consecutive samples. 
                   Instead of jumping exactly one full time_window_samples worth (tmax-tmin; the default) 
                   each time, you can specify a smaller stride to get overlapping windows. If None, 
                   defaults to time_window_samples (no overlap).
            task: Type of task for the competition. Currently only "speech" is supported for 
                 speech vs silence classification. "phoneme" classification is not yet implemented.
            download: Whether to download files from HuggingFace if not found locally (True) or 
                     throw an error if files are missing locally (False).

        Note:
            ⚠️ This dataset loads the specific holdout session ('0', '2025', 'COMPETITION_HOLDOUT', '1') 
            that is used for competition evaluation.
            
            When making predictions, ensure your final submission matches the expected number of 
            timepoints. Use the generate_submission_in_csv() method to create properly formatted 
            submission files.

        Returns:
            Data samples with shape (channels, time) where channels=306 MEG channels.
            For speech task, labels are arrays indicating speech (1) vs silence (0) for each sample.
        """
        # Path to the data
        self.data_path = data_path
        self.task = task
        self.dataset = None
        if task == "speech":
            try:
                self.dataset = LibriBrainSpeechHoldout(
                    data_path=self.data_path,
                    tmin = tmin,
                    tmax = tmax,
                    include_run_keys=[("0", "2025", "COMPETITION_HOLDOUT", "1")],
                    standardize=standardize,
                    clipping_boundary=clipping_boundary,
                    preprocessing_str="bads+headpos+sss+notch+bp+ds",
                    preload_files=False,
                    include_info=True,
                    stride=stride,
                    download=download
                )
                self.samples = self.dataset.samples
            except Exception as e:
                warnings.warn(f"Failed to load speech dataset: {e}")
                raise RuntimeError("Failed to load speech dataset. Check the data path and parameters.")
        if task == "phoneme":
            raise NotImplementedError(f"Task '{task}' is not supported yet.")


    def generate_submission_in_csv(self, predictions, output_path: str):
        """
        Generates a submission file in CSV format for the LibriBrain competition.
        The file contains the run keys and the corresponding labels.
        Args:
            predictions (List[Tensor]): List of scalar tensors, each representing a speech probability.
            output_path (str): Path to save the CSV file.
        """
        if self.task == "speech":
            if len(predictions) != SPEECH_HOLDOUT_PREDICTIONS:
                raise (ValueError(
                    f"Length of speech predictions ({len(predictions)}) does not match the expected number of segments ({SPEECH_HOLDOUT_PREDICTIONS})."))
            if predictions[0].shape[0] != SPEECH_OUTPUT_DIM:
                raise (ValueError(
                    f"Speech prediction dimension {predictions[0].shape[0]} does not match expected size (1 for scalar probability)."))
            with open(output_path, mode='w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["idx", "speech_prob"])

                for idx, tensor in enumerate(predictions):
                    # Ensure we extract the scalar float from tensor
                    speech_prob = tensor.item() if isinstance(
                        tensor, torch.Tensor) else float(tensor)
                    writer.writerow([idx, speech_prob])


    def speech_labels(self):
        return self.dataset.speech_labels if self.task == "speech" else None

    def __len__(self):
        return len(self.dataset.samples)

    def __getitem__(self, idx):
        # returns channels x time
        return self.dataset[idx]


if __name__ == "__main__":
    output_path = ""

    dataset = LibriBrainCompetitionHoldout(
        data_path = "/Users/gilad/Desktop/Projects/PNPL/LibriBrain/serialized",
        tmax=0.8,
        task="speech")

    # Create a DataLoader for the dataset
    dataloader = DataLoader(dataset, batch_size=1, shuffle=False, num_workers=0)
    segments_to_predict = len(dataset)

    random_predictions = []
    for i, sample in enumerate(tqdm(dataloader)):
        segment = sample[0]
#        prediction = model.predict(segment)  # Assuming model is defined and has a predict method
        random_predictions.append(torch.rand(1))  # Random prediction for each sample
    dataset.generate_submission_in_csv(random_predictions, "holdout_speech_predictions.csv")