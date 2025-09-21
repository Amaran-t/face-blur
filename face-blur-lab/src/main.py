import cv2
import numpy as np
from PIL import Image

# ---------- Настройки ----------
INPUT_IMAGE = "images/actor.jpg"         # Положи сюда фото актёра/актрисы
SUNGLASSES_PNG = "images/sunglasses.png" # PNG с альфой (готовый файл уже лежит в папке images/)
OUTPUT_NO_GLASSES = "images/result_blur_no_glasses.jpg"
OUTPUT_WITH_GLASSES = "images/result_blur_with_glasses.jpg"

# Параметры овала относительно прямоугольника лица
ELLIPSE_SCALE_X = 1.05  # ширина овала относительно ширины лица
ELLIPSE_SCALE_Y = 1.20  # высота овала относительно высоты лица
ELLIPSE_SHIFT_Y = 0.05  # смещение центра овала вниз (доля высоты лица)

# Параметры кружков глаз
EYE_RADIUS_FACTOR = 0.25  # радиус круга глаза как доля средней ширины глаза (по каскаду)

# Размытие
BLUR_KSIZE = (55, 55)  # ядро Гаусса
BLUR_SIGMA = 0         # авто

# ---------- Хелперы ----------
def load_cascade(name):
    path = cv2.data.haarcascades + name
    cascade = cv2.CascadeClassifier(path)
    if cascade.empty():
        raise RuntimeError(f"Не найден каскад {name} по пути {path}")
    return cascade

face_cascade = load_cascade("haarcascade_frontalface_default.xml")
eye_cascade  = load_cascade("haarcascade_eye.xml")

def overlay_transparent(bg_bgr, overlay_rgba, x, y, overlay_w=None, overlay_h=None):
    """Наложение PNG с альфой на BGR-картинку at (x,y)."""
    img = Image.fromarray(cv2.cvtColor(bg_bgr, cv2.COLOR_BGR2RGB)).convert("RGBA")
    ov = Image.fromarray(overlay_rgba, "RGBA")
    if overlay_w is not None and overlay_h is not None:
        ov = ov.resize((overlay_w, overlay_h), resample=Image.Resampling.LANCZOS)
    img.paste(ov, (x, y), ov)
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2BGR)

def blur_face_except_eyes(img_bgr, face_rect, eyes_in_face):
    """Размывает лицо внутри овала, НО сохраняет зоны глаз нерезкими (резкими)."""
    (fx, fy, fw, fh) = face_rect
    h, w = img_bgr.shape[:2]

    # Маска овала лица
    mask = np.zeros((h, w), dtype=np.uint8)
    center = (int(fx + fw/2), int(fy + fh*(0.5 + ELLIPSE_SHIFT_Y)))
    axes   = (int(fw*ELLIPSE_SCALE_X/2), int(fh*ELLIPSE_SCALE_Y/2))
    cv2.ellipse(mask, center, axes, 0, 0, 360, 255, -1)

    # Маска глаз (зоны исключения из размытия)
    eyes_mask = np.zeros((h, w), dtype=np.uint8)
    for (ex, ey, ew, eh) in eyes_in_face:
        cx = fx + ex + ew//2
        cy = fy + ey + eh//2
        r  = int(max(ew, eh) * EYE_RADIUS_FACTOR)
        cv2.circle(eyes_mask, (cx, cy), r, 255, -1)

    blur_mask = cv2.bitwise_and(mask, cv2.bitwise_not(eyes_mask))
    blurred = cv2.GaussianBlur(img_bgr, BLUR_KSIZE, BLUR_SIGMA)
    blur_mask_3 = cv2.merge([blur_mask, blur_mask, blur_mask])
    out = np.where(blur_mask_3==255, blurred, img_bgr)
    return out

def draw_debug_shapes(img_bgr, face_rect, eyes_in_face):
    (fx, fy, fw, fh) = face_rect
    center = (int(fx + fw/2), int(fy + fh*(0.5 + ELLIPSE_SHIFT_Y)))
    axes   = (int(fw*ELLIPSE_SCALE_X/2), int(fh*ELLIPSE_SCALE_Y/2))
    cv2.ellipse(img_bgr, center, axes, 0, 0, 360, (0, 255, 255), 2)  # овал
    for (ex, ey, ew, eh) in eyes_in_face:
        cx = fx + ex + ew//2
        cy = fy + ey + eh//2
        r  = int(max(ew, eh) * EYE_RADIUS_FACTOR)
        cv2.circle(img_bgr, (cx, cy), r, (0, 128, 255), 2)           # глаза

