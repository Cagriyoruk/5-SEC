# 5-SEC
## Product Mission

For - Anyone uses social media
Who - Doesn't want to spend a lot of time searching moments in the video
The - 5-SEC is a - Convenience
That - finds the important part of the videos
Unlike - GOOGLE
Our Product - has more functions to edit the videos.

## Define Customers
- People use social media.
- People are interested in videography.
- People who don't know how to edit videos.
- Editing Companies that wants to use our feature. 

## User Stories
- As a User, I want the highlights of my videos so that I can save time.
- As a User, I want a user-friendly interface so that I can interact easily.
- As a User, I want to edit my videos so that I don't have to use any other software.
- As a User, I want to share my videos.
- As a User, I want my videos  to be categorized so that I can find them easier. 
- As a User, I want recommendation of filters for my videos based on choice of other users. 

## Define MVP 
A Web-app that gives the highlights of a video.

## System Design
![](https://github.com/Cagriyoruk/5-SEC/blob/master/5-Sec%20System%20Design.png)

# Kaggle Competetion
The 3rd YouTube-8M Video Understanding Challenge / Temporal localization of topics within video

Imagine being able to search for the moment in any video where an adorable kitten sneezes, even though the uploader didn’t title or describe the video with such descriptive metadata. Now, apply that same concept to videos that cover important or special events like a baby’s first steps or a game-winning goal -- and now we have the ability to quickly find and share special video moments. This technology is called temporal concept localization within video and Google Research can use your help to advance the state of the art in this area.

In most web searches, video retrieval and ranking is performed by matching query terms to metadata and other video-level signals. However, we know that videos can contain an array of topics that aren’t always characterized by the uploader, and many of these miss localizations to brief but important moments within the video. Temporal localization can enable applications such as improved video search (including search within video), video summarization and highlight extraction, action moment detection, improved video content safety, and many others.

In previous years, participants worked on advancements in video-level annotations, building both unconstrained and constrained models. In this third challenge based on the YouTube 8M dataset, Kagglers will localize video-level labels to the precise time in the video where the label actually appears, and do this at an unprecedented scale. To put it another way: at what point in the video does the cat sneeze?

## Evaluation
Submissions are evaluated according to the Mean Average Precision @ K (MAP@K), where K=100,000.
![213](https://user-images.githubusercontent.com/55101879/70405266-916c2400-1a0a-11ea-8b71-b41af691ea07.png)

where C is the number of Classes, P(k) is the precision at cutoff k, n is the number of Segments predicted per Class, rel(k) is an indicator function equaling 1 if the item at rank k is a relevant (correct) Class, or zero otherwise, and Nc is the number of positively-labeled segments for the each Class.

IMPORTANT: The evaluation for this competition is different in some important ways:

As noted above, for each Class you are predicting relevant Segments (and not the other way around).

Not all test segments have been human-rated, and only human-rated segments are used in scoring. All segments that were not explicitly rated (as either containing a Class, or not containing a Class) are removed from the prediction list before scoring.

The Public/Private Test split is performed at the Segment level, not the Class level. In other words, all classes (i.e., submission rows) are evaluated for the Public and Private leaderboard, but only segments for the particular split will be used in the prediction and ground truth.

## Youtube 8M Dataset
Frame-Level Data(Train):  
Size of 1.5 TB 
Each Video Has:
Id: Unique id for the video
Labels: List of labels
Each frame has rgb feature
Each frame has audio feature

Segment-Level Data(Validate/Test):
In addition to id, labels and frame level features they come with:
Segment_start_time
Segment_end_time
Segment_labels
Segment_scores

Both files are in TFRecords format which is a simple format for storing a sequence of binary records.

## Model Selection and Our Goal
Overall, frame level models;
Frame Level Logistic regression, 
DBOF(Deep Bag of Frames),
LSTM(Long Short-Term Memory) 
performance are better than video level model MoE(Mixture of Experts).

Our goal is to achieve 0.7 accuracy on kaggle’s test data set.

## Leaderboard
![12312](https://user-images.githubusercontent.com/55101879/70405435-2ff88500-1a0b-11ea-8457-773d7c3e7293.png)


## Successfully Trained Models
Small-Frame / 0.02 accuracy : Trained on 1 tfrecord file to test the training code.

48-Frame level Model / 0.66 accuracy : 48 Hours trained Frame- Level Logistic Regression Model. Trained on all of the dataset.

48-DBOF Model / 0.71 accuracy : 48 Hours trained Deep Bag Of Frames Model. Trained on all of the dataset.

## Extracting Features
Our machine learning model is taking tfrecord files for test, train and validation. To use local videos, we needed to change the video files to tfrecord files. But these tfrecord files should include the features of the video(rgb and audio). For this problem, we used mediapipe library to extract the features. After building mediapipe sucessfully, we runned these commands and extracted the features of the videos. After that we runned the command for annotating local videos.

### Steps to run the YouTube-8M feature extraction graph

1.  Checkout the mediapipe repository.

    ```bash
    git clone https://github.com/google/mediapipe.git
    cd mediapipe
    ```

2.  Download the PCA and model data.

    ```bash
    mkdir /tmp/mediapipe
    cd /tmp/mediapipe
    curl -O http://data.yt8m.org/pca_matrix_data/inception3_mean_matrix_data.pb
    curl -O http://data.yt8m.org/pca_matrix_data/inception3_projection_matrix_data.pb
    curl -O http://data.yt8m.org/pca_matrix_data/vggish_mean_matrix_data.pb
    curl -O http://data.yt8m.org/pca_matrix_data/vggish_projection_matrix_data.pb
    curl -O http://download.tensorflow.org/models/image/imagenet/inception-2015-12-05.tgz
    tar -xvf /tmp/mediapipe/inception-2015-12-05.tgz
    ```

3.  Get the VGGish frozen graph.

    Note: To run step 3 and step 4, you must have Python 2.7 or 3.5+ installed
    with the TensorFlow 1.14+ package installed.

    ```bash
    # cd to the root directory of the MediaPipe repo
    cd -
    python -m mediapipe.examples.desktop.youtube8m.generate_vggish_frozen_graph
    ```

4.  Generate a MediaSequence metadata from the input video.

    Note: the output file is /tmp/mediapipe/metadata.pb

    ```bash
    # change clip_end_time_sec to match the length of your video.
    python -m mediapipe.examples.desktop.youtube8m.generate_input_sequence_example \
      --path_to_input_video=/absolute/path/to/the/local/video/file \
      --clip_end_time_sec=120
    ```

5.  Run the MediaPipe binary to extract the features.

    ```bash
    bazel build -c opt \
      --define MEDIAPIPE_DISABLE_GPU=1 --define no_aws_support=true \
      mediapipe/examples/desktop/youtube8m:extract_yt8m_features

    GLOG_logtostderr=1 bazel-bin/mediapipe/examples/desktop/youtube8m/extract_yt8m_features \
      --calculator_graph_config_file=mediapipe/graphs/youtube8m/feature_extraction.pbtxt \
      --input_side_packets=input_sequence_example=/tmp/mediapipe/metadata.pb  \
      --output_side_packets=output_sequence_example=/tmp/mediapipe/features.pb
    ```

### Steps to run the YouTube-8M model inference graph with a local video

1.  Make sure you have the features.pb from the feature extraction pipeline.

2.  Copy the baseline model [(model card)](https://drive.google.com/file/d/1xTCi9-Nm9dt2KIk8WR0dDFrIssWawyXy/view) to local.

    ```bash
    curl -o /tmp/mediapipe/yt8m_baseline_saved_model.tar.gz data.yt8m.org/models/baseline/saved_model.tar.gz

    tar -xvf /tmp/mediapipe/yt8m_baseline_saved_model.tar.gz -C /tmp/mediapipe
    ```

3.  Build and run the inference binary.

    ```bash
    bazel build -c opt --define='MEDIAPIPE_DISABLE_GPU=1' \
      mediapipe/examples/desktop/youtube8m:model_inference

    # segment_size is the number of seconds window of frames.
    # overlap is the number of seconds adjacent segments share.
    GLOG_logtostderr=1 bazel-bin/mediapipe/examples/desktop/youtube8m/model_inference \
      --calculator_graph_config_file=mediapipe/graphs/youtube8m/local_video_model_inference.pbtxt \
      --input_side_packets=input_sequence_example_path=/tmp/mediapipe/features.pb,input_video_path=/absolute/path/to/the/local/video/file,output_video_path=/tmp/mediapipe/annotated_video.mp4,segment_size=5,overlap=4
    ```
