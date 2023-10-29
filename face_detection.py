import sys
import cv2
from pathlib import Path
import tomllib


def get_image_files():
    input_dir = Path(config["input_dir"])
    image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]
    file_list = input_dir.glob("*")

    # 画像のファイル名の配列
    image_files = [input_dir.joinpath(
        file.name) for file in file_list if file.suffix.lower() in image_extensions]
    return image_files


def face_cutter(cascade, image_file):

    # オプションからの読み込み
    output_dir = config['output_dir']
    face_scale_top = config['face_scale_top']
    face_scale_side = config['face_scale_side']
    face_scale_bottom = config['face_scale_bottom']
    min_size = (int(config['min_size']), int(config['min_size']))
    min_neighbors = config['min_neighbors']
    debug = config['debug']
    debug_dir = config['debug_dir']

    mkdir(output_dir)
    mkdir(debug_dir)

    img = cv2.imread(str(image_file.resolve()), cv2.IMREAD_COLOR)

    org_img_height, org_img_width, org_img_hchannels = img.shape

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = cascade.detectMultiScale(gray,
        scaleFactor=1.1,
        minNeighbors=min_neighbors,
        minSize=min_size)
    
    for index, item in enumerate(faces):
        [x, y, w, h] = item

        center_x = x + w / 2
        center_y = y + h / 2

        # 検出した顔の座標の拡張（左端）
        x1 = round(center_x - w / 2 * face_scale_side)
        if x1 < 0:
            x1 = 0

        # 上
        y1 = round(center_y - h / 2 * face_scale_top)
        if y1 < 0:
            y1 = 0

        # 右
        x2 = round(center_x + w / 2 * face_scale_side)
        if x2 > org_img_width:
            x2 = org_img_width

        # 下
        y2 = round(center_y + h / 2 * face_scale_bottom)
        if y2 > org_img_height:
            y2 = org_img_height

        if debug:
            # capture
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(
                img, "capture",  (x1+4, y1+32),  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # match
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img, "match(" + str(w) + "," + str(h) + ")",
                        (x+4, y + 32),  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            debug_dir = Path(debug_dir)
            debug_output_filename = str(
                debug_dir.joinpath(image_file.name).resolve())

            cv2.imwrite(debug_output_filename, img)
        else:
            cropped_img = img[y1:y2, x1:x2]

            output_dir = Path(output_dir)
            output_filename = image_file.stem + "_" + str(index) + ".png"
            debug_output_filename = str(
                output_dir.joinpath(output_filename).resolve())

            cv2.imwrite(debug_output_filename, cropped_img)


def mkdir(path):

    path = Path(path)
    if not path.exists():
        path.mkdir()


if __name__ == "__main__":

    # config
    global config
    path = Path("config.toml")
    txt = path.read_text(encoding="utf-8")
    config = tomllib.loads(txt)["face_detection"]

    cascade = cv2.CascadeClassifier('lbpcascade_animeface.xml')
    image_files = get_image_files()

    for image_file in image_files:
        face_cutter(cascade, image_file)
