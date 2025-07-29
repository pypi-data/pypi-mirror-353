import imageio
import numpy as np

def get_frames_from_mp4(videoPath, NumberOfFrames=10):

    reader = imageio.get_reader(videoPath)

    frames = []
    frameNumber = 0

    for frame in reader:
        if NumberOfFrames and frameNumber >= NumberOfFrames:
            break
        if frame.shape[2] == 4:  # If RGBA, ignore alpha channel
            frame = frame[:, :, :3]

        greyFrame = np.dot(frame[..., :3], [0.2989, 0.5870, 0.1140]).astype(np.uint8)
        frames.append(greyFrame)
        frameNumber += 1

    reader.close()
    return np.array(frames)
