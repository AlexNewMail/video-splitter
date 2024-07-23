from __future__ import print_function

import math
import os
import shlex
import subprocess
import shutil

RATIO = 0.85


def get_video_length(filename):
    output = subprocess.check_output(("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                                      "default=noprint_wrappers=1:nokey=1", filename)).strip()
    video_length = int(float(output))
    print("Video length in seconds: " + str(video_length))

    return video_length


def ceildiv(a, b):
    return int(math.ceil(a / float(b)))


def split_by_seconds(filename, split_length, dir_name, vcodec="copy", acodec="copy",
                     extra="", video_length=None, **kwargs):
    if split_length and split_length <= 0:
        print("Split length can't be 0")
        return

    if not video_length:
        video_length = get_video_length(filename)

    split_count = ceildiv(video_length, split_length)
    if split_count == 1:
        shutil.copyfile(filename, dir_name + "/" + filename)
        print("Video length is less then the target split length.")
        return

    split_cmd = ["ffmpeg", "-i", filename, "-vcodec", vcodec, "-acodec", acodec] + shlex.split(extra)
    try:
        filebase = ".".join(filename.split(".")[:-1])
        fileext = filename.split(".")[-1]
    except IndexError as e:
        raise IndexError("No . in filename. Error: " + str(e))
    for n in range(0, split_count):
        split_args = []
        if n == 0:
            split_start = 0
        else:
            split_start = split_length * n

        split_args += ["-ss", str(split_start), "-t", str(split_length),
                       dir_name + "/" + filebase + "-" + str(n + 1) + "-of-" +
                       str(split_count) + "." + fileext]

        print("About to run: " + " ".join(split_cmd + split_args))
        subprocess.check_output(split_cmd + split_args)


def main():
    videos = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith(('.mp4', '.avi', '.mov', '.wmv'))]
    for video in videos:

        dir_name = "splits-" + video.replace(' ', '-')
        if os.path.isdir(dir_name):
            continue

        os.mkdir(dir_name)

        video_length = get_video_length(video)
        file_size = os.stat(video).st_size
        split_filesize = int(1024 * 1024 * 20 * RATIO)

        split_length = int(split_filesize / float(file_size) * video_length)
        split_by_seconds(video, split_length, dir_name, video_length=video_length)


if __name__ == '__main__':
    main()
