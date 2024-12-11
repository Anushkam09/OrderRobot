from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robot():
    """
    get .csv file
    order robots on the rsb website
    save each html receipt as pdf
    save ss of each robot order
    embed ss in pdf
    create zip file of all pdfs

    """
    open_the_website()
    orders = get_orders()
    for order in orders:
        close_pop_up()
        fill_in_orders(order)
    archive_to_zip()
    

def open_the_website():
    """This will open the robocorp website"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def get_orders():
    """Download the orders file, read it as a table, and return the result"""
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)
    library = Tables()
    orders = library.read_table_from_csv(
    "orders.csv", columns=["Order number","Head","Body","Legs","Address"]
    )
    return orders

def close_pop_up():
    """Close the consitutional rights pop up"""
    page = browser.page()
    page.click("text=OK")

def fill_in_orders(order):
    """Takes in orders and fill them"""
    print(order)
    page = browser.page()
    page.select_option("#head", str(order["Head"]))
    page.click("#id-body-"+str(order["Body"]))
    page.fill("input[placeholder='Enter the part number for the legs']", value= order["Legs"])
    page.fill("#address", order["Address"])
    page.click("#order")
    page = browser.page()
    element = page.locator("div.alert.alert-danger")
    if element.count() > 0:
        fill_in_orders(order)
    else:
        pdf_path = store_as_pdf(order["Order number"])
        img_path = get_the_ss(order["Order number"])
        embed_screenshot_to_receipt(pdf_path,img_path)
        page.click("text=ORDER ANOTHER ROBOT")

def store_as_pdf(order_num):
    page = browser.page()
    receipt = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf_path = "output/pdfs/" + str(order_num) +".pdf"
    pdf.html_to_pdf(receipt, pdf_path)
    return pdf_path

def get_the_ss(order_num):
    page = browser.page()
    browser.configure(
        slowmo= 200
    )
    img_path = "output/imgs/" +str(order_num)+ ".png"
    page.locator("#robot-preview-image").screenshot(path= img_path)
    return img_path

def embed_screenshot_to_receipt(pdf_path,img_path):
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(image_path=img_path, source_path=pdf_path, output_path=pdf_path)

def archive_to_zip():
    lib = Archive()
    lib.archive_folder_with_zip("output/pdfs", "output/mydocs.zip")


