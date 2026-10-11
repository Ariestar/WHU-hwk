#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <time.h>
#include <ar.h>
#include <elf.h>
#include <arpa/inet.h>

#define AR_MAGIC "!<arch>\n"
#define AR_MAGIC_LEN 8
#define MAX_SYMBOLS 1024
#define MAX_FILES 256

typedef struct {
    char name[256];
    char file_owner[256];
    uint32_t file_offset;
} SymbolEntry;

typedef struct {
    SymbolEntry entries[MAX_SYMBOLS];
    int count;
} SymbolTable;

typedef struct {
    char filename[256];
    size_t size;
    time_t mtime;
    mode_t mode;
    uint32_t uid;
    uint32_t gid;
    uint8_t *data;
    uint32_t ar_offset;
} ObjectFile;

/* 将 32 位整数转换为大端序 (Big Endian) */
static uint32_t to_be32(uint32_t val) {
    return htonl(val);
}

static uint32_t from_be32(uint32_t val) {
    return ntohl(val);
}

/* 解析单个 .o 文件的 ELF 符号表，提取全局/弱定义符号 */
int extract_symbols_from_elf(const char *filepath, const char *shortname, SymbolTable *symtab) {
    FILE *fp = fopen(filepath, "rb");
    if (!fp) {
        fprintf(stderr, "[-] 打开文件失败: %s\n", filepath);
        return -1;
    }

    Elf64_Ehdr ehdr;
    if (fread(&ehdr, 1, sizeof(ehdr), fp) != sizeof(ehdr)) {
        fprintf(stderr, "[-] 读取 ELF 头部失败: %s\n", filepath);
        fclose(fp);
        return -1;
    }

    /* 校验 ELF 魔数 */
    if (memcmp(ehdr.e_ident, ELFMAG, SELFMAG) != 0) {
        fprintf(stderr, "[-] 非合法的 ELF 文件: %s\n", filepath);
        fclose(fp);
        return -1;
    }

    /* 读取所有节区头部 */
    Elf64_Shdr *shdrs = malloc(ehdr.e_shnum * sizeof(Elf64_Shdr));
    if (!shdrs) {
        fclose(fp);
        return -1;
    }
    fseek(fp, ehdr.e_shoff, SEEK_SET);
    if (fread(shdrs, sizeof(Elf64_Shdr), ehdr.e_shnum, fp) != ehdr.e_shnum) {
        fprintf(stderr, "[-] 读取节区头部表失败: %s\n", filepath);
        free(shdrs);
        fclose(fp);
        return -1;
    }

    /* 寻找 .symtab 与对应的 .strtab */
    int symtab_idx = -1;
    for (int i = 0; i < ehdr.e_shnum; i++) {
        if (shdrs[i].sh_type == SHT_SYMTAB) {
            symtab_idx = i;
            break;
        }
    }

    if (symtab_idx == -1) {
        /* 没有符号表（可能已被 strip） */
        free(shdrs);
        fclose(fp);
        return 0;
    }

    Elf64_Shdr *symtab_hdr = &shdrs[symtab_idx];
    int strtab_idx = symtab_hdr->sh_link;
    Elf64_Shdr *strtab_hdr = &shdrs[strtab_idx];

    /* 读取符号表数据 */
    int num_symbols = symtab_hdr->sh_size / sizeof(Elf64_Sym);
    Elf64_Sym *symbols = malloc(symtab_hdr->sh_size);
    fseek(fp, symtab_hdr->sh_offset, SEEK_SET);
    if (fread(symbols, 1, symtab_hdr->sh_size, fp) != symtab_hdr->sh_size) {
        free(symbols);
        free(shdrs);
        fclose(fp);
        return -1;
    }

    /* 读取字符串表数据 */
    char *strtab = malloc(strtab_hdr->sh_size);
    fseek(fp, strtab_hdr->sh_offset, SEEK_SET);
    if (fread(strtab, 1, strtab_hdr->sh_size, fp) != strtab_hdr->sh_size) {
        free(symbols);
        free(strtab);
        free(shdrs);
        fclose(fp);
        return -1;
    }

    /* 提取全局/弱符号且有定义的符号 (st_shndx != SHN_UNDEF) */
    for (int i = 0; i < num_symbols; i++) {
        unsigned char bind = ELF64_ST_BIND(symbols[i].st_info);
        unsigned char type = ELF64_ST_TYPE(symbols[i].st_info);
        if ((bind == STB_GLOBAL || bind == STB_WEAK) && symbols[i].st_shndx != SHN_UNDEF) {
            const char *sym_name = strtab + symbols[i].st_name;
            if (strlen(sym_name) > 0 && symtab->count < MAX_SYMBOLS) {
                strncpy(symtab->entries[symtab->count].name, sym_name, 255);
                strncpy(symtab->entries[symtab->count].file_owner, shortname, 255);
                symtab->count++;
                printf("  [+] 发现全局符号: %-20s (类型: %s, 来源: %s)\n",
                       sym_name,
                       (type == STT_FUNC ? "函数" : (type == STT_OBJECT ? "变量" : "其它")),
                       shortname);
            }
        }
    }

    free(symbols);
    free(strtab);
    free(shdrs);
    fclose(fp);
    return 0;
}

