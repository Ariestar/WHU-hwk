#!/usr/bin/env python3
import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_run_font(run, font_east_asia="SimSun", font_ascii="Times New Roman", size_pt=10.5, bold=False, italic=False, color=(0, 0, 0)):
    run.font.name = font_ascii
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = RGBColor(*color)
    rPr = run._r.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), font_ascii)
    rFonts.set(qn('w:hAnsi'), font_ascii)
    rFonts.set(qn('w:eastAsia'), font_east_asia)
    rPr.append(rFonts)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_background(cell, color_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_table_borders_three_line(table):
    tblPr = table._tbl.tblPr
    tblBorders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
        f'  <w:bottom w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
        f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>'
        f'  <w:insideV w:val="none"/>'
        f'  <w:left w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(tblBorders)

def add_title(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(text)
    set_run_font(run, font_east_asia="SimHei", font_ascii="Arial", size_pt=18, bold=True)
    return p

def add_subtitle(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(14)
    run = p.add_run(text)
    set_run_font(run, font_east_asia="SimSun", font_ascii="Times New Roman", size_pt=12, bold=False, color=(50, 50, 50))
    return p

def add_h1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    set_run_font(run, font_east_asia="SimHei", font_ascii="Arial", size_pt=14, bold=True)
    return p

def add_h2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    set_run_font(run, font_east_asia="SimHei", font_ascii="Arial", size_pt=12, bold=True)
    return p

def add_h3(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    set_run_font(run, font_east_asia="SimHei", font_ascii="Arial", size_pt=10.5, bold=True)
    return p

def add_body(doc, text, indent=True):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.3
    p.paragraph_format.space_after = Pt(4)
    if indent:
        p.paragraph_format.first_line_indent = Pt(21)
    run = p.add_run(text)
    set_run_font(run, font_east_asia="SimSun", font_ascii="Times New Roman", size_pt=10.5)
    return p

def add_bullet(doc, text, bold_prefix=None):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.space_after = Pt(3)
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        set_run_font(r_pre, font_east_asia="SimHei", font_ascii="Arial", size_pt=10.5, bold=True)
    run = p.add_run(text)
    set_run_font(run, font_east_asia="SimSun", font_ascii="Times New Roman", size_pt=10.5)
    return p

def add_image_block(doc, img_path, caption_text):
    if not os.path.exists(img_path):
        print(f"[-] 图片缺失: {img_path}")
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run()
    run.add_picture(img_path, width=Inches(6.0))

    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_before = Pt(2)
    cap.paragraph_format.space_after = Pt(8)
    r_cap = cap.add_run(caption_text)
    set_run_font(r_cap, font_east_asia="KaiTi", font_ascii="Times New Roman", size_pt=9.5, italic=False, color=(50, 50, 50))

def main():
    root_dir = "/home/wolllf/Coding/WHU-hwk"
    doc_out = os.path.join(root_dir, "计算机系统导论_实验一_链接_实验报告.docx")
    screenshots_dir = os.path.join(root_dir, "screenshots")

    doc = Document()

    # 页面边距 2.54 cm
    for sec in doc.sections:
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin = Inches(1.0)
        sec.right_margin = Inches(1.0)

    # 标题与副标题
    add_title(doc, "计算机系统导论（下）实验报告")
    add_subtitle(doc, "实验一：链接 (Linking)")

    # 规范学生信息表（标准三线表）
    info_tbl = doc.add_table(rows=3, cols=4)
    info_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders_three_line(info_tbl)

    headers_and_data = [
        [("课程名称", True), ("计算机系统导论（下）", False), ("实验题目", True), ("实验一：链接", False)],
        [("学生姓名", True), ("刘丰源", False), ("实验地点", True), ("A237 / A238", False)],
        [("实验环境", True), ("Ubuntu 24.04 LTS (x86_64)", False), ("编译器版本", True), ("GCC 13.3.0", False)]
    ]

    for r_idx, row in enumerate(headers_and_data):
        for c_idx, (text, is_hdr) in enumerate(row):
            cell = info_tbl.cell(r_idx, c_idx)
            set_cell_margins(cell, 80, 80, 100, 100)
            if is_hdr:
                set_cell_background(cell, "F5F5F5")
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(text)
            set_run_font(run, font_east_asia="SimHei" if is_hdr else "SimSun",
                         font_ascii="Arial" if is_hdr else "Times New Roman",
                         size_pt=10, bold=is_hdr)

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # 一、实验目的
    add_h1(doc, "一、实验目的")
    add_body(doc, "1. 掌握 ELF 可重定位目标文件的内部结构，理解节头表、代码节、数据节与符号表的作用。")
    add_body(doc, "2. 掌握符号解析规则，区分全局符号、外部未定义符号与局部符号。")
    add_body(doc, "3. 掌握重定位算法的计算过程，理解 PC 相对寻址与绝对寻址在汇编指令修补中的具体执行机制。")
    add_body(doc, "4. 掌握静态库的打包、按需链接机制以及共享库在运行时的显式动态加载（dlopen/dlsym）。")
    add_body(doc, "5. 依据 ELF 文件格式规范，编写程序实现静态库打包、符号索引生成与目标文件提取（选做）。")

    # 二、实验环境
    add_h1(doc, "二、实验环境")
    add_bullet(doc, "Ubuntu 24.04 LTS (x86_64 架构)", "操作系统：")
    add_bullet(doc, "gcc 13.3.0（编译选项包括 -Og, -Wall, -c, -static, -shared, -fpic, -rdynamic, -no-pie）", "编译器：")
    add_bullet(doc, "GNU Binutils（nm, readelf, objdump, ar）", "二进制工具链：")
    add_bullet(doc, "glibc 2.39, libdl", "运行环境：")

    # 三、实验内容与步骤
    add_h1(doc, "三、实验内容与结果分析")

    # 3.1 基础实验一
    add_h2(doc, "3.1 基础实验一：目标文件、符号表与 ELF 结构分析")
    add_body(doc, "按照教材图 7.1 准备源代码 main.c 与 sum.c。main.c 中定义全局数组 array 并调用外部函数 sum 进行累加；sum.c 中实现具体的求和逻辑。")
    add_image_block(doc, os.path.join(screenshots_dir, "exp1_01_source_code.png"), "图 1-1 main.c 与 sum.c 源代码")

    add_body(doc, "执行命令 gcc -Og -Wall -c main.c sum.c 分别编译生成可重定位目标文件 main.o 与 sum.o。")
    add_image_block(doc, os.path.join(screenshots_dir, "exp1_02_gcc_compile.png"), "图 1-2 编译生成 main.o 与 sum.o 目标文件")

    add_h3(doc, "1. nm 符号表分析")
    add_body(doc, "执行 nm main.o sum.o 查看两模块导出的符号及属性：")
    add_image_block(doc, os.path.join(screenshots_dir, "exp1_03_nm_symbols.png"), "图 1-3 nm 工具查看符号表输出")
    add_body(doc, "输出结果中符号类型含义如下：")
    add_bullet(doc, "main.o 中的 array 标记为 'D'，表示位于已初始化数据段（.data）的全局变量。")
    add_bullet(doc, "main.o 中的 main 标记为 'T'，表示位于代码段（.text）的全局函数。")
    add_bullet(doc, "main.o 中的 sum 标记为 'U'，表示 Undefined（未定义符号），main.c 仅声明了该函数，由链接器在后续链接阶段从其他模块中解析。")
    add_bullet(doc, "sum.o 中的 sum 标记为 'T'，为外部模块提供全局函数定义。")

    add_h3(doc, "2. readelf -S 节头表分析")
    add_body(doc, "执行 readelf -S main.o 观察 ELF 文件的节区分布：")
    add_image_block(doc, os.path.join(screenshots_dir, "exp1_04_readelf_sections.png"), "图 1-4 readelf -S 查看 main.o 节头表")
    add_body(doc, "各主要节区属性如下：")
    add_bullet(doc, ".text (PROGBITS, AX)：存放已编译机器指令，分配内存且具备可执行权限。")
    add_bullet(doc, ".data (PROGBITS, WA)：存放已初始化的全局变量 array，分配内存且具备可写权限。")
    add_bullet(doc, ".bss (NOBITS, WA)：存放未初始化的全局变量，目标文件中不占用磁盘空间。")
    add_bullet(doc, ".symtab 与 .strtab：分别保存符号表条目与符号名称字符串池。")
    add_bullet(doc, ".rela.text (RELA)：保存代码节中外部引用的重定位条目，链接器合并代码节时依据此表修补指令操作数。")

    add_h3(doc, "3. objdump -d -r 反汇编与重定位条目分析")
    add_body(doc, "执行 objdump -d -r main.o 对 main.o 进行反汇编并显示重定位条目：")
    add_image_block(doc, os.path.join(screenshots_dir, "exp1_05_objdump_reloc.png"), "图 1-5 objdump -d -r 反汇编与重定位条目")
    add_body(doc, "反汇编指令与重定位标记对应关系如下：")
    add_bullet(doc, "偏移 0xd 处的指令为 lea 0x0(%rip), %rdi，操作数为 00 00 00 00。紧随其后的偏移 0x10 处标记了 R_X86_64_PC32 array-0x4 重定位条目。编译器在编译期填入 0 作为占位符，由链接器填入运行时相对偏移。")
    add_bullet(doc, "偏移 0x14 处的指令为 call 19 <main+0x19>，操作数为 00 00 00 00。紧随其后的偏移 0x15 处标记了 R_X86_64_PLT32 sum-0x4 重定位条目。函数跳转地址留待链接器计算并填入相对位移。")

    # 3.2 基础实验二
    add_h2(doc, "3.2 基础实验二：重定位算法推导与验证")
    add_h3(doc, "1. 重定位算法原理")
    add_body(doc, "链接器完成符号解析后，将所有输入模块的同名节合并为连续节区，并为每个符号分配运行时虚拟地址。随后依据 Elf64_Rela 结构中的 offset、symbol、type 与 addend 修补代码与数据中的引用。")
    add_body(doc, "教材图 7.10 规定的 PC 相对重定位算法为：")
    add_body(doc, "refaddr = ADDR(s) + r.offset; （引用的运行时虚拟地址）\n*refptr = (unsigned) (ADDR(r.symbol) + r.addend - refaddr);", indent=False)

    add_h3(doc, "2. 重定位条目提取与可执行文件生成")
    add_body(doc, "执行 readelf -r main.o 与 objdump -dx main.o 提取重定位条目：")
    add_image_block(doc, os.path.join(screenshots_dir, "exp2_01_objdump_main_reloc.png"), "图 2-1 提取重定位条目与节详细信息")

    add_body(doc, "执行 gcc -Og -Wall -o prog main.c sum.c 编译生成可执行文件 prog，同时使用 -no-pie 选项生成对比程序 prog_nopie。运行两个程序，退出状态码均为 3，验证了执行正确性。")
    add_image_block(doc, os.path.join(screenshots_dir, "exp2_02_compile_prog.png"), "图 2-2 编译生成可执行文件并验证运行结果")

    add_body(doc, "使用 objdump -d 反汇编观察链接器修补后的可执行文件指令：")
    add_image_block(doc, os.path.join(screenshots_dir, "exp2_03_objdump_prog_disasm.png"), "图 2-3 可执行文件反汇编指令比对")

    add_h3(doc, "3. 手工计算推导过程")
    add_body(doc, "以可执行文件 prog（PIE 模式）为例，链接器分配的运行时地址为：\nADDR(main) = 0x1129，ADDR(sum) = 0x1150，ADDR(array) = 0x4010。")
    add_body(doc, "(1) array 符号的重定位推导：\n"
                  "r.offset 为 0x10，对应 refaddr = 0x1129 + 0x10 = 0x1139。\n"
                  "r.addend 为 -4。\n"
                  "代入公式计算修补值：\n"
                  "*refptr = ADDR(array) + r.addend - refaddr = 0x4010 + (-4) - 0x1139 = 0x400c - 0x1139 = 0x2ed3。\n"
                  "对应反汇编指令：1136: 48 8d 3d d3 2e 00 00 (lea 0x2ed3(%rip), %rdi)。指令操作数字节为 d3 2e 00 00（小端序 0x00002ed3），与推导结果完全吻合。\n"
                  "CPU 执行该指令时，RIP 指向下一条指令地址 0x113d，有效地址 = 0x113d + 0x2ed3 = 0x4010，准确命中 array。")

    add_body(doc, "(2) sum 符号的重定位推导：\n"
                  "r.offset 为 0x15，对应 refaddr = 0x1129 + 0x15 = 0x113e。\n"
                  "r.addend 为 -4。\n"
                  "代入公式计算修补值：\n"
                  "*refptr = ADDR(sum) + r.addend - refaddr = 0x1150 + (-4) - 0x113e = 0x114c - 0x113e = 0x0e。\n"
                  "对应反汇编指令：113d: e8 0e 00 00 00 (call 1150 <sum>)。操作数字节为 0e 00 00 00，与推导结果一致。\n"
                  "CPU 执行 call 指令时，下一条指令地址为 0x1142，目标跳转地址 = 0x1142 + 0x0e = 0x1150，准确进入 sum 函数入口。")

    add_body(doc, "编写验证脚本 calc.py 执行自动化验算，全部推导用例均输出 PASS。")
    add_image_block(doc, os.path.join(screenshots_dir, "exp2_04_relocation_calculation.png"), "图 2-4 calc.py 自动化重定位验算通过")

    # 3.3 基础实验三
    add_h2(doc, "3.3 基础实验三：静态链接与动态链接机制")
    add_h3(doc, "1. 静态库实验")
    add_body(doc, "编写 addvec.c、multvec.c 及 vector.h。执行 gcc -c 编译各模块后，使用 ar rcs libvector.a addvec.o multvec.o 打包生成静态库。使用 ar -t 查看成员文件，使用 nm 查看包含的全部导出符号。")
    add_image_block(doc, os.path.join(screenshots_dir, "exp3_01_static_lib_build.png"), "图 3-1 静态库打包与符号表检查")

    add_body(doc, "编写 main2.c（仅调用 addvec），执行静态链接命令 gcc -static -o prog2c main2.o ./libvector.a。运行程序，正确输出 z = [4 6]。")
    add_body(doc, "执行 nm prog2c | grep -E 'addvec|multvec' 进行验证：符号表中仅存在 addvec 与 addcnt，不存在 multvec 与 multcnt。此结果验证了链接器按需提取目标模块的原则：未被引用的目标文件不参与最终链接，从而减小可执行文件体积。")
    add_image_block(doc, os.path.join(screenshots_dir, "exp3_02_static_lib_link_run.png"), "图 3-2 静态链接运行与符号按需提取验证")

    add_h3(doc, "2. 动态加载和链接共享库实验")
    add_body(doc, "使用 gcc -shared -fpic -o libvector.so addvec.c multvec.c 生成位置无关共享库。编写 dll.c，通过标准动态接口 dlopen(\"./libvector.so\", RTLD_LAZY) 在执行期加载库文件，通过 dlsym 获取 addvec 函数指针，调用后通过 dlclose 释放。")
    add_body(doc, "执行 gcc -rdynamic -o prog2r dll.c -ldl 编译并运行，输出计算结果 z = [4 6]。")
    add_image_block(doc, os.path.join(screenshots_dir, "exp3_03_dynamic_lib_build_run.png"), "图 3-3 共享库生成与动态加载测试")

    add_h3(doc, "3. ldd 工具对比分析")
    add_body(doc, "使用 ldd 命令对比分析 prog2c 与 prog2r：\n"
                  "prog2c 输出 'not a dynamic executable'，表明静态链接已将所需库函数全部合并进目标文件，运行时脱离动态链接器独立执行。\n"
                  "prog2r 显示依赖 libc.so.6 与动态装载器 ld-linux-x86-64.so.2，其依赖列表中不包含 libvector.so。libvector.so 由程序在运行期通过 dlopen 系统调用显式映射进进程地址空间。")
    add_image_block(doc, os.path.join(screenshots_dir, "exp3_04_ldd_analysis.png"), "图 3-4 ldd 工具分析依赖对比")

    # 3.4 进阶实验四
    add_h2(doc, "3.4 进阶实验四：简易静态库打包工具 mylib 的实现与测试（选做）")
    add_h3(doc, "1. 设计目标与规范")
    add_body(doc, "编写 C 语言程序 mylib，模拟 ar 与 ranlib 的功能。要求能够遍历目标文件、解析 ELF 符号表、提取全局符号并生成包含符号索引表的 .a 归档文件，同时支持 -t 列出文件与 -x 提取文件。")
    add_body(doc, "实现要点如下：")
    add_bullet(doc, "严格遵循 Unix/GNU ar 格式标准：首部写入 8 字节魔数 '!<arch>\\n'，成员头部使用 60 字节 struct ar_hdr，保持 2 字节对齐。")
    add_bullet(doc, "ELF 符号解析：利用 /usr/include/elf.h 读取 Elf64_Ehdr 与 Elf64_Shdr，定位 SHT_SYMTAB 节与 SHT_STRTAB 节。遍历符号表，提取绑定属性为 STB_GLOBAL 或 STB_WEAK 且有效定义（st_shndx != SHN_UNDEF）的全局函数与全局变量。")
    add_bullet(doc, "生成符号索引表：在归档首部生成名称为 '/' 的特殊成员，内容包括符号总数（大端序 uint32_t）、所属文件偏移数组（大端序 uint32_t 数组）及符号名字符串池。")
    add_bullet(doc, "支持 -c（打包）、-t（列表）、-x（解压提取）与 -s（打印符号索引）选项。")

    add_image_block(doc, os.path.join(screenshots_dir, "exp4_01_mylib_source.png"), "图 4-1 mylib 工具编译构建")

    add_h3(doc, "2. 打包与符号索引构建测试")
    add_body(doc, "设计测试模块 test1.c（包含 math_add, g_counter1）与 test2.c（包含 math_sub, g_counter2）。执行 ./mylib -c libtest.a test1.o test2.o，程序成功解析 ELF 节区并完成静态库打包。")
    add_image_block(doc, os.path.join(screenshots_dir, "exp4_02_mylib_pack_and_index.png"), "图 4-2 mylib 打包静态库并构建符号索引")

    add_h3(doc, "3. 列表展示与目标文件提取测试")
    add_body(doc, "执行 ./mylib -t libtest.a 查看成员列表，执行 ./mylib -s libtest.a 输出符号到文件偏移的映射关系。")
    add_image_block(doc, os.path.join(screenshots_dir, "exp4_03_mylib_list_t.png"), "图 4-3 mylib -t 与 -s 选项执行结果")

    add_body(doc, "删除磁盘中的 test1.o 后，执行 ./mylib -x libtest.a test1.o，成功从归档文件中还原出目标文件。")
    add_image_block(doc, os.path.join(screenshots_dir, "exp4_04_mylib_extract_x.png"), "图 4-4 mylib -x 解压提取目标文件")

    add_h3(doc, "4. GNU 工具链兼容性验证")
    add_body(doc, "调用系统内置 GNU 工具对 mylib 生成的 libtest.a 进行交叉检验：\n"
                  "1. ar -t libtest.a 正常列出库成员。\n"
                  "2. nm libtest.a 直接读取 mylib 生成的符号索引并列出各全局符号。\n"
                  "3. 编写 main_test.c 调用 math_add 与 math_sub，执行 gcc -o test_prog main_test.c ./libtest.a 成功完成链接，运行 ./test_prog 输出预期结果。")
    add_image_block(doc, os.path.join(screenshots_dir, "exp4_05_mylib_compatibility.png"), "图 4-5 GNU 工具链兼容性验证全通过")

    # 四、实验总结
    add_h1(doc, "四、实验总结")
    add_body(doc, "本次实验完成了链接过程的理论分析与实践验证，主要总结如下：")
    add_body(doc, "1. 深入掌握了 ELF 文件的组织方式，明确了代码段、数据段、符号表与重定位表的映射关系。符号解析阶段链接器通过符号表协调全局符号的定义与外部引用。")
    add_body(doc, "2. 完整验证了重定位算法的运算逻辑。PC 相对寻址机制中操作数表示相对于下一条指令的位移量，计算中引入 -4 修正项抵消了操作数自身占据的 4 字节偏移。手工推导数据与可执行文件的反汇编机器码完全一致。")
    add_body(doc, "3. 明确了静态库与动态库的运行特性。静态库在链接期按需合并目标模块，动态共享库支持运行时按需加载，两类机制在空间占用与部署灵活性方面各有适用场景。")
    add_body(doc, "4. 独立实现了符合工业标准的静态库打包工具 mylib，掌握了底层二进制头结构解析、字节序转换以及归档索引表的构建方法，加深了对系统底层链接机制的理解。")

    doc.save(doc_out)
    print(f"[+] 规范学术格式 Word 实验报告生成成功: {doc_out} (大小: {os.path.getsize(doc_out)} 字节)")

if __name__ == "__main__":
    main()
