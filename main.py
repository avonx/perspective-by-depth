import numpy as np
from PIL import Image, ImageDraw
import os

# 床の深度マップを生成する関数
def create_floor_depth_map(size, camera_height, camera_angle, vanish_point=None,
                           uniform_noise_intensity=70, radial_noise_intensity=100,
                           visualize_horizon=False, visualize_vanish_point=False,
                           visualize_lines=False, lines_count=16):
    # 深度マップの初期化
    depth_map = np.zeros((size[1], size[0]), dtype=np.float32)
    # カメラ角度をラジアンに変換
    camera_angle_radians = np.radians(camera_angle)
    
    # 消失点が指定されていない場合は中心を消失点とする
    if vanish_point is None:
        vanish_point = (size[0] // 2, size[1] // 2)

    # 水平線のY座標を計算
    horizon_y = vanish_point[1] - np.tan(camera_angle_radians / 2) * camera_height
    # 深度の最大値
    max_depth = 255

    # 各ピクセルの深度を計算
    for y in range(size[1]):
        pixel_height = y - horizon_y
        if pixel_height < 0:
            depth = 0
        else:
            depth = np.clip((pixel_height / (size[1] - horizon_y)) * max_depth, 0, max_depth)
        depth_map[y, :] = depth

    # ノイズの追加
    uniform_noise = np.random.normal(0, uniform_noise_intensity, (size[1], size[0]))
    x, y = np.indices((size[1], size[0]))
    radial_mask = np.sqrt((y - vanish_point[0])**2 + (x - vanish_point[1])**2) / np.sqrt(size[0]**2 + size[1]**2)
    radial_noise = radial_mask * radial_noise_intensity
    depth_map += uniform_noise + radial_noise
    # 深度値のクリッピング
    depth_map = np.clip(depth_map, 0, 255)

    # 深度マップをRGBに変換して画像化
    depth_map_rgb = np.stack([depth_map]*3, axis=-1)
    image = Image.fromarray(depth_map_rgb.astype(np.uint8))
    draw = ImageDraw.Draw(image)

    # 水平線、消失点、放射状の線を可視化するオプション
    if visualize_horizon:
        draw.line([(0, horizon_y), (size[0], horizon_y)], fill=(0, 0, 255), width=2)
    if visualize_lines:
        for i in range(lines_count):
            angle = np.radians(i * (360 / lines_count))
            end_x = vanish_point[0] + np.cos(angle) * size[0]
            end_y = vanish_point[1] + np.sin(angle) * size[1]
            draw.line([vanish_point, (end_x, end_y)], fill=(0, 255, 0), width=2)
    if visualize_vanish_point:
        radius = 5  # 消失点の半径
        upper_left = (vanish_point[0] - radius, vanish_point[1] - radius)
        bottom_right = (vanish_point[0] + radius, vanish_point[1] + radius)
        draw.ellipse([upper_left, bottom_right], fill=(255, 0, 0))

    return image

# 画像サイズやカメラのパラメータ
size = (512, 512)
camera_height = 10
camera_angle = 90
steps = 10  # 消失点の移動ステップ数
uniform_noise_intensity = 50
radial_noise_intensity = 150

# 生成した深度マップを保存するためのリスト
images = []
output_folder = "output"
# 出力フォルダが存在しない場合は作成
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

visualize = False

# 異なる消失点で深度マップを生成し、画像として保存
for i in range(steps + 1):
    vanish_point_x = i * size[0] // steps
    vanish_point = (vanish_point_x, size[1] // 2)
    image = create_floor_depth_map(size, camera_height, camera_angle, vanish_point,
                                   uniform_noise_intensity, radial_noise_intensity,
                                   visualize_horizon=visualize, visualize_vanish_point=visualize,
                                   visualize_lines=visualize)
    images.append(image)
    image.save(os.path.join(output_folder, f"depth_map_{i}_{str(visualize)}.png")) 