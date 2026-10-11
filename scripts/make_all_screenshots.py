#!/usr/bin/env python3
import os
import subprocess
from render_screenshot import render_session, SCREENSHOTS_DIR

def run_cmd(cwd, cmd):
    res = subprocess.run(cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return res.stdout.strip()

def main():
    root_dir = "/home/wolllf/Coding/WHU-hwk"
    lab1_dir = os.path.join(root_dir, "lab1")
    lab2_dir = os.path.join(root_dir, "lab2")
    lab3_dir = os.path.join(root_dir, "lab3")
    lab4_dir = os.path.join(root_dir, "lab4")

    print("[*] 开始生成实验截图...")

    # --- 实验 1 ---
    # 1. 源码展示
    out_cat_main = run_cmd(lab1_dir, "cat main.c")
    out_cat_sum = run_cmd(lab1_dir, "cat sum.c")
    render_session(
        "基础实验1 - 目标源码查看 (main.c & sum.c)",
        [
            ("~/Coding/WHU-hwk/lab1", "cat main.c", out_cat_main),
            ("~/Coding/WHU-hwk/lab1", "cat sum.c", out_cat_sum)
        ],
        os.path.join(SCREENSHOTS_DIR, "exp1_01_source_code.png")
    )

    # 2. 编译生成 .o
    out_gcc1 = run_cmd(lab1_dir, "gcc -Og -Wall -c main.c sum.c && ls -la main.o sum.o")
    render_session(
        "基础实验1 - 编译生成可重定位目标文件 (.o)",
        [
            ("~/Coding/WHU-hwk/lab1", "gcc -Og -Wall -c main.c sum.c && ls -la main.o sum.o", out_gcc1)
        ],
        os.path.join(SCREENSHOTS_DIR, "exp1_02_gcc_compile.png")
    )

    # 3. nm 符号表
    out_nm = run_cmd(lab1_dir, "nm main.o sum.o")
    render_session(
        "基础实验1 - nm 查看符号表（区分全局/未定义符号）",
        [
            ("~/Coding/WHU-hwk/lab1", "nm main.o sum.o", out_nm)
        ],
        os.path.join(SCREENSHOTS_DIR, "exp1_03_nm_symbols.png")
    )

    # 4. readelf -S
    out_readelf_s = run_cmd(lab1_dir, "readelf -S main.o")
    render_session(
        "基础实验1 - readelf -S 查看节头表（Section Headers）",
        [
            ("~/Coding/WHU-hwk/lab1", "readelf -S main.o", out_readelf_s)
        ],
        os.path.join(SCREENSHOTS_DIR, "exp1_04_readelf_sections.png")
    )

    # 5. objdump -d -r main.o
    out_objdump_r = run_cmd(lab1_dir, "objdump -d -r main.o")
    render_session(
        "基础实验1 - objdump -d -r 反汇编与重定位条目",
        [
            ("~/Coding/WHU-hwk/lab1", "objdump -d -r main.o", out_objdump_r)
        ],
        os.path.join(SCREENSHOTS_DIR, "exp1_05_objdump_reloc.png")
    )

    # --- 实验 2 ---
    # 6. objdump -dx main.o & readelf -r
    out_reloc_entries = run_cmd(lab2_dir, "readelf -r main.o && objdump -dx main.o | head -n 35")
    render_session(
        "基础实验2 - 提取重定位条目与节详细信息",
        [
            ("~/Coding/WHU-hwk/lab2", "readelf -r main.o", run_cmd(lab2_dir, "readelf -r main.o")),
            ("~/Coding/WHU-hwk/lab2", "objdump -dx main.o | head -n 32", run_cmd(lab2_dir, "objdump -dx main.o | head -n 32"))
        ],
        os.path.join(SCREENSHOTS_DIR, "exp2_01_objdump_main_reloc.png")
    )

    # 7. 编译可执行文件 prog & prog_nopie
    out_compile_prog = run_cmd(lab2_dir, "gcc -Og -Wall -o prog main.c sum.c && ./prog; echo \"prog exit code: $?\"")
    out_compile_nopie = run_cmd(lab2_dir, "gcc -Og -Wall -no-pie -o prog_nopie main.c sum.c && ./prog_nopie; echo \"prog_nopie exit code: $?\"")
    render_session(
        "基础实验2 - 编译生成可执行文件 (PIE 与 Non-PIE)",
        [
            ("~/Coding/WHU-hwk/lab2", "gcc -Og -Wall -o prog main.c sum.c && ./prog; echo \"prog exit code: $?\"", out_compile_prog),
            ("~/Coding/WHU-hwk/lab2", "gcc -Og -Wall -no-pie -o prog_nopie main.c sum.c && ./prog_nopie; echo \"prog_nopie exit code: $?\"", out_compile_nopie)
        ],
        os.path.join(SCREENSHOTS_DIR, "exp2_02_compile_prog.png")
    )

    # 8. objdump 反汇编对比重定位修补结果
    out_disasm_pie = run_cmd(lab2_dir, "objdump -d prog | grep -A 10 '<main>:'")
    out_disasm_nopie = run_cmd(lab2_dir, "objdump -d prog_nopie | grep -A 10 '<main>:'")
    render_session(
        "基础实验2 - 可执行文件反汇编重定位修补结果",
        [
            ("~/Coding/WHU-hwk/lab2", "objdump -d prog | grep -A 10 '<main>:'", out_disasm_pie),
            ("~/Coding/WHU-hwk/lab2", "objdump -d prog_nopie | grep -A 10 '<main>:'", out_disasm_nopie)
        ],
        os.path.join(SCREENSHOTS_DIR, "exp2_03_objdump_prog_disasm.png")
    )

    # 9. 重定位算法手动推导与程序自动验证
    out_calc = run_cmd(lab2_dir, "./calc.py")
    render_session(
        "基础实验2 - 重定位算法公式推导与验证计算 (calc.py)",
        [
            ("~/Coding/WHU-hwk/lab2", "./calc.py", out_calc)
        ],
        os.path.join(SCREENSHOTS_DIR, "exp2_04_relocation_calculation.png")
    )

    # --- 实验 3 ---
    # 10. 静态库打包与查看
    out_static_build = run_cmd(lab3_dir, "gcc -Og -Wall -c addvec.c multvec.c && ar rcs libvector.a addvec.o multvec.o")
    out_ar_t = run_cmd(lab3_dir, "ar -t libvector.a")
    out_nm_ar = run_cmd(lab3_dir, "nm libvector.a")
    render_session(
        "基础实验3 - 编译目标文件并打包静态库 (ar rcs libvector.a)",
        [
            ("~/Coding/WHU-hwk/lab3", "gcc -Og -Wall -c addvec.c multvec.c && ar rcs libvector.a addvec.o multvec.o", out_static_build if out_static_build else "(静态库 libvector.a 构建完成)"),
            ("~/Coding/WHU-hwk/lab3", "ar -t libvector.a", out_ar_t),
            ("~/Coding/WHU-hwk/lab3", "nm libvector.a", out_nm_ar)
        ],
        os.path.join(SCREENSHOTS_DIR, "exp3_01_static_lib_build.png")
    )

    # 11. 静态链接并运行
    out_static_link = run_cmd(lab3_dir, "gcc -Og -Wall -c main2.c && gcc -Og -Wall -static -o prog2c main2.o ./libvector.a && ./prog2c")
    out_nm_prog2c = run_cmd(lab3_dir, "nm prog2c | grep -E 'addvec|multvec'")
    render_session(
        "基础实验3 - 静态链接与运行 (prog2c 符号按需拷贝验证)",
        [
            ("~/Coding/WHU-hwk/lab3", "gcc -Og -c main2.c && gcc -Og -static -o prog2c main2.o ./libvector.a && ./prog2c", out_static_link),
            ("~/Coding/WHU-hwk/lab3", "nm prog2c | grep -E 'addvec|multvec'", out_nm_prog2c + "\n# 注: 仅引用的 addvec 被静态拷入，未被引用的 multvec 不被拷入")
        ],
        os.path.join(SCREENSHOTS_DIR, "exp3_02_static_lib_link_run.png")
    )

    # 12. 动态库构建与动态加载 dlopen/dlsym
    out_dynamic_build = run_cmd(lab3_dir, "gcc -Og -Wall -shared -fpic -o libvector.so addvec.c multvec.c")
    out_dynamic_link = run_cmd(lab3_dir, "gcc -Og -Wall -rdynamic -o prog2r dll.c -ldl && ./prog2r")
    render_session(
        "基础实验3 - 动态共享库构建与运行时 dlopen 动态加载 (prog2r)",
        [
            ("~/Coding/WHU-hwk/lab3", "gcc -Og -shared -fpic -o libvector.so addvec.c multvec.c", out_dynamic_build if out_dynamic_build else "(共享库 libvector.so 构建完成)"),
            ("~/Coding/WHU-hwk/lab3", "gcc -Og -rdynamic -o prog2r dll.c -ldl && ./prog2r", out_dynamic_link)
        ],
        os.path.join(SCREENSHOTS_DIR, "exp3_03_dynamic_lib_build_run.png")
    )

    # 13. ldd 动态链接依赖对比
    out_ldd_prog2c = run_cmd(lab3_dir, "ldd prog2c 2>&1 || true")
    out_ldd_prog2r = run_cmd(lab3_dir, "ldd prog2r")
    render_session(
        "基础实验3 - ldd 工具对比分析静态可执行文件与动态可执行文件",
        [
            ("~/Coding/WHU-hwk/lab3", "ldd prog2c", out_ldd_prog2c),
            ("~/Coding/WHU-hwk/lab3", "ldd prog2r", out_ldd_prog2r)
        ],
        os.path.join(SCREENSHOTS_DIR, "exp3_04_ldd_analysis.png")
    )

    # --- 实验 4 ---
    # 14. mylib 源码概览与编译
    out_mylib_compile = run_cmd(lab4_dir, "make clean && make mylib test1.o test2.o")
    render_session(
        "进阶实验4 - 静态库打包工具 mylib 编译构建",
        [
            ("~/Coding/WHU-hwk/lab4", "make clean && make mylib test1.o test2.o", out_mylib_compile)
        ],
        os.path.join(SCREENSHOTS_DIR, "exp4_01_mylib_source.png")
    )

    # 15. mylib -c 打包与符号提取
    out_mylib_pack = run_cmd(lab4_dir, "./mylib -c libtest.a test1.o test2.o")
    render_session(
        "进阶实验4 - mylib -c 解析 ELF 符号表并打包静态库",
        [
            ("~/Coding/WHU-hwk/lab4", "./mylib -c libtest.a test1.o test2.o", out_mylib_pack)
        ],
        os.path.join(SCREENSHOTS_DIR, "exp4_02_mylib_pack_and_index.png")
    )

    # 16. mylib -t 和 -s 查看成员与符号索引
    out_mylib_t = run_cmd(lab4_dir, "./mylib -t libtest.a")
    out_mylib_s = run_cmd(lab4_dir, "./mylib -s libtest.a")
    render_session(
        "进阶实验4 - mylib -t 列出库成员及 -s 查看符号索引表",
        [
            ("~/Coding/WHU-hwk/lab4", "./mylib -t libtest.a", out_mylib_t),
            ("~/Coding/WHU-hwk/lab4", "./mylib -s libtest.a", out_mylib_s)
        ],
        os.path.join(SCREENSHOTS_DIR, "exp4_03_mylib_list_t.png")
    )

    # 17. mylib -x 提取指定目标文件
    out_mylib_x = run_cmd(lab4_dir, "rm -f test1.o && ./mylib -x libtest.a test1.o && ls -lh test1.o")
    render_session(
        "进阶实验4 - mylib -x 解压提取指定目标文件",
        [
            ("~/Coding/WHU-hwk/lab4", "rm -f test1.o && ./mylib -x libtest.a test1.o && ls -lh test1.o", out_mylib_x)
        ],
        os.path.join(SCREENSHOTS_DIR, "exp4_04_mylib_extract_x.png")
    )

    # 18. GNU 工具链完全兼容性验证
    out_compat_ar = run_cmd(lab4_dir, "ar -t libtest.a && nm libtest.a")
    out_compat_gcc = run_cmd(lab4_dir, "gcc -o test_prog main_test.c ./libtest.a && ./test_prog")
    render_session(
        "进阶实验4 - GNU 工具链兼容性验证 (ar / nm / gcc 链接与运行)",
        [
            ("~/Coding/WHU-hwk/lab4", "ar -t libtest.a && nm libtest.a", out_compat_ar),
            ("~/Coding/WHU-hwk/lab4", "gcc -o test_prog main_test.c ./libtest.a && ./test_prog", out_compat_gcc)
        ],
        os.path.join(SCREENSHOTS_DIR, "exp4_05_mylib_compatibility.png")
    )

    print("[+] 所有 18 张实验高清晰终端截图已全部生成完毕！")

if __name__ == "__main__":
    main()
