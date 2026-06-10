import openai
import pandas as pd
import csv
import os
import xlrd
import time
import requests

ArticleResearchlist = []
ArticleTypelist = []
high_entropy_elements_list = []
abstract_processedlist = []
title_processedlist = []
ArticleResearch = []
ArticleType = []
high_entropy_elements = []
abstract_processed = []
title_processed = []
GPToutputlist = []
GPToutput = []
a = 1
counts = 0


def api_exchange():
    # Set up GPT API key
    with open('./api_key.txt', 'r') as f:
        api_key = f.read().strip()

    return api_key


# main function to extract high entropy elements from abstracts
def Catalytic_Extract(abstract, a):
    api_key = api_exchange()

    # 使用新版 OpenAI API
    client = openai.OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com/v1"  # DeepSeek API 端点
    )

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a research chemist focus on High Entropy materials and electrochemical analysis."},
                {"role": "user",
                 "content": "High entropy materials is defined as materials consisting of at least five different metals. It is also been named as High Entropy Alloys or HEAs."},
                {"role": "user",
                 "content": "The definition of Catalytic: making a chemical reaction happen more quickly by using a catalyst"},
                {"role": "user", "content": f"Abstract: {abstract}"},
                {"role": "user", "content": f"Title: {a}"},
                {"role": "user",
                 "content": "This is a Abstract from a article, analysis this abstract with title, answer the questions as follows, all section should be fill, if you are uncertain about specific item,fill NULL"},
                {"role": "user",
                 "content": "If the counts of Elements is less than five, please check your answer, read the abstract and title again and reply again"},
                {"role": "user", "content": "Your reply must be strictly standardized as the following questions:"},
                {"role": "user", "content": "Article research on Catalytic: Yes or No"},
                {"role": "user", "content": "Article research on Oxygen Reduction Reaction: Yes or No"},
                {"role": "user", "content": "Article research on High entropy materials: Yes or No"},
                {"role": "user", "content": "Article Type: Research or Review"},
                {"role": "user", "content": "Specific Elements: 1, 2, 3, etc."},
                {"role": "user",
                 "content": "To be noted, if you are unsure, please reply 'NULL', and the elements should be symbolized with English abbreviation only, for example, if the elements are Iron, Cobalt, Nickel, please reply 'Fe, Co, Ni'"},
            ],
            timeout=30.0,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"API Error: {e}")
        return "API time out"


for file_name in os.listdir('./Pub Lib'):
    file_path = './Pub Lib/' + file_name

    try:
        reader = pd.read_excel(file_path, sheet_name=0, header=0, index_col=0)

        # 获取列数据
        title_list = reader['Article Title']
        abstract_list = reader['Abstract']

        for row in range(len(abstract_list)):
            # 使用 iloc 进行位置索引，避免警告
            abstract = abstract_list.iloc[row]
            title = title_list.iloc[row]

            counts += 1
            if counts > 0:
                GPToutput = Catalytic_Extract(abstract, a)
                a += 1
                if a == 4:
                    a = 1

                # 如果API超时，重试最多3次
                retry_count = 0
                while GPToutput == "API time out" and retry_count < 3:
                    time.sleep(20)
                    GPToutput = Catalytic_Extract(abstract, a)
                    retry_count += 1
                    print(f"API time out，waiting for 20s to request again (attempt {retry_count})")

                GPToutputlist.append(GPToutput)
                abstract_processedlist.append(abstract)
                title_processedlist.append(title)

                print(f"Title: {title}")
                print(f"GPToutput: {GPToutput}")
                print(f"Already finished {counts} articles")
                print("-" * 50)

                # 添加短暂延迟避免API限制
                time.sleep(1)

        # 保存结果
        df = pd.DataFrame({
            'output': GPToutputlist,
            'title': title_processedlist,
            'abstract': abstract_processedlist
        })

        # 修改这一行
        output_file = f'./{file_name}_secondclean.csv'

        # 改为（例如保存到当前目录的 output 文件夹）
        output_dir = './output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_file = os.path.join(output_dir, f'{os.path.splitext(file_name)[0]}_secondclean.csv')
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"Results saved to {output_file}")

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")