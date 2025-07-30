# 並列リクエスト [reqreq]
# 【動作確認 / 使用例】

import sys
from sout import sout
import ezpip
reqreq = ezpip.load_develop("reqreq", "../", develop_flag = True)

# 並列リクエスト [reqreq]
resp = reqreq([
	{"url": "https://example.com", "method": "GET"},
	{"url": "https://example.com", "method": "POST", "data": {"test": "test"}},
], error = "raw")
sout(resp)

# 省略表記
resp = reqreq([
	"https://example.com",	# getの場合は省略できる
	("https://example.com", "post", {"test": "test2"}),	# methodは小文字指定もOK
	["https://example.com", "POST", {"test": "test3"}],	# リストでもタプルでも指定できる
])
sout(resp)

# その他引数
resp = reqreq(
	["https://example.com"],
	resp_format = "raw",	# 返値のフォーマット (text: default, raw: requestsの返値のまま)
	error = None,	# 例外発生時に何を返すかを指定 ("raw" 指定の時だけは例外オブジェクトをそのまま返す; defaultはNone)
)
sout(resp)
