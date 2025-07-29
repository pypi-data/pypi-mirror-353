English description follows Japanese.

## 変換イメージ（Conversion Example）
<img src="https://archive.org/download/html2img_html_example/html2img_html_example.png" height="150" style="vertical-align: middle;">
<span style="font-size: 24px; vertical-align: middle;">▶</span>
<img src="https://archive.org/download/html2img_html_example/html2img_convertion_result.png" height="150" style="vertical-align: middle;">


---

## 概要

`html2img` は、**HTMLを画像に変換する**ための軽量ツールです。指定された HTML スニペットを描画し、スクリーンショットとして保存します。内部では [Playwright](https://playwright.dev/) を使用しており、ブラウザでの忠実な描画結果を取得できます。

## 特徴

* HTMLスニペット → PNG画像へ簡単変換
* Playwright を利用して高精度レンダリング
* ビューポートサイズのカスタマイズが可能
* 依存最小、シンプルなAPI設計

## インストール方法

```bash
pip install html2img
playwright install
```

⚠️ **注意**
2行目の `playwright install` を忘れると動作しません。

## 使い方

```python
import html2img

html = '<span style="color:gray;">Hello,</span><br>World!'
html2img(html, "result.png")

# ウインドウサイズ（ビューポート）の指定も可能
html2img(html, "small.png", viewport = (100, 100))
```

## 引数

* `html`：描画対象の HTML 文字列
* `filename`：保存先の画像ファイル名（PNG推奨）
* `viewport`（任意）：タプル `(幅, 高さ)` を指定することでレンダリング領域を調整可能

## 発展的な引数
* `viewport` の y を `None` に指定すると、コンテンツの長さに応じてスクショ縦幅が自動的に調整される
* `scale` を指定する (例えば4.0) と、サブピクセルレンダリングのような形で高画質で描画される

## 注意点

* CSSやJavaScriptを含めることも可能ですが、外部リソースへの依存がある場合は動作しないことがあります。

---

## Overview

`html2img` is a lightweight utility to **convert HTML snippets into image files**. It renders the given HTML using a real browser engine and captures a screenshot. Internally, it uses [Playwright](https://playwright.dev/) for precise rendering.

## Features

* Simple HTML-to-image conversion
* High-fidelity rendering via Playwright
* Optional viewport size configuration
* Minimal API, easy to integrate

## Installation

```bash
pip install html2img
playwright install
```

⚠️ **Note**
You **must** run `playwright install` after installing the library to download the necessary browser engines.

## Usage

```python
import html2img

html = '<span style="color:gray;">Hello,</span><br>World!'
html2img(html, "result.png")

# You can also specify the window (viewport) size
html2img(html, "small.png", viewport = (100, 100))
```

## Parameters
* `html`: The HTML string to render
* `filename`: Output file path (PNG recommended)
* `viewport` (optional): Tuple `(width, height)` for controlling the viewport size

こちらが英訳です：

## Advanced Arguments
* If the `y` value of `viewport` is set to `None`, the screenshot height will automatically adjust according to the content length.
* Specifying `scale` (e.g., 4.0) enables high-resolution rendering, similar to subpixel rendering.

## Notes
* Supports inline CSS and JavaScript. External resources may not load depending on the environment.
