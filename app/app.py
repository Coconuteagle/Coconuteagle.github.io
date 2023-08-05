from flask import Flask, render_template, request, jsonify
import openai
from nltk.tokenize import sent_tokenize
from flask_cors import CORS
import os

openai.api_key = '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'

import os

app = Flask(__name__, template_folder=os.path.join("..", "_site"))

text = '''
사립유치원

'''

from nltk.tokenize import sent_tokenize



def find_relevant_parts(text, user_question):
    keywords = user_question.lower().split()
    text_parts = text.lower().split(';')  # Here, we split by ';'
    
    first_word = keywords[0]  # Get the first word of the question
    second_word = keywords[1] if len(keywords) > 1 else ""  # Get the second word of the question

    selected_parts = []

    # For the first word
    for length in [3, 4, 5]:  # For each length (3, 4, 5)
        first_word_prefix = first_word[:length]  # Get the prefix of the first word

        # Find sentences that contain a word that exactly matches the prefix of the first word
        prefix_parts = [part for part in text_parts if any(word.startswith(first_word_prefix) for word in part.split()) and part not in selected_parts]

        # If there are sentences with the word, add them to the selected parts, up to a limit of 2
        selected_parts.extend(prefix_parts[:2])

        # Stop when we have 5 sentences
        if len(selected_parts) >= 5:
            break

    # For the second word
    second_word_parts = [part for part in text_parts if second_word in part.split() and part not in selected_parts]
    selected_parts.extend(second_word_parts[:3])  # Add up to 3 sentences with the second word

    for length in [2, 3]:  # For each length (2, 3)
        second_word_prefix = second_word[:length]  # Get the prefix of the second word

        # Find sentences that contain a word that exactly matches the prefix of the second word
        prefix_parts = [part for part in text_parts if any(word.startswith(second_word_prefix) for word in part.split()) and part not in selected_parts]

        # If there are sentences with the word, add them to the selected parts, up to a limit of 2
        selected_parts.extend(prefix_parts[:2])

        # Stop when we have 10 sentences
        if len(selected_parts) >= 10:
            break

    # Then find the rest of the sentences
    if len(selected_parts) < 10:  # Change this to the number of sentences you want
        scores = [(sum([keyword in part for keyword in keywords]), part) for part in text_parts if part not in selected_parts]
        scores.sort(reverse=True)

        for score, part in scores:
            part_sentences = 1  # each part is a sentence because we split by '. '
            if len(selected_parts) + part_sentences <= 10:  # Change this to the number of sentences you want
                selected_parts.append(part)
            if len(selected_parts) >= 10:  # Change this to the number of sentences you want
                break

    return selected_parts  # This will return a list of sentences




@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_question = data.get('question')

    # 사용자 질문에 관한 텍스트 추출
    relevant_text = find_relevant_parts(text, user_question)

    # GPT에 전달할 시스템 메시지 작성
    system_message = f"{relevant_text}\n\n 앞의 내용을 바탕으로 최대 3문장 이내로 답해줘"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_question}
        ]
    )

    return jsonify(answer=response['choices'][0]['message']['content'])
