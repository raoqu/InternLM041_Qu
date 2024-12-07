# MindSearch深度解析及实践

# 1. 部署MindSearch到Huggingface

## 1.1 Github codespace
1 在硅基流动上注册API KEY
![](imgs/silicon-apikey.png)

2. 新建Github codespace

进入[Github codespaces](https://github.com/codespaces)，使用Blank模板创建一个新的sapce

初始化conda环境
```shell
conda create -n mindsearch python=3.10 -y
conda init
source activate base
conda activate mindsearch
git clone https://github.com/InternLM/MindSearch.git && cd MindSearch && git checkout ae5b0c5
pip install -r requirements.txt
```
![](imgs/github-codespace.png)

3. 在codespace中启动应用前后端

3.1 启动后端

在codespace中初始化key并执行后端指令
```shell
export SILICON_API_KEY='.....'
python -m mindsearch.app --lang cn --model_format internlm_silicon --search_engine DuckDuckGoSearch --asy
```
![](imgs/mindsearch-backend.png)

这个时候后端通过 8002 端口暴露出 FastAPI 接口，可以通过在浏览器的codespace映射到8002端口的域名映射进行访问
![](imgs/mindsearch-fastapi.png)

3.2 启动前端

在codespace新开一个terminal，并输出以下命令启动前端gradio应用
```shell
cd /workspaces/codespaces-blank/MindSearch
conda activate mindsearch
python frontend/mindsearch_gradio.py
```

![](imgs/front-gradio.png)

通过映射到7882的商品的space域名访问应用进行测试

![](imgs/mindsearch-demo.png)

## 1.2 Huggingface space 部署

### 1.2.1 Huggingface space 部署及试运行

从InternLM的官方MindSearch Space(https://huggingface.co/spaces/internlm/MindSearch)复制出一个新的Space
![](imgs/space-duplicate.png)

等待Huggingface space部署过程，过程耗时较长，需耐心等待
![](imgs/hf-deploy.png)

完成自己的 [Hugginface Space](https://huggingface.co/spaces/raoqu/MindSearch) 部署

在运行过程中会发现任务执行很容易失败

![](imgs/hf-error.png)

### 1.2.2 问题排查与修复

这个时候，通过观察huggingface space的 Logs 查看出现错误的原因，会发现大量的io超时

再向上追溯，会发现duckduckgo的限速异常

![](imgs/duckduckgo-error.png)

为了解决这个问题，将代码clone到本地进行验证，调试会更方便一些

```shell
git clone https://huggingface.co/spaces/raoqu/MindSearch
conda create --n ai python=3.10 -y
conda activate ai
export SILICON_API_KEY = '...'
python app.py
```

通过查看代码可以看到 app.py 中实际上是通过 `os.system` 启动了后端代码，然后并行用gradio启动前端服务

并且代码中指定了搜索引擎使用的是 DuckDuckGoSearch

![](imgs/code.png)

这时候本地启动也会出现与 Huggingface 上相同的问题，通过代码可以查看可选的搜索引擎还有 Bing、Brave、Google和腾讯的搜索服务。可以看到除了DuckDuckGo以外，其他的搜索引擎都需要申请相应的API key
![](imgs/search-engine.png)

这时候选择改成Google作为搜索引擎，新注册的Serper用户会有一些免费的API调用额度，访问[Serper](https://serper.dev/)

![](imgs/serper-web.png)

以前已经注册过，可以利用serper的key，如果没有在页面中新建就可以了

![](imgs/serper-key.png)

修改代码中的搜索引擎参数为 `GoogleSearch`

![](imgs/code-modified.png)

根据代码里的映射关系，重新设置环境变量`GOOGLE_SERPER_API_KEY`，重新运行发现仍然会报403异常

再仔细分析代码，会发现后端应用代码中的片断，依赖的是另外一个环境变量 `WEB_SEARCH_API_KEY`

![](imgs/env-vars.png)

添加环境变量，重新运行，本地运行成功
```shell
export WEB_SEARCH_API_KEY='替换成自己的Serper API key'
```

![](imgs/local-success.png)

通过seper页面，可以观察知道，在刚刚的 MindSearch 运行中进行了 8 次搜索调用

![](imgs/serper-count.png)

### 1.2.3 重新部署Huggingface Space

由于添加了对Serper的依赖，因此需要为Huggingface Space添加新的环境变量`WEB_SEARCH_API_KEY` 和 `GOOGLE_SERPER_API_KEY`(New Secret)
![](imgs/space-secret.png)

通过Git 提交代码并push到Huggingface代码仓库
```shell
cd MindSearch
git add app.py
git commit -m "Change search engine"
git push
```

重新访问 [Huggingface Space](https://huggingface.co/spaces/raoqu/MindSearch)，应用会触发重新部署

等待部署完成后重试应用，会发现应用能够正常运行了

![](imgs/hf-success.png)

# 2. 部署Streamlit版本到Huggingface

## 2.1 方案分析
gradio版本与steramlit版本仅仅是前端代码差异，而后端服务本身没有差异，因此只需要将已经部署的gradio版本Duplicate到新的Space，然后用Streamlit版本的前端python代码进行覆盖

同时，Github codespace中部署过gradio版本的前端应用，但是是后端和前端是分别启动的。而官方Huggingface Space应用中，`app.py`实际上是gradio前端版本基础上，在代码中通过系统调用自动完成了后端服务的启动过程。因此依葫芦画瓢，对steramlit前端应用修改相应代码即可。

## 2.2 着手实践

基于Streamlit模板创建一个[新的space](https://huggingface.co/spaces/raoqu/MindSearchSl)
![](imgs/streamlit-space.png)

添加秘钥配置
![](imgs/streamlit-keys.png)

克隆代码到本地，复制原有的MindSearch应用代码，基于steramlit demo基础之上进行修改
```
conda activate ai
git clone https://huggingface.co/spaces/raoqu/MindSearchSl
git clone git@github.com:InternLM/MindSearch.git InternlmMindSearch
cd MindSearchStreamlit
cp -f ../InternlmMindSearch/frontend/mindsearch_streamlit.py ./app.py
cp -rf ../MindSearch/mindsearch .
cp -f ../MindSearch/requirements.txt .
find . -name "__pycache__" -type d|xargs rm -rf
git add .
export SILICON_API_KEY='...'
export GOOGLE_SERPER_API_KEY='...'
export WEB_SEARCH_API_KEY='...'
```

修改 `requirements.txt`，添加对 `streamlit` 的依赖
```
pip install -r requirements.txt
```

打开 [app.py](code/app.py)修改代码，优先启动后端服务（参照app.py）
![](imgs/streamlit-code.png)

```
streamlit run app.py
```
![](imgs/streamlit-run.png)

提交代码
```
git add app.py
git commit -m "提交"
git push
```

部署成功后的 Huggingface Space
![](imgs/streamlit-hf.png)

可以看到MindSearch给出了非常有效的回答
![](imgs/hf-response.png)