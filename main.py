import openai
import gradio as gr
import os
import time
import json
import pandas as pd

def get_completion(prompt, model='gpt-3.5-turbo-16k', system_message='你是一个得力的助手', temperature=0.7): 
    start_time = time.time() 
    max_retries = 3
    retries = 0
    while retries < max_retries:
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {'role': 'system', 'content': f'{system_message}'},
                    {'role': 'user', 'content': f'{prompt}'}],
                temperature=temperature,
                stream=True)
            break
        except Exception as e:
            gr.Info(f'发生错误：{e}\n20秒后重试')
            retries += 1
            time.sleep(20)
    if retries == max_retries:
        gr.Error('已达最大重试次数，程序停止运行')
    collected_messages = []
    for chunk in response:
        chunk_message = chunk['choices'][0]['delta']
        collected_messages.append(chunk_message)
        full_reply_content = ''.join([m.get('content', '') for m in collected_messages])
        yield full_reply_content
    cost_time = time.time() - start_time
    if cost_time <= 20:
        time.sleep(int(20-cost_time)+1)
        
def login(api_key):
    try:
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo-16k',
            messages=[
                {'role': 'user', 'content': '请说：“你来辣？”'}
            ],
            temperature=0,
            stream=True)
        collected_messages = []
        for chunk in response:
            chunk_message = chunk['choices'][0]['delta']
            collected_messages.append(chunk_message)
            full_reply_content = ''.join([m.get('content', '') for m in collected_messages])
            yield full_reply_content
    except Exception as e:
        gr.Info(e)

def process_input(input_text):
    lines = input_text.strip().split('\n')
    return lines

def from_path_get_ctt(path):
    ctt_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    ctt_list.append(content)
    return ctt_list

def initial_all():
    return -1, -1, -1

def who_big(num_qs, qs_list):
    if num_qs >= len(qs_list):
        return 1
    else:
        num_qs_requests = len(qs_list)//num_qs
        add_one_or_not = len(qs_list)%num_qs
        if add_one_or_not > 0:
            num_qs_requests += 1
        return num_qs_requests
    
def update_now_ctt_index(now_ctt_index, start_index):
    if now_ctt_index == -1:
        return start_index
    else:
        return now_ctt_index+1

example_json = '[{"翻译结果": "在这里写入翻译结果1"},{"翻译结果": "在这里写入翻译结果2"}]'

sys_msg = f'你是一个翻译助手，按照[[[翻译要求]]]中的要求进行翻译"""需要翻译的句子"""中的句子，并且以json格式输出翻译结果，输出的json包含一个键，翻译结果，其值即为翻译结果。\n例如：\n{example_json}\n'
    
def initial_or_get_prompt(num_qs_requests, now_prompt, now_qs_index, qs_list, ctt_list, now_ctt_index, system_msg):
    if num_qs_requests == 1:
        try:
            prompt = system_msg + '\n\n' + '[[[' + '\n'.join(qs_list) + ']]]' + '\n\n"""' + ctt_list[now_ctt_index] + '"""'
        except IndexError:
            prompt = '请说：“已经完成辣！！”'
        return now_qs_index, prompt
    elif now_ctt_index == -1:
        return now_qs_index, now_prompt
    else:
        return 0, now_prompt
    
def get_now_prompt(num_qs_requests, now_qs_index, now_ctt_index, num_qs, qs_list, ctt_list, now_prompt, system_msg):
    if now_qs_index == -1:
        return now_prompt
    else:
        start_index = now_qs_index * num_qs
        end_index = start_index + num_qs
        qs_list_slice = qs_list[start_index:end_index]
        try:
            prompt = system_msg + '\n\n' + '[[[' + '\n'.join(qs_list_slice) + ']]]' + '\n\n"""' + ctt_list[now_ctt_index] + '"""'
        except IndexError:
            prompt = '请说：“已经完成辣！！”'
        return prompt

def update_now_qs_index_or_ctt_index(num_qs_requests, now_qs_index, now_ctt_index):
    if num_qs_requests == 1:
        return now_qs_index, now_ctt_index+1
    elif num_qs_requests-1 == now_qs_index:
        return now_qs_index, now_ctt_index+1
    else:
        return now_qs_index+1, now_ctt_index
    
def return_x(x):
    return x
    
def add_one(x):
    return x+1

def process_input(input_text):
    lines = input_text.strip().split('\n')
    return lines

def process_txt_file(txt_file):
    path = txt_file.name
    with open(path, 'r', encoding='utf-8') as temp_file:
        data = [line.strip() for line in temp_file]
    return data

def input_ctt_files(files):
    ctt_list = []
    for file in files:
        path = file.name
        if path.endswith('.txt'):
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                ctt_list.append(content)
    return ctt_list

