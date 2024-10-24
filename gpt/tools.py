from langchain.tools import Tool

def text_tool():
    from .views import generate_text  
    return Tool(
        name="Text Generation Tool",
        func=generate_text, 
        description="Generate text from a given prompt"
    )

def image_tool():
    from .views import generate_text_to_image  
    return Tool(
        name="Image Generation Tool",
        func=generate_text_to_image,
        description="Generate an image from a given prompt"
    )
