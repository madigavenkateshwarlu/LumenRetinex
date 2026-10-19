LumenRetinex — Low-Light Image Enhancement

A Digital Image Processing (DIP) project using Retinex theory to enhance images captured in low-light conditions.

LumenRetinex is a web-based image enhancement application designed to improve the visibility of dark images while preserving important image details and natural-looking colours. It uses image processing techniques such as logarithmic transformation, Single-Scale Retinex (SSR), Multi-Scale Retinex (MSR), and illumination-reflectance decomposition.

Table of Contents

- "Project Overview" (#project-overview)
- "Problem Statement" (#problem-statement)
- "Objectives" (#objectives)
- "Features" (#features)
- "Digital Image Processing Concepts" (#digital-image-processing-concepts)
- "Algorithms Implemented" (#algorithms-implemented)
- "Technologies Used" (#technologies-used)
- "Project Architecture" (#project-architecture)
- "Project Structure" (#project-structure)
- "Installation" (#installation)
- "How to Run" (#how-to-run)
- "How to Use" (#how-to-use)
- "Application Screenshots" (#application-screenshots)
- "Testing and Evaluation" (#testing-and-evaluation)
- "Limitations" (#limitations)
- "Future Enhancements" (#future-enhancements)
- "Conclusion" (#conclusion)
- "References" (#references)
- "Author" (#author)

Project Overview

Images captured in poor lighting conditions may appear dark, unclear, and low in contrast. Important objects, textures, and colour information can become difficult to identify.

LumenRetinex addresses this problem using Digital Image Processing techniques. The application accepts an input image, applies a selected enhancement method, and produces an enhanced output image.

The project focuses on improving image visibility while attempting to preserve useful details and natural colour information.

Problem Statement

To develop a web-based image enhancement system that improves the visibility and contrast of low-light images using Retinex-based image processing techniques and logarithmic transformation.

Objectives

- Enhance images captured in low-light environments.
- Improve brightness and contrast.
- Implement Single-Scale Retinex and Multi-Scale Retinex methods.
- Study illumination and reflectance decomposition.
- Preserve useful image details and colour information.
- Provide a simple web interface for uploading and processing images.
- Compare original images with their enhanced results.
- Evaluate enhancement using image statistics and visual inspection.

Features

- Image Upload: Select an image from your device.
- Low-Light Enhancement: Improve visibility in dark images.
- Logarithmic Transformation: Expand details in darker intensity ranges.
- Single-Scale Retinex (SSR): Estimate illumination using a Gaussian surround at one scale.
- Multi-Scale Retinex (MSR): Combine Retinex results from multiple scales.
- Illumination-Reflectance Decomposition: Represent an image in terms of illumination and reflectance.
- Colour Preservation: Use luminance-based processing where implemented to help retain natural colours.
- Enhanced Image Output: Display or save the processed image.
- Image Statistics: Inspect available brightness, contrast, or related measurements.
- Web-Based Interface: Use the application through a browser.

The availability of individual features depends on the implementation in the current version of the application.

Digital Image Processing Concepts

1. Retinex Theory

Retinex theory, associated with Edwin H. Land and John J. McCann, explains how visual perception can estimate surface reflectance despite changes in illumination.

A simplified image formation model is:

[
I(x,y)=R(x,y),L(x,y)
]

Where:

- (I(x,y)) is the observed image.
- (R(x,y)) is the reflectance component.
- (L(x,y)) is the illumination component.
- (x,y) represent pixel coordinates.

The observed image contains information about both the illumination falling on a scene and the reflectance of its surfaces.

Taking logarithms gives:

[
\log I(x,y)=\log R(x,y)+\log L(x,y)
]

Retinex methods estimate and compensate for illumination variations to reveal details in dark regions.

2. Logarithmic Transformation

Logarithmic transformation can expand lower intensity values while compressing higher values.

A common transformation is:

[
s=c\log(1+r)
]

Where:

- (r) is the input pixel intensity.
- (s) is the output intensity.
- (c) is a scaling constant.

For an 8-bit image, the result is normally normalized or clipped to the valid intensity range.

3. Single-Scale Retinex (SSR)

Single-Scale Retinex uses a Gaussian-filtered version of the image to estimate local illumination.

[
SSR(x,y)=\log(I(x,y)+\epsilon)
-\log((G_\sigma*I)(x,y)+\epsilon)
]

Where:

- (I(x,y)) is the input intensity.
- (G_\sigma) is a Gaussian surround function.
- (*) denotes convolution.
- (\sigma) controls the scale of the Gaussian filter.
- (\epsilon) is a small positive value used to avoid taking the logarithm of zero.

SSR can improve local contrast, but its output depends strongly on the selected scale and may require normalization.

4. Multi-Scale Retinex (MSR)

Multi-Scale Retinex combines results obtained using different Gaussian scales.

[
MSR(x,y)=\sum_{k=1}^{K}w_k
\left[
\log(I(x,y)+\epsilon)
-\log((G_{\sigma_k}*I)(x,y)+\epsilon)
\right]
]

Where:

- (K) is the number of scales.
- (\sigma_k) is the Gaussian scale for the (k)-th result.
- (w_k) is its weight, commonly selected so that the weights sum to one.

Multiple scales help balance local detail enhancement with broader illumination correction. However, aggressive enhancement may introduce noise, colour shifts, or unnatural contrast.

5. Image Evaluation

The project can compare the original and enhanced images using available measurements.

Mean intensity

[
\mu=\frac{1}{MN}\sum_{x=1}^{M}\sum_{y=1}^{N}I(x,y)
]

Intensity standard deviation

[
\sigma_I=
\sqrt{\frac{1}{MN}\sum_{x=1}^{M}\sum_{y=1}^{N}
(I(x,y)-\mu)^2}
]

Where (M) and (N) are the image dimensions.

Mean intensity provides an indication of average brightness, while standard deviation describes intensity variation. Neither measurement alone proves that an enhancement is perceptually better.

Algorithms Implemented

Logarithmic Transformation

Maps darker intensity values into a wider output range to make details more visible.

Single-Scale Retinex

Uses one Gaussian scale to estimate illumination and calculate a reflectance-oriented output.

Multi-Scale Retinex

Combines Retinex outputs across multiple scales to balance local and larger-scale enhancement.

Illumination-Reflectance Decomposition

Models the observed image as the product of illumination and reflectance. The estimated components can help explain the image formation process and guide enhancement.

Refer to the corresponding source files in the "algorithms/" directory for the exact implementation and parameter values.

Technologies Used

Technology| Purpose
Python| Backend application and image processing
Flask| Web application framework
OpenCV| Image processing and filtering
NumPy| Numerical operations and array manipulation
HTML| Web page structure
CSS| Web interface styling
JavaScript| Browser-side interactions, where implemented
Git and GitHub| Version control and source code hosting

Project Architecture

The application follows a basic web-based image processing workflow:

1. The user opens the web application.
2. The user selects and uploads an image.
3. Flask receives the image and routes the request to the appropriate processing function.
4. The selected image enhancement algorithm processes the image.
5. The application returns the enhanced output and any supported statistics.
6. The browser displays the results to the user.

Project Structure

LowLightEnhancement/
│
├── algorithms/
│   ├── retinex.py
│   └── decomposition.py
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/
│   └── index.html
│
├── uploads/
│
├── screenshots/
│   ├── home.png
│   ├── original-image.png
│   ├── enhanced-result.png
│   └── image-statistics.png
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── test_opencv.py

Note: This is an illustrative structure. Keep the actual filenames and folders in your README consistent with the files present in your repository. Remove example entries that do not exist.

Installation

Prerequisites

Install the following software:

- Python 3
- pip
- Git (optional, for cloning the repository)
- A modern web browser

1. Clone the repository

git clone https://github.com/madigavenkateshwarlu/LumenRetinex.git

2. Open the project directory

cd LumenRetinex

3. Create a virtual environment

On Windows:

python -m venv venv

Activate it:

venv\Scripts\activate

4. Install dependencies

pip install -r requirements.txt

If installation fails, check that the Python version is compatible with the packages listed in "requirements.txt".

How to Run

From the project directory, execute:

python app.py

Wait for Flask to display the local development server address in the terminal. Open that address in your browser. It is commonly:

http://127.0.0.1:5000

The actual address and port depend on the configuration in "app.py".

Important: Run this development server locally. Do not expose it publicly without appropriate security and deployment configuration.

How to Use

1. Start the Flask application.
2. Open the local URL in a browser.
3. Select a low-light image from your device.
4. Choose an enhancement method if the interface provides algorithm selection.
5. Run the enhancement.
6. View the original and enhanced outputs.
7. Review the available image statistics.
8. Save or download the result if supported by the interface.
9. Try other enhancement methods and compare their results.

Application Screenshots

Add screenshots captured from your actual running application to the "screenshots/" directory.

1. Home and Image Upload

"LumenRetinex Home" (screenshots/home.png)

2. Original Low-Light Image

"Original Low-Light Image" (screenshots/original-image.png)

3. Enhanced Image Result

"Enhanced Image Result" (screenshots/enhanced-result.png)

4. Image Statistics

"Image Statistics" (screenshots/image-statistics.png)

Replace these example paths if your screenshot filenames differ. GitHub will display the images once the corresponding files are committed and pushed.

Testing and Evaluation

Test the application using different types of low-light images, such as indoor scenes, night scenes, and images containing both dark and bright regions.

Test case| Expected outcome
Upload a valid image| The image is accepted and processed
Apply logarithmic transformation| Darker intensity regions become more visible
Apply SSR| Retinex processing produces an output image
Apply MSR| Multiple scales contribute to enhancement
Process a low-light image| Visibility may improve without excessive artefacts
Upload an unsupported or invalid file| The application handles the error appropriately
Inspect output dimensions| The output dimensions are consistent with the implementation
Review image statistics| Displayed measurements match the calculated output

Results

Record the actual results after testing the application.

Measurement| Original image| Enhanced image
Mean brightness| Enter measured value| Enter measured value
Contrast / standard deviation| Enter measured value| Enter measured value
Visual detail| Describe observed result| Describe observed result
Colour appearance| Describe observed result| Describe observed result

Do not enter estimated values as measured results. Use actual outputs from your application and include representative before-and-after screenshots.

Limitations

- Enhancement quality depends on the input image and selected parameters.
- Very dark images may contain insufficient information to recover missing details.
- Amplifying dark regions may also amplify image noise.
- Retinex processing may introduce colour shifts or halos in some images.
- Brightness and contrast statistics do not fully measure perceptual quality.
- Processing time depends on image dimensions and the algorithm.
- Supported file formats and upload limits depend on the application configuration.

Future Enhancements

Possible improvements include:

- Add more enhancement algorithms for comparison.
- Provide interactive controls for Retinex scales and enhancement strength.
- Add side-by-side and adjustable before-and-after comparisons.
- Include objective evaluation metrics such as PSNR and SSIM when a suitable reference image is available.
- Add batch image processing.
- Improve error handling and upload validation.
- Provide downloadable processing reports.
- Improve the responsive design for mobile devices.
- Explore real-time video enhancement.

Conclusion

LumenRetinex demonstrates how Digital Image Processing techniques can be applied to low-light image enhancement through a web-based interface. By studying logarithmic transformation, Single-Scale Retinex, Multi-Scale Retinex, and illumination-reflectance decomposition, the project illustrates methods for improving visibility and understanding illumination variation in digital images.

The project also provides a foundation for further experiments in image enhancement, computer vision, and computational photography.

References

1. Land, E. H., & McCann, J. J. (1971). Lightness and Retinex Theory. Journal of the Optical Society of America, 61(1), 1–11. https://doi.org/10.1364/JOSA.61.000001

2. OpenCV Documentation. OpenCV: Open Source Computer Vision Library. https://docs.opencv.org/

3. NumPy Documentation. NumPy User Guide. https://numpy.org/doc/

4. Flask Documentation. Flask Web Development. https://flask.palletsprojects.com/

5. Jobson, D. J., Rahman, Z., & Woodell, G. A. (1997). A Multiscale Retinex for Bridging the Gap Between Color Images and the Human Observation of Scenes. IEEE Transactions on Image Processing, 6(7), 965–976. https://doi.org/10.1109/83.597272

Author

Project: LumenRetinex — Low-Light Image Enhancement
Domain: Digital Image Processing
Repository: https://github.com/madigavenkateshwarlu/LumenRetinex

Student Name: Add your full name
Department: Add your department
Institution: Add your college or university
Academic Year: Add your academic year

---

Developed as an academic Digital Image Processing project.