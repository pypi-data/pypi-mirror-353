# 🔍 Yandex Reverse Image Search Tool

- [🔍 Yandex Reverse Image Search Tool](#-yandex-reverse-image-search-tool)
  - [✨ Features](#-features)
  - [📦 Installation](#-installation)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [🚀 Usage](#-usage)
    - [💻 Command Line Interface](#-command-line-interface)
    - [📝 Input Types](#-input-types)
    - [🐍 Python API](#-python-api)
  - [⚙️ Configuration](#️-configuration)
  - [⚖️ Disclaimer](#️-disclaimer)
  - [📄 License](#-license)
  - [🤝 Contributing](#-contributing)

A professional reverse image search and crawling tool that uses Yandex's image search engine to find and download similar images.

## ✨ Features

- Advanced reverse image search with Yandex's AI engine
- Support for local images, URLs, and directories
- Multi-process parallel processing
- Automatic resume for interrupted operations

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Google Chrome
- ChromeDriver (matching your Chrome version)

### Installation

1. Install Python dependencies: ``pip install yandex-ris``
2. Install Google Chrome and ChromeDriver

``` bash
>>> which chromedriver
/usr/local/bin/chromedriver
>>> which google-chrome
/usr/bin/google-chrome
>>> google-chrome --version
Google Chrome 137.0.7151.68 
>>> chromedriver --version
ChromeDriver 137.0.7151.68 (2989ffee9373ea8b8623bd98b3cb350a8e95cadc-refs/branch-heads/7151@{#1873})
```

## 🚀 Usage

### 💻 Command Line Interface

```bash
# Basic usage with a single image
yandex-ris -i image.jpg -o output_dir

# Process all images in a directory
yandex-ris -i images_folder -o output_dir

# Process images from a URL
yandex-ris -i https://example.com/image.jpg -o output_dir

# Process images from a list file
yandex-ris -i image_list.txt -o output_dir

# With custom options
yandex-ris -i input_path -o output_dir -m 200 -w 4 -t 8
```

### 📝 Input Types
The tool supports multiple input types:
1. Single image file (e.g., `image.jpg`)
2. Directory containing images (will recursively scan for images)
3. Image URL (e.g., `https://example.com/image.jpg`)
4. Text file containing a list of paths/URLs (one per line)

### 🐍 Python API

```python
from yandex_ris import YandexImageCrawler

crawler = YandexImageCrawler(
    output_dir="downloaded_images",
    max_images=100,
    workers=4,
    download_threads=4
)

# Process a single image
crawler.process_images(["path/to/image.jpg"])

# Process multiple images
crawler.process_images([
    "path/to/image1.jpg",
    "path/to/image2.jpg",
    "https://example.com/image.jpg"
])
```

## ⚙️ Configuration

- `--input`, `-i`: Input path (file, directory or URL) (required)
- `--output`, `-o`: Output root directory (default: downloaded_images)
- `--max-images`, `-m`: Maximum images to download per source (default: 100)
- `--pause-time`, `-p`: Page load wait time in seconds (default: 7)
- `--workers`, `-w`: Number of parallel processing workers (default: 2)
- `--download-threads`, `-t`: Download threads per process (default: 4)
- `--log-level`: Logging level (default: INFO)

## ⚖️ Disclaimer

This tool is provided solely for research and educational purposes. By using this tool, you agree to abide by the following terms and conditions:

1. **Permitted Use**: This tool is intended strictly for non-commercial, research, and educational use.
2. **Prohibited Use**: Any use of this tool for unlawful, malicious, or unauthorized purposes is strictly prohibited.
3. **User Responsibility**: Users are fully responsible for ensuring that their use of this tool complies with all applicable local, national, and international laws and regulations.
4. **Liability Disclaimer**: The developers, contributors, and maintainers of this tool shall not be held liable for any direct, indirect, incidental, or consequential damages arising from the use or misuse of this tool.
5. **No Warranty**: This tool is provided "as is", without any warranties, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, or non-infringement.
6. **Consequences of Misuse**: Any misuse of this tool, particularly for malicious or illegal activities, may result in the violation of laws and could lead to civil or criminal penalties.

By using this tool, you acknowledge that you have read, understood, and agreed to be bound by these terms.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.