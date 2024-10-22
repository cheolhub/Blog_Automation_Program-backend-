import requests
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from io import BytesIO

# 텍스트를 자동으로 줄바꿈하여 지정된 영역에 맞춰 중앙에 배치하는 함수
def draw_text_in_box(draw, text, font, box_x1, box_y1, box_x2, box_y2):
    # 텍스트가 들어갈 최대 너비와 높이 계산 (흰 선 두께 및 추가 여백 반영)
    max_width = box_x2 - box_x1 - 20  # 20 픽셀 여백 추가
    max_height = box_y2 - box_y1 - 20

    # 텍스트를 줄바꿈하여 여러 줄로 나누기
    lines = []
    words = text.split(' ')
    line = ""

    for word in words:
        test_line = f"{line} {word}".strip()
        text_width, _ = draw.textsize(test_line, font=font)
        if text_width <= max_width:
            line = test_line
        else:
            lines.append(line)
            line = word
    lines.append(line)  # 마지막 줄 추가

    # 전체 텍스트 블록의 높이 계산
    total_text_height = sum([draw.textsize(line, font=font)[1] for line in lines])

    # 텍스트 블록이 상자의 가운데에 위치하도록 y_offset 계산
    y_offset = box_y1 + (max_height - total_text_height) // 2

    # 각 줄을 상자 내에 그리기 (가로 중앙 정렬)
    for line in lines:
        text_width, text_height = draw.textsize(line, font=font)
        x_offset = box_x1 + (max_width - text_width) // 2  # 가로 중앙 정렬
        draw.text((x_offset, y_offset), line, font=font, fill="white")
        y_offset += text_height  # 다음 줄의 y 위치 계산

# 썸네일을 생성하는 함수 정의
def make_thumbnail(image_url, title_text):
    # 이미지 다운로드 및 밝기 조절
    image_request = requests.get(image_url)
    image = Image.open(BytesIO(image_request.content)).convert("RGBA")

    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(0.2) # 밝기

    draw = ImageDraw.Draw(image, "RGBA")
    img_width, img_height = image.size

    # 흰 사각형 테두리 추가
    border_thickness = 10
    draw.rectangle(
        [(60, 80), (img_width - 60, img_height - 80)],  # 좌상단과 우하단 좌표
        outline="white",
        width=border_thickness
    )

    # 텍스트(제목) 추가: 한글 폰트 적용
    try:
        font_path = "fonts/Jua-Regular.ttf"  # 윈도우 시스템에 있는 한글 폰트 경로
        font_size = 90
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print("지정한 폰트를 찾을 수 없습니다. 기본 글꼴을 사용합니다.")
        font = ImageFont.load_default()

    # 텍스트가 줄바꿈되어 상자 안에 들어가도록 텍스트 그리기
    box_x1, box_y1 = 60 + border_thickness + 30, 80 + border_thickness + 30  # 흰 선 두께(10)와 여백(30) 반영
    box_x2, box_y2 = img_width - 60 - border_thickness - 30, img_height - 80 - border_thickness - 30
    draw_text_in_box(draw, title_text, font, box_x1, box_y1, box_x2, box_y2)

    # 최종 이미지 저장
    output_image_path = "thumbnail.png"
    image.save(output_image_path)
    thumbnail_url = f'/static/{output_image_path}'

    return thumbnail_url