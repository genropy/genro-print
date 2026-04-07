# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0

"""Basic tests for genro-print package."""


def test_import() -> None:
    """Test that the package can be imported."""
    import genro_print

    assert genro_print.__version__ == "0.2.0"


def test_builders_import() -> None:
    """Test that all builders can be imported."""
    from genro_print import PrintBuilder, PrintLRCBuilder, PrintStyledBuilder

    assert PrintBuilder is not None
    assert PrintLRCBuilder is not None
    assert PrintStyledBuilder is not None


def test_apps_import() -> None:
    """Test that all app classes can be imported."""
    from genro_print import PrintApp, LRCPrintApp, StyledPrintApp

    assert PrintApp is not None
    assert LRCPrintApp is not None
    assert StyledPrintApp is not None


def test_builder_schemas() -> None:
    """Test that each builder has expected elements in schema."""
    from genro_print import PrintBuilder, PrintLRCBuilder, PrintStyledBuilder

    print_tags = {n.label for n in PrintBuilder._class_schema if not n.label.startswith("@")}
    assert "document" in print_tags
    assert "paragraph" in print_tags
    assert "drawstring" in print_tags
    assert "bar_chart" in print_tags

    lrc_tags = {n.label for n in PrintLRCBuilder._class_schema if not n.label.startswith("@")}
    assert "document" in lrc_tags
    assert "layout" in lrc_tags
    assert "row" in lrc_tags
    assert "cell" in lrc_tags

    styled_tags = {n.label for n in PrintStyledBuilder._class_schema if not n.label.startswith("@")}
    assert "document" in styled_tags
    assert "styledblock" in styled_tags
    assert "statictext" in styled_tags
    assert "labeledtext" in styled_tags


def test_print_app_render() -> None:
    """Test PrintApp end-to-end PDF generation."""
    from genro_print import PrintApp

    class TestReport(PrintApp):
        def recipe(self, root):
            root.document(width=210.0, height=297.0)
            root.paragraph(content="Hello World")

    report = TestReport()
    pdf = report.render()
    assert isinstance(pdf, bytes)
    assert len(pdf) > 100
    assert pdf[:5] == b"%PDF-"


def test_lrc_app_render() -> None:
    """Test LRCPrintApp end-to-end PDF generation."""
    from genro_print import LRCPrintApp

    class TestReport(LRCPrintApp):
        def recipe(self, root):
            layout = root.layout(width=210.0, height=297.0, top=10.0, bottom=10.0)
            row = layout.row(height=30.0)
            row.cell(width=60.0, content="Left")
            row.cell(content="Right")

    report = TestReport()
    pdf = report.render()
    assert isinstance(pdf, bytes)
    assert len(pdf) > 100
    assert pdf[:5] == b"%PDF-"


def test_styled_app_render() -> None:
    """Test StyledPrintApp end-to-end PDF generation."""
    from genro_print import StyledPrintApp

    class TestReport(StyledPrintApp):
        def recipe(self, root):
            doc = root.document(width=210.0, height=297.0)
            block = doc.styledblock(fontname="Helvetica-Bold", size=14.0, color="navy")
            block.statictext(x=20.0, y=50.0, text="Test")

    report = TestReport()
    pdf = report.render()
    assert isinstance(pdf, bytes)
    assert len(pdf) > 100
    assert pdf[:5] == b"%PDF-"


def test_data_binding() -> None:
    """Test ^pointer data binding with store()."""
    from genro_print import PrintApp

    class TestReport(PrintApp):
        def store(self, data):
            data["title"] = "Dynamic Title"

        def recipe(self, root):
            root.document(width=210.0, height=297.0)
            root.paragraph(content="^title", style="Title")

    report = TestReport()
    pdf = report.render()
    assert isinstance(pdf, bytes)
    assert len(pdf) > 100
