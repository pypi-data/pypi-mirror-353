# HTML画像化 [html2img]
# 【動作確認 / 使用例】

import sys
import ezpip
html2img = ezpip.load_develop("html2img", "../", develop_flag = True)

html = '<span style="color:gray;">Hello,</span><br>World!'
html2img(html, "result.png", viewport = (100, 100))

# 高画質化
html2img(
	html,	# 描画対象のhtml
	output_path = "result2.png",	# 出力パス
	viewport = (100, 100),	# 描画キャンバスの大きさ (yをNone指定するとコンテンツの長さに応じる)
	scale = 4.0,	# 何倍の画質で描画するか
)

# コンテンツの長さに応じる
html2img(
	html,	# 描画対象のhtml
	output_path = "result3.png",	# 出力パス
	viewport = (100, None),	# 描画キャンバスの大きさ (yをNone指定するとコンテンツの長さに応じる)
	scale = 4.0,	# 何倍の画質で描画するか
)