/* 格式化写入 ar_hdr 头部 */
void fill_ar_header(struct ar_hdr *hdr, const char *name, time_t mtime,
                    uid_t uid, gid_t gid, mode_t mode, size_t size) {
    memset(hdr, ' ', sizeof(struct ar_hdr));
    char name_buf[32];
    snprintf(name_buf, sizeof(name_buf), "%s", name);
    int len = strlen(name_buf);
    if (len > 16) len = 16;
    memcpy(hdr->ar_name, name_buf, len);

    char tmp[32];
    snprintf(tmp, sizeof(tmp), "%-12ld", (long)mtime);
    memcpy(hdr->ar_date, tmp, 12);

    snprintf(tmp, sizeof(tmp), "%-6u", (unsigned)uid);
    memcpy(hdr->ar_uid, tmp, 6);

    snprintf(tmp, sizeof(tmp), "%-6u", (unsigned)gid);
    memcpy(hdr->ar_gid, tmp, 6);

    snprintf(tmp, sizeof(tmp), "%-8o", (unsigned)(mode & 0777));
    memcpy(hdr->ar_mode, tmp, 8);

    snprintf(tmp, sizeof(tmp), "%-10zu", size);
    memcpy(hdr->ar_size, tmp, 10);

    memcpy(hdr->ar_fmag, ARFMAG, 2);
}

/* 打包生成静态库 .a */
int create_archive(const char *ar_path, char **filenames, int file_count) {
    printf("[*] 正在解析目标文件符号并构建静态库: %s\n", ar_path);
    SymbolTable symtab;
    memset(&symtab, 0, sizeof(symtab));

    ObjectFile *files = malloc(file_count * sizeof(ObjectFile));
    if (!files) return -1;

    for (int i = 0; i < file_count; i++) {
        struct stat st;
        if (stat(filenames[i], &st) < 0) {
            fprintf(stderr, "[-] 无法获取文件属性: %s\n", filenames[i]);
            free(files);
            return -1;
        }

        const char *base = strrchr(filenames[i], '/');
        const char *shortname = base ? base + 1 : filenames[i];
        strncpy(files[i].filename, shortname, 255);
        files[i].size = st.st_size;
        files[i].mtime = st.st_mtime;
        files[i].mode = st.st_mode;
        files[i].uid = st.st_uid;
        files[i].gid = st.st_gid;

        FILE *fp = fopen(filenames[i], "rb");
        if (!fp) {
            fprintf(stderr, "[-] 无法读取文件: %s\n", filenames[i]);
            free(files);
            return -1;
        }
        files[i].data = malloc(files[i].size);
        if (fread(files[i].data, 1, files[i].size, fp) != files[i].size) {
            fclose(fp);
            free(files);
            return -1;
        }
        fclose(fp);

        printf("[*] 解析目标文件 [%d/%d]: %s\n", i + 1, file_count, shortname);
        extract_symbols_from_elf(filenames[i], shortname, &symtab);
    }

    /* 构建 GNU ar 格式符号索引成员 (Member name: "/               ") */
    /* 格式：
     * uint32_t num_syms (Big Endian)
     * uint32_t offsets[num_syms] (Big Endian)
     * char strings[] (以 '\0' 分隔)
     */
    size_t strtab_size = 0;
    for (int i = 0; i < symtab.count; i++) {
        strtab_size += strlen(symtab.entries[i].name) + 1;
    }

    size_t index_payload_size = 4 + symtab.count * 4 + strtab_size;
    size_t index_member_padded_size = index_payload_size + (index_payload_size % 2);

    /* 计算各目标文件在静态库中的偏移量 */
    uint32_t current_offset = AR_MAGIC_LEN + sizeof(struct ar_hdr) + index_member_padded_size;
    for (int i = 0; i < file_count; i++) {
        files[i].ar_offset = current_offset;
        current_offset += sizeof(struct ar_hdr) + files[i].size + (files[i].size % 2);
    }

    /* 映射符号表中每个符号所属文件的偏移 */
    for (int i = 0; i < symtab.count; i++) {
        for (int j = 0; j < file_count; j++) {
            if (strcmp(symtab.entries[i].file_owner, files[j].filename) == 0) {
                symtab.entries[i].file_offset = files[j].ar_offset;
                break;
            }
        }
    }

    /* 写入 .a 文件 */
    FILE *out = fopen(ar_path, "wb");
    if (!out) {
        fprintf(stderr, "[-] 创建静态库输出文件失败: %s\n", ar_path);
        free(files);
        return -1;
    }

    /* 1. 写入魔数 */
    fwrite(AR_MAGIC, 1, AR_MAGIC_LEN, out);

    /* 2. 写入符号索引头与内容 */
    struct ar_hdr idx_hdr;
    fill_ar_header(&idx_hdr, "/               ", time(NULL), 0, 0, 0, index_payload_size);
    fwrite(&idx_hdr, 1, sizeof(idx_hdr), out);

    uint32_t be_num = to_be32(symtab.count);
    fwrite(&be_num, 4, 1, out);
    for (int i = 0; i < symtab.count; i++) {
        uint32_t be_off = to_be32(symtab.entries[i].file_offset);
        fwrite(&be_off, 4, 1, out);
    }
    for (int i = 0; i < symtab.count; i++) {
        fwrite(symtab.entries[i].name, 1, strlen(symtab.entries[i].name) + 1, out);
    }
    if (index_payload_size % 2 != 0) {
        fputc('\n', out);
    }

    /* 3. 写入每个目标文件 */
    for (int i = 0; i < file_count; i++) {
        struct ar_hdr f_hdr;
        char name_with_slash[300];
        snprintf(name_with_slash, sizeof(name_with_slash), "%s/", files[i].filename);
        fill_ar_header(&f_hdr, name_with_slash, files[i].mtime, files[i].uid,
                       files[i].gid, files[i].mode, files[i].size);
        fwrite(&f_hdr, 1, sizeof(f_hdr), out);
        fwrite(files[i].data, 1, files[i].size, out);
        if (files[i].size % 2 != 0) {
            fputc('\n', out);
        }
        free(files[i].data);
    }

    fclose(out);
    free(files);

    printf("[+] 静态库 %s 打包成功！包含 %d 个目标文件，共建立 %d 个符号索引。\n",
           ar_path, file_count, symtab.count);
    return 0;
}

