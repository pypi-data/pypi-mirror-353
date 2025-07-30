from usdm4_excel import USDM4Excel


def test_integration():
    usdm4_excel = USDM4Excel()
    usdm4_excel.to_excel(
        "tests/test_files/usdm.json", "tests/test_files/usdm_excel.xlsx"
    )
