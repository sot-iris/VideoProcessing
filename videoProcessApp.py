from moviepy.tools import subprocess_call
from moviepy.config import get_setting
from moviepy.editor import VideoFileClip

import streamlit as st
import cv2
import os
import imageio
import time
import pandas as pd

def ffmpeg_extract_subclip(filename, t1, t2, targetname=None):
    """ Makes a new video file playing video file ``filename`` between
    the times ``t1`` and ``t2``. """
    name, ext = os.path.splitext(filename)
    if not targetname:
        T1, T2 = [int(1000*t) for t in [t1, t2]]
        targetname = "%sSUB%d_%d.%s" % (name, T1, T2, ext)

    cmd = [get_setting("FFMPEG_BINARY"),"-y",
           "-ss", "%0.2f"%t1,
           "-i", filename,
           "-t", "%0.2f"%(t2-t1),
           "-vcodec", "copy", "-acodec", "copy", targetname]

    subprocess_call(cmd)

st.markdown("""## **VideoProcessing** | Bradbury Lab""")
st.markdown("""##### For this script to work, please ensure that the mappings csv header has 'ID' above the animal IDs and 'Code' above the coded letterings in the first row.""")
firstVideo = 0
secondVideo = 0
csv = None
directory = None

with st.form(key='Config'):
    st.write("""
        #### Configure the video processing parameters
        """)

    configColumn = st.columns(2)
    csv = configColumn[0].text_input("Specify the path to the CSV file for the animal mappings")
    directory = configColumn[1].text_input("Specify the directory where the videos are kept")
    secondsCols = st.columns(2)
    firstVideo = secondsCols[0].number_input("Seconds to remove from V1", max_value=9999, value=0)
    secondVideo = secondsCols[1].number_input("Seconds to remove from V2", max_value=9999, value=0)
    st.form_submit_button("Submit")

if directory and csv:
    st.write("""
        ##### If the following is satisfactory, click Process Videos.
        """)
    st.write(f"The directory where videos are kept: **{directory}**")
    st.write(f"The CSV file where the animals mappings are: **{csv}**")
    st.write(f"The number of seconds to remove from V1 videos: **{firstVideo}**")
    st.write(f"The number of seconds to remove from V2 videos: **{secondVideo}**")

    if st.button("Process Videos"):

        mappings = pd.read_csv(csv)
        mappings.set_index("ID", inplace=True)
        diction = mappings.to_dict()
        code = diction['Code']

        all_videos = [vid for vid in os.listdir(directory) if vid.endswith('.MP4')]
        video_one = [vid for vid in all_videos if 'v1' in vid.split("_")[-1]]
        video_two = [vid for vid in all_videos if 'v2' in vid.split("_")[-1]]

        new_directory = os.path.join(directory, 'BlindedVideos')

        try:
            os.mkdir(new_directory)
            print(f"{new_directory} created.")
        except:
            pass

        for video in video_one:
            first = time.time()
            original = video.split("_")
            x, y, z = video.split("_")[1].split("-")
            new = original.copy()
            new[1] = f'{code[int(x)]}-{code[int(y)]}-{code[int(z)]}'
            new_filename = "_".join(new)

            clip = VideoFileClip(os.path.join(directory, video))
            ffmpeg_extract_subclip(os.path.join(directory, video), seconds_from_v1, clip.duration,  targetname=os.path.join(new_directory, new_filename))

            second = time.time()
            print(f"Video took {second-first} seconds to process.")

        for video in video_two:
            first = time.time()
            original = video.split("_")
            x, y, z = video.split("_")[1].split("-")
            new = original.copy()
            new[1] = f'{code[int(x)]}-{code[int(y)]}-{code[int(z)]}'
            new_filename = "_".join(new)

            clip = VideoFileClip(os.path.join(directory, video))
            ffmpeg_extract_subclip(os.path.join(directory, video), 0, clip.duration-seconds_from_v2,  targetname=os.path.join(new_directory, new_filename))

            second = time.time()
            print(f"Video took {second-first} seconds to process.")
