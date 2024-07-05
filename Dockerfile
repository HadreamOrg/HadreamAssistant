FROM python:3.8-slim
ENV LANG C.UTF-8
ENV PATH /usr/local/bin:$PATH
ENV PYTHON_VERSION 3.8.5
COPY . /app
WORKDIR /app
RUN apt-get -o "Acquire::https::Proxy=https://mirrors.tuna.tsinghua.edu.cn/debian/" update && apt-get -o "Acquire::https::Proxy=https://mirrors.tuna.tsinghua.edu.cn/debian/" install build-essential -y
RUN apt-get -o "Acquire::https::Proxy=https://mirrors.tuna.tsinghua.edu.cn/debian/" install libasound-dev libportaudio2 libportaudiocpp0 portaudio19-dev -y && pip install pyaudio
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
EXPOSE 6680
CMD python ./run_ha.py
