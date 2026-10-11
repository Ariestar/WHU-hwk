#!/usr/bin/env python3
import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, color_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_heading_1(doc, text):
    h = doc.add_heading(text, level=1)
    h.paragraph_format.space_before = Pt(16)
    h.paragraph_format.space_after = Pt(6)
    h.paragraph_format.keep_with_next = True
    for run in h.runs:
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = RGBColor(31, 78, 121)
    return h

def add_heading_2(doc, text):
    h = doc.add_heading(text, level=2)
    h.paragraph_format.space_before = Pt(12)
    h.paragraph_format.space_after = Pt(4)
    h.paragraph_format.keep_with_next = True
    for run in h.runs:
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = RGBColor(47, 85, 151)
    return h

def add_heading_3(doc, text):
    h = doc.add_heading(text, level=3)
    h.paragraph_format.space_before = Pt(8)
    h.paragraph_format.space_after = Pt(3)
    h.paragraph_format.keep_with_next = True
    for run in h.runs:
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = RGBColor(68, 114, 196)
    return h

def add_paragraph(doc, text, bold_prefix=None):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.space_after = Pt(4)
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.bold = True
        r_pre.font.size = Pt(10.5)
        r_pre.font.color.rgb = RGBColor(38, 38, 38)
    r = p.add_run(text)
    r.font.size = Pt(10.5)
    r.font.color.rgb = RGBColor(51, 51, 51)
    return p

