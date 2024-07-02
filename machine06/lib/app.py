from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Run your Python code here
        result = run_python_code(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'result': result})

def calc_heart_rate(video_path):
    import cv2
    import numpy as np
    import scipy.fftpack as fftpack
    from scipy import signal

    faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml")

    # Read in and simultaneously preprocess video
    def read_video(path):
        cap = cv2.VideoCapture(path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        video_frames = []
        face_rects = ()

        while cap.isOpened():
            ret, img = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            roi_frame = img

            # Detect face

            face_rects = faceCascade.detectMultiScale(gray, 1.3, 5)

            # Select ROI
            # if len(face_rects) > 0:
            for (x, y, w, h) in face_rects:
                roi_frame = img[int((h / 30) + y):int((h / 5) + y), int((w / 3) + x):int((w / 1.4) + x)]
            if roi_frame.size != img.size:
                roi_frame = cv2.resize(roi_frame, (500, 500))
                frame = np.ndarray(shape=roi_frame.shape, dtype="float")
                frame[:] = roi_frame
                video_frames.append(frame)

        frame_ct = len(video_frames)
        cap.release()

        return video_frames, frame_ct, fps

    # Build Gaussian image pyramid
    def build_gaussian_pyramid(img, levels):
        float_img = np.ndarray(shape=img.shape, dtype="float")
        float_img[:] = img
        pyramid = [float_img]

        for i in range(levels - 1):
            float_img = cv2.pyrDown(float_img)
            pyramid.append(float_img)

        return pyramid

    # Build Laplacian image pyramid from Gaussian pyramid
    def build_laplacian_pyramid(img, levels):
        gaussian_pyramid = build_gaussian_pyramid(img, levels)
        laplacian_pyramid = []

        for i in range(levels - 1):
            upsampled = cv2.pyrUp(gaussian_pyramid[i + 1])
            (height, width, depth) = upsampled.shape
            gaussian_pyramid[i] = cv2.resize(gaussian_pyramid[i], (height, width))
            diff = cv2.subtract(gaussian_pyramid[i], upsampled)
            laplacian_pyramid.append(diff)

        laplacian_pyramid.append(gaussian_pyramid[-1])

        return laplacian_pyramid

    # Build video pyramid by building Laplacian pyramid for each frame
    def build_video_pyramid(frames):
        lap_video = []

        for i, frame in enumerate(frames):
            pyramid = build_laplacian_pyramid(frame, 3)
            for j in range(3):
                if i == 0:
                    lap_video.append(np.zeros((len(frames), pyramid[j].shape[0], pyramid[j].shape[1], 3)))
                lap_video[j][i] = pyramid[j]

        return lap_video

    # Temporal bandpass filter with Fast-Fourier Transform
    def fft_filter(video, freq_min, freq_max, fps):
        fft = fftpack.fft(video, axis=0)
        frequencies = fftpack.fftfreq(video.shape[0], d=1.0 / fps)
        bound_low = (np.abs(frequencies - freq_min)).argmin()
        bound_high = (np.abs(frequencies - freq_max)).argmin()
        fft[:bound_low] = 0
        fft[bound_high:-bound_high] = 0
        fft[-bound_low:] = 0
        iff = fftpack.ifft(fft, axis=0)
        result = np.abs(iff)
        result *= 100  # Amplification factor

        return result, fft, frequencies

    # Calculate heart rate from FFT peaks
    def find_heart_rate(fft, freqs, freq_min, freq_max):
        fft_maximums = []

        for i in range(fft.shape[0]):
            if freq_min <= freqs[i] <= freq_max:
                fftMap = abs(fft[i])
                fft_maximums.append(fftMap.max())
            else:
                fft_maximums.append(0)

        peaks, properties = signal.find_peaks(fft_maximums)
        max_peak = -1
        max_freq = 0

        # Find frequency with max amplitude in peaks
        for peak in peaks:
            if fft_maximums[peak] > max_freq:
                max_freq = fft_maximums[peak]
                max_peak = peak

        return freqs[max_peak] * 60

    # Frequency range for Fast-Fourier Transform
    freq_min = 1
    freq_max = 1.8

    # Preprocessing phase
    video_frames, frame_ct, fps = read_video(video_path)

    # Build Laplacian video pyramid
    lap_video = build_video_pyramid(video_frames)
    heart_rate = 0
    for i, video in enumerate(lap_video):

        if i == 0 or i == len(lap_video) - 1:
            continue

        # Eulerian magnification with temporal FFT filtering

        _, fft, frequencies = fft_filter(video, freq_min, freq_max, fps)

        # Calculate heart rate

        heart_rate = find_heart_rate(fft, frequencies, freq_min, freq_max)

    return heart_rate

def run_python_code(file_path):
    return calc_heart_rate(file_path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

