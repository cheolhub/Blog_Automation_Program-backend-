from flask import Flask, request, jsonify
from openai import OpenAI
import json
import thumbnail_generator

client = OpenAI()


app = Flask(__name__)



# GPT를 이용한 게시글 수동 생성
@app.route('/generate_post', methods=['POST'])
def generate_post():
    data = request.json
    keyword = data.get('keyword')
    tone = data.get('tone')  # 해요체, 습니다체, 반말
    image_style = data.get('image_style')  # 실사, 일러스트 등
    core_content = data.get('core_content')  # 핵심 내용
    print(f"keyword : {keyword}, tone : {tone}, image_style = {image_style}, core_content = {core_content}")

    # GPT 요청 프롬프트 생성 (유저)
    prompt = (
        f"Create a blog post about '{keyword}' in {tone} style. "
        f"Make sure to include the following key points: {core_content}. "
        f"Output the response in JSON format with a title, headers, and content sections."
    )

    # Chat GPT를 통해 구조화된 게시글 생성
    try:
        # 최신 API 호출 방식 사용
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."}, # 수정 필요
                {"role": "user", "content": prompt}
            ]
        )

        # 응답 내용 출력 및 반환
        result = response.choices[0].message.content
        print("다음은 코드 출력입니다.")
        print(result)
        print("이상입니다.")



        # JSON 응답 구조로 파싱하기
        try:
            result_data = json.loads(result)  # 문자열 result를 JSON 파싱
        except json.JSONDecodeError:
            return jsonify({"error": "Failed to decode JSON response from GPT"}), 500
        
        print("파싱 ok")



        # DALL·E API를 이용하여 제목과 헤더에 맞는 이미지 생성 , 이 try catch문 의미 없는지 확인 필요
        try:
            # 제목과 헤더 리스트를 이용해 이미지 프롬프트 생성
            image_prompts = [result_data['title']] + result_data['headers']
        except KeyError as e:
            return jsonify({"error": f"Missing key in result data: {str(e)}"}), 500
        image_urls = []


        for prompt_text in image_prompts:
            # 이미지 생성 요청
            print(f"이미지 생성 중: {prompt_text}")  # 각 프롬프트 확인
            image_response = client.images.generate(
                model="dall-e-3",
                prompt=f"A {image_style} illustration of {prompt_text}",
                size="1024x1024",
                quality="standard",
                n=1,
            )
            print(f"image_response: {image_response}") 
            image_urls.append(image_response.data[0].url) # 이미지 url 저장
            break #일단 썸네일만 받아오게 break 걸어놓음


        image_url = image_urls[0]
        image_urls[0] = thumbnail_generator.make_thumbnail(image_url, result_data['title'])







        # JSON 응답: 게시글 데이터와 이미지 URL 함께 반환
        return jsonify({
            'content': result_data,
            'images': image_urls
        })




    except Exception as e:
        print(f"Error occurred: {str(e)}")  # 오류 발생 시 메시지 출력
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)









