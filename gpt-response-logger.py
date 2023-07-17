#!/usr/bin/env python
# coding: utf-8

# In[8]:

import os
import subprocess
import json
import sys
import openai

# Read API key from file
with open('../api_key.txt', 'r', encoding='utf-8') as file:
    api_key = file.read().strip()

# Set the OpenAI API key
openai.api_key = api_key

# 확인할 커밋 개수 : 100개
max_commit = int(sys.argv[`]) 

def read_checkout_file(file):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        print(f"File Open 오류:")
        content = ''
    return content

def write_checkout_file(file_path, content):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except:
        print(f"File Write 오류")
        
def ask_to_gpt(file, content):
    # Make a question using the API
    question = "Can you check the following code and if there is any CWE or CVE related vulnerability, can you point it out the number of CWE or CVE and describe it?\n" + content
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=[
            {"role": "user", "content": question}
        ],
    )
    # generated answer
    answer = response['choices'][0]['message']['content'].strip()
    # Record the answer
    try:
        file = file.replace('.java', '.txt')
        file_path = os.path.join('commits', f'{os.path.basename(file)}')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(answer)   
    except:
        print(f"Answer Write 오류")

# print(json.dumps(json_data, indent = '\t'))

# 각 commit의 변경된 파일 목록에서 각 파일들의
# before change 또는 after change를 구한다.
# git checkout을 사용해 당시 파일 내용을 불러오고 저장 -> ChatGPT API에 질문한다.
# git checkout HEAD -- <file_path> 를 사용해 돌려놓는 것을 잊지 않는다.

# 다만 이 경우 커밋에서 변경된 파일이 여러개일 경우, 부분적으로밖에 물어보지 못한다. 이를 해결하기 위해서
# 1) 여러 파일의 커밋일 경우 동일한 세션에서 누적해서 물어본다
# 2) commitHash로 branch를 새로 파서 옮긴다. 그 안에서 수정된 부분이 call graph로 연결된 메소드들을 모은다.

cnt = 0

import os

def read_java_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith("before.java"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    content = f.read()
                    print(content)
                    try:
                        ask_to_gpt(file_path.replace("before.java", "response.txt"), content)
                    except:
                        print("Response Error")

# 현재 디렉토리에서 자바 파일 읽기
current_directory = os.getcwd()
read_java_files(current_directory)


for commit in json_data:
    if cnt > max_commit:
        break
    elif commit['changed_file_list'] != []:
        cnt += 1
        print(cnt)
    else:
        continue
        
    for file in commit['changed_file_list']:
        print(file)
        
        
        file_path = os.path.join('commits', f'{cnt}_answer_{os.path.basename(file)}')
        try:
            ask_to_gpt(file_path, before_content)
        except:
            print("Response Error")