/* 列出静态库中的目标文件 (-t) */
int list_archive(const char *ar_path) {
    FILE *fp = fopen(ar_path, "rb");
    if (!fp) {
        fprintf(stderr, "[-] 打开文件失败: %s\n", ar_path);
        return -1;
    }

    char magic[AR_MAGIC_LEN];
    if (fread(magic, 1, AR_MAGIC_LEN, fp) != AR_MAGIC_LEN || memcmp(magic, AR_MAGIC, AR_MAGIC_LEN) != 0) {
        fprintf(stderr, "[-] 非有效静态库文件: %s\n", ar_path);
        fclose(fp);
        return -1;
    }

    printf("静态库文件: %s 包含的内容列表:\n", ar_path);
    printf("%-20s %-12s %-10s %s\n", "文件名", "大小 (字节)", "权限", "修改时间");
    printf("------------------------------------------------------------\n");

    struct ar_hdr hdr;
    while (fread(&hdr, 1, sizeof(hdr), fp) == sizeof(hdr)) {
        if (memcmp(hdr.ar_fmag, ARFMAG, 2) != 0) break;

        char name[17] = {0};
        memcpy(name, hdr.ar_name, 16);
        for (int i = 15; i >= 0 && name[i] == ' '; i--) name[i] = '\0';

        char size_str[11] = {0};
        memcpy(size_str, hdr.ar_size, 10);
        size_t size = strtoul(size_str, NULL, 10);

        char date_str[13] = {0};
        memcpy(date_str, hdr.ar_date, 12);
        time_t mtime = (time_t)strtol(date_str, NULL, 10);

        char mode_str[9] = {0};
        memcpy(mode_str, hdr.ar_mode, 8);
        long mode = strtol(mode_str, NULL, 8);

        char time_buf[64] = {0};
        struct tm *tm_info = localtime(&mtime);
        if (tm_info) strftime(time_buf, sizeof(time_buf), "%Y-%m-%d %H:%M:%S", tm_info);

        /* 去除末尾的 '/' */
        char clean_name[32] = {0};
        strncpy(clean_name, name, 31);
        char *slash = strchr(clean_name, '/');
        if (slash) *slash = '\0';

        if (strcmp(clean_name, "") == 0 && name[0] == '/') {
            printf("%-20s %-12zu %-10o %s (符号索引表)\n", "[Symbol Table /]", size, (unsigned)mode, time_buf);
        } else {
            printf("%-20s %-12zu %-10o %s\n", clean_name, size, (unsigned)mode, time_buf);
        }

        fseek(fp, size + (size % 2), SEEK_CUR);
    }

    fclose(fp);
    return 0;
}

