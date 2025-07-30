from typing import Any, TypeAlias

import openpyxl as op

from ka_uts_path.pathnm import PathNm
from ka_uts_xls.op.ioopathwb import IooPathWb

TyWb: TypeAlias = op.workbook.workbook.Workbook

TyArr = list[Any]
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoA = dict[Any, TyAoA]
TyDoAoD = dict[Any, TyAoD]
TyPath = str
TyPathnm = str
TySheet = int | str

TnWb = None | TyWb


class IooPathnmWb:

    @staticmethod
    def write(
            wb: TnWb, pathnm: TyPathnm, **kwargs) -> None:
        _path: TyPath = PathNm.sh_path(pathnm, kwargs)
        IooPathWb.write(wb, _path)

    @staticmethod
    def write_wb_from_doaod(
            doaod: TyDoAoD, pathnm: str, **kwargs) -> None:
        _path: TyPath = PathNm.sh_path(pathnm, kwargs)
        IooPathWb.write_wb_from_doaod(doaod, _path)
