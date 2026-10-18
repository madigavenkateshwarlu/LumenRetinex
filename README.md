LumenRetinex 🌙

Low-Light Image Enhancement Using Digital Image Processing

LumenRetinex is a web-based Digital Image Processing (DIP) project designed to improve the visibility and appearance of images captured under poor lighting conditions. It implements classical image enhancement techniques and provides a web interface for uploading images and viewing enhancement results.

📌 Project Overview

Images captured in low-light environments often suffer from poor visibility, low contrast, and loss of detail. LumenRetinex applies image processing techniques to improve brightness, contrast, and visual clarity.

🎯 Objectives

- Enhance images captured in low-light conditions.
- Implement classical Digital Image Processing algorithms.
- Compare original images with enhanced outputs.
- Display image quality measurements before and after processing.
- Provide a simple web interface for image enhancement.

⚙️ Technologies Used

- Python — core image processing
- Flask — web application
- OpenCV — image manipulation and enhancement
- NumPy — numerical operations
- HTML and CSS — web interface
- JavaScript — frontend interactions

🧠 Algorithms

The project includes the following techniques:

1. Logarithmic Transformation — expands dark intensity levels to improve visibility.
2. Single-Scale Retinex (SSR) — estimates illumination using a Gaussian-blurred image and enhances reflectance.
3. Multi-Scale Retinex (MSR) — combines Retinex results at multiple scales.
4. Illumination–Reflectance Decomposition — separates an image into illumination and reflectance components for analysis and enhancement.

The available algorithms can be selected and evaluated according to their implementation in the application.

✨ Features

- Upload an image through a web interface.
- Process low-light images using supported algorithms.
- View original and enhanced images side by side.
- Inspect intermediate outputs where available, such as illumination and reflectance.
- Review image brightness, contrast, and processing-time measurements where implemented.
- Download or save enhanced results if supported by the current interface.

📁 Project Structure

LumenRetinex/
├── algorithms/
│   ├── decomposition.py
│   ├── logarithmic.py
│   └── retinex.py
├── static/
│   ├── script.js
│   └── style.css
├── templates/
│   └── index.html
├── uploads/
├── app.py
├── requirements.txt
├── test_opencv.py
├── .gitignore
└── README.md

The structure above describes the main files in the project. Your local files may contain additional modules.

🚀 Installation and Setup

Prerequisites

- Python 3.10 or later, compatible with the dependencies in "requirements.txt"
- Git
- A modern web browser

1. Clone the repository

git clone https://github.com/madigavenkateshwarlu/LumenRetinex.git
cd LumenRetinex

2. Create a virtual environment

Windows:

python -m venv venv
.\venv\Scripts\Activate.ps1

3. Install dependencies

python -m pip install -r requirements.txt

4. Run the application

python app.py

Open the local address displayed in the terminal. If the application uses the default Flask port, visit:

"http://127.0.0.1:5000/"

🧪 Testing

Run the available OpenCV test script:

python test_opencv.py

For meaningful evaluation, test multiple low-light images and compare their original and enhanced versions.

📊 Evaluation

Possible evaluation measures include:

- Mean brightness: average pixel intensity.
- Contrast: variation in pixel intensity.
- Processing time: time required to enhance an image.
- Visual quality: visibility of objects, details, and image noise.

The results depend on the input image, algorithm parameters, and lighting conditions. Brightness improvement alone does not guarantee better image quality.

🔬 Applications

- Nighttime photography
- Low-light surveillance images
- Indoor photography
- Image preprocessing for computer vision
- Digital image restoration and enhancement

⚠️ Limitations

- Enhancement quality varies with the input image.
- Increasing brightness may also amplify noise.
- Retinex parameters and Gaussian scales affect the final result.
- The project is intended for image enhancement and educational evaluation, not as a guarantee of improved accuracy in every computer vision task.

🔮 Future Enhancements

- Add more enhancement algorithms for comparison.
- Include objective image quality metrics.
- Build a dataset-based evaluation module.
- Improve noise reduction and color preservation.
- Add batch image processing and export options.
- Deploy the web application online.

👨‍💻 Author

Madiga Venkateshwarlu

GitHub: "@madigavenkateshwarlu" (https://github.com/madigavenkateshwarlu)

📄 License

No license has been selected yet. Specify an appropriate open-source license before permitting others to reuse or redistribute this project.

---

Developed as a Digital Image Processing project to explore classical techniques for low-light image enhancement.