/* 提取指定目标文件 (-x) */
int extract_archive(const char *ar_path, const char *target_name) {
    FILE *fp = fopen(ar_path, "rb");
    if (!fp) {
        fprintf(stderr, "[-] 打开文件失败: %s\n", ar_path);
        return -1;
    }

    char magic[AR_MAGIC_LEN];
    if (fread(magic, 1, AR_MAGIC_LEN, fp) != AR_MAGIC_LEN || memcmp(magic, AR_MAGIC, AR_MAGIC_LEN) != 0) {
        fprintf(stderr, "[-] 非有效静态库文件: %s\n", ar_path);
        fclose(fp);
        return -1;
    }

    struct ar_hdr hdr;
    int extracted = 0;

    while (fread(&hdr, 1, sizeof(hdr), fp) == sizeof(hdr)) {
        if (memcmp(hdr.ar_fmag, ARFMAG, 2) != 0) break;

        char name[17] = {0};
        memcpy(name, hdr.ar_name, 16);
        for (int i = 15; i >= 0 && name[i] == ' '; i--) name[i] = '\0';

        char size_str[11] = {0};
        memcpy(size_str, hdr.ar_size, 10);
        size_t size = strtoul(size_str, NULL, 10);

        char clean_name[32] = {0};
        strncpy(clean_name, name, 31);
        char *slash = strchr(clean_name, '/');
        if (slash) *slash = '\0';

        /* 跳过特殊索引成员 */
        if (clean_name[0] == '\0' && name[0] == '/') {
            fseek(fp, size + (size % 2), SEEK_CUR);
            continue;
        }

        /* 判断是否匹配提取目标 */
        if (target_name == NULL || strcmp(clean_name, target_name) == 0) {
            printf("[*] 正在解压提取: %s (%zu 字节)\n", clean_name, size);
            uint8_t *buf = malloc(size);
            if (fread(buf, 1, size, fp) != size) {
                free(buf);
                fclose(fp);
                return -1;
            }

            FILE *out = fopen(clean_name, "wb");
            if (!out) {
                fprintf(stderr, "[-] 无法写入目标文件: %s\n", clean_name);
                free(buf);
                fclose(fp);
                return -1;
            }
            fwrite(buf, 1, size, out);
            fclose(out);
            free(buf);
            extracted++;

            if (size % 2 != 0) fseek(fp, 1, SEEK_CUR);
            if (target_name != NULL) break;
        } else {
            fseek(fp, size + (size % 2), SEEK_CUR);
        }
    }

    fclose(fp);
    if (extracted == 0) {
        printf("[-] 未在静态库中找到指定目标文件: %s\n", target_name ? target_name : "(全部)");
        return -1;
    }
    printf("[+] 成功提取 %d 个文件。\n", extracted);
    return 0;
}

