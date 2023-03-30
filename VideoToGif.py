import tkinter as tk
from tkinter import filedialog, ttk
from moviepy.editor import *
from moviepy.video.io.ffmpeg_writer import FFMPEG_VideoWriter
import os
import threading
import queue

progress_queue = queue.Queue()


def start_conversion_thread():
    conversion_thread = threading.Thread(target=convert_to_gif)
    conversion_thread.start()


def browse_video_file():
    video_path = filedialog.askopenfilename(title="Select a video file")
    entry_video_path.delete(0, tk.END)
    entry_video_path.insert(0, video_path)


def browse_output_directory():
    output_dir = filedialog.askdirectory(title="Select output directory")
    entry_output_dir.delete(0, tk.END)
    entry_output_dir.insert(0, output_dir)


def update_progressbar():
    try:
        progress = progress_queue.get_nowait()
    except queue.Empty:
        pass
    else:
        progressbar['value'] = progress
        progress_var.set(f"{progress:.2f}%")

    root.after(100, update_progressbar)


def convert_to_gif():
    video_path = entry_video_path.get()
    output_dir = entry_output_dir.get()

    output_name = entry_output_name.get() or os.path.splitext(os.path.basename(video_path))[0]
    if not output_name.lower().endswith('.gif'):
        output_name += '.gif'
    output_path = os.path.join(output_dir, output_name)
    frame_rate = int(entry_frame_rate.get())
    resolution = int(entry_resolution.get()) if entry_resolution.get() else None

    clip = VideoFileClip(video_path)
    clip_duration = clip.duration
    current_frame = 0

    if resolution is not None:
        clip = clip.resize(height=resolution)

    with FFMPEG_VideoWriter(
            output_path,
            clip.size,
            fps=frame_rate,
            codec='gif',
            preset="slow",
            ffmpeg_params=['-vf', 'format=rgb24,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse=dither=sierra2_4a']) as writer:

        for frame in clip.iter_frames(fps=frame_rate, logger='bar'):
            writer.write_frame(frame)
            current_frame += 1
            progress = (current_frame / (clip_duration * frame_rate)) * 100
            progress_queue.put(progress)

    clip.close()


root = tk.Tk()
root.title("Video to GIF Converter")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

entry_video_path = tk.Entry(frame, width=50)
entry_video_path.grid(row=0, column=0, padx=5, pady=5)

button_browse_video = tk.Button(frame, text="Browse Video", command=browse_video_file)
button_browse_video.grid(row=0, column=1, padx=5, pady=5)

entry_output_dir = tk.Entry(frame, width=50)
entry_output_dir.grid(row=1, column=0, padx=5, pady=5)

button_browse_output = tk.Button(frame, text="Browse Output Directory", command=browse_output_directory)
button_browse_output.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame, text="Output Name (optional):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

entry_output_name = tk.Entry(frame, width=50)
entry_output_name.grid(row=3, column=0, padx=5, pady=5)

tk.Label(frame, text="Frame rate:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)

entry_frame_rate_var = tk.IntVar(value=12)
entry_frame_rate = tk.Entry(frame, width=10, textvariable=entry_frame_rate_var)
entry_frame_rate.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)

tk.Label(frame, text="Resolution height (optional):").grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)

entry_resolution = tk.Entry(frame, width=10)
entry_resolution.grid(row=7, column=0, padx=5, pady=5, sticky=tk.W)

entry_resolution_var = tk.StringVar()
entry_resolution = tk.Entry(frame, width=10, textvariable=entry_resolution_var)
entry_resolution.grid(row=7, column=0, padx=5, pady=5, sticky=tk.W)

button_convert = tk.Button(frame, text="Convert to GIF", command=start_conversion_thread)
button_convert.grid(row=9, column=0, padx=5, pady=5, sticky=tk.W)

progressbar = ttk.Progressbar(frame, orient=tk.HORIZONTAL, length=300, mode='determinate')
progressbar.grid(row=10, column=0, padx=5, pady=5, sticky=tk.W)

progress_var = tk.StringVar()
progress_label = tk.Label(frame, textvariable=progress_var)
progress_label.grid(row=10, column=1, padx=5, pady=5, sticky=tk.W)

root.after(100, update_progressbar)
root.mainloop()
