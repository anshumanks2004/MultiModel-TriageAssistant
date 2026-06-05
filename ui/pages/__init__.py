# pages package — import each page module for use in app.py
from ui.pages import about_page, home_page, image_page, report_page, symptom_page

__all__ = ["home_page", "symptom_page", "image_page", "report_page", "about_page"]
