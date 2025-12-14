from md_spreadsheet_parser.models import Table


def test_insert_row():
    t = Table(headers=["A", "B"], rows=[["1", "2"], ["3", "4"]])

    # Insert at beginning
    t2 = t.insert_row(0)
    assert len(t2.rows) == 3
    assert t2.rows[0] == ["", ""]
    assert t2.rows[1] == ["1", "2"]

    # Insert at end
    t3 = t.insert_row(2)
    assert len(t3.rows) == 3
    assert t3.rows[2] == ["", ""]
    assert t3.rows[1] == ["3", "4"]


def test_insert_column():
    t = Table(headers=["A", "B"], rows=[["1", "2"]])

    # Insert at middle
    t2 = t.insert_column(1)
    assert t2.headers == ["A", "", "B"]
    assert t2.rows[0] == ["1", "", "2"]

    # Insert at end (append)
    t3 = t.insert_column(2)
    assert t3.headers == ["A", "B", ""]
    assert t3.rows[0] == ["1", "2", ""]
