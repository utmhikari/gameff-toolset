import logger
import os
import json
import xlrd
from util import get_iter_diff

EXCEL_EXTENSIONS = ['xls', 'xlsx']
LOGGER = logger.get_logger('EXCEL_DIFFER')


class ExcelDiffer:
    """
    Excel Differ
    Must With Header
    Optional With Header Description
    """

    def __init__(self,
                 start_row: int = 2,
                 start_col: int = 0,
                 header_row: int = 0,
                 header_desc_row: int = 1):
        self._start_row = start_row
        self._start_col = start_col
        self._header_row = header_row
        self._header_desc_row = header_desc_row

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
            if f.startswith("~$"):
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
    def _pprint_report(r):
        """
        pretty print report
        :param r: report
        :return: pretty printed report string
        """
        return json.dumps(r, ensure_ascii=False, indent=2)

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

    def _diff_file(self, f1, f2):
        """
        get file diff
        :param f1: file 1
        :param f2: file 2
        :return: file diff report dict
        """
        LOGGER.info("Get file diff --- src: %s, dest: %s" % (f1, f2))
        modified = False
        file_diff = {
            "added_sheets": [],
            "removed_sheets": [],
            "modified_sheets": [],
        }
        d1 = xlrd.open_workbook(f1)
        d2 = xlrd.open_workbook(f2)
        sheets1 = d1.sheet_names()
        sheets2 = d2.sheet_names()
        removed_sheets, kept_sheets, added_sheets = get_iter_diff(sheets1, sheets2)
        if len(removed_sheets) > 0:
            file_diff["removed_sheets"] = removed_sheets
            modified = True
        if len(added_sheets) > 0:
            file_diff["added_sheets"] = added_sheets
            modified = True
        for sheet_name in kept_sheets:
            sheet1 = d1.sheet_by_name(sheet_name)
            sheet2 = d2.sheet_by_name(sheet_name)
            LOGGER.info("Get sheet %s diff --- src: %s, dest: %s" % (sheet_name, f1, f2))
            try:
                sheet_diff = self._diff_sheet(sheet1, sheet2)
                if sheet_diff:
                    modified = True
                    file_diff["modified_sheets"].append(sheet_diff)
            except Exception as e:
                LOGGER.exception("Error while differing sheet %s of %s and %s! %s"
                                 % (sheet_name, f1, f2, e))
        return file_diff if modified else None

    def _diff_sheet(self, s1: xlrd.sheet.Sheet, s2: xlrd.sheet.Sheet):
        """
        get sheet diff
        :param s1: sheet 1
        :param s2: sheet 2
        :return: sheet diff of s1 and s2
        """
        sheet_diff = {
            "added_cols": [],
            "removed_cols": [],
            "modified_cols": [],
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
        # please do not change col name frequently!
        if len(removed_cols) > 0:
            sheet_diff["removed_cols"] = [{"name": h, "indices": header_cols1[h]} for h in removed_cols]
            modified = True
        if len(added_cols) > 0:
            sheet_diff["added_cols"] = [{"name": h, "indices": header_cols2[h]} for h in added_cols]
            modified = True
        for h in kept_cols:
            cols1, cols2 = header_cols1[h], header_cols2[h]
            l1, l2 = len(cols1), len(cols2)
            if l1 > l2:
                sheet_diff["removed_cols"].append({"name": h, "indices": cols1[l2 - l1:]})
                header_cols1[h] = cols1[:l2]
                modified = True
            elif l1 < l2:
                sheet_diff["added_cols"].append({"name": h, "indices": cols2[l1 - l2:]})
                header_cols2[h] = cols2[:l1]
                modified = True
        print(json.dumps(header_cols1, ensure_ascii=False, indent=2))
        print(json.dumps(header_cols2, ensure_ascii=False, indent=2))
        # TODO: map cols, diff data that both contains
        return sheet_diff if modified else None

    def get_diff_report(self, src_dir: str, dest_dir: str) -> (dict, str):
        """
        generate diff report from directories including excel files
        :param src_dir: directory containing source excel files
        :param dest_dir: directory containing destination excel files
        :return: report dict and string
        """
        LOGGER.info("Get excel diff report --- src: %s, dest: %s" % (src_dir, dest_dir))
        report = {
            "added_files": [],
            "removed_files": [],
            "modified_files": [],
        }
        src_files = ExcelDiffer.get_excel_files(src_dir)
        dest_files = ExcelDiffer.get_excel_files(dest_dir)
        LOGGER.info("Src excel files: %s" % list(src_files))
        LOGGER.info("Dest excel files: %s" % list(dest_files))
        rm, kp, ad = get_iter_diff(src_files, dest_files)
        report["removed_files"] = rm
        report["added_files"] = ad
        for kf in kp:
            f1 = os.path.join(src_dir, kf)
            f2 = os.path.join(dest_dir, kf)
            try:
                ret = self._diff_file(f1, f2)
                if ret:
                    ret["filename"] = kf
                    report["modified_files"].append(ret)
            except Exception as e:
                msg = "Error while differing excel file %s and %s! %s" % (f1, f2, e)
                LOGGER.exception(msg)
                report["errors"].append(msg)
        return report, ExcelDiffer._pprint_report(report)


if __name__ == '__main__':
    ed = ExcelDiffer()
    src = './test/table_differ/excel_differ/src'
    dest = './test/table_differ/excel_differ/dest'
    _r, _rs = ed.get_diff_report(src, dest)
    LOGGER.info(_rs)
