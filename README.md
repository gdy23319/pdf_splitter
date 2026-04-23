# PDF幻灯片分割工具

一个强大的Python工具，用于将包含多个幻灯片的PDF页面自动分割成单独的页面，无需Adobe Acrobat。

fork自https://github.com/lyk82468246/pdf_splitter

运行`python .\batch_split.py`，把/before里的四合一pdf（默认2行2列）split并保存至/after。

**事后会移除/before里的文件**


## 🆕 新功能亮点

- 🗜️ **智能压缩**: 内置PDF压缩功能，可将文件大小减少90%以上，同时保持质量无损
- 🔗 **智能合并**: 默认将所有分割页面合并成一个完整的PDF文件
- 🗑️ **空白页检测**: 自动识别并移除分割后的空白页面
- ✂️ **页眉页脚裁剪**: 自动裁掉页码等页眉页脚内容
- 🎯 **完全白边裁剪**: 几乎零边距的精确白边清除
- 📄 **灵活输出**: 支持合并输出、单独文件或两者兼有

## 功能特点

- 🔍 **智能布局检测**: 自动识别页面中的幻灯片布局（如2x2、2x3、3x2等）
- ✂️ **精确分割**: 准确分割每个幻灯片为独立的PDF页面
- 🎯 **智能裁剪**: 自动检测并裁剪多余的白边（几乎零边距）
- 🗜️ **高效压缩**: 内置多级压缩算法，大幅减少文件大小而不损失质量
- 📁 **批量处理**: 支持处理整个PDF文档的所有页面
- 🔧 **灵活配置**: 支持手动指定布局和自定义参数
- 💯 **矢量保持**: 完全保留原始PDF的矢量元素和文字质量
- 🔗 **智能合并**: 默认合并所有分割页面为一个PDF文件
- 🗑️ **空白页过滤**: 自动检测并移除空白页面

## 技术优势

- **纯Python实现**: 无需安装Adobe Acrobat或其他商业软件
- **图像分析**: 使用先进的图像处理算法检测幻灯片边界
- **矢量操作**: 直接操作PDF对象，保持最高质量
- **跨平台**: 支持Windows、macOS和Linux

## 安装依赖

```bash
# 安装所需的Python包
pip install -r requirements.txt
```

或者手动安装：

```bash
pip install PyMuPDF Pillow numpy tqdm
```

## 使用方法

### 基本用法（推荐）

```bash
# 自动检测布局并分割，输出合并的PDF文件
python pdf_splitter.py input.pdf

# 指定输出目录
python pdf_splitter.py input.pdf -o output_folder
```

### 高级用法

```bash
# 输出单独文件而不合并
python pdf_splitter.py input.pdf --no-merge

# 同时输出合并文件和单独文件
python pdf_splitter.py input.pdf --separate-files

# 手动指定布局为2行3列
python pdf_splitter.py input.pdf --rows 2 --cols 3

# 保留页眉页脚（不裁剪页码）
python pdf_splitter.py input.pdf --no-crop-header-footer

# 保留空白页面
python pdf_splitter.py input.pdf --keep-blank-pages

# 禁用自动裁剪白边
python pdf_splitter.py input.pdf --no-auto-crop

# 自定义裁剪边距
python pdf_splitter.py input.pdf --crop-margin 0.05

# 设置压缩级别（1-4，4为最高压缩）
python pdf_splitter.py input.pdf --compression-level 4

# 禁用PDF压缩优化
python pdf_splitter.py input.pdf --no-optimize
```

## 参数说明

### 基本参数
- `input_pdf`: 输入PDF文件路径
- `-o, --output`: 输出目录（可选）

### 布局控制
- `--rows`: 手动指定行数
- `--cols`: 手动指定列数
- `--no-auto-detect`: 禁用自动布局检测

### 输出控制
- `--no-merge`: 不合并输出，保存为单独文件
- `--separate-files`: 同时保存单独文件和合并文件

### 裁剪控制
- `--no-auto-crop`: 禁用自动裁剪白边
- `--crop-margin`: 裁剪边距比例（默认0.02）
- `--no-crop-header-footer`: 不裁剪页眉页脚
- `--keep-blank-pages`: 保留空白页面

