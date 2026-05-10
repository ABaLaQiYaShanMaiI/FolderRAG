import logging

logger = logging.getLogger(__name__)


def parse_office(filepath, filetype):
    try:
        if filetype == "docx":
            from docx import Document
            doc = Document(filepath)
            text = "\n".join(para.text for para in doc.paragraphs)
            return {
                "extract_type": "text",
                "text": text,
                "metadata": {"mime": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
            }
        elif filetype == "pptx":
            from pptx import Presentation
            prs = Presentation(filepath)
            text = "\n".join(
                shape.text for slide in prs.slides for shape in slide.shapes if hasattr(shape, "text")
            )
            return {
                "extract_type": "text",
                "text": text,
                "metadata": {"mime": "application/vnd.openxmlformats-officedocument.presentationml.presentation"},
            }
        elif filetype == "xlsx":
            import openpyxl
            wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
            text_parts = []
            for sheet_name in wb.sheetnames:
                ws = wb[sheet_name]
                text_parts.append(f"--- Sheet: {sheet_name} ---")
                for row in ws.iter_rows(values_only=True):
                    row_text = " | ".join(str(cell) if cell is not None else "" for cell in row)
                    if row_text.strip():
                        text_parts.append(row_text)
            text = "\n".join(text_parts)
            wb.close()
            return {
                "extract_type": "text",
                "text": text,
                "metadata": {"mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
            }
        return None
    except Exception as e:
        logger.exception("Failed to parse office file %s (type=%s): %s", filepath, filetype, e)
        return None
