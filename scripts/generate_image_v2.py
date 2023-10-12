import requests
import random
import io
import base64
import os
import time
import json, re

import numpy as np
from PIL import Image, PngImagePlugin

def read_json(json_name, key="random"):
  """JSONCを読みこんでランダムで抽出して返す関数

  Args:
      json_name (str): json名
      mode (str, optional): randomで辞書からランダム選択、それ以外にすれば指定可能 Defaults to "random".

  Returns:
      str: 選ばれし者
  """
  try:
    with open("../json/"+json_name+".jsonc", "r", encoding="utf-8") as f:
        text = f.read()
        re_text = re.sub(r'/\*[\s\S]*?\*/|//.*', '', text) 
        data = json.loads(re_text)
    if key == "random":
      random.seed()
      key_list = list(data.keys())
      selected_key = random.choice(key_list)
      word = data[selected_key]
    else:
      word = data[key]
    return word
  except Exception as e:
     print(e)
     print(json_name)
     exit()

def additional_word(word):
  """プロンプトをランダムに追加するための関数

  Args:
      word (_type_): _description_

  Returns:
      _type_: _description_
  """
  try:
    random.seed()
    # print("clothes")
    word = word + ", " + read_json("clothes")
    # print("emotion")
    word = word + ", " +  read_json("emotion")
    # print("quality")
    word = word + ", " +  read_json("quality")
    # print("pose")
    word = word + ", " +  read_json("pose")
    # print("hair")
    word = word + ", " +  read_json("hair")
    # haircolor
    word = word + ", " + read_json("color") +  " hair,"
    word = word + ", " + read_json("color") +  " eyes,"
    return word
  except Exception as e:
    print(e)
    exit()

# APIに送る内容を初期化
params = {
  "restore_faces": True,
  "face_restorer": "CodeFormer",
  "codeformer_weight": 0.5,
  "sd_model_checkpoint": "",
  "prompt": "",
  "negative_prompt": "",
  "seed": -1,
  "seed_enable_extras": False,
  "subseed": -1,
  "subseed_strength": 0,
  "seed_resize_from_h": 0,
  "seed_resize_from_w": 0,
  "steps": random.randint(15,40),
  "cfg_scale": random.randint(7.0, 10.0),
  "denoising_strength": 0.35,
  "batch_count": 1,
  "batch_size": 1,
  "base_size": 900,
  "max_size": 900,
  "tiling": False,
  "highres_fix": False,
  "firstphase_height": 600,
  "firstphase_width": 900,
  "upscaler_name": "None",
  "filter_nsfw": False,
  "include_grid": False,
  "sample_path": "outputs/kakapo-out",
  "sampler_index": "",
  "orig_height": 600,
  "sampler_name": ""
}

# CLIP初期化
option_payload = {
    "CLIP_stop_at_last_layers": 1
}
response = requests.post(url="http://192.168.0.3:7860/sdapi/v1/options", json=option_payload)


def main():
    
    # 出力先フォルダのパス
    out_dir = ""
    # 生成する画像数
    num_of_images = 10000
    # image_size = [[619, 450], [500, 500], [450,619]]
    # image_size = [[550, 550], [450,619]]
    # 生成する画像サイズ
    image_size = [[800, 500]]

    # 保存先フォルダがない場合作成
    if os.path.exists(out_dir) == False:
       print("create out_dir:"+str(out_dir))
       os.mkdir(out_dir)

    # 生成開始
    for i in range(0, num_of_images):
        try:
            time.sleep(np.random.rand())
            # ベースワードの選択
            word = read_json("base", "human")
            # ワード追加処理
            word = additional_word(word)
            # 使用モデル
            params["sd_model_checkpoint"] = read_json("model", "anything")
            # samplerの選択
            params["sampler_name"] = read_json("sampler", "DDIM")
            # ポジティブプロンプト
            params["prompt"] = word
            # スケール選択
            params["cfg_scale"] = float(random.randint(6, 7))
            # ステップ数選択
            params["steps"] = float(random.randint(30, 30))
            # 顔の整形をするかどうか
            params["restore_faces"] = False
            # ネガティブプロンプト
            params["negative_prompt"] = read_json("ng_prompt", "iikanzi")
            # 画像サイズ
            size = random.randint(0, len(image_size)-1)
            params["firstphase_height"] = image_size[size][1]
            params["firstphase_width"] = image_size[size][0]


            param = params
            print(str(i+1)+"/"+str(num_of_images))
            # APIに画像生成リクエストを出す。(生成失敗してもリトライするためループ)
            while True:
              try:
                # URLは自分のローカルIP
                r = requests.post(url="http://192.168.0.3:7860/sdapi/v1/txt2img", json=param).json()
                for im in r["images"]:
                    print("test1")
                    image = Image.open(io.BytesIO(base64.b64decode(im.split(",",1)[0])))
                    png_payload = {
                                      "image": "data:image/png;base64," + im
                                  }
                    # URLは自分のローカルIP
                    response2 = requests.post(url="http://192.168.0.3:7860/sdapi/v1/png-info", json=png_payload)
                    pnginfo = PngImagePlugin.PngInfo()
                    pnginfo.add_text("parameters", response2.json().get("info"))
                    image.save(out_dir+str(i)+".png", pnginfo=pnginfo)
                break
              except Exception as e:
                 print(e)
                 print("retry")
            print("prompt:"+word)
        except Exception as e:
            print("error")
            print(e)
            break
        
if __name__ == "__main__":
    main()