# gameff-toolset

游戏项目研发日常小工具脚本合集

a toolset for daily office work on game project development

## Requirements

python >= 3.5

## Usage

ctrl+c & ctrl+v

## Modules

### Excel Differ

[blog](http://utmhikari.top/2020/01/23/testlife/excel_diff/)

为策划和测试人员准备，跟进策划表的修改

输入两个包含excel文件的文件夹，可为同名的excel文件做diff，输出结果报告。
需要指定表头行，数据起始行，数据起始列（以0为首）。暂不支持表头为一列的情况，需要自行转置。

see `lib/excel_differ.py` for details

all indices are based on `(0, 0)` in default, yet excel uses `(1, 1)` at left top, set `use_excel_indices=True` in ExcelDiffer constructor to fix the problem

view `test/excel_differ/report.json` for report example

```text
{
    added_files: [(str) file name from dest dir],
    removed_files: [(str) file name from dest dir],
    modified_files: [
        {
            name: (str) file name,
            added_sheets: [(str) sheet name from dest file],
            removed_sheets: [(str) sheet name from src file],
            modified_sheets: [
                {
                    name: (str) sheet name,
                    added_cols: [
                        {
                            name: (str) col/header name,
                            indices: [(int) idx of added cols from dest sheet]
                        }
                    ],
                    removed_cols: [
                        {
                            name: (str) col/header name,
                            indices: [(int) idx of removed cols from src sheet]
                        }
                    ],
                    modified data: {
                        moved_rows: {
                            (str(int)) src_row_idx: (int) dest_row_idx
                        },
                        duplicated_src_rows: {
                            (str(int)) dup_src_row_idx: (int) first_exist_src_row_idx
                        },
                        duplicated_dest_rows: {
                            (str(int)) dup_dest_row_idx: (int) first_exist_dest_row_idx
                        },
                        added rows: [(int) added rows from dest sheet, exclude duplicated rows],
                        removed rows: [(int) removed rows from src sheet, exclude duplicated rows],
                        modified cells: [
                            {
                                src_row: (int) row idx of src cell,
                                dest_row: (int) row idx of dest cell,
                                src_col: (int) col idx of src cell,
                                dest_col: (int) col idx of dest cell,
                                src_val: (str) value of src cell,
                                dest_val: (str) value of dest cell
                            }
                        ]
                    }
                }
            ]
        }
    ]
}
```

### Table Checker

Base table checker with global checker object and checker functions with decorators

基于python的导表检查业务逻辑设计模式

用一个全局的`table_checker`维护所有导表检查规则的函数。

用户只需要在特定目录下写python文件，import全局的`table_checker`，调用`add_checker`装饰器，就可以注册导表规则到导表检查pipeline

call `table_checker.check` to check the table data, users can also customize the logic if table data of prev commit will also be checked

see `lib/table_checker.py` and `test/table_checker_test` for details

### Git Repo Manager

A git repo manager based on [gitpython](https://gitpython.readthedocs.io/en/stable/intro.html)

set envvar `GIT_PYTHON_GIT_EXECUTABLE` to the path of git executable

一个简易的git repo管理类。基于gitpython。现有的功能有：

- get latest commit info
- get file list at specific directory

如果需要用到git repo缓存之类的操作，可以由这个扩展。但需要用异步框架

## miscs

- lua table differ and table tostring script (`lualib/diff_table.lua`)
