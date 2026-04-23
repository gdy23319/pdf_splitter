# PDF幻灯片分割工具

用于将包含多个幻灯片的PDF页面自动分割成单独的页面，无需Adobe Acrobat。

fork自https://github.com/lyk82468246/pdf_splitter

运行`python .\batch_split.py`，可以把/before里的四合一pdf（默认2行2列）split并保存至/after。

**事后会移除/before里的文件**

配置环境：python version = 13

```shell
python -m venv venv

#windows:
venv\Scripts\activate

pip install -r requirements.txt
```