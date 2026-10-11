# WHU-hwk: 计算机系统导论（下）上机实验一：链接

武汉大学《计算机系统导论（下）》课程上机实验一（链接 Linking）完整实现工程、原理分析、截图集与实验报告。

---

## 📄 产物文档

- **Word 实验报告**：[`计算机系统导论_实验一_链接_实验报告.docx`](计算机系统导论_实验一_链接_实验报告.docx) （已插入全套 18 张高清晰终端实验截图）
- **Markdown 在线报告**：[`REPORT.md`](REPORT.md)
- **原始实验要求**：[`93111149e80526ba6426869b8d8f332c.docx`](93111149e80526ba6426869b8d8f332c.docx)

---

## 📁 目录结构

```text
.
├── 93111149e80526ba6426869b8d8f332c.docx   # 原始实验要求文档
├── 计算机系统导论_实验一_链接_实验报告.docx   # 完整实验报告 Word 版（含所有高清截图）
├── REPORT.md                                # 完整实验报告 Markdown 版
├── README.md                                # 项目说明与快速上手
├── Makefile                                 # 顶层 Makefile，支持一键构建与测试
├── lab1/                                    # 基础实验 1：观察目标文件、符号表与 ELF 结构
│   ├── main.c                               # 教材图 7.1 主程序
│   ├── sum.c                                # 教材图 7.1 求和函数
│   └── Makefile                             # 构建规则
├── lab2/                                    # 基础实验 2：重定位算法推导与验证
│   ├── main.c
│   ├── sum.c
│   ├── calc.py                              # 重定位算法自动化验算与推导脚本
│   └── Makefile
├── lab3/                                    # 基础实验 3：静态链接与动态链接
│   ├── addvec.c                             # 教材图 7.6 向量加法
│   ├── multvec.c                            # 教材图 7.6 向量乘法
│   ├── vector.h                             # 头文件
│   ├── main2.c                              # 静态链接调用主程序
│   ├── dll.c                                # 运行时 dlopen 动态加载共享库主程序
│   └── Makefile
├── lab4/                                    # 进阶实验 4：简易静态库打包工具 mylib（选做）
│   ├── mylib.c                              # ELF 符号解析与归档索引打包工具实现
│   ├── test1.c                              # 测试模块 1
│   ├── test2.c                              # 测试模块 2
│   ├── main_test.c                          # 兼容性测试主程序
│   └── Makefile
├── screenshots/                             # 实验全过程高清终端截图 (18 张)
└── scripts/                                 # 报告与截图自动化生成脚本
    ├── render_screenshot.py                 # 高清终端视窗渲染脚本
    ├── make_all_screenshots.py              # 全流程截图批量生成脚本
    └── generate_docx_report.py              # Word 实验报告生成脚本
```

---

## 🚀 快速开始与实验复现

### 1. 一键编译所有实验目标

```bash
make
```

### 2. 一键运行所有实验与测试用例

```bash
make test
```

测试包含：
- Lab 1 目标文件与可执行文件生成及运行测试（返回值状态码 3）
- Lab 2 重定位算法手动推导与自动化数学验算脚本 `calc.py`
- Lab 3 静态链接可执行文件 `prog2c` 与动态运行时加载 `prog2r` 运行验证（输出 `z = [4 6]`）
- Lab 4 自研 `mylib` 工具打包、成员列表查看、符号索引表导出、目标文件解压，以及 GCC 链接自研静态库并成功运行

### 3. 一键清理构建产物

```bash
make clean
```

### 4. 重新生成全套截图与 Word 实验报告

```bash
# 批量运行并捕获 18 张终端截图
uv run --with pillow python3 scripts/make_all_screenshots.py

# 重新生成 Word 实验报告
uv run --with python-docx python3 scripts/generate_docx_report.py
```

---

## 🔬 实验内容概述

### 基础实验 1：观察目标文件、符号表与 ELF 结构
- 编写 `main.c` 和 `sum.c`（教材图 7.1）。
- 运用 `nm` 观察符号表，区分全局已定义符号（`T`/`D`）与未定义外部符号（`U`）。
- 运用 `readelf -S` 剖析 `.text`, `.data`, `.bss`, `.symtab`, `.strtab`, `.rela.text` 等关键节区。
- 运用 `objdump -d -r` 反汇编观察外部符号调用的占位符及重定位条目。

### 基础实验 2：重定位算法推导与验证
- 深入剖析 CS:APP 图 7.10 重定位算法原理。
- 提取 `R_X86_64_PC32` 与 `R_X86_64_PLT32` 重定位条目参数（`offset`, `symbol`, `addend`）。
- 手动推导 PC 相对引用的修补公式：`*refptr = ADDR(symbol) + addend - refaddr`。
- 与编译器生成的可执行文件反汇编指令进行精确比对，数值吻合。

### 基础实验 3：静态链接与动态链接
- 静态库构建：使用 `ar rcs libvector.a` 打包向量运算模块，验证静态链接符号“按需拷贝”机制（未引用的 `multvec.o` 不被拷入最终程序）。
- 动态加载共享库：生成 `libvector.so`，利用 `dlopen`、`dlsym`、`dlclose` 实现运行期显式动态装载。
- 利用 `ldd` 对比分析静态二进制程序与动态加载程序的底层依赖差异。

### 进阶实验 4：实现简易静态库打包工具 `mylib`（选做）
- 基于 `/usr/include/elf.h` 解析 ELF64 节头表，提取 `.symtab` 中导出的全局函数与全局变量。
- 按照工业标准生成包含大端序符号索引头（Ranlib 机制）的静态库归档文件。
- 实现了 `-c`（打包）、`-t`（列出成员）、`-x`（提取文件）、`-s`（查看符号索引）全套命令行选项。
- 经过系统内置官方工具链交叉验证，GNU `ar -t`、`nm` 及 `gcc` 可直接识别并链接 `mylib` 生成的静态库并正常运行。
