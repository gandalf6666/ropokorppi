from robocorp.tasks import task
from robocorp import browser
import shutil

from RPA.HTTP import HTTP
from RPA.Tables import Tables 
from RPA.PDF import PDF

import time

def get_orders():
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    orders = Tables().read_table_from_csv(path="orders.csv",header=True)
    return orders

def open_robot_order_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def close_annoying_modal():
    page = browser.page()
    page.click("button:text('OK')")

def fill_form(orders):
    page = browser.page()
    page.select_option("#head", str(orders["Head"]))
    page.click("#id-body-"+str(orders["Body"]))
    page.get_by_placeholder("Enter the part number for the").fill(str(orders["Legs"]))
    page.fill("#address", orders["Address"])
    page.click("button:text('Preview')")
    while page.is_visible("#order"):
        page.click("button:text('ORDER')")
        time.sleep(1)

def store_receipt_as_pdf(order_number):
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf_file = "output/receipts/"+order_number+".pdf"
    pdf.html_to_pdf(receipt_html, pdf_file)
    return pdf_file

def screenshot_robot(order_number):
    page = browser.page()
    screenshot = "output/"+order_number+".png"
    page.screenshot(path=screenshot)
    return screenshot

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    pdf.add_files_to_pdf(screenshot, pdf_file, True)

def next_order():
    page = browser.page()
    page.click("button:text('ORDER ANOTHER ROBOT')")

def archive_receipts(save_to, folder_to_archive):
    shutil.make_archive(save_to+"/"+folder_to_archive, "zip", save_to, folder_to_archive)

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=500,
    )
    orders = get_orders()
    open_robot_order_website()
    for row in orders:
        close_annoying_modal()
        fill_form(row)
        pdf_file=store_receipt_as_pdf(str(row["Order number"]))
        shot=screenshot_robot(str(row["Order number"]))
        screenshot = [shot]
        embed_screenshot_to_receipt(screenshot, pdf_file)
        next_order()
    archive_receipts("output", "receipts")