def place_sunglasses(img_bgr, face_rect, eyes_in_face, sunglasses_path):
    """Накладывает очки, масштабируя по расстоянию между глазами (min 2 глаза)."""
    if len(eyes_in_face) < 2:
        return img_bgr

    (fx, fy, fw, fh) = face_rect
    eyes_sorted = sorted(eyes_in_face, key=lambda e: e[0])
    left_eye  = eyes_sorted[0]
    right_eye = eyes_sorted[-1]

    lx = fx + left_eye[0] + left_eye[2]//2
    ly = fy + left_eye[1] + left_eye[3]//2
    rx = fx + right_eye[0] + right_eye[2]//2
    ry = fy + right_eye[1] + right_eye[3]//2

    eye_dist = np.hypot(rx - lx, ry - ly)
    glasses_w = int(eye_dist * 2.2)

    sg = cv2.imread(sunglasses_path, cv2.IMREAD_UNCHANGED)
    if sg is None:
        print("Не удалось загрузить sunglasses.png")
        return img_bgr
    gh, gw = sg.shape[:2]
    if sg.shape[2] == 3:
        sg = cv2.cvtColor(sg, cv2.COLOR_BGR2BGRA)
    aspect = gh / gw
    glasses_h = int(glasses_w * aspect)

    cx = int((lx + rx) / 2)
    cy = int((ly + ry) / 2) - int(0.15 * glasses_h)
    x = cx - glasses_w // 2
    y = cy - glasses_h // 2

    out = overlay_transparent(img_bgr, sg, x, y, overlay_w=glasses_w, overlay_h=glasses_h)
    return out

def main():
    img = cv2.imread(INPUT_IMAGE)
    if img is None:
        raise FileNotFoundError(f"Не найдено изображение {INPUT_IMAGE}. Положи фото актёра в папку images/ под именем actor.jpg")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 1) Лицо
    face_cascade = load_cascade("haarcascade_frontalface_default.xml")
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(120, 120))
    if len(faces) == 0:
        raise RuntimeError("Лицо не найдено. Возьми фронтальное фото без сильных наклонов/очков, большее разрешение.")

    faces_sorted = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
    (fx, fy, fw, fh) = faces_sorted[0]

    # 2) Глаза в ROI
    eye_cascade  = load_cascade("haarcascade_eye.xml")
    face_roi_gray = gray[fy:fy+fh, fx:fx+fw]
    eyes = eye_cascade.detectMultiScale(face_roi_gray, scaleFactor=1.1, minNeighbors=5, minSize=(25, 25))

    eyes_filtered = []
    for (ex, ey, ew, eh) in eyes:
        if ey + eh/2 < fh * 0.65:  # верхние 2/3 лица
            eyes_filtered.append((ex, ey, ew, eh))

    # Визуальный дебаг
    debug_img = img.copy()
    draw_debug_shapes(debug_img, (fx, fy, fw, fh), eyes_filtered)
    cv2.imwrite("images/debug_shapes.jpg", debug_img)

    # 3) Размытие лица без глаз
    out_no_glasses = blur_face_except_eyes(img.copy(), (fx, fy, fw, fh), eyes_filtered)
    cv2.imwrite(OUTPUT_NO_GLASSES, out_no_glasses)

    # 4) Очки поверх результата
    out_with_glasses = place_sunglasses(out_no_glasses.copy(), (fx, fy, fw, fh), eyes_filtered, SUNGLASSES_PNG)
    cv2.imwrite(OUTPUT_WITH_GLASSES, out_with_glasses)

    print("Готово! Смотри файлы в папке images/:")
    print(" - debug_shapes.jpg (овал+кружки)")
    print(f" - {OUTPUT_NO_GLASSES}")
    print(f" - {OUTPUT_WITH_GLASSES}")

if __name__ == "__main__":
    main()
