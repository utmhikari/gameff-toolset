import logger
import os


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
                    abs_p = p.replace(r, '', count=1)
                    if abs_p.startswith('/'):
                        abs_p = abs_p.replace('/', '', count=1)
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
    def _pprint_report(report):
        return str(report)

    def _diff_file(self, f1, f2):
        pass

    def _diff_data(self, d1, d2):
        pass

    def get_diff_report(self, src_dir: str, dest_dir: str) -> (dict, str):
        """
        generate diff report from directories including excel files
        :param src_dir: directory containing source excel files
        :param dest_dir: directory containing destination excel files
        :return: report dict and string
        """
        report = {
            "added_files": [],
            "removed_files": [],
            "modified_files": [],
        }
        src_files = ExcelDiffer.get_excel_files(src_dir)
        dest_files = ExcelDiffer.get_excel_files(dest_dir)
        kept_files = list()
        for sf in src_files:
            if sf in dest_files:
                kept_files.append(sf)
                dest_files.remove(sf)
            else:
                report["removed_files"].append(sf)
        for df in dest_files:
            report["added_files"].append(df)
        # TODO: diff files kept by both
        return report, ExcelDiffer._pprint_report(report)



