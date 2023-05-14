# Data analyzer script

The folder contains all code used for doing low level data computations.
The scripts do to the following:
- Extract reaction time and anticipatory eye movement data from raw eye-tracking data files.
- Computes various data quality measures of the eye-tracking.
- Computes aggregated data from the reaction time and the anticipatory eye movements data for the
  latter hypothesis testing.

# How to run

The main script is the `analyzer.py` file. All other python codes are called from this main script.
As such the analyzer script is not a stand alone code. It works only in the context of the whole
ASRT experiment folder.

To run this python script you can run it from command line:
```
python <analyzer_path> <raw_data_path>
```

Where `<analyzer_path>` is the absolute path of the main analyzer script and `<raw_data_path>` is the absolute
path of the raw eye-tracking data recorded during the ASRT experiment.

Example usage:
```
python C:\Child_ASRT_eye_tracking\data_analysis\analyzer.py C:\raw_data_child
```

After you run it, the script will read the given folder and iterate through the logs of all the
participants and generate different types of data under the `/data` subfolder.

# Prerequisites (before you run)

This analyzer script depends on the other python scripts in the ASRT experiment folder, so to run
it you'll need to download the whole git repository.

Dependencies:
- asrt.py: Analyzer uses some of the code in the experiment script to handle data.
- settings file: The settings directory should contain the settings file of the experiment, since
  these settings affects how the analyzer interprets the log files.
- All other analyzer scripts: The main analyzer script is just an orchestrator which controls the
  data analysis and calls the other analyzer scripts to do the different steps of the data analysis.

# Input structure

The analyzer script has one command line argument, which is the folder of the logs recorded
with the ASRT experiment script. This folder should contain separate files for all participants
with a name like `subject_2__log.txt` where `2` is the identifier of the participant.

So the raw data folder should have the following structure:
```
raw_data_child (folder)
--> subject_2__log.txt
--> subject_3__log.txt
--> subject_4__log.txt
--> subject_5__log.txt
--> subject_6__log.txt
```

The internal structure of the data files are managed by the experiment script, so that should be
compatible with the analyzer script.

# Steps of data analysis

## 1. Computing reaction times and anticipatory data from raw eye-tracking data.
<b>Input</b>: Raw eye-tracking data files in the raw data folder passed as a command line argument.

These data files contain the eye-tracking samples. Every line means one sample of recorded eye
position and all the properties of the current trial, where that data was recorded (e.g. trial type,
stimulus, trial number, etc).

For more detailed description of the raw data fields check the related code book:
[code_book_raw_data.txt](code_book_raw_data.txt)

<b>Output</b>: Trial level data files under `data\trial_data` folder.

The output of this step contains one row for all trials. All the trial related properties are
copied from the raw data to this aggregated data. Furthermore two additional fields are
calculated during this step:
- `RT (ms)`: The time elapsed between the stimulus was first displayed and the participant
    fixated on the stimulus.
- `last_AOI_before_stimulus`: The identifier of the last AOI, where the participant looked
    before the stimulus appeared on the screen.

Note: This step will drop all data line, where the `block` field has a `0` value, because these
blocks are calibration validation blocks which are not used for the final data analyses.

## 2. Extend trial level data with some additional fields.
<b>Input</b>: Trial level data folder: `data\trial_data`.

During this step we will work with the aggregated data which now contains one row for all trials.

<b>Output</b>: Extended trial level data files under `data\trial_data_extended` folder.

There are five additional fields computed by this step:
- `repetition`: The current trial has the same stimulus as the previous trial.
- `trill`: The trial before the previous trial has the same stimulus as the current trial (e.g. 1-3-1, 2-3-2).
- `high_low_learning`: The current trial is part of a low probability or a high probability
                       triplet (based on the learning sequence).
- `has_anticipation`: The last recorded AOI before the stimulus was displayed, differs from the
                      stimulus of the previous trial.
- `has_learnt_anticipation`: The anticipation follows the structure of the learning sequence.

For more detailed description of the computed fields check the related code book:
[code_book_computed_data](code_book_computed_data.txt)

## 3. Compute statistical learning related reaction time data.

<b>Input</b>: Extended trial level data folder: `data\trial_data_extended`.

<b>Output</b>: Aggregated reaction time data files under `data\statistical_learning` folder.

The aggregation is done based on the triplet type (high vs low) and the epoch (1..8), since these
properties can be used later for the actual data analysis. The reaction time difference between the
high and low probability triplets might indicate statistical learning.

The aggregation means a median calculation here. We also exclude some of the trials before computing
the median of the related reaction times:
- `repetition`: Because of the eye-tracking experiment, the participant might still look at the same
    spot, where the the stimulus was displayed in the previous trial. So during a repetition the
    reaction time might be irrealistcly fast without the participant actually had an intentional eye-movement.
- `trill`: It's a common method in an ASRT experiments to exclude trills, because the participants might
    have a preexisting tendency to react differently to these elements.
- `preparatory trial`: There are some (2/5) preparatory trials at the beginning of all blocks which
    are not meant to be part of the data analyses.

For more detailed description of the computed fields check the related code book:
[code_book_computed_data](code_book_computed_data.txt)

## 4. Compute learning data of the interference epoch alone (HL, LH, LL)

<b>Input</b>: Extended trial level data folder: `data\trial_data_extended`.

<b>Output</b>: Aggregated reaction time data files under `data\interference` folder.

In this case, we again compute median data of the different reaction times. However here we calculate
the effect of both sequences (learning vs interference) during the interference epoch (epoch 7).
We've got the reaction times for low and high probability trials both based on the learning and
the interference sequence: LL, HL, LH.

The trial exclusion is the same as in the statistical learning computation (e.g. repetition, trill,
preparatory trial).

For more detailed description of the computed fields check the related code book:
[code_book_computed_data](code_book_computed_data.txt)

## 5. Compute anticipatory eye-movements ratio.

<b>Input</b>: Extended trial level data folder: `data\trial_data_extended`.

<b>Output</b>: Aggregated anticipatory eye-movement data files under `data\anticipatory_movements` folder.

During this computation step we compute the number of trials where there were anticipatory
eye-movements (see `has_anticipation` field) and where these eye movements followed the structure
of the learning sequence (see `has_learnt_anticipation` field). The ratio of these two values
indicates how many learning dependant anticipatory eye-movements we could record, relative to
all anticipatory eye-movements. Any increase in this value might indicate statistical learning.

The trial exclusion is the same as in the statistical learning computation (e.g. repetition,
trill, preparatory trial).

For more detailed description of the computed fields check the related code book:
[code_book_computed_data](code_book_computed_data.txt)

## 6-9. Compute eye-tracking quality data.

There are four other computations which works on the raw eye-tracking data and shows the data
quality of the eye-tracking in the different epochs.

<b>Input</b>: Raw eye-tracking data files in the raw data folder passed as a command line argument.

<b>Output</b>: Aggregated data quality measure for all participants and for all epochs.

Following data quality measures are computed.
- `missing_data_ratio`: The percentage of missing data inside the given epoch.

    Output folder: `data\missing_data`

- `median_distance_cm`: Median distance of the participant's eye from the screen.

    Output folder: `data\distance_data`

- `RMS(S2S)_median`: Root-mean-square of the sample-to-sample distances, which is an indicator of
                     the eye-tracking precision.

    Output folder: `data\RMS_S2S`

- `RMS(E2E)_median`: Root-mean-square of the eye-to-eye distances.

    Output folder: `data\RMS_E2E`

For more detailed description of the computed fields check the related code book:
[code_book_computed_data](code_book_computed_data.txt)