def process_excel(excel):
    path = excel.name
    df = pd.read_excel(path, header=None)
    ctts = df[0].tolist()
    return ctts

def decode_json(json_output):
    try:
        if isinstance(json_output, str):
            json_data = json.loads(json_output)
        else:
            json_data = json_output
        list_results = [item['翻译结果'] for item in json_data]
        return list_results
    except Exception:
        return []

def update_dataframe(result_df, ctt_index, now_qs_index, num_qs, qs_list, stream_output, num_qs_requests, ctt_list):
    if num_qs_requests == -1:
        now_qs_index = 0
    if ctt_index <= len(ctt_list):
        start_index = now_qs_index * num_qs
        end_index = start_index + num_qs
        qs_list_slice = qs_list[start_index:end_index]
        result_df.loc[ctt_index, 'ctt_index'] = ctt_index
        if len(decode_json(stream_output)) == len(qs_list_slice):
            result_df.loc[ctt_index, qs_list_slice] = decode_json(stream_output)
        else:
            result_df.loc[ctt_index, qs_list[now_qs_index]] = stream_output
    else:
        result_df.loc[ctt_index, qs_list[0]] = stream_output
    return result_df
    
def save_last_row(result_df, result_excel='./结果文件.xlsx'):
    try:
        excel_df = pd.read_excel(result_excel)
    except FileNotFoundError:
        excel_df = pd.DataFrame()
    last_row = result_df.iloc[[-1]]
    excel_df = excel_df.append(last_row, ignore_index=True)
    excel_df.to_excel(result_excel, index=False)
    
