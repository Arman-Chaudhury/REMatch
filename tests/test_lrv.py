from datetime import date

from property_watch.lrv import parse_sales, to_sbl


def test_sbl_numeric_block():
    assert to_sbl("21.-222-464") == "21222  04640"


def test_sbl_short_block_zero_padded():
    assert to_sbl("55.-89-10") == "55089  00100"


def test_sbl_letter_block():
    assert to_sbl("24.-B-897") == "24  B  08970"


def test_sbl_four_digit_block():
    assert to_sbl("57.-6001-120") == "570600101200"


def test_sbl_lettered_lot():
    assert to_sbl("46.-579-16.C") == "46579  0016C"


SALES_HTML = """
<div class="tab-pane" id="infosalestab"><table><tbody>
  <tr><td>08/29/2023</td><td>$720,000</td><td>14416</td><td>0912</td><td>OTHER UNUSUAL FACTORS</td></tr>
  <tr><td>08/16/2004</td><td>$0</td><td>11864</td><td>0192</td><td></td></tr>
</tbody></table></div>
"""


def test_parse_sales():
    first, second = parse_sales(SALES_HTML)
    assert first == {"sale_date": date(2023, 8, 29), "price": 720_000,
                     "book": "14416", "page": "0912", "condition": "OTHER UNUSUAL FACTORS"}
    assert second["price"] == 0 and second["condition"] is None


def test_parse_sales_page_without_table():
    assert parse_sales("<html><body>no sales here</body></html>") == []
