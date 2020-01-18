# gameff-toolset

a toolset for daily office work on game project development
游戏项目研发日常小工具脚本合集

## requirements

python >= 3.5

## usage

ctrl+c & ctrl+v

## modules

### excel differ

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

## miscs

- lua table differ and table tostring script (`lib/diff_table.lua`)
