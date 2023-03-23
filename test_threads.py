import numpy as np
import concurrent.futures

def find_downward_segments(signal, threshold):
    print(signal)
    segments = []
    start_idx = None
    for i in range(len(signal)):
        if start_idx is None:
            if signal[i] < threshold:
                start_idx = i
        elif signal[i] >= threshold:
            segments.append((start_idx, i-1))
            start_idx = None
    if start_idx is not None:
        segments.append((start_idx, len(signal)-1))
    return segments

def find_downward_segments_parallel(signal, threshold, num_threads=4):
    segments = []
    start_indices = []
    for i in range(num_threads):
        print(int(i * len(signal) / num_threads))
        start_indices.append(int(i * len(signal) / num_threads))
    start_indices.append(len(signal))

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(find_downward_segments, signal[start_indices[i]:start_indices[i+1]], threshold) for i in range(num_threads)]
        for future in concurrent.futures.as_completed(futures):
            segments.extend(future.result())

    return segments

# Example usage
signal = np.array([10, 9, 8, 7, 6, 5, 7, 3, 2, 1, 5, 4, 3, 2, 1, 2, 3, 4, 5])
threshold = 3
segments = find_downward_segments_parallel(signal, threshold, num_threads=10)
print(segments)
