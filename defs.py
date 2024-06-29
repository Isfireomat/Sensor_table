import numpy as np
import queue

def generate_frames(start_point, end_point, transition_time, fps):
    num_frames = int(transition_time * fps)
    
    t = np.linspace(0, 1, num_frames)
    t = 1 - (1 - t)**2  
    
    frames = queue.Queue()
    
    for i in range(num_frames):
        current_frame = np.array([
            start_point[0] + t[i] * (end_point[0] - start_point[0]),
            start_point[1] + t[i] * (end_point[1] - start_point[1]),
            start_point[2] + t[i] * (end_point[2] - start_point[2])
        ])
        frames.put(current_frame)
    
    return frames

if __name__ == "__main__":
    pass