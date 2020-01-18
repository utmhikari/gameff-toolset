# gameff-toolset

a toolset for daily office work on game project development
游戏研发日常小工具合集

## requirements

python >= 3.5

## usage

ctrl+c and ctrl+v

## modules

### excel differ

做日常excel的diff。输入两个文件夹，输出结果报告。

see `lib/excel_differ.py` for details

view `test/excel_differ/report.json` for report example

```json
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

all indices are based on `(0, 0)` in default, yet excel uses `(1, 1)` at left top

set `use_excel_indices=True` in ExcelDiffer constructor to fix the problem