### 压缩控制
- `--compression-level`: 压缩级别（1-4，默认3）
- `--no-optimize`: 禁用PDF压缩优化

## 使用示例

### 示例1：处理标准6格幻灯片PDF

```bash
python pdf_splitter.py lecture_slides.pdf
```

输出：
```
成功打开PDF文件: lecture_slides.pdf
总页数: 10
处理第 1 页...
检测到的布局: 2行 x 3列
  保存: page_001_part_01.pdf
  保存: page_001_part_02.pdf
  保存: page_001_part_03.pdf
  保存: page_001_part_04.pdf
  保存: page_001_part_05.pdf
  保存: page_001_part_06.pdf
...
正在合并 60 个分割页面...
已启用PDF优化 (压缩级别: 3)

✅ 合并文件已保存: lecture_slides_split_merged.pdf

分割完成！
输入页数: 10
有效输出页数: 60
输出目录: lecture_slides_split
```

## 示例

假设你有一个PDF，每页包含6个幻灯片（2行3列布局）：

```bash
python pdf_splitter.py presentation.pdf
```

工具会：
1. 自动检测到2x3布局
2. 将每页分割成6个独立的幻灯片
3. 自动裁剪页眉页脚（去除页码）
4. 自动裁剪每个幻灯片的白边（几乎零边距）
5. 自动移除空白页面
6. **将所有有效页面合并成一个PDF文件**
7. **应用智能压缩算法，大幅减少文件大小**
8. 保存到`presentation_split/`目录，文件名为`presentation_split_merged.pdf`

## 输出文件说明

### 默认模式（合并输出）
- 输出一个合并的PDF文件：`{原文件名}_split_merged.pdf`
- 包含所有有效的分割页面

### 单独文件模式
- 每个分割页面保存为单独文件：`page_001_part_01.pdf`、`page_001_part_02.pdf`等

### 双模式输出
- 既有合并文件，也有单独文件

## Python代码使用

### 基本使用（默认合并）

```python
from pdf_splitter import PDFSplitter

# 创建分割器
splitter = PDFSplitter("input.pdf", "output_folder")

# 执行分割（默认合并输出）
success = splitter.split_pdf()

if success:
    print("分割完成！输出为合并的PDF文件")
```

### 高级配置

```python
# 完全自定义配置
success = splitter.split_pdf(
    auto_detect=True,           # 自动检测布局
    auto_crop=True,             # 自动裁剪白边
    crop_margin=0.001,          # 极小边距（0.1%）
    merge_output=True,          # 合并输出（默认）
    separate_files=False,       # 不保存单独文件
    crop_header_footer=True,    # 裁剪页眉页脚（默认）
    remove_blank_pages=True,    # 移除空白页（默认）
    optimize_output=True,       # 启用压缩优化（默认）
    compression_level=3         # 压缩级别（默认3）
)
```

### 单独文件模式

```python
# 输出单独文件
success = splitter.split_pdf(
    merge_output=False,         # 不合并
    auto_crop=True,             # 完全裁剪白边
    crop_header_footer=True,    # 裁剪页眉页脚
    remove_blank_pages=True     # 移除空白页
)
```

### 双模式输出

```python
# 同时输出合并文件和单独文件
success = splitter.split_pdf(
    merge_output=True,          # 合并输出
    separate_files=True,        # 同时保存单独文件
    auto_crop=True,             # 完全裁剪白边
    crop_header_footer=True,    # 裁剪页眉页脚
    remove_blank_pages=True,    # 移除空白页
    optimize_output=True,       # 启用压缩优化
    compression_level=4         # 最高压缩级别
)
```

## 🗜️ PDF压缩功能详解

### 压缩效果展示

以实际测试为例：
- **原始PDF**: 2.25 MB (18页)
- **分割后无压缩**: 47.33 MB (85页)
- **分割后压缩级别4**: 3.17 MB (85页)
- **压缩率**: 93.3% (从47.33MB压缩到3.17MB)

