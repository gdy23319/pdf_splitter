#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF分割工具使用示例

这个脚本展示了如何在Python代码中使用PDFSplitter类的新功能
"""

import os
from pdf_splitter import PDFSplitter


def example_basic_usage():
    """基本使用示例 - 默认合并输出"""
    print("=== 基本使用示例（默认合并输出）===")
    
    # 假设有一个输入文件
    input_file = "sample_slides.pdf"
    
    if not os.path.exists(input_file):
        print(f"示例文件 {input_file} 不存在，请先准备一个PDF文件")
        return
    
    # 创建分割器
    splitter = PDFSplitter(input_file)
    
    # 执行分割（使用默认设置，默认合并为一个PDF）
    success = splitter.split_pdf()
    
    if success:
        print("✅ 分割成功！输出为合并的PDF文件")
    else:
        print("❌ 分割失败！")


def example_separate_files_mode():
    """单独文件模式示例"""
    print("\n=== 单独文件模式示例 ===")
    
    input_file = "sample_slides.pdf"
    output_dir = "separate_output"
    
    if not os.path.exists(input_file):
        print(f"示例文件 {input_file} 不存在，请先准备一个PDF文件")
        return
    
    # 创建分割器，指定输出目录
    splitter = PDFSplitter(input_file, output_dir)
    
    # 不合并，保存为单独文件
    success = splitter.split_pdf(
        merge_output=False,      # 不合并
        auto_crop=True,          # 完全裁剪白边
        crop_header_footer=True, # 裁剪页眉页脚
        remove_blank_pages=True  # 移除空白页
    )
    
    if success:
        print("✅ 单独文件分割完成！")
        print(f"📁 输出目录: {output_dir}")
    else:
        print("❌ 单独文件分割失败！")


def example_both_modes():
    """同时输出两种模式示例"""
    print("\n=== 同时输出合并文件和单独文件 ===")
    
    input_file = "sample_slides.pdf"
    output_dir = "both_output"
    
    if not os.path.exists(input_file):
        print(f"示例文件 {input_file} 不存在，请先准备一个PDF文件")
        return
    
    # 创建分割器，指定输出目录
    splitter = PDFSplitter(input_file, output_dir)
    
    # 同时保存合并文件和单独文件
    success = splitter.split_pdf(
        merge_output=True,       # 合并输出
        separate_files=True,     # 同时保存单独文件
        auto_crop=True,          # 完全裁剪白边
        crop_header_footer=True, # 裁剪页眉页脚
        remove_blank_pages=True  # 移除空白页
    )
    
    if success:
        print("✅ 双模式输出完成！")
        print(f"📁 输出目录: {output_dir}")
    else:
        print("❌ 双模式输出失败！")


def example_custom_settings():
    """自定义设置示例"""
    print("\n=== 自定义设置示例 ===")
    
    input_file = "sample_slides.pdf"
    output_dir = "custom_output"
    
    if not os.path.exists(input_file):
        print(f"示例文件 {input_file} 不存在，请先准备一个PDF文件")
        return
    
    # 创建分割器，指定输出目录
    splitter = PDFSplitter(input_file, output_dir)
    
    # 手动指定布局，保留页眉页脚，保留空白页
    success = splitter.split_pdf(
        auto_detect=False,       # 禁用自动检测
        rows=2,                  # 指定2行
        cols=3,                  # 指定3列
        crop_margin=0.03,        # 3%的裁剪边距
        auto_crop=True,          # 启用自动裁剪
        merge_output=True,       # 合并输出
        crop_header_footer=False, # 不裁剪页眉页脚
        remove_blank_pages=False  # 保留空白页
    )
    
    if success:
        print("✅ 自定义分割成功！")
        print(f"📁 输出目录: {output_dir}")
    else:
        print("❌ 自定义分割失败！")


def example_batch_processing():
    """批量处理示例"""
    print("\n=== 批量处理示例 ===")
    
    # 查找当前目录下的所有PDF文件
    pdf_files = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("当前目录下没有找到PDF文件")
        return
    
    print(f"找到 {len(pdf_files)} 个PDF文件:")
    for pdf_file in pdf_files:
        print(f"  - {pdf_file}")
    
    # 批量处理
    success_count = 0
    for pdf_file in pdf_files:
        print(f"\n处理文件: {pdf_file}")
        
        # 为每个文件创建单独的输出目录
        output_dir = f"output_{os.path.splitext(pdf_file)[0]}"
        
        splitter = PDFSplitter(pdf_file, output_dir)
        success = splitter.split_pdf(
            merge_output=True,       # 默认合并
            auto_crop=True,          # 完全裁剪白边
            crop_header_footer=True, # 裁剪页眉页脚
            remove_blank_pages=True  # 移除空白页
        )
        
        if success:
            success_count += 1
            print(f"✅ {pdf_file} 处理成功")
        else:
            print(f"❌ {pdf_file} 处理失败")
    
    print(f"\n批量处理完成: {success_count}/{len(pdf_files)} 个文件成功")


def example_layout_detection():
    """布局检测示例"""
    print("\n=== 布局检测示例 ===")
    
    input_file = "sample_slides.pdf"
    
    if not os.path.exists(input_file):
        print(f"示例文件 {input_file} 不存在，请先准备一个PDF文件")
        return
    
    # 创建分割器
    splitter = PDFSplitter(input_file)
    
    # 打开PDF
    if splitter.open_pdf():
        # 检测前几页的布局
        for page_num in range(min(3, len(splitter.doc))):
            rows, cols = splitter.detect_layout(page_num)
            print(f"第 {page_num + 1} 页检测到的布局: {rows}行 x {cols}列")
        
        splitter.close_pdf()
    else:
        print("无法打开PDF文件")


def example_advanced_cropping():
    """高级裁剪功能示例"""
    print("\n=== 高级裁剪功能示例 ===")
    
    input_file = "sample_slides.pdf"
    output_dir = "advanced_output"
    
    if not os.path.exists(input_file):
        print(f"示例文件 {input_file} 不存在，请先准备一个PDF文件")
        return
    
    # 创建分割器
    splitter = PDFSplitter(input_file, output_dir)
    
    # 使用最严格的裁剪设置
    success = splitter.split_pdf(
        auto_crop=True,          # 启用自动裁剪
        crop_margin=0.001,       # 极小边距（0.1%）
        crop_header_footer=True, # 裁剪页眉页脚
        remove_blank_pages=True, # 移除空白页
        merge_output=True        # 合并输出
    )
    
    if success:
        print("✅ 高级裁剪完成！白边已完全清除")
        print(f"📁 输出目录: {output_dir}")
    else:
        print("❌ 高级裁剪失败！")


def main():
    """主函数"""
    print("PDF分割工具使用示例")
    print("=" * 50)
    
    # 运行各种示例
    example_basic_usage()
    example_separate_files_mode()
    example_both_modes()
    example_custom_settings()
    example_batch_processing()
    example_layout_detection()
    example_advanced_cropping()
    
    print("\n" + "=" * 50)
    print("示例运行完成！")
    print("\n新功能总结：")
    print("✅ 默认合并所有分割页面为一个PDF")
    print("✅ 可选择同时输出单独文件")
    print("✅ 完全裁剪白边（几乎零边距）")
    print("✅ 自动裁剪页眉页脚（去除页码）")
    print("✅ 自动检测并移除空白页")
    print("\n提示:")
    print("1. 请确保有PDF文件在当前目录下进行测试")
    print("2. 可以修改这个脚本来适应你的具体需求")
    print("3. 查看README.md获取更多使用说明")


if __name__ == "__main__":
    main()