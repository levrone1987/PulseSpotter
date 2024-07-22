from nicegui import ui
from datetime import datetime
from PIL import Image

# function to handle the search action
def perform_search():
    selected_websites = [site for idx, site in enumerate(websites) if website_checks[idx].value]
    start_date = start_date_input.value
    end_date = end_date_input.value
    keyword = keyword_input.value
    
    # Display the selected values (For demonstration, normally you would perform your search here)
    print(f"Websites: {selected_websites}")
    print(f"Start Date: {start_date}")
    print(f"End Date: {end_date}")
    print(f"Keyword: {keyword}")
    
    # load and display the image
    image_path = "sample.jpg"  # Update this path to your .jpeg file
    with Image.open(image_path) as img:
        ui.image(img).classes('w-full h-full')

# list of websites
websites = ["Website 1", "Website 2", "Website 3", "Website 4"]
website_checks = []

# create the GUI
@ui.page('/')
def main_page():
    ui.label('PulseSpotter').classes('text-2xl mb-4')

    with ui.row().classes('w-full'):
        with ui.card():
            ui.label('Select Websites').classes('text-xl')
            for site in websites:
                checkbox = ui.checkbox(site)
                website_checks.append(checkbox)

        with ui.row().classes('gap-4'):
            with ui.card():
                ui.label('Start Date:').classes('text-xl')
                global start_date_input
                start_date_input = ui.date(value=datetime.now().strftime('%Y-%m-%d'))

            with ui.card():
                ui.label('End Date:').classes('text-xl')
                global end_date_input
                end_date_input = ui.date(value=datetime.now().strftime('%Y-%m-%d'))

        with ui.card():
            ui.label('Keyword of Interest').classes('text-xl')
            global keyword_input
            keyword_input = ui.input()

    ui.button('Search', on_click=perform_search).classes('mt-4')

    with ui.row().classes('w-full mt-4'):
        ui.label('Visualization').classes('text-xl')
        # Placeholder for where the image would be displayed
        #ui.image('topics_demo.jpg').classes('w-full h-96')  # Making the image larger
        #ui.image('topics_demo.jpg').classes('w-1/2 h-48')
        ui.image('topics_demo.jpg').classes('w-1/2')
ui.run()

