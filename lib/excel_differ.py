import logger
import os
import json
import xlrd
from util import get_iter_diff, lis, ppt

EXCEL_EXTENSIONS = ['xls', 'xlsx']
LOGGER = logger.get_logger('EXCEL_DIFFER')


class ExcelDiffer:
    """
    Excel Differ
    Users must specify header row, start row and start col
    Only support header as row now~
    see get_diff_report method for details
    """
    def __init__(self,
                 start_row: int = 1,
                 start_col: int = 0,
                 header_row: int = 0,
                 row_modify_threshold: float = 0.66,
                 use_excel_indices: bool = False):
        """
        :param start_row: start row of data
        :param start_col: start col of data
        :param header_row: start row of header
        :param row_modify_threshold: the ratio threshold to judge if the dest row is modified from the src row
        :param use_excel_indices: whether +1 to all indices as excel shows (row 1, col 1) on left top
        """
        self._start_row = start_row
        self._start_col = start_col
        self._header_row = header_row
        self._row_modify_threshold = row_modify_threshold
        self._use_excel_indices = use_excel_indices

    @staticmethod
    def _get_excel_files(r, d, fs: set):
        """
        get excel files recursively
        :param r: root
        :param d: current dir
        :param fs: excel files
        :return: None
        """
        if not os.path.isdir(d) or not os.path.exists(d):
            return
        f_list = os.listdir(d)
        for f in f_list:
            if f.startswith('~$'):
                continue
            p = os.path.join(d, f)
            if os.path.isfile(p):
                _, f_ext = os.path.splitext(p)
                if f_ext.replace('.', '') in EXCEL_EXTENSIONS:
                    abs_p = p.replace(r, '', 1)
                    if abs_p.startswith(os.path.sep):
                        abs_p = abs_p.replace(os.path.sep, '', 1)
                    fs.add(abs_p)
            elif os.path.isdir(p):
                ExcelDiffer._get_excel_files(r, p, fs)

    @staticmethod
    def get_excel_files(directory: str) -> set:
        """
        get excel files recursively from a specific direcotry
        :param directory: directory
        :return: excel file list
        """
        files = set()
        ExcelDiffer._get_excel_files(directory, directory, files)
        return files

    def diff_file(self, f1: str, f2: str):
        """
        get file diff
        :param f1: file path 1
        :param f2: file path 2
        :return: file diff report dict
        """
        LOGGER.info('Get file diff --- src: %s, dest: %s' % (f1, f2))
        modified = False
        file_diff = {
            'added_sheets': [],
            'removed_sheets': [],
            'modified_sheets': [],
        }
        d1 = xlrd.open_workbook(f1)
        d2 = xlrd.open_workbook(f2)
        sheets1 = d1.sheet_names()
        sheets2 = d2.sheet_names()
        removed_sheets, kept_sheets, added_sheets = get_iter_diff(sheets1, sheets2)
        if len(removed_sheets) > 0:
            file_diff['removed_sheets'] = removed_sheets
            modified = True
        if len(added_sheets) > 0:
            file_diff['added_sheets'] = added_sheets
            modified = True
        for sheet_name in kept_sheets:
            sheet1 = d1.sheet_by_name(sheet_name)
            sheet2 = d2.sheet_by_name(sheet_name)
            LOGGER.info('Get sheet %s diff --- src: %s, dest: %s' % (sheet_name, f1, f2))
            try:
                sheet_diff = self.diff_sheet(sheet1, sheet2)
                if sheet_diff:
                    sheet_diff['name'] = sheet_name
                    modified = True
                    file_diff['modified_sheets'].append(sheet_diff)
            except Exception as e:
                LOGGER.exception('Error while differing sheet %s of %s and %s! %s'
                                 % (sheet_name, f1, f2, e))
        return file_diff if modified else None

    def diff_sheet(self, s1: xlrd.sheet.Sheet, s2: xlrd.sheet.Sheet):
        """
        get sheet diff
        :param s1: sheet 1
        :param s2: sheet 2
        :return: sheet diff of s1 and s2
        """
        sheet_diff = {
            'added_cols': [],
            'removed_cols': [],
            'modified_data': {},
        }
        modified = True
        # diff header
        headers1 = [str(v) for v in s1.row_values(self._header_row, start_colx=self._start_col)]
        headers2 = [str(v) for v in s2.row_values(self._header_row, start_colx=self._start_col)]
        # may contain header with same name
        header_cols1, header_cols2 = dict(), dict()
        l1, l2 = len(headers1), len(headers2)
        for i in range(l1):
            h1 = headers1[i]
            if h1 not in header_cols1.keys():
                header_cols1[h1] = list()
            header_cols1[h1].append(i)
        for i in range(l2):
            h2 = headers2[i]
            if h2 not in header_cols2.keys():
                header_cols2[h2] = list()
            header_cols2[h2].append(i)
        removed_cols, kept_cols, added_cols = get_iter_diff(header_cols1.keys(), header_cols2.keys())
        # please do not change col name or switch data frequently!
        if len(removed_cols) > 0:
            sheet_diff['removed_cols'] = [{'name': h, 'indices': header_cols1[h]} for h in removed_cols]
            modified = True
        if len(added_cols) > 0:
            sheet_diff['added_cols'] = [{'name': h, 'indices': header_cols2[h]} for h in added_cols]
            modified = True
        for h in kept_cols:
            cols1, cols2 = header_cols1[h], header_cols2[h]
            l1, l2 = len(cols1), len(cols2)
            if l1 > l2:
                sheet_diff['removed_cols'].append({'name': h, 'indices': cols1[l2 - l1:]})
                header_cols1[h] = cols1[:l2]
                modified = True
            elif l1 < l2:
                sheet_diff['added_cols'].append({'name': h, 'indices': cols2[l1 - l2:]})
                header_cols2[h] = cols2[:l1]
                modified = True
        # map cols
        cols1_header = dict()
        cols1_cols2 = dict()
        for header in header_cols1:
            if header in kept_cols:
                col1_indices = header_cols1[header]
                col2_indices = header_cols2[header]
                while len(col1_indices) > 0 and len(col2_indices) > 0:
                    col_idx1 = col1_indices.pop()
                    col_idx2 = col2_indices.pop()
                    cols1_header[col_idx1] = header
                    cols1_cols2[col_idx1] = col_idx2
        indices1 = list(cols1_header.keys())
        indices1.sort()
        d1, d2 = [], []
        if self._start_row > s1.nrows:
            LOGGER.warn('Sheet %s: start row %d is larger than num rows %d!' %
                        (s1.name, self._start_row, s1.nrows))
        else:
            for i in range(self._start_row, s1.nrows):
                d1.append([str(s1.cell_value(i, c)) for c in indices1])
        if self._start_row > s2.nrows:
            LOGGER.warn('Sheet %s: start row %d is larger then num rows %d!' %
                        (s2.name, self._start_row, s2.nrows))
        else:
            for i in range(self._start_row, s2.nrows):
                d2.append([str(s2.cell_value(i, cols1_cols2[c])) for c in indices1])
        # diff data
        data_diff = self.diff_data(d1, d2)
        if data_diff:
            modified = True
            data_diff['modified_cells'] = [
                dict(d, **{
                    'src_col': indices1[d['src_col']] + self._start_col,
                    'dest_col': cols1_cols2[indices1[d['dest_col']]] + self._start_col,
                })
                for d in data_diff['modified_cells']
            ]
            sheet_diff['modified_data'] = data_diff
        # +1 to all indices if using excel
        if modified and self._use_excel_indices:
            sheet_diff = ExcelDiffer._convert_idx_of_sheet_diff(sheet_diff)
        return sheet_diff if modified else None

    @staticmethod
    def _convert_idx_of_sheet_diff(sheet_diff: dict):
        """
        +1 to all indices in sheet diff
        :param sheet_diff: sheet diff
        :return: new sheet diff
        """
        sd = dict()
        if 'name' in sheet_diff.keys():
            sd['name'] = sheet_diff['name']
        for k in ['added_cols', 'removed_cols']:
            if k in sheet_diff.keys():
                sd[k] = [
                    {
                        'name': c['name'],
                        'indices': [i + 1 for i in c['indices']]
                    }
                    for c in sheet_diff[k]
                ]
        if 'modified_data' in sheet_diff.keys():
            sd['modified_data'] = dict()
            md = sheet_diff['modified_data']
            for k in ['moved_rows', 'duplicated_src_rows', 'duplicated_dest_rows']:
                if k in md.keys():
                    sd[k] = dict()
                    for sr in md[k]:
                        sd[k][int(sr) + 1] = md[k] + 1
            for k in ['removed_rows', 'added_rows']:
                if k in md.keys():
                    sd[k] = [i + 1 for i in md[k]]
            if 'modified_cells' in md.keys():
                sd['modified_cells'] = [
                    dict(mc, **{
                        'src_row': mc['src_row'] + 1,
                        'dest_row': mc['dest_row'] + 1,
                        'src_col': mc['src_col'] + 1,
                        'dest_col': mc['dest_col'] + 1,
                    })
                    for mc in md['modified_cells']
                ]
        return sd

    def diff_data(self, d1: [[str]], d2: [[str]]):
        """
        generate data diff
        :param d1: data 1
        :param d2: data 2
        :return: data diff
        """
        data_diff = {
            'moved_rows': dict(),
            'duplicated_src_rows': dict(),
            'duplicated_dest_rows': dict()
        }
        # get rows both have, remove duplicates
        row_hashes1, row_hashes2 = dict(), dict()
        kept_rows = dict()
        for i in range(len(d1)):
            row_hash1 = '|||'.join(d1[i])
            if row_hash1 in row_hashes1.keys():
                data_diff['duplicated_src_rows'][i + self._start_row] = \
                    row_hashes1[row_hash1] + self._start_row
            else:
                row_hashes1[row_hash1] = i
        for i in range(len(d2)):
            row_hash2 = '|||'.join(d2[i])
            if row_hash2 in row_hashes2.keys():
                data_diff['duplicated_dest_rows'][i + self._start_row] = \
                    row_hashes2[row_hash2] + self._start_row
            else:
                row_hashes2[row_hash2] = i
                if row_hash2 in row_hashes1.keys():
                    kept_rows[row_hashes1[row_hash2]] = i
        # get mapping of kept indices
        kept_indices1 = list(kept_rows.keys())
        if len(kept_indices1) == 0:
            diff = self._diff_modified_data(d1, d2, list(range(len(d1))), list(range(len(d2))))
        else:
            kept_indices1.sort()
            kept_indices2 = [kept_rows[idx] for idx in kept_indices1]
            # get LIS of kept indices 2
            lis_indices2 = lis(kept_indices2)
            if len(lis_indices2) == len(kept_indices2) and len(lis_indices2) == len(d2):
                return None  # no change
            lis_indices1 = list()
            i, j, l, lisl = 0, 0, len(kept_indices1), len(lis_indices2)
            # get moved rows
            while i < l and j < len(lis_indices2):
                if kept_indices2[i] == lis_indices2[j]:
                    lis_indices1.append(kept_indices1[i])
                    j += 1
                else:
                    data_diff['moved_rows'][kept_indices1[i] + self._start_row] = \
                        kept_indices2[i] + self._start_row
                i += 1
            left_rows1 = list(set(list(range(len(d1))))
                              .difference(kept_rows.keys())
                              .difference(set([idx - self._start_row for idx in data_diff['duplicated_src_rows'].keys()])))
            left_rows1.sort()
            left_rows2 = list(set(list(range(len(d2))))
                              .difference(kept_rows.values())
                              .difference(set([idx - self._start_row for idx in data_diff['duplicated_dest_rows'].keys()])))
            left_rows2.sort()
            rd1 = [d1[i] for i in left_rows1]
            rd2 = [d2[i] for i in left_rows2]
            # ppt(rd1)
            # ppt(left_rows1)
            # ppt(rd2)
            # ppt(left_rows2)
            diff = self._diff_modified_data(rd1, rd2, left_rows1, left_rows2)
            # ppt(diff)
        data_diff['modified_cells'] = [
            dict(d, **{
                'src_row': d['src_row'] + self._start_row,
                'dest_row': d['dest_row'] + self._start_row,
            })
            for d in diff['modified_cells']
        ]
        data_diff['removed_rows'] = [self._start_row + i for i in diff['removed_rows']]
        data_diff['added_rows'] = [self._start_row + i for i in diff['added_rows']]
        return data_diff

    def _diff_modified_data(self, d1, d2, rows1, rows2):
        """
        diff, assuming that data1 and data 2 must have diff
        :param d1: data 1
        :param d2: data 2
        :return:
        """
        diff = {
            'modified_cells': [],
            'added_rows': [],
            'removed_rows': []
        }
        i1 = 0
        visited_i2 = set()
        while i1 < len(rows1):
            dest_row = -1
            r1 = d1[i1]
            i2 = 0
            while i2 < len(rows2):
                if i2 not in visited_i2:
                    r2 = d2[i2]
                    col_l = min(len(r1), len(r2))  # col len should be same in fact
                    same_cnt, diffs = 0, []
                    for j in range(col_l):
                        if r1[j] == r2[j]:
                            same_cnt += 1
                        else:
                            diffs.append({
                                'src_row': rows1[i1],
                                'dest_row': rows2[i2],
                                'src_col': j,
                                'dest_col': j,
                                'src_val': r1[j],
                                'dest_val': r2[j]
                            })
                    if same_cnt / col_l >= self._row_modify_threshold:
                        diff['modified_cells'].extend(diffs)
                        dest_row = rows2[i2]
                        break
                i2 += 1
            if dest_row >= 0:
                visited_i2.add(i2)
            else:
                diff['removed_rows'].append(rows1[i1])
            i1 += 1
        for i2 in range(len(rows2)):
            if i2 not in visited_i2:
                diff['added_rows'].append(rows2[i2])
        return diff

    def get_diff_report(self, src_dir: str, dest_dir: str) -> (dict, str):
        """
        generate diff report from directories including excel files
        input 2 directories of excel files, output diff of 2 directories
        the whole report includes: {
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
        :param src_dir: directory containing source excel files
        :param dest_dir: directory containing destination excel files
        :return: report dict and string
        """
        LOGGER.info('Get excel diff report --- src: %s, dest: %s' % (src_dir, dest_dir))
        report = {
            'added_files': [],
            'removed_files': [],
            'modified_files': [],
        }
        src_files = ExcelDiffer.get_excel_files(src_dir)
        dest_files = ExcelDiffer.get_excel_files(dest_dir)
        LOGGER.info('Src excel files: %s' % list(src_files))
        LOGGER.info('Dest excel files: %s' % list(dest_files))
        rm, kp, ad = get_iter_diff(src_files, dest_files)
        report['removed_files'] = rm
        report['added_files'] = ad
        for kf in kp:
            f1 = os.path.join(src_dir, kf)
            f2 = os.path.join(dest_dir, kf)
            try:
                ret = self.diff_file(f1, f2)
                if ret:
                    ret['name'] = kf
                    report['modified_files'].append(ret)
                else:
                    LOGGER.info("File %s did not change...", kf)
            except Exception as e:
                msg = 'Error while differing excel file %s and %s! %s' % (f1, f2, e)
                LOGGER.exception(msg)
                report['errors'].append(msg)
        return report


if __name__ == '__main__':
    ed = ExcelDiffer()
    src = './test/excel_differ/src'
    dest = './test/excel_differ/dest'
    _r = ed.get_diff_report(src, dest)
    report_file = './test/excel_differ/report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(_r, ensure_ascii=False, indent=2))
        f.close()
