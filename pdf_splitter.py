#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF幻灯片分割工具
一站式解决一页多张PPT幻灯片的PDF分割问题，无需Acrobat

作者: Assistant
功能:
- 自动检测一页中多个幻灯片的布局
- 智能分割PDF页面
- 自动裁剪白边和页边距
- 支持多种布局（2x2, 2x3, 3x2等）
"""

import fitz  # PyMuPDF
import os
import sys
import argparse
from typing import List, Tuple, Optional
import numpy as np
from PIL import Image
import io


class PDFSplitter:
    def __init__(self, input_path: str, output_dir: str = None):
        """
        初始化PDF分割器
        
        Args:
            input_path: 输入PDF文件路径
            output_dir: 输出目录，默认为输入文件同目录下的split文件夹
        """
        self.input_path = input_path
        self.output_dir = output_dir or os.path.join(
            os.path.dirname(input_path), 
            f"{os.path.splitext(os.path.basename(input_path))[0]}_split"
        )
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.doc = None
        
    def open_pdf(self):
        """打开PDF文档"""
        try:
            self.doc = fitz.open(self.input_path)
            print(f"成功打开PDF文件: {self.input_path}")
            print(f"总页数: {len(self.doc)}")
            return True
        except Exception as e:
            print(f"打开PDF文件失败: {e}")
            return False
    
    def close_pdf(self):
        """关闭PDF文档"""
        if self.doc:
            self.doc.close()
    
    def detect_layout(self, page_num: int = 0) -> Tuple[int, int]:
        """
        检测页面布局（行数和列数）
        
        Args:
            page_num: 页面编号
            
        Returns:
            (rows, cols): 行数和列数的元组
        """
        if not self.doc:
            return (1, 1)
            
        page = self.doc[page_num]
        
        # 将页面转换为图像进行分析
        mat = fitz.Matrix(2.0, 2.0)  # 放大2倍以提高检测精度
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("png")
        
        # 使用PIL处理图像
        img = Image.open(io.BytesIO(img_data))
        img_array = np.array(img.convert('L'))  # 转为灰度图
        
        # 检测水平和垂直分割线
        rows, cols = self._detect_grid_lines(img_array)
        
        print(f"检测到的布局: {rows}行 x {cols}列")
        return rows, cols
    
    def _detect_grid_lines(self, img_array: np.ndarray) -> Tuple[int, int]:
        """
        通过检测分割线来确定网格布局
        
        Args:
            img_array: 图像数组
            
        Returns:
            (rows, cols): 行数和列数
        """
        height, width = img_array.shape
        
        # 检测水平分割线（用于确定行数）
        horizontal_profile = np.mean(img_array, axis=1)
        h_threshold = np.mean(horizontal_profile) - np.std(horizontal_profile)
        
        # 检测垂直分割线（用于确定列数）
        vertical_profile = np.mean(img_array, axis=0)
        v_threshold = np.mean(vertical_profile) - np.std(vertical_profile)
        
        # 查找分割线
        h_lines = self._find_separator_lines(horizontal_profile, h_threshold, min_length=width//10)
        v_lines = self._find_separator_lines(vertical_profile, v_threshold, min_length=height//10)
        
        # 根据分割线数量确定行列数
        rows = len(h_lines) + 1 if h_lines else self._guess_rows_by_content(img_array)
        cols = len(v_lines) + 1 if v_lines else self._guess_cols_by_content(img_array)
        
        # 限制在合理范围内
        rows = max(1, min(rows, 4))
        cols = max(1, min(cols, 4))
        
        return rows, cols
    
    def _find_separator_lines(self, profile: np.ndarray, threshold: float, min_length: int) -> List[int]:
        """查找分割线位置"""
        lines = []
        in_line = False
        line_start = 0
        
        for i, value in enumerate(profile):
            if value < threshold and not in_line:
                in_line = True
                line_start = i
            elif value >= threshold and in_line:
                in_line = False
                if i - line_start >= min_length:
                    lines.append((line_start + i) // 2)
        
        return lines
    
    def _guess_rows_by_content(self, img_array: np.ndarray) -> int:
        """通过内容密度猜测行数"""
        height = img_array.shape[0]
        
        # 将图像分成几个水平条带，检查内容分布
        for rows in [2, 3, 4]:
            strip_height = height // rows
            content_strips = []
            
            for i in range(rows):
                start = i * strip_height
                end = min((i + 1) * strip_height, height)
                strip = img_array[start:end, :]
                content_density = np.sum(strip < 200) / strip.size  # 非白色像素比例
                content_strips.append(content_density)
            
            # 如果各条带的内容密度相近，说明可能是这个行数
            if len(content_strips) > 1:
                density_std = np.std(content_strips)
                density_mean = np.mean(content_strips)
                if density_std / density_mean < 0.5 and density_mean > 0.1:
                    return rows
        
        return 3  # 默认返回3行
    
    def _guess_cols_by_content(self, img_array: np.ndarray) -> int:
        """通过内容密度猜测列数"""
        width = img_array.shape[1]
        
        # 将图像分成几个垂直条带，检查内容分布
        for cols in [2, 3, 4]:
            strip_width = width // cols
            content_strips = []
            
            for i in range(cols):
                start = i * strip_width
                end = min((i + 1) * strip_width, width)
                strip = img_array[:, start:end]
                content_density = np.sum(strip < 200) / strip.size  # 非白色像素比例
                content_strips.append(content_density)
            
            # 如果各条带的内容密度相近，说明可能是这个列数
            if len(content_strips) > 1:
                density_std = np.std(content_strips)
                density_mean = np.mean(content_strips)
                if density_std / density_mean < 0.5 and density_mean > 0.1:
                    return cols
        
        return 2  # 默认返回2列
    
    def optimize_pdf_resources(self, doc: fitz.Document, compression_level: int = 3) -> fitz.Document:
        """
        优化PDF资源，减少文件大小
        
        Args:
            doc: 要优化的PDF文档
            compression_level: 压缩级别 (1-4, 1最快，4最小)
            
        Returns:
            优化后的PDF文档
        """
        try:
            # 创建临时文档进行优化
            temp_doc = fitz.open()
            temp_doc.insert_pdf(doc)
            
            # 设置压缩选项
            deflate_level = min(9, compression_level * 2 + 1)  # 1->3, 2->5, 3->7, 4->9
            
            # 直接在内存中优化，避免临时文件问题
            import io
            
            # 保存到内存缓冲区
            pdf_bytes = temp_doc.write(
                garbage=4,  # 最高级别的垃圾回收
                clean=True,  # 清理未使用的对象
                deflate=True,  # 启用deflate压缩
                deflate_images=True,  # 压缩图片
                deflate_fonts=True,  # 压缩字体
                linear=True,  # 线性化PDF
                pretty=False  # 不美化输出
            )
            
            temp_doc.close()
            
            # 从内存缓冲区创建新文档
            optimized_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            return optimized_doc
                
        except Exception as e:
            print(f"PDF优化失败: {e}")
            return doc
    
    def merge_documents_optimized(self, docs: List[fitz.Document], compression_level: int = 3) -> fitz.Document:
        """
        优化合并多个PDF文档，去重资源
        
        Args:
            docs: 要合并的PDF文档列表
            compression_level: 压缩级别 (1-4)
            
        Returns:
            合并并优化后的PDF文档
        """
        if not docs:
            return fitz.open()
        
        try:
            # 创建新的合并文档
            merged_doc = fitz.open()
            
            # 逐个插入页面
            for doc in docs:
                merged_doc.insert_pdf(doc)
            
            # 优化合并后的文档
            optimized_doc = self.optimize_pdf_resources(merged_doc, compression_level)
            merged_doc.close()
            
            return optimized_doc
            
        except Exception as e:
            print(f"优化合并失败: {e}")
            # 回退到普通合并
            merged_doc = fitz.open()
            for doc in docs:
                merged_doc.insert_pdf(doc)
            return merged_doc
    
    def split_page(self, page_num: int, rows: int, cols: int, crop_margin: float = 0.02, 
                   crop_header_footer: bool = True) -> List[fitz.Document]:
        """
        分割单个页面
        
        Args:
            page_num: 页面编号
            rows: 行数
            cols: 列数
            crop_margin: 裁剪边距比例
            crop_header_footer: 是否裁剪页眉页脚
            
        Returns:
            分割后的文档列表
        """
        if not self.doc:
            return []
        
        page = self.doc[page_num]
        
        # 如果需要，先裁剪页眉页脚
        if crop_header_footer:
            page_rect = self.crop_header_footer(page_num)
        else:
            page_rect = page.rect
        
        # 计算每个子页面的尺寸
        sub_width = page_rect.width / cols
        sub_height = page_rect.height / rows
        
        # 计算裁剪边距
        margin_x = sub_width * crop_margin
        margin_y = sub_height * crop_margin
        
        split_docs = []
        
        for row in range(rows):
            for col in range(cols):
                # 计算子页面的矩形区域（相对于裁剪后的页面）
                x0 = page_rect.x0 + col * sub_width + margin_x
                y0 = page_rect.y0 + row * sub_height + margin_y
                x1 = page_rect.x0 + (col + 1) * sub_width - margin_x
                y1 = page_rect.y0 + (row + 1) * sub_height - margin_y
                
                # 创建裁剪矩形
                clip_rect = fitz.Rect(x0, y0, x1, y1)
                
                # 创建新文档
                new_doc = fitz.open()
                new_page = new_doc.new_page(width=clip_rect.width, height=clip_rect.height)
                
                # 复制并裁剪内容
                new_page.show_pdf_page(
                    fitz.Rect(0, 0, clip_rect.width, clip_rect.height),
                    self.doc,
                    page_num,
                    clip=clip_rect
                )
                
                split_docs.append(new_doc)
        
        return split_docs
    
    def crop_header_footer(self, page_num: int, header_ratio: float = 0.05, footer_ratio: float = 0.05) -> fitz.Rect:
        """
        裁剪页眉页脚区域
        
        Args:
            page_num: 页面编号
            header_ratio: 页眉裁剪比例
            footer_ratio: 页脚裁剪比例
            
        Returns:
            裁剪后的页面矩形
        """
        if not self.doc:
            return fitz.Rect()
        
        page = self.doc[page_num]
        page_rect = page.rect
        
        # 计算裁剪区域
        header_height = page_rect.height * header_ratio
        footer_height = page_rect.height * footer_ratio
        
        cropped_rect = fitz.Rect(
            page_rect.x0,
            page_rect.y0 + header_height,
            page_rect.x1,
            page_rect.y1 - footer_height
        )
        
        return cropped_rect
    
    def is_blank_page(self, doc: fitz.Document, content_threshold: float = 0.01) -> bool:
        """
        检测是否为空白页
        
        Args:
            doc: 文档
            content_threshold: 内容阈值（内容像素占比）
            
        Returns:
            是否为空白页
        """
        if len(doc) == 0:
            return True
        
        page = doc[0]
        
        # 转换为图像进行内容检测
        mat = fitz.Matrix(1.0, 1.0)  # 使用较低分辨率以提高速度
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        img_array = np.array(img.convert('L'))
        
        # 计算非白色像素比例
        non_white_pixels = np.sum(img_array < 240)  # 阈值240，低于此值认为是内容
        total_pixels = img_array.size
        content_ratio = non_white_pixels / total_pixels
        
        return content_ratio < content_threshold
    
    def auto_crop_whitespace(self, doc: fitz.Document, margin: float = 0.002) -> fitz.Document:
        """
        自动裁剪白边（精确优化版）
        
        Args:
            doc: 输入文档
            margin: 保留的边距比例（默认0.2%，几乎完全裁剪）
            
        Returns:
            裁剪后的文档
        """
        if len(doc) == 0:
            return doc
        
        page = doc[0]
        
        # 使用更高分辨率进行精确检测
        mat = fitz.Matrix(4.0, 4.0)  # 4倍分辨率提高检测精度
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        
        # 转换为RGB数组进行多层次分析
        img_rgb = np.array(img.convert('RGB'))
        img_gray = np.array(img.convert('L'))
        
        # 多层次白边检测
        content_bounds = self._detect_content_bounds_advanced(img_rgb, img_gray)
        
        if content_bounds:
            # 转换回PDF坐标系
            scale_x = page.rect.width / img_rgb.shape[1]
            scale_y = page.rect.height / img_rgb.shape[0]
            
            left = content_bounds[0] * scale_x
            top = content_bounds[1] * scale_y
            right = content_bounds[2] * scale_x
            bottom = content_bounds[3] * scale_y
            
            # 添加极小的边距
            margin_x = max(0.5, (right - left) * margin)  # 至少保留0.5个点的边距
            margin_y = max(0.5, (bottom - top) * margin)
            
            crop_rect = fitz.Rect(
                max(0, left - margin_x),
                max(0, top - margin_y),
                min(page.rect.width, right + margin_x),
                min(page.rect.height, bottom + margin_y)
            )
            
            # 验证裁剪区域有效性
            if crop_rect.width > 0 and crop_rect.height > 0:
                # 创建裁剪后的新文档
                new_doc = fitz.open()
                new_page = new_doc.new_page(width=crop_rect.width, height=crop_rect.height)
                new_page.show_pdf_page(
                    fitz.Rect(0, 0, crop_rect.width, crop_rect.height),
                    doc,
                    0,
                    clip=crop_rect
                )
                
                doc.close()
                return new_doc
        
        return doc
    
    def _detect_content_bounds(self, img_array: np.ndarray, threshold: int = 240) -> Optional[Tuple[int, int, int, int]]:
        """
        检测图像中内容的边界
        
        Args:
            img_array: 图像数组
            threshold: 白色阈值
            
        Returns:
            (left, top, right, bottom) 或 None
        """
        # 创建内容掩码（非白色区域）
        content_mask = img_array < threshold
        
        # 查找内容区域
        rows_with_content = np.any(content_mask, axis=1)
        cols_with_content = np.any(content_mask, axis=0)
        
        if not np.any(rows_with_content) or not np.any(cols_with_content):
            return None
        
        top = np.argmax(rows_with_content)
        bottom = len(rows_with_content) - np.argmax(rows_with_content[::-1]) - 1
        left = np.argmax(cols_with_content)
        right = len(cols_with_content) - np.argmax(cols_with_content[::-1]) - 1
        
        return (left, top, right, bottom)
    
    def _detect_content_bounds_advanced(self, img_rgb: np.ndarray, img_gray: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        高级内容边界检测（多层次分析）
        
        Args:
            img_rgb: RGB图像数组
            img_gray: 灰度图像数组
            
        Returns:
            (left, top, right, bottom) 或 None
        """
        # 多种检测策略
        strategies = [
            # 策略1: 严格白色检测 (RGB所有通道都>=252)
            lambda: np.all(img_rgb >= 252, axis=2),
            # 策略2: 灰度严格检测 (>=250)
            lambda: img_gray >= 250,
            # 策略3: 近白色检测 (>=245)
            lambda: img_gray >= 245,
            # 策略4: 宽松检测 (>=240)
            lambda: img_gray >= 240
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                is_white = strategy()
                content_mask = ~is_white
                
                # 查找内容区域
                rows_with_content = np.any(content_mask, axis=1)
                cols_with_content = np.any(content_mask, axis=0)
                
                if np.any(rows_with_content) and np.any(cols_with_content):
                    # 找到有效内容，计算边界
                    top = np.argmax(rows_with_content)
                    bottom = len(rows_with_content) - np.argmax(rows_with_content[::-1]) - 1
                    left = np.argmax(cols_with_content)
                    right = len(cols_with_content) - np.argmax(cols_with_content[::-1]) - 1
                    
                    # 验证边界合理性
                    if (right - left) > 10 and (bottom - top) > 10:  # 内容区域不能太小
                        return (left, top, right, bottom)
                        
            except Exception:
                continue
        
        return None
    
    def split_pdf(self, auto_detect: bool = True, rows: int = None, cols: int = None, 
                  crop_margin: float = 0.02, auto_crop: bool = True, merge_output: bool = True,
                  separate_files: bool = False, crop_header_footer: bool = True,
                  remove_blank_pages: bool = True, optimize_output: bool = True,
                  compression_level: int = 3) -> bool:
        """
        分割整个PDF文档
        
        Args:
            auto_detect: 是否自动检测布局
            rows: 手动指定行数
            cols: 手动指定列数
            crop_margin: 裁剪边距比例
            auto_crop: 是否自动裁剪白边
            merge_output: 是否合并所有分割页面为一个PDF（默认True）
            separate_files: 是否同时保存单独的文件（默认False）
            crop_header_footer: 是否裁剪页眉页脚（默认True）
            remove_blank_pages: 是否移除空白页（默认True）
            optimize_output: 是否优化输出文件大小（默认True）
            compression_level: 压缩级别1-4，1最快4最小（默认3）
            
        Returns:
            是否成功
        """
        if not self.open_pdf():
            return False
        
        try:
            all_split_docs = []  # 存储所有分割后的文档用于合并
            total_output_pages = 0
            blank_pages_removed = 0
            
            for page_num in range(len(self.doc)):
                print(f"处理第 {page_num + 1} 页...")
                
                # 检测或使用指定的布局
                if auto_detect:
                    page_rows, page_cols = self.detect_layout(page_num)
                else:
                    page_rows, page_cols = rows or 3, cols or 2
                
                # 分割页面
                split_docs = self.split_page(page_num, page_rows, page_cols, crop_margin, crop_header_footer)
                
                # 处理分割后的页面
                for i, split_doc in enumerate(split_docs):
                    # 检查是否为空白页
                    if remove_blank_pages and self.is_blank_page(split_doc):
                        print(f"  跳过空白页: page_{page_num + 1:03d}_part_{i + 1:02d}")
                        split_doc.close()
                        blank_pages_removed += 1
                        continue
                    
                    # 自动裁剪白边
                    if auto_crop:
                        split_doc = self.auto_crop_whitespace(split_doc)
                    
                    # 如果需要合并，添加到列表中
                    if merge_output:
                        all_split_docs.append(split_doc)
                    
                    # 如果需要保存单独文件
                    if separate_files or not merge_output:
                        output_filename = f"page_{page_num + 1:03d}_part_{i + 1:02d}.pdf"
                        output_path = os.path.join(self.output_dir, output_filename)
                        
                        # 保存时使用压缩选项
                        if optimize_output:
                            split_doc.save(output_path, 
                                         garbage=4, clean=True, deflate=True,
                                         deflate_images=True, deflate_fonts=True)
                        else:
                            split_doc.save(output_path)
                        
                        print(f"  保存: {output_filename}")
                        
                        # 如果不合并，关闭文档
                        if not merge_output:
                            split_doc.close()
                    
                    total_output_pages += 1
            
            # 合并所有分割页面为一个PDF
            if merge_output and all_split_docs:
                print(f"\n正在合并 {len(all_split_docs)} 个分割页面...")
                
                if optimize_output:
                    # 使用优化合并
                    merged_doc = self.merge_documents_optimized(all_split_docs, compression_level)
                    print(f"已启用PDF优化 (压缩级别: {compression_level})")
                else:
                    # 普通合并
                    merged_doc = fitz.open()
                    for split_doc in all_split_docs:
                        merged_doc.insert_pdf(split_doc)
                
                # 在保存完成后再关闭所有分割文档
                # 注意：优化合并方法内部会处理文档关闭
                
                # 保存合并后的PDF到输出目录
                base_name = os.path.splitext(os.path.basename(self.input_path))[0]
                merged_filename = f"{base_name}_split_merged.pdf"
                merged_path = os.path.join(self.output_dir, merged_filename)
                
                # 保存时也使用压缩选项
                if optimize_output:
                    merged_doc.save(merged_path, 
                                   garbage=4, clean=True, deflate=True,
                                   deflate_images=True, deflate_fonts=True)
                else:
                    merged_doc.save(merged_path)
                
                merged_doc.close()
                
                # 现在关闭所有分割文档
                for split_doc in all_split_docs:
                    if not split_doc.is_closed:
                        split_doc.close()
                
                print(f"\n✅ 合并文件已保存: {merged_path}")
            
            print(f"\n分割完成！")
            print(f"输入页数: {len(self.doc)}")
            print(f"有效输出页数: {total_output_pages}")
            if blank_pages_removed > 0:
                print(f"移除空白页数: {blank_pages_removed}")
            print(f"输出目录: {self.output_dir}")
            
            return True
            
        except Exception as e:
            print(f"分割过程中出错: {e}")
            return False
        finally:
            self.close_pdf()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="PDF幻灯片分割工具")
    parser.add_argument("input", help="输入PDF文件路径")
    parser.add_argument("-o", "--output", help="输出目录")
    parser.add_argument("-r", "--rows", type=int, help="手动指定行数")
    parser.add_argument("-c", "--cols", type=int, help="手动指定列数")
    parser.add_argument("--no-auto-detect", action="store_true", help="禁用自动布局检测")
    parser.add_argument("--no-auto-crop", action="store_true", help="禁用自动白边裁剪")
    parser.add_argument("--crop-margin", type=float, default=0.02, help="裁剪边距比例 (默认: 0.02)")
    parser.add_argument("--no-merge", action="store_true", help="不合并输出，保存为单独文件")
    parser.add_argument("--separate-files", action="store_true", help="同时保存单独文件和合并文件")
    parser.add_argument("--no-crop-header-footer", action="store_true", help="不裁剪页眉页脚")
    parser.add_argument("--keep-blank-pages", action="store_true", help="保留空白页面")
    parser.add_argument("--no-optimize", action="store_true", help="禁用PDF文件大小优化")
    parser.add_argument("--compression-level", type=int, choices=[1,2,3,4], default=3, 
                       help="压缩级别 (1=最快, 4=最小, 默认: 3)")
    
    args = parser.parse_args()
    
    # 检查输入文件
    if not os.path.exists(args.input):
        print(f"错误: 输入文件不存在: {args.input}")
        return 1
    
    # 创建分割器
    splitter = PDFSplitter(args.input, args.output)
    
    # 执行分割
    success = splitter.split_pdf(
        auto_detect=not args.no_auto_detect,
        rows=args.rows,
        cols=args.cols,
        crop_margin=args.crop_margin,
        auto_crop=not args.no_auto_crop,
        merge_output=not args.no_merge,
        separate_files=args.separate_files,
        crop_header_footer=not args.no_crop_header_footer,
        remove_blank_pages=not args.keep_blank_pages,
        optimize_output=not args.no_optimize,
        compression_level=args.compression_level
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())