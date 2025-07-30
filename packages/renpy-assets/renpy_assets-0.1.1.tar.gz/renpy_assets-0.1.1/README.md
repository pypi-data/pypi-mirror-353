# renpy-assets

A command-line interface for automating asset management in Ren'Py visual novel projects.

Easily scan your project for assets (images, audio, fonts), and generate boilerplate declarations to speed up scripting in `.rpy` files.

---

## ✨ Features

### 🔍 Scan Assets

Identify all assets in your Ren'Py project based on type:

* `images` – `.png`, `.jpg`, `.jpeg`, `.webp`
* `audio` – `.mp3`, `.ogg`, `.wav`, `.opus`
* `fonts` – `.ttf`, `.otf`, `.woff`, `.woff2`

Usage:

```bash
renpy-assets scan images
renpy-assets scan audio --directory assets/audio
```

### 🪄 Generate Declarations

Automatically generate image declarations from your asset folders:

```bash
renpy-assets generate images --directory game/images
```

This creates boilerplate like:

```renpy
image bg room = "images/bg room.png"
image character happy = "images/character happy.png"
```

You can copy-paste this into `.rpy` files or direct it into a file with redirection (`> output.rpy`).

---

## 📦 Installation

```bash
pip install renpy-assets
```

(Coming soon to PyPI!)

For local development:

```bash
git clone https://github.com/jeje1197/renpy-assets
cd renpy-assets
pip install -e .
```

---

## 📁 Project Layout

```
src/
  renpy_assets/
    cli.py
    commands/
      scan.py
      generate.py
    utils/
      file_utilities.py

tests/
```

---

## 🧪 Testing

Run the tests using:

```bash
pytest
```

Make sure you're in the root directory and `src` is on the Python path.

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to get involved.