with gr.Blocks() as sleeplessGPT_face:
    
    login_please = gr.Markdown('# 先登录')
    with gr.Group():
        api_key = gr.Textbox(
            label='输入你的OpenAI API Key',
            info='获取方法见项目说明，多线程记得使用不同的API Key',
            placeholder='形如sk-...')
        test_output = gr.Textbox(label='测试输入的API Key是否可用', info='显示“你来辣？”即为可用')
        log_btn = gr.Button(value='测试')
        log_btn.click(fn=login, inputs=api_key, outputs=test_output)
    gr.Examples(['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'], inputs=api_key)
        
    sleeplessgpt = gr.Markdown('# SleeplessGPT')    
    with gr.Tab('sleeplessgpt_block'):
        with gr.Row():
            with gr.Column():
                gr.Markdown('## 想问的问题')
                with gr.Tab('直接填写问题'):
                    qs = gr.Textbox(
                        lines=5, container=False,
                        value='请把这段话翻译成英文。\n请把这段话翻译成日文。\n请把这段话翻译成韩文。\n请把这段话翻译成法文。')
                with gr.Tab('上传写有问题的txt'):
                    qs_file = gr.File(label='请确保txt每行写着一个问题')
            with gr.Column():
                gr.Markdown('## 想处理的文本')
                with gr.Tab('填写文件夹路径'):
                    ctt_path = gr.Textbox(container=False, info='自动读取该路径下的所有txt', value='./examples/ctts')
                with gr.Tab('拖入待处理的txt'):
                    ctt_files = gr.File(label='全选，拖入', file_count='directory')
                with gr.Tab('上传excel'):
                    ctt_excel = gr.File(label='请确保待处理的文本在excel的第一列')
        
        with gr.Row():
            save_qs_text = gr.Textbox(show_label=False, max_lines=5, interactive=False)
            save_ctt_text = gr.Textbox(show_label=False, max_lines=5, interactive=False)
        
        with gr.Row():
            save_qs = gr.JSON(visible=False)
            save_ctt = gr.JSON(visible=False)
            start_index = gr.Number(label='从index几开始',info='index代表文本序号，第一条文本的index为0，以此类推', value=0, precision=0, interactive=True)
            end_index = gr.Number(label='到index几结束', info='-1代表最后一条文本的index', value=-1, precision=0, interactive=True)
            num_qs = gr.Slider(1, 20, value=4, step=1, label='同时提问几个问题', info='如果有超过4个问题，建议每次问4个及以下，同时提问的数量过多有可能导致GPT回答出错', interactive=True)

        with gr.Row():
            with gr.Column():
                system_message = gr.Textbox(lines=5, label='system message', info='填写每次提问时都想告诉GPT的要求',value=sys_msg, interactive=True)
            with gr.Column():
                slct_model = gr.Dropdown(
                    choices=['gpt-3.5-turbo-16k', 'text-davinci-003'],
                    value='gpt-3.5-turbo-16k',
                    label='选择模型',
                    info='默认选择gpt3.5 16k上下文版本',
                    interactive=True,
                    scale=1)
                slct_temperature = gr.Slider(
                    0, 2, step=0.1, value=0.5,
                    label='选择temperature', info='温度越低越理性', interactive=True)
        start_btn = gr.Button(value='开始运行')
        reset_btn = gr.Button(value='重新开始运行前，按我归零index')
        with gr.Row():
            now_prompt = gr.Textbox(label='当前向GPT发送的完整prompt', info='即为system message+问题+文本', interactive=False)
            stream_output = gr.Textbox(label='GPT的输出', info='实时的流式输出', interactive=False)
        with gr.Row():
            num_qs_requests = gr.Number(label='num_qs_requests', value=-1, precision=0, visible=False)
            now_ctt_index = gr.Number(label='当前正在处理的文本index', value=-1, precision=0, interactive=False)
            now_qs_index = gr.Number(label='当前正在提问的问题index', value=-1, precision=0, interactive=False)
        with gr.Row():
            result_df = gr.Dataframe(label='处理结果，所见即所得，目前只支持dataframe', value=pd.DataFrame(), type='pandas', wrap=True, interactive=False)
            output_done_signiture = gr.Number(value=0, precision=0, visible=False)
    
    with gr.Tab('oneq_onea_block'):
        one_question_one_answer = gr.Markdown('# 一问一答')
        gr.Markdown('## 可以在这里测试、调整system message和问题')
        with gr.Row():
            with gr.Column():
                system_message_oq = gr.Textbox(lines=5, label='system message', info='填写每次提问时都想告诉GPT的要求', value=sys_msg, interactive=True)
            with gr.Column():
                slct_model_oq = gr.Dropdown(
                    choices=['gpt-3.5-turbo-16k', 'text-davinci-003'],
                    value='gpt-3.5-turbo-16k',
                    label='选择模型',
                    info='默认选择gpt3.5 16k上下文版本',
                    interactive=True)
                slct_temperature_oq = gr.Slider(
                    0, 2, step=0.1, value=0.7,
                    label='选择temperature', info='温度越低越理性', interactive=True)   
        oneq = gr.Textbox(lines=2, label='问题', interactive=True)
        onea = gr.Textbox(lines=2, label='回答', interactive=False)
        oneq_onea_btn = gr.Button(value='提问')
        oneq_onea_btn.click(fn=get_completion, inputs=[oneq, slct_model_oq, system_message_oq, slct_temperature_oq], outputs=onea)    
    
    qs_file.upload(
        fn=process_txt_file, inputs=qs_file, outputs=save_qs)
    qs.change(
        fn=process_input, inputs=qs, outputs=save_qs)
    save_qs.change(
        fn=return_x, inputs=save_qs, outputs=save_qs_text)
    ctt_files.upload(
        fn=input_ctt_files, inputs=ctt_files, outputs=save_ctt)
    ctt_excel.upload(
        fn=process_excel, inputs=ctt_excel, outputs=save_ctt)
    ctt_path.change(
        fn=from_path_get_ctt, inputs=ctt_path, outputs=save_ctt)
    save_ctt.change(
        fn=return_x, inputs=save_ctt, outputs=save_ctt_text)
    
    reset_btn.click(fn=initial_all, outputs=[num_qs_requests, now_ctt_index, now_qs_index])
    start_btn.click(fn=who_big, inputs=[num_qs, save_qs], outputs=num_qs_requests)
    start_btn.click(fn=update_now_ctt_index, inputs=[now_ctt_index, start_index], outputs=now_ctt_index)
    now_ctt_index.change(
        fn=initial_or_get_prompt,
        inputs=[num_qs_requests, now_prompt, now_qs_index, save_qs, save_ctt, now_ctt_index, system_message],
        outputs=[now_qs_index, now_prompt])
    now_qs_index.change(
        fn=get_now_prompt,
        inputs=[num_qs_requests, now_qs_index, now_ctt_index, num_qs, save_qs, save_ctt, now_prompt, system_message],
        outputs=now_prompt)
    now_prompt.change(fn=get_completion, inputs=[now_prompt, slct_model, system_message, slct_temperature], outputs=stream_output)
    stream_output.change(
        fn=add_one, inputs=output_done_signiture, outputs=output_done_signiture)
    output_done_signiture.change(
        fn=update_dataframe,
        inputs=[result_df, now_ctt_index, now_qs_index, num_qs, save_qs, stream_output, num_qs_requests, save_ctt],
        outputs=result_df)
    
    result_df.change(fn=save_last_row, inputs=result_df)
    result_df.change(
        fn=update_now_qs_index_or_ctt_index,
        inputs=[num_qs_requests, now_qs_index, now_ctt_index],
        outputs=[now_qs_index, now_ctt_index])
    
sleeplessGPT_face.queue()
sleeplessGPT_face.launch(inbrowser=True)