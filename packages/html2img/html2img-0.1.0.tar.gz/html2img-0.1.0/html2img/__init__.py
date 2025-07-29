# HTML画像化 [html2img]

import sys
from playwright.sync_api import sync_playwright

# HTML画像化 [html2img]
def html2img(
	html,	# 描画対象のhtml
	output_path = "output.png",	# 出力パス
	viewport = (800, None),	# 描画キャンバスの大きさ (yをNone指定するとコンテンツの長さに応じる)
	scale = 1.0,	# 何倍の画質で描画するか
):
	with sync_playwright() as p:
		browser = p.chromium.launch()
		w, h = viewport
		if h is None: h = 10
		context = browser.new_context(
			viewport = {'width': w, 'height': h},
			device_scale_factor = scale	# 何倍の画質で描画するか
		)
		page = context.new_page()
		page.set_content(html)
		kwargs = ({"full_page": True} if viewport[1] is None else {})	# y方向サイズの自動調整
		page.screenshot(path = output_path, **kwargs)
		browser.close()

# モジュールと関数の同一視
sys.modules[__name__] = html2img