### 压缩级别说明

| 级别 | 压缩强度 | 处理速度 | 适用场景 |
|------|----------|----------|----------|
| 1    | 轻度压缩 | 最快     | 快速处理，文件大小要求不严格 |
| 2    | 中度压缩 | 较快     | 平衡压缩效果和处理速度 |
| 3    | 高度压缩 | 中等     | **默认推荐**，最佳平衡点 |
| 4    | 最高压缩 | 较慢     | 最小文件大小，质量要求高 |

### 压缩技术特点

✅ **质量无损**: 完全保持PDF的视觉质量和文字清晰度  
✅ **智能优化**: 自动识别和优化重复资源  
✅ **兼容性强**: 压缩后的PDF与所有PDF阅读器兼容  
✅ **内存高效**: 使用内存缓冲区，避免临时文件问题  

### 使用建议

- **日常使用**: 使用默认压缩级别3，获得最佳效果
- **存储优先**: 使用压缩级别4，获得最小文件大小
- **速度优先**: 使用压缩级别1或禁用压缩(`--no-optimize`)
- **质量检查**: 压缩后建议检查PDF内容，确保符合预期

## 支持的PDF格式

- 标准PDF文档
- 扫描版PDF（图像型PDF）
- 混合内容PDF
- 加密PDF（需要先解密）

## 常见问题

**Q: 分割后的PDF质量如何？**
A: 工具使用PyMuPDF的矢量操作，完全保留原始质量，不会有任何压缩或质量损失。

**Q: 默认输出是什么格式？**
A: 默认将所有分割页面合并成一个PDF文件，方便查看和使用。如需单独文件，使用`--no-merge`参数。

**Q: 如何确保页码被完全去除？**
A: 工具默认启用页眉页脚裁剪功能，会在分割前先裁掉页码等内容。

**Q: 空白页会被自动处理吗？**
A: 是的，工具会自动检测并移除分割后的空白页面，确保输出只包含有效内容。

**Q: 支持哪些布局？**
A: 支持常见的幻灯片布局，如1x2、2x1、2x2、2x3、3x2、3x3等。工具会自动检测最合适的布局。

**Q: 如何处理不规则布局？**
A: 可以使用`--rows`和`--cols`参数手动指定布局，或调整`--crop-margin`参数来优化分割效果。

**Q: PDF压缩效果如何？**
A: 内置的智能压缩算法可以将文件大小减少90%以上，同时保持完全的质量无损。压缩通过资源去重、图片优化、字体压缩等多种技术实现。

**Q: 压缩级别有什么区别？**
A: 压缩级别1-4分别对应不同的压缩强度，级别4提供最高压缩率但处理时间稍长。默认级别3在压缩效果和速度间取得最佳平衡。

**Q: 可以禁用压缩功能吗？**
A: 可以使用`--no-optimize`参数完全禁用压缩功能，或在Python代码中设置`optimize_output=False`。

## 技术原理

1. **布局检测**: 使用图像分析技术检测页面中的内容分布
2. **页眉页脚裁剪**: 在分割前先识别并裁掉页码等页眉页脚内容
3. **边界识别**: 通过像素分析找到每个幻灯片的精确边界
4. **矢量分割**: 使用PyMuPDF的`show_pdf_page`方法进行无损分割
5. **智能裁剪**: 多层次像素分析，实现几乎零边距的精确白边清除
6. **空白页检测**: 分析内容密度自动识别并过滤空白页面
7. **智能合并**: 将所有有效页面合并为一个便于使用的PDF文件
8. **高效压缩**: 
   - **资源去重**: 识别并合并重复的字体、图片等资源
   - **图片优化**: 无损压缩图片数据，减少存储空间
   - **字体压缩**: 优化字体嵌入，移除未使用的字符
   - **对象清理**: 垃圾回收未使用的PDF对象
   - **流压缩**: 使用deflate算法压缩PDF内容流

## 许可证

本项目采用MIT许可证，可自由使用和修改。

## 贡献

欢迎提交Issue和Pull Request来改进这个工具！