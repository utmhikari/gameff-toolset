import logger
import os
import json
import xlrd
from util import get_list_diff

EXCEL_EXTENSIONS = ['xls', 'xlsx']
LOGGER = logger.get_logger('EXCEL_DIFFER')


class ExcelDiffer:
    """
    Excel Differ
    """
    def __init__(self, start_row=2, start_col=0, field_row=0, field_name_row=1):
        self._start_row = start_row if isinstance(start_row, int) else -1
        self._start_col = start_col if isinstance(start_col, int) else -1
        self._field_row = field_row if isinstance(field_row, int) else -1
        self._field_name_row = field_name_row if isinstance(field_name_row, int) else -1



    @staticmethod
    def _get_excel_files(r, d, fs: set):
        if not os.path.isdir(d) or not os.path.exists(d):
            return
        f_list = os.listdir(d)
        for f in f_list:
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

    @staticmethod
    def _pprint_report(r):
        return json.dumps(r, ensure_ascii=False, indent=2)

    def _diff_file(self, f1, f2, filename=""):
        modified = False
        diff_report = {
            "filename": filename,
            "added_sheets": [],
            "removed_sheets": [],
            "modified_sheets": [],
        }
        sheet_diff_report = {
            "added_cols": [],
            "removed_cols": [],
            "modified_cols": [],
        }
        d1 = xlrd.open_workbook(f1)
        d2 = xlrd.open_workbook(f2)
        sheets1 = d1.sheet_names()
        sheets2 = d2.sheet_names()
        added_sheets, kept_sheets, removed_sheets = get_list_diff(sheets1, sheets2)
        diff_report["added_sheets"] = added_sheets
        diff_report["removed_sheets"] = removed_sheets
        if len(added_sheets) > 0 or len(removed_sheets) > 0:
            modified = True
        return diff_report if modified else None

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
            "errors": []
        }
        src_files = ExcelDiffer.get_excel_files(src_dir)
        dest_files = ExcelDiffer.get_excel_files(dest_dir)
        LOGGER.info("Src excel files: %s" % list(src_files))
        LOGGER.info("Dest excel files: %s" % list(dest_files))
        rm, kp, ad = get_list_diff(src_files, dest_files)
        report["removed_files"] = rm
        report["added_files"] = ad
        for kf in kp:
            f1 = os.path.join(src_dir, kf)
            f2 = os.path.join(dest_dir, kf)
            try:
                ret = self._diff_file(f1, f2, kf)
                if ret:
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
