#import shinyswatch
import os
from typing import List
from shiny import *
from shiny.types import NavSetArg
from shiny.types import ImgData
from shiny.ui import h4
import skimage.io as io
from skimage import filters, segmentation
from skimage.color import rgb2gray
import matplotlib.pyplot as plt
import numpy as np
import requests
from shinywidgets import output_widget, register_widget
from plotly import graph_objects as go
from utils import *
from dotenv import load_dotenv

def nav_controls(prefix: str) -> List[NavSetArg]:
    return [
        ui.nav(
            "basic",
            "Adjust the slider and press the Show button for a normal distribution",
            ui.layout_sidebar(
                ui.panel_sidebar(
                    ui.input_slider("slider1", "N", 0, 100, 20),
                    ui.input_radio_buttons(
                        "colorRB", "Color of the graph", ["red", "blue", "green"]
                    ),
                    
                    ui.input_action_button(
                        "run", "Show", class_="btn-primary w-100"
                    ), 
                ),
                
                 ui.panel_main(
                    ui.output_plot("plot", hover=True),
                ),
            ) 
        ), 
        ui.nav(
        "Widgets",
            output_widget("fig", width='1200px', height='1200px'), 
        ),     
        ui.nav(
            "API",
            "Choose an image category and push <Get> to get a random image.",
            ui.layout_sidebar(
                ui.panel_sidebar(
                    ui.input_select(id="categorySelect",
                         label="Select a category",
                         choices=["nature", "technology", "wildlife"],
                    ),
                    ui.input_action_button("apiGet","Get", class_="btn-primary w-100"),
                ),            
                ui.panel_main(ui.panel_well((ui.output_image("image", width='10%', height='10%', inline=True),), width=4))
            ), 
            ui.panel_conditional(
                "output.image",
                ui.layout_sidebar(
                    ui.panel_sidebar(               
                        ui.input_action_button("blurBtn","Segmentize", class_="btn-primary w-100"),
                    ),
                    ui.panel_main(
                        ui.output_image("processedplot", inline=False),
                    ),
                )   
            )
        ),
        ui.nav_control(
            ui.a(
                "Py-Shiny",
                href="https://shiny.posit.co/py/",
                target="_blank",
            )
        ),
    ]


app_ui = ui.page_navbar(
    #shinyswatch.theme.superhero(),
    *nav_controls("page_navbar"),
    title="Shiny for Python demo",
    bg="#AAC426",
    inverse=False,
    fluid=False,
    id="navbar_id",
    # footer=ui.div(
    #     {"style": "width:80%;margin: 0 auto"},
    #     ui.tags.style(
    #         """
    #         h4 {
    #             margin-top: 3em;
    #         }
    #         """
    #     ),
       
    #     #h4("Some real cool tabs to show"),
    #     #ui.navset_tab_card(*nav_controls("Demo of Shiny")),
    #    # h4("The result:"),
    #     #ui.output_plot("plot"),

    #         ),  
 )
        

def server(input, output, session):

    load_dotenv()
    # Register widgets
    fig = create_graph()  
    register_widget("fig", fig)

    ##############
    #   1st TAB  #
    ############## 
    @output
    @render.plot
    @reactive.event(input.run)
    def plot():
        np.random.seed(19680801)
        x = 100 + 15 * np.random.randn(437)
        plt.hist(x, input.slider1(), density=True, color=input.colorRB())

     ##############
    #   2nd TAB  #
    ############## 
    @reactive.Effect
    def _():
        fig
    ##############
    #   3rd TAB  #
    ############## 
    @output
    @render.image
    @reactive.event(input.apiGet)
    async def image() -> ImgData:
        category=str(input.categorySelect())
        apikey = os.getenv("NINJA_API_KEY")
        api_url = 'https://api.api-ninjas.com/v1/randomimage?category={}'.format(category)
        with open('file.png', 'wb') as f:
             f.write(requests.get(api_url, headers={'X-Api-Key': apikey, 'Accept': 'image/jpg'}).content)
        return {"src": "file.png", "width":'50%',"height":'50%',}
    
    @output
    @render.image
    @reactive.event(input.blurBtn)
    async def processedplot():
        # Setting plot size 
        plt.figure(figsize=(8, 8))

        # Sample Image of scikit-image package
        img = io.imread("file.png")
        gray_img = rgb2gray(img)
        # Computing Otsu's thresholding value
        threshold = filters.threshold_otsu(gray_img)
 
        # Computing binarized values using the obtained
        # threshold
        binarized_img = (gray_img > threshold)*1
        plt.subplot(2,2,1)
        plt.title("Threshold: >"+str(threshold))
 
        # Displaying the binarized image
        plt.imshow(binarized_img, cmap = "gray")
 
        # Computing Ni black's local pixel
        # threshold values for every pixel
        threshold = filters.threshold_niblack(gray_img)
 
        # Computing binarized values using the obtained
        # threshold
        binarized_img = (gray_img > threshold)*1
        plt.subplot(2,2,2)
        plt.title("Niblack Thresholding")
 
        # Displaying the binarized image
        plt.imshow(binarized_img, cmap = "gray")
 
        # Computing Sauvola's local pixel threshold
        # values for every pixel - Not Binarized
        threshold = filters.threshold_sauvola(gray_img)
        plt.subplot(2,2,3)
        plt.title("Sauvola Thresholding (ST)")
 
        # Displaying the local threshold values
        plt.imshow(threshold, cmap = "gray")
 
        # Computing Sauvola's local pixel
        # threshold values for every pixel - Binarized
        binarized_img= (gray_img > threshold)*1
        plt.subplot(2,2,4)
        plt.title("ST - Converting to 0's and 1's")
 
        # Displaying the binarized image
        plt.imshow(binarized_img, cmap = "gray")
        plt.savefig("processed.png")
        return {"src": "processed.png", "width":'90%',}
        

app = App(app_ui, server, debug=False)