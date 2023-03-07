# (c) @AbirHasan2005

import os
import shlex
import asyncio
from typing import List
from subprocess import PIPE
from configs import Config


async def merge_many_videos_to_one_video_fast(
        input_videos_list_txt_file_path: str, output_video_dir: str, output_video_name: str = "output.mkv"
):
    """
    Merge many videos to one video. Videos should be in same format and codec.
    """
    if not os.path.exists(input_videos_list_txt_file_path):
        raise ValueError("Videos List TXT File Not Exists")
    if not os.path.isdir(output_video_dir):
        os.makedirs(output_video_dir)
    output_video_path = os.path.join(output_video_dir, output_video_name)
    cmd = shlex.split(
        "ffmpeg -f concat -safe 0 "
        f"-i {shlex.quote(input_videos_list_txt_file_path)} -c copy {shlex.quote(output_video_path)}"
    )
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=PIPE,
        stderr=PIPE
    )
    stdout, stderr = await process.communicate()
    return (stdout.decode('utf-8', 'replace').strip(),
            stderr.decode('utf-8', 'replace').strip(),
            process.returncode,
            process.pid)


async def merge_many_videos_to_one_video_slow(
        input_videos_list: List[str], output_video_dir: str, output_video_name: str = "output.mkv"
):
    """
    Merge many videos to one video. Videos can be in different formats and codecs.

    It will safely merge the videos to one H.264 MKV video.
    """
    if not input_videos_list:
        raise ValueError("Videos List is Empty")
    if not os.path.isdir(output_video_dir):
        os.makedirs(output_video_dir)
    output_video_path = os.path.join(output_video_dir, output_video_name)
    videos_list_args = "-i " + " -i ".join(input_videos_list)
    filter_complex_value = shlex.quote(
        "[0:v]"
        "scale=1920:1080:force_original_aspect_ratio=decrease,"
        "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,"
        "setsar=1[v0];"
        "[1:v]"
        "scale=1920:1080:force_original_aspect_ratio=decrease,"
        "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,"
        "setsar=1[v1];"
        "[2:v]"
        "scale=1920:1080:force_original_aspect_ratio=decrease,"
        "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,"
        "setsar=1[v2];"
        "[v0][0:a][v1][1:a][v2][2:a]"
        "concat=n=3:v=1:a=1[v][a]"
    )
    cmd = shlex.split(
        f"ffmpeg {videos_list_args} "
        f"-filter_complex {filter_complex_value} "
        f"-map {shlex.quote('[v]')} -map {shlex.quote('[a]')} "
        f"-c:v libx264 -preset {Config.ENCODING_SPEED_PRESET} -crf 28 -c:a copy "
        f"{shlex.quote(output_video_path)}"
    )
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=PIPE,
        stderr=PIPE
    )
    stdout, stderr = await process.communicate()
    return (stdout.decode('utf-8', 'replace').strip(),
            stderr.decode('utf-8', 'replace').strip(),
            process.returncode,
            process.pid)


async def add_watermark_to_video(
        input_watermark_img_path: str, input_video_path: str, output_video_dir: str,
        output_video_name: str = "output.mkv", watermark_position: str = "bottom-right", pixel_gap: int = 15
):
    """
    Add watermark to video: top-left, top-middle, top-right, middle-left, center, middle-right, bottom-left, bottom-middle, bottom-right

    With a gap of 15 pixels between the watermark and the border of the video
    """
    if watermark_position == "top-left":
        watermark_position_arg = f"overlay={pixel_gap}:{pixel_gap}"
    elif watermark_position == "top-middle":
        watermark_position_arg = f"overlay=(W-w)/2:{pixel_gap}"
    elif watermark_position == "top-right":
        watermark_position_arg = f"overlay=W-w-{pixel_gap}:{pixel_gap}"
    elif watermark_position == "middle-left":
        watermark_position_arg = f"overlay={pixel_gap}:(H-h)/2"
    elif watermark_position == "center":
        watermark_position_arg = "overlay=(W-w)/2:(H-h)/2"
    elif watermark_position == "middle-right":
        watermark_position_arg = f"overlay=W-w-{pixel_gap}:(H-h)/2"
    elif watermark_position == "bottom-left":
        watermark_position_arg = f"overlay={pixel_gap}:H-h-{pixel_gap}"
    elif watermark_position == "bottom-middle":
        watermark_position_arg = f"overlay=(W-w)/2:H-h-{pixel_gap}"
    elif watermark_position == "bottom-right":
        watermark_position_arg = f"overlay=W-w-{pixel_gap}:H-h-{pixel_gap}"
    else:
        raise ValueError("Invalid Watermark Position")
    if not os.path.isdir(output_video_dir):
        os.makedirs(output_video_dir)
    output_video_path = os.path.join(output_video_dir, output_video_name)
    cmd = shlex.split(
        f"ffmpeg -i {shlex.quote(input_video_path)} -i {shlex.quote(input_watermark_img_path)} "
        f"-filter_complex {shlex.quote(watermark_position_arg)} "
        f"-c:v libx264 -preset {Config.ENCODING_SPEED_PRESET} -crf 28 -c:a copy "
        f"{shlex.quote(output_video_path)}"
    )
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=PIPE,
        stderr=PIPE
    )
    stdout, stderr = await process.communicate()
    return (stdout.decode('utf-8', 'replace').strip(),
            stderr.decode('utf-8', 'replace').strip(),
            process.returncode,
            process.pid)


async def change_video_quality(
        input_video_path: str, output_video_dir: str, output_video_name: str = "output.mkv", video_quality: int = 720
):
    """
    Change Video Quality to 144p, 240p, 360p, 480p, 720p, 1080p, 1440p, 2160p
    """
    if f"{video_quality}p" not in Config.ALLOWED_QUALITIES:
        raise ValueError(f"Video Quality should be {' or '.join(Config.ALLOWED_QUALITIES)}")
    if not os.path.isdir(output_video_dir):
        os.makedirs(output_video_dir)
    output_video_path = os.path.join(output_video_dir, output_video_name)
    vf_arg_value = shlex.quote(
        f"scale='if(gt(a,16/9),{video_quality},-2)':'if(gt(a,16/9),-2,ih)',"
        f"scale=w=min(iw\,{video_quality}):h=min(ih\,{video_quality}):force_original_aspect_ratio=decrease"
    )
    cmd = shlex.split(
        f"ffmpeg -i {shlex.quote(input_video_path)} "
        f"-vf {vf_arg_value} "
        f"-c:v libx264 -preset {Config.ENCODING_SPEED_PRESET} -crf 28 -c:a copy "
        f"{shlex.quote(output_video_path)}"
    )
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=PIPE,
        stderr=PIPE
    )
    stdout, stderr = await process.communicate()
    return (stdout.decode('utf-8', 'replace').strip(),
            stderr.decode('utf-8', 'replace').strip(),
            process.returncode,
            process.pid)
