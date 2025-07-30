# 並列リクエスト [reqreq]

import sys
import json
import mulmap
import requests
from sout import sout

# リクエスト単体を正規化
def normalize_one(obj, err):
	# 文字列・タプル指定の場合の型を揃える
	if type(obj) == type(""):
		obj = [obj]
	elif type(obj) == type(()):
		obj = list(obj)
	elif type(obj) not in [type([]), type({})]:
		raise err
	# リストの場合の処理
	if type(obj) == type([]):
		if len(obj) > 3: raise err	# リストが長すぎる場合
		obj = {k: e for k, e
			in zip(["url", "method", "data"], obj)}	# zipはシーケンスの短い方にそろう
	# 辞書の処理
	obj = {k: obj[k] for k in obj}	# 汚染防止でシャローコピー
	obj["method"] = obj.get("method", "GET")	# GETの省略を解除
	obj["method"] = obj["method"].upper()	# methodを大文字にする
	if obj["method"] not in ["GET", "POST"]: raise err	# methodの正当性確認
	if "url" not in obj: raise err	# urlキーの存在の確認
	if type(obj["url"]) != type(""): raise err
	return obj

# クエリの正規化
def normalize_query(req_ls):
	err = Exception("[reqreq error] invalid request format")
	# 外側がリストであることを確認
	if type(req_ls) != type([]): raise err
	# 内側を正規化
	return [normalize_one(e, err) for e in req_ls]	# リクエスト単体を正規化

# 1回のリクエストを送る
def one_req(req_dic, resp_format, error):
	if req_dic["method"] == "GET":
		request_func = requests.get
	elif req_dic["method"] == "POST":
		request_func = requests.post
	else:
		raise Exception("[reqreq error] invalid method")
	# リクエストを投げる
	try:
		kwargs = ({"json": req_dic["data"]} if "data" in req_dic else {})
		resp = request_func(req_dic["url"], **kwargs)
	except Exception as err_obj:
		if error == "raw": return err_obj
		return error
	# レスポンスの処理
	if resp_format == "raw": return resp
	if resp_format == "text": return resp.text
	raise Exception("[reqreq error] invalid resp_format")

# 並列リクエスト [reqreq]
def reqreq(
	req_ls,	# 複数個のリクエストのリスト
	resp_format = "text",	# 返値のフォーマット ("text": default, "raw": requestsの返値のまま)
	error = None,	# 例外発生時に何を返すかを指定 ("raw" 指定の時だけは例外オブジェクトをそのまま返す; defaultはNone)
):
	# クエリの正規化
	req_ls = normalize_query(req_ls)
	# 並列で呼ぶ
	def f(req_dic): return one_req(req_dic, resp_format, error)	# 1回のリクエストを送る
	resp_ls = mulmap(f, req_ls)
	return resp_ls

# moduleオブジェクトと関数を同一視
sys.modules[__name__] = reqreq