def add_code_block(doc, code_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F6F8FA")
    set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(code_text)
    run.font.name = "Courier New"
    run.font.size = Pt(9.5)
    run.font.color.rgb = RGBColor(36, 41, 47)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_image_with_caption(doc, img_path, caption_text):
    if not os.path.exists(img_path):
        print(f"[-] 图片不存在: {img_path}")
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run()
    run.add_picture(img_path, width=Inches(6.0))

    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_before = Pt(0)
    cap.paragraph_format.space_after = Pt(8)
    r_cap = cap.add_run(caption_text)
    r_cap.font.size = Pt(9.5)
    r_cap.font.italic = True
    r_cap.font.color.rgb = RGBColor(89, 89, 89)

def main():
    root_dir = "/home/wolllf/Coding/WHU-hwk"
    doc_out = os.path.join(root_dir, "计算机系统导论_实验一_链接_实验报告.docx")
    screenshots_dir = os.path.join(root_dir, "screenshots")

    doc = Document()

    # 页面边距设置 (2.54cm)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # 1. 标题
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_p.paragraph_format.space_before = Pt(12)
    title_p.paragraph_format.space_after = Pt(4)
    r_title = title_p.add_run("计算机系统导论（下）上机实验一：链接")
    r_title.bold = True
    r_title.font.size = Pt(22)
    r_title.font.color.rgb = RGBColor(31, 78, 121)

    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_p.paragraph_format.space_after = Pt(16)
    r_sub = sub_p.add_run("实验报告与原理分析（基础实验 1-3 & 进阶选做实验 4）")
    r_sub.font.size = Pt(14)
    r_sub.font.color.rgb = RGBColor(89, 89, 89)

    # 信息表格
    info_tbl = doc.add_table(rows=2, cols=4)
    info_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    info_data = [
        [("课程名称", True), ("计算机系统导论（下）", False), ("实验名称", True), ("实验一：链接 (Linking)", False)],
        [("学生姓名", True), ("Ariestar", False), ("实验环境", True), ("Ubuntu 24.04 LTS (x86_64)", False)]
    ]
    for r_idx, row in enumerate(info_data):
        for c_idx, (text, is_hdr) in enumerate(row):
            cell = info_tbl.cell(r_idx, c_idx)
            set_cell_margins(cell, 80, 80, 100, 100)
            if is_hdr:
                set_cell_background(cell, "EBF1F5")
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(text)
            run.font.size = Pt(10)
            run.bold = is_hdr
            run.font.color.rgb = RGBColor(31, 78, 121) if is_hdr else RGBColor(51, 51, 51)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 一、实验目的与背景
    add_heading_1(doc, "一、实验目的与背景")
    add_paragraph(doc, "链接（Linking）是将各种代码和数据片段收集并组合成为一个单一文件的过程，这个文件可被加载（复制）到内存并执行。链接可以执行于编译时（compile time）、加载时（load time）以及运行时（run time）。理解链接器的工作机制对于构造大型程序、避免难以排查的运行时错误、理解作用域以及共享库动态加载机制具有核心意义。")
    add_paragraph(doc, "本次实验对应《深入理解计算机系统》（CS:APP 3e）第七章“链接”，通过系统实践深入探究以下核心内容：")
    add_paragraph(doc, "1. 观察并分析可重定位目标文件（ELF 格式）的节区结构、符号表及重定位条目。\n"
                      "2. 掌握重定位的核心算法，基于重定位条目与符号地址手动推导重定位修补值，并与编译器生成的实际指令进行完全验算。\n"
                      "3. 掌握静态库的构建与按需链接机制，以及基于 dlopen/dlsym 的共享库运行时动态加载机制。\n"
                      "4. （进阶选做）自主设计并实现简易静态库打包工具 mylib，深入底层解析 ELF 符号表并生成符合标准规范的归档索引表。")

    # 二、基础实验 1
    add_heading_1(doc, "二、基础实验1：观察目标文件、符号表与 ELF 结构")
    add_heading_2(doc, "1. 实验代码准备")
    add_paragraph(doc, "按照教材图 7.1，编写两个 C 语言源文件 main.c 与 sum.c：")
    add_paragraph(doc, "• main.c：定义全局已初始化数组 array[2] = {1, 2}，在 main 函数中调用外部函数 sum(array, 2) 并返回求和结果。\n"
                      "• sum.c：实现 sum 函数，遍历数组并累加元素求和。")
    add_image_with_caption(doc, os.path.join(screenshots_dir, "exp1_01_source_code.png"), "图 1-1：main.c 与 sum.c 源代码展示")

    add_heading_2(doc, "2. 编译生成可重定位目标文件")
    add_paragraph(doc, "使用 gcc -Og -Wall -c main.c sum.c 分别编译生成可重定位目标文件 main.o 和 sum.o：")
    add_image_with_caption(doc, os.path.join(screenshots_dir, "exp1_02_gcc_compile.png"), "图 1-2：编译生成 main.o 与 sum.o 目标文件")

    add_heading_2(doc, "3. nm 工具查看符号表与符号解析分析")
    add_paragraph(doc, "执行 nm main.o sum.o 观察两个模块的符号表：")
    add_image_with_caption(doc, os.path.join(screenshots_dir, "exp1_03_nm_symbols.png"), "图 1-3：nm 工具查看目标文件符号表")
    add_paragraph(doc, "【符号表输出分析】：\n"
                      "• main.o 中的 array：类型标识为 'D'，表示该符号是已初始化的全局数据变量（位于 .data 节），在 main.o 中被定义。\n"
                      "• main.o 中的 main：类型标识为 'T'，表示全局函数代码符号（位于 .text 节），在 main.o 中被定义。\n"
                      "• main.o 中的 sum：类型标识为 'U'，表示 Undefined（未定义外部符号）。main.c 仅声明了 sum 但未在此模块中定义，必须由链接器在后续链接阶段从其他模块（sum.o）中进行符号解析解析定位。\n"
                      "• sum.o 中的 sum：类型标识为 'T'，表示全局函数代码符号，为外部模块提供了符号定义。")

    add_heading_2(doc, "4. readelf -S 查看节头表（Section Headers）")
    add_paragraph(doc, "执行 readelf -S main.o 观察 ELF 节区结构与属性：")
    add_image_with_caption(doc, os.path.join(screenshots_dir, "exp1_04_readelf_sections.png"), "图 1-4：readelf -S 查看 main.o 的节头表")
    add_paragraph(doc, "【核心节区说明】：\n"
                      "1. .text (PROGBITS, AX)：存放已编译的机器代码指令。Flags 为 AX (Allocated + Executable)，表示程序运行时需要分配内存且具有可执行权限。\n"
                      "2. .data (PROGBITS, WA)：存放已初始化的全局变量（如 array[2]）。Flags 为 WA (Writable + Allocated)，具有读写与内存分配权限。\n"
                      "3. .bss (NOBITS, WA)：存放未初始化的全局/静态变量。在目标文件中不占用实际磁盘空间（NOBITS），仅在运行时占内存。\n"
                      "4. .symtab (SYMTAB)：符号表，记录程序中定义和引用的所有函数与全局变量信息。\n"
                      "5. .strtab (STRTAB)：字符串表，存放符号名和节名对应的具体字符串文本。\n"
                      "6. .rela.text (RELA, I)：包含 .text 节的重定位条目列表。链接器将各目标文件合并时，利用该节的信息修补代码中的外部引用。")

    add_heading_2(doc, "5. objdump -d -r 反汇编与重定位条目解析")
    add_paragraph(doc, "执行 objdump -d -r main.o 对 main.o 进行反汇编并同步显示关联的重定位条目：")
    add_image_with_caption(doc, os.path.join(screenshots_dir, "exp1_05_objdump_reloc.png"), "图 1-5：objdump -d -r 反汇编与重定位条目")
    add_paragraph(doc, "【反汇编指令与重定位标记分析】：\n"
                      "• 偏移 0xd 处的指令：lea 0x0(%rip), %rdi，机器码为 48 8d 3d 00 00 00 00。紧随其后的偏移 0x10 处标记了重定位条目 R_X86_64_PC32 array-0x4。因为编译时 array 的实际虚拟地址未知，编译器在此处暂时填入 00 00 00 00 占位，并指示链接器在链接时修补该 4 字节偏移。\n"
                      "• 偏移 0x14 处的指令：call 19 <main+0x19>，机器码为 e8 00 00 00 00。紧随其后的偏移 0x15 处标记了重定位条目 R_X86_64_PLT32 sum-0x4。同样，sum 的目标跳转地址在编译时未知，编译器用 00 00 00 00 占位，留待链接器计算并填入正确的相对偏移量。")

    # 三、基础实验 2
    add_heading_1(doc, "三、基础实验2：重定位算法推导与验证")
    add_heading_2(doc, "1. 重定位算法原理（教材图 7.10）")
    add_paragraph(doc, "链接器在符号解析完成后执行重定位（Relocation）：首先将所有输入目标文件中的同类型节合并为一个大节，并为每个节和符号分配运行时虚拟地址；随后依据重定位条目修改代码节和数据节中所有对符号的引用。")
    add_paragraph(doc, "ELF 64 位标准重定位条目结构为 Elf64_Rela，包含：\n"
                      "• r.offset：需要被修改的引用在当前节中的字节偏移量。\n"
                      "• r.symbol：被引用的符号。\n"
                      "• r.type：重定位类型（如 PC 相对寻址 R_X86_64_PC32 或绝对寻址 R_X86_64_32）。\n"
                      "• r.addend：符号偏移调整量（加数）。")
    add_paragraph(doc, "根据 CS:APP 图 7.10，重定位计算算法如下：\n"
                      "1. 计算引用的运行时虚拟地址：refaddr = ADDR(s) + r.offset；\n"
                      "2. 若重定位类型为 PC 相对引用（R_X86_64_PC32 / R_X86_64_PLT32）：\n"
                      "   *refptr = (unsigned) (ADDR(r.symbol) + r.addend - refaddr)；\n"
                      "3. 若重定位类型为绝对引用（R_X86_64_32）：\n"
                      "   *refptr = (unsigned) (ADDR(r.symbol) + r.addend)。")

    add_heading_2(doc, "2. 提取重定位条目与符号地址")
    add_paragraph(doc, "使用 readelf -r main.o 和 objdump -dx main.o 提取重定位条目信息：")
    add_image_with_caption(doc, os.path.join(screenshots_dir, "exp2_01_objdump_main_reloc.png"), "图 2-1：提取 main.o 的重定位条目详细信息")
    add_paragraph(doc, "重定位条目明细：\n"
                      "• 条目 1 (array)：offset = 0x10, type = R_X86_64_PC32, symbol = array, addend = -4 (-0x4)。\n"
                      "• 条目 2 (sum)：offset = 0x15, type = R_X86_64_PLT32, symbol = sum, addend = -4 (-0x4)。")

    add_heading_2(doc, "3. 编译生成可执行文件与符号地址确认")
    add_paragraph(doc, "编译生成可执行文件 prog（默认 PIE）以及 prog_nopie（指定 -no-pie）：")
    add_image_with_caption(doc, os.path.join(screenshots_dir, "exp2_02_compile_prog.png"), "图 2-2：编译生成可执行文件并验证运行结果（返回状态码 3）")
    add_paragraph(doc, "通过 objdump -d 反汇编观察链接器合并节区并完成重定位修补后的可执行文件：")
    add_image_with_caption(doc, os.path.join(screenshots_dir, "exp2_03_objdump_prog_disasm.png"), "图 2-3：可执行文件 main 函数反汇编对比")

    add_heading_2(doc, "4. 手动重定位计算推导与精确验算")
    add_paragraph(doc, "【推导验证 1：PIE 模式可执行文件 prog】\n"
                      "在 prog 中，符号分配的运行时虚拟基地址为：\n"
                      "• ADDR(main) = 0x1129\n"
                      "• ADDR(sum)  = 0x1150\n"
                      "• ADDR(array) = 0x4010\n\n"
                      "(1) 对 array 符号的 PC 相对重定位：\n"
                      "• 引用在 main 中的偏移为 0x10，因此 refaddr = ADDR(main) + 0x10 = 0x1129 + 0x10 = 0x1139；\n"
                      "• r.addend = -4；\n"
                      "• 代入公式：*refptr = ADDR(array) + r.addend - refaddr = 0x4010 + (-4) - 0x1139 = 0x400C - 0x1139 = 0x2ED3；\n"
                      "• 反汇编指令为：1136: 48 8d 3d d3 2e 00 00 (lea 0x2ed3(%rip), %rdi)。机器码偏移字段为 d3 2e 00 00（小端序 0x00002ed3），与手动推导完全一致！\n"
                      "• 寻址验证：下一条指令地址 (0x113d) + 0x2ed3 = 0x4010 = ADDR(array)，精准命中 array！\n\n"
                      "(2) 对 sum 符号的 PC 相对重定位：\n"
                      "• 引用在 main 中的偏移为 0x15，因此 refaddr = ADDR(main) + 0x15 = 0x1129 + 0x15 = 0x113E；\n"
                      "• r.addend = -4；\n"
                      "• 代入公式：*refptr = ADDR(sum) + r.addend - refaddr = 0x1150 + (-4) - 0x113E = 0x114C - 0x113E = 0x0E；\n"
                      "• 反汇编指令为：113d: e8 0e 00 00 00 (call 1150 <sum>)。机器码偏移字段为 0e 00 00 00（小端序 0x0e），与手动推导完全一致！\n"
                      "• 寻址验证：call 指令下一条指令地址 (0x1142) + 0x0e = 0x1150 = ADDR(sum)，精准跳转至 sum 入口！")

    add_paragraph(doc, "【推导验证 2：非 PIE 模式可执行文件 prog_nopie】\n"
                      "在 prog_nopie 中，符号基地址分配为经典静态地址空间：\n"
                      "• ADDR(main) = 0x401106, ADDR(sum) = 0x401130, ADDR(array) = 0x404010。\n"
                      "• array 处 refaddr = 0x401106 + 0x10 = 0x401116。计算值 = 0x404010 - 4 - 0x401116 = 0x2EF6。\n"
                      "  指令机器码：48 8d 3d f6 2e 00 00，完全一致！\n"
                      "• sum 处 refaddr = 0x401106 + 0x15 = 0x40111B。计算值 = 0x401130 - 4 - 0x40111B = 0x11。\n"
                      "  指令机器码：e8 11 00 00 00，完全一致！")

    add_image_with_caption(doc, os.path.join(screenshots_dir, "exp2_04_relocation_calculation.png"), "图 2-4：编写自动化验算脚本 calc.py 执行重定位数学推导全通过")

    # 四、基础实验 3
    add_heading_1(doc, "四、基础实验3：静态链接与动态链接")
    add_heading_2(doc, "1. 静态库实验（教材图 7.6 ~ 7.8）")
    add_paragraph(doc, "静态库（Archive 文件，以 .a 为后缀）是将多个可重定位目标文件打包在一起的集合。链接时，链接器仅复制被应用程序引用的目标模块，极大节约了可执行文件的空间。")
    add_paragraph(doc, "实验步骤：\n"
                      "1. 编写向量加法 addvec.c、向量乘法 multvec.c 以及接口头文件 vector.h；\n"
                      "2. 编译目标文件并使用 ar 工具打包：ar rcs libvector.a addvec.o multvec.o；\n"
                      "3. 使用 ar -t 查看库内成员文件，使用 nm 查看库中包含的所有符号。")
    add_image_with_caption(doc, os.path.join(screenshots_dir, "exp3_01_static_lib_build.png"), "图 3-1：打包静态库并查看库中包含的目标文件与符号")

    add_paragraph(doc, "编写主程序 main2.c（仅调用了 addvec），并执行静态链接：\n"
                      "gcc -c main2.c\n"
                      "gcc -static -o prog2c main2.o ./libvector.a\n"
                      "运行可执行文件输出正确计算结果：z = [4 6]。")
    add_paragraph(doc, "【静态库符号按需解析验证】：\n"
                      "执行 nm prog2c | grep -E 'addvec|multvec'，发现输出中仅包含 addvec 和 addcnt，而 multvec 和 multcnt 完全不存在。这证明了链接器对静态库的处理原则：从左至右扫描，只拷贝真正被引用的目标文件（addvec.o），未被引用的文件（multvec.o）被直接丢弃，不占用最终可执行文件体积。")
    add_image_with_caption(doc, os.path.join(screenshots_dir, "exp3_02_static_lib_link_run.png"), "图 3-2：静态库链接、运行输出及按需拷贝机制验证")

    add_heading_2(doc, "2. 动态加载和链接共享库实验（教材图 7.17）")
    add_paragraph(doc, "共享库（Shared Library，在 Linux 下为 .so 文件）支持在运行时由应用程序显式加载并动态链接，无需在编译期将库绑定到可执行文件中。Linux 提供了动态链接加载器接口：\n"
                      "• dlopen()：打开并加载指定的共享库文件；\n"
                      "• dlsym()：根据符号名称字符串查找函数或变量的虚拟地址；\n"
                      "• dlerror()：返回最近一次调用动态链接 API 发生的错误字符串；\n"
                      "• dlclose()：卸载共享库。")
    add_paragraph(doc, "实验步骤：\n"
                      "1. 使用 -shared -fpic 选项生成位置无关代码的共享库：gcc -shared -fpic -o libvector.so addvec.c multvec.c；\n"
                      "2. 编写 dll.c，使用 dlopen(\"./libvector.so\", RTLD_LAZY) 加载共享库，通过 dlsym 获取 addvec 函数指针并调用；\n"
                      "3. 编译可执行文件：gcc -rdynamic -o prog2r dll.c -ldl；\n"
                      "4. 执行 ./prog2r，成功输出结果：z = [4 6]。")
    add_image_with_caption(doc, os.path.join(screenshots_dir, "exp3_03_dynamic_lib_build_run.png"), "图 3-3：共享库编译与运行时动态加载 (dlopen/dlsym)")

    add_heading_2(doc, "3. ldd 工具对比分析")
    add_paragraph(doc, "使用 ldd 命令分别分析 prog2c 与 prog2r：\n"
                      "• prog2c：输出 'not a dynamic executable'。表明由于采用了静态链接，所有依赖库代码（包括 C 运行时库）均已固化在程序内部，运行时无需任何动态链接器支持。\n"
                      "• prog2r：显示依赖 libc.so.6 与 ld-linux-x86-64.so.2，但是依赖列表中并无 libvector.so！这证明 libvector.so 并非编译时强制依赖，而是在程序运行到 dlopen 语句时才被按需动态装载进进程地址空间，适用于插件化架构与热更新。")
    add_image_with_caption(doc, os.path.join(screenshots_dir, "exp3_04_ldd_analysis.png"), "图 3-4：ldd 工具对比分析静态可执行文件与动态可执行文件")

    # 五、进阶实验 4
    add_heading_1(doc, "五、进阶实验4：实现简易静态库打包工具 mylib（选做）")
    add_heading_2(doc, "1. 设计目标与规范")
    add_paragraph(doc, "进阶实验要求自主实现一个 C 语言程序 mylib，能够遍历当前目录下的所有 .o 目标文件，解析其符号表并打包生成类似 ar 命令生成的静态库 .a 文件，同时生成符号索引表（ranlib 机制），并提供 -t 列出库成员和 -x 解压目标文件的功能。")
    add_paragraph(doc, "【核心实现规范】：\n"
                      "1. 归档格式规范：严格遵循 Unix/GNU ar 格式规范，以 8 字节魔数 '!<arch>\\n' 开头，各成员文件前均包含 60 字节的 struct ar_hdr（文件名、修改时间、UID、GID、权限模态、文件大小及 '`\\n' 结束符），保证 2 字节对齐。\n"
                      "2. ELF 符号解析：直接引入 /usr/include/elf.h，解析 ELF64 头部（Elf64_Ehdr）、节头表（Elf64_Shdr），定位符号表 .symtab 与字符串表 .strtab。筛选绑定属性为 STB_GLOBAL 或 STB_WEAK 且有效定义（st_shndx != SHN_UNDEF）的全局函数与全局变量。\n"
                      "3. 符号索引表生成（Ranlib 索引）：将符号索引作为归档文件的第一个成员，成员名规范为 '/               '。索引数据区存放符号总数（大端序 uint32_t）、各符号所属目标文件在归档内的文件偏移量列表（大端序 uint32_t 数组），以及紧随其后的 null 结尾符号名称字符串池。\n"
                      "4. 命令行交互设计：\n"
                      "   • mylib -c <lib.a> [file.o ...]：打包目标文件（未指定时自动通过 opendir 扫描当前目录下 *.o）；\n"
                      "   • mylib -t <lib.a>：列出库中所有成员、大小、权限与时间；\n"
                      "   • mylib -x <lib.a> [file.o]：提取并解压指定目标文件；\n"
                      "   • mylib -s <lib.a>：格式化打印符号索引表（符号名到归档文件偏移映射）。")

    add_heading_2(doc, "2. 编译与模块结构")
    add_paragraph(doc, "设计测试模块 test1.c（提供全局变量 g_counter1 与函数 math_add）和 test2.c（提供全局变量 g_counter2 与函数 math_sub），编译生成 mylib 工具及测试目标文件：")
    add_image_with_caption(doc, os.path.join(screenshots_dir, "exp4_01_mylib_source.png"), "图 4-1：mylib 工具编译构建过程")

    add_heading_2(doc, "3. 打包生成静态库与符号索引构建")
    add_paragraph(doc, "执行 ./mylib -c libtest.a test1.o test2.o，程序自动打开 ELF 目标文件并遍历节区符号表，成功提取全部全局符号并生成包含 ranlib 符号索引的静态库 libtest.a：")
    add_image_with_caption(doc, os.path.join(screenshots_dir, "exp4_02_mylib_pack_and_index.png"), "图 4-2：mylib 提取全局符号并生成静态库 libtest.a")

    add_heading_2(doc, "4. 库成员列表 (-t) 与符号索引查看 (-s)")
    add_paragraph(doc, "执行 ./mylib -t libtest.a 列出库内包含的目标文件信息，执行 ./mylib -s libtest.a 打印详细的符号到文件偏移映射关系：")
    add_image_with_caption(doc, os.path.join(screenshots_dir, "exp4_03_mylib_list_t.png"), "图 4-3：mylib -t 列出库成员与 -s 查看符号索引表")

    add_heading_2(doc, "5. 提取指定目标文件 (-x)")
    add_paragraph(doc, "先删除本地的 test1.o，随后执行 ./mylib -x libtest.a test1.o。mylib 成功定位到库中对应成员，并将二进制数据还原写回到磁盘中：")
    add_image_with_caption(doc, os.path.join(screenshots_dir, "exp4_04_mylib_extract_x.png"), "图 4-4：mylib -x 从静态库中提取指定目标文件")

    add_heading_2(doc, "6. 与 GNU 官方工具链完全兼容性验证")
    add_paragraph(doc, "为了严格验证 mylib 生成的静态库是否完全符合工业标准，直接调用系统内置的 GNU 官方工具进行交叉验证：\n"
                      "1. 使用官方 ar -t libtest.a：完美识别库成员，准确列出 test1.o 与 test2.o；\n"
                      "2. 使用官方 nm libtest.a：直接利用 mylib 构建的符号索引，正确打印各模块的全局符号；\n"
                      "3. 使用官方 gcc 链接测试程序：gcc -o test_prog main_test.c ./libtest.a。链接过程无任何警告与错误，运行 ./test_prog 正确输出累加与计算结果！")
    add_image_with_caption(doc, os.path.join(screenshots_dir, "exp4_05_mylib_compatibility.png"), "图 4-5：GNU ar、nm 与 gcc 链接运行完全兼容性测试通过")

    # 六、实验总结与心得体会
    add_heading_1(doc, "六、实验总结与心得体会")
    add_paragraph(doc, "通过本次计算机系统导论“链接”实验，我们全面且系统地探索了编译系统底层的链接机制，获得了以下深刻认识：\n"
                      "1. 深刻理解了 ELF 目标文件结构：掌握了 .text, .data, .bss, .symtab, .rela.text 等关键节区在编译与链接中的角色，理解了符号解析如何匹配未定义符号（'U'）与全局定义符号（'T'/'D'）。\n"
                      "2. 掌握了重定位的本质与计算细节：通过手动推导与验算，彻底掌握了 PC 相对寻址（R_X86_64_PC32 / R_X86_64_PLT32）为何需要引入 addend = -4 以及减去 refaddr 的物理意义（因 PC 指针总是指向下一条指令的起始地址）；清晰认识到了 PIE 与非 PIE 地址空间的布局差异。\n"
                      "3. 厘清了静态链接与动态链接的应用场景：验证了静态库的“按需链接”机制，理解了其为何能减小代码冗余；掌握了 dlopen/dlsym 的运行时动态加载原理，体会到现代软件插件架构与热更新的底层基石。\n"
                      "4. 进阶实现了简易打包工具 mylib：通过直接与 /usr/include/elf.h 与 ar.h 打交道，亲自解析节头、符号表以及大端序索引构建，不仅加深了对二进制文件格式的敬畏与理解，更通过了 GNU 官方工具的严格兼容测试，大幅提升了系统级底层编程能力。")

    doc.save(doc_out)
    print(f"[+] Word 实验报告生成成功: {doc_out} (大小: {os.path.getsize(doc_out)} 字节)")

if __name__ == "__main__":
    main()