/* 显示静态库符号索引表 (-s) */
int show_symbols(const char *ar_path) {
    FILE *fp = fopen(ar_path, "rb");
    if (!fp) {
        fprintf(stderr, "[-] 打开文件失败: %s\n", ar_path);
        return -1;
    }

    char magic[AR_MAGIC_LEN];
    if (fread(magic, 1, AR_MAGIC_LEN, fp) != AR_MAGIC_LEN || memcmp(magic, AR_MAGIC, AR_MAGIC_LEN) != 0) {
        fprintf(stderr, "[-] 非有效静态库文件: %s\n", ar_path);
        fclose(fp);
        return -1;
    }

    struct ar_hdr hdr;
    if (fread(&hdr, 1, sizeof(hdr), fp) != sizeof(hdr) || memcmp(hdr.ar_fmag, ARFMAG, 2) != 0) {
        fprintf(stderr, "[-] 读取成员头失败: %s\n", ar_path);
        fclose(fp);
        return -1;
    }

    if (hdr.ar_name[0] != '/') {
        printf("[-] 未在静态库头部检测到符号索引表。\n");
        fclose(fp);
        return -1;
    }

    char size_str[11] = {0};
    memcpy(size_str, hdr.ar_size, 10);
    size_t size = strtoul(size_str, NULL, 10);

    uint32_t num_syms_be;
    if (fread(&num_syms_be, 4, 1, fp) != 1) {
        fclose(fp);
        return -1;
    }
    uint32_t num_syms = from_be32(num_syms_be);

    uint32_t *offsets = malloc(num_syms * sizeof(uint32_t));
    for (uint32_t i = 0; i < num_syms; i++) {
        uint32_t off_be;
        if (fread(&off_be, 4, 1, fp) != 1) {
            free(offsets);
            fclose(fp);
            return -1;
        }
        offsets[i] = from_be32(off_be);
    }

    size_t strtab_len = size - 4 - num_syms * 4;
    char *strtab = malloc(strtab_len);
    if (fread(strtab, 1, strtab_len, fp) != strtab_len) {
        free(offsets);
        free(strtab);
        fclose(fp);
        return -1;
    }

    printf("============================================================\n");
    printf("静态库 %s 符号索引表 (共 %u 个符号条目):\n", ar_path, num_syms);
    printf("%-24s %-16s\n", "符号名称 (Symbol)", "目标文件偏移 (Offset)");
    printf("------------------------------------------------------------\n");

    char *p = strtab;
    for (uint32_t i = 0; i < num_syms; i++) {
        printf("%-24s 0x%08x (%u)\n", p, offsets[i], offsets[i]);
        p += strlen(p) + 1;
    }
    printf("============================================================\n");

    free(offsets);
    free(strtab);
    fclose(fp);
    return 0;
}

void print_usage(const char *prog) {
    printf("简易静态库打包工具 (mylib - Mini Archiver & Ranlib)\n");
    printf("用法:\n");
    printf("  %s -c <lib.a> [file1.o file2.o ...]  创建静态库（未指定文件时自动扫描当前目录下的 *.o）\n", prog);
    printf("  %s -t <lib.a>                        列出静态库中的目标文件\n", prog);
    printf("  %s -x <lib.a> [file.o]               提取指定目标文件（未指定时提取全部）\n", prog);
    printf("  %s -s <lib.a>                        查看静态库中的符号索引表 (Symbol Index)\n", prog);
}

int main(int argc, char **argv) {
    if (argc < 2) {
        print_usage(argv[0]);
        return 1;
    }

    if (strcmp(argv[1], "-t") == 0) {
        if (argc < 3) {
            fprintf(stderr, "[-] 请指定静态库文件路径: %s -t <lib.a>\n", argv[0]);
            return 1;
        }
        return list_archive(argv[2]);
    } else if (strcmp(argv[1], "-x") == 0) {
        if (argc < 3) {
            fprintf(stderr, "[-] 请指定静态库文件路径: %s -x <lib.a> [file.o]\n", argv[0]);
            return 1;
        }
        const char *target = (argc >= 4) ? argv[3] : NULL;
        return extract_archive(argv[2], target);
    } else if (strcmp(argv[1], "-s") == 0) {
        if (argc < 3) {
            fprintf(stderr, "[-] 请指定静态库文件路径: %s -s <lib.a>\n", argv[0]);
            return 1;
        }
        return show_symbols(argv[2]);
    } else if (strcmp(argv[1], "-c") == 0) {
        if (argc < 3) {
            fprintf(stderr, "[-] 请指定输出静态库文件路径: %s -c <lib.a> [files...]\n", argv[0]);
            return 1;
        }
        const char *out_lib = argv[2];
        if (argc > 3) {
            return create_archive(out_lib, &argv[3], argc - 3);
        } else {
            /* 遍历当前目录下的所有 .o 文件 */
            printf("[*] 未显式指定目标文件，自动遍历当前目录下的所有 .o 文件...\n");
            DIR *dir = opendir(".");
            if (!dir) {
                perror("[-] 无法打开当前目录");
                return 1;
            }
            struct dirent *ent;
            char *o_files[MAX_FILES];
            int count = 0;
            while ((ent = readdir(dir)) != NULL) {
                int len = strlen(ent->d_name);
                if (len > 2 && strcmp(ent->d_name + len - 2, ".o") == 0) {
                    o_files[count] = strdup(ent->d_name);
                    count++;
                    if (count >= MAX_FILES) break;
                }
            }
            closedir(dir);

            if (count == 0) {
                fprintf(stderr, "[-] 当前目录下未发现任何 .o 目标文件。\n");
                return 1;
            }
            int ret = create_archive(out_lib, o_files, count);
            for (int i = 0; i < count; i++) free(o_files[i]);
            return ret;
        }
    } else {
        print_usage(argv[0]);
        return 1;
    }
}
