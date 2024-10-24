from django.shortcuts import render, redirect
from django.http import JsonResponse
import html2text
import uuid
from bs4 import BeautifulSoup
from django.views.decorators.csrf import csrf_exempt
import requests
import base64
import time
import threading
import json
from .models import chat_history
from django.conf import settings
from django.contrib import messages
import re
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models.functions import TruncDate
from datetime import datetime
from django.core.serializers import serialize
import os
from django.utils.html import escape
from django.utils.safestring import mark_safe
from huggingface_hub import InferenceClient
client = InferenceClient(api_key=settings.API_KEY_HUGGINGFACE)

from langchain.memory import ConversationBufferMemory


from langchain_core.messages import HumanMessage, AIMessage

def get_or_create_memory(request):
    chat_history_user = request.session.get('chat_history', [])
    
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        input_key="input",
        output_key="output"
    )

    
    if chat_history_user:
        for item in chat_history_user:
            if item['role'] == 'user':
                memory.chat_memory.add_message(HumanMessage(content=item['content']))
            elif item['role'] == 'bot':
                memory.chat_memory.add_message(AIMessage(content=item['content']))

    
    if request.user.is_authenticated:
        uuid_is = request.session['new_uuid']
        user_history = chat_history.objects.filter(uuid=uuid_is).order_by('date')
        for chat in user_history:
            memory.chat_memory.add_message(HumanMessage(content=chat.user_message))
            memory.chat_memory.add_message(AIMessage(content=chat.bot_response))

    return memory





def generate_unique_uuid():
    while True:
        new_uuid = uuid.uuid4()
        check_uuid = chat_history.objects.filter(uuid=str(new_uuid)).exists()
        if not check_uuid:
            return str(new_uuid)

def home(request):
    try:
        if 'new_uuid' in request.session:
            pass
        else:
            raise KeyError("UUID not found")
    except Exception as e:
        
        if request.user.is_authenticated:
            if 'new_uuid' in request.session:
                pass
            else:
                new_chat_id = generate_unique_uuid()
                request.session['new_uuid'] = new_chat_id
        else:
            
            print(f"User not authenticated or missing uuid: {e}")

    all_chats = chat_history.objects.filter(
        username=request.user.username
    ).annotate(
        chat_date=TruncDate('timestamp')
    ).distinct('chat_date').order_by('-chat_date')  
    formatted_dates = [chat.chat_date.strftime('%b. %d, %Y') for chat in all_chats]
    return render(request, 'index.html',{'all_chats':formatted_dates})






def generate_text(request, prompt, memory):
  
    memory = get_or_create_memory(request)

 
   
    
    chat_uuid = ""
    try:
        chat_uuid = request.session['new_uuid']
    except Exception as e:
        print("User not authenticated or no UUID: ", e)

    url = settings.TEXT_TO_TEXT  

    payload = json.dumps({
        "messages": [{"role": "user", "content": prompt}],
        "mode": "instruct",
        "max_new_tokens": 200,
        "temperature": 0.8
    })

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {settings.AUTH_TOKEN}' 
    }

    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        data = json.loads(response.text)
        content = data['choices'][0]['message']['content']
        
       
        memory.save_context({"input": prompt}, {"output": content})

       
        # request.session['chat_history'] = memory.chat_memory.messages

  
        chat_save = chat_history.objects.create(user_message=prompt, uuid=chat_uuid, bot_response=content, username=request.user.username)
        chat_save.save()
      
    else:
        content = "I can't understand, please try again"
        chat_save = chat_history.objects.create(user_message=prompt, uuid=chat_uuid, bot_response=content, username=request.user.username)
        chat_save.save()
    return content


def get_chat_history(request):
    memory = get_or_create_memory(request)
    chat_history = memory.chat_memory

    
    try:
        
        history_str = str(chat_history)
    except Exception as e:
        history_str = f"Error converting chat history to string: {e}"

   
    return chat_history





def generate_text_to_image(request, prompt, memory):
    memory = get_or_create_memory(request)


   
    chat_uuid = ""
    try:
        chat_uuid = request.session['new_uuid']
    except Exception as e:
        print("User not authenticated or no UUID: ", e)

    try:
        url = settings.TEXT_TO_IMAGE  

        payload = {"prompt": prompt, "steps": 5}
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            image_data = base64.b64decode(response.json().get('image'))
            image_filename = f"{prompt.replace(' ', '_')}.png"
            media_directory = os.path.join(settings.MEDIA_ROOT, 'Bot_response')
            media_path = os.path.join(media_directory, image_filename)

            os.makedirs(media_directory, exist_ok=True)
            with open(media_path, 'wb') as f:
                f.write(image_data)

            chat_save = chat_history.objects.create(
                user_message=prompt,
                bot_response="Generated Image",
                image_path=os.path.join('Bot_response', image_filename),
                username=request.user.username,
                uuid=chat_uuid
            )
            chat_save.save()
            memory.save_context({"input": prompt}, {"output": image_filename})
            return image_filename

        else:
            raise Exception("Image generation failed")

    except Exception as e:
        print(f"Error generating image: {e}")
        chat_save = chat_history.objects.create(
            user_message=prompt,
            bot_response=str(e),
            username=request.user.username,
            uuid=chat_uuid
        )
        chat_save.save()
        return "Something went wrong..!!!"





# def generate_text_to_image(request, prompt):
#     try:
#         # Generate the image
#         output = client.text_to_image(
#             prompt=prompt,
#             model=settings.TEXT_IMAGE_MODEL,
#             num_images=1,
#             guidance_scale=7.5,
#         )

#         # Construct the image filename and path
#         image_filename = f"{prompt.replace(' ', '_')}.png"
#         media_directory = os.path.join(settings.MEDIA_ROOT, 'Bot_response')  # Subfolder
#         media_path = os.path.join(media_directory, image_filename)

#         # Ensure the Bot_response directory exists
#         os.makedirs(media_directory, exist_ok=True)

#         # Save the output image to the media path
#         output.save(media_path)

#         # Save the chat history with the image path
#         chat_save = chat_history.objects.create(
#             user_message=prompt,
#             bot_response="Generated Image",
#             image_path=os.path.join('Bot_response', image_filename),  # Store relative path
#             username=request.user.username
#         )
#         chat_save.save()

#         print(f"Image generated and saved as {media_path}")
#         return image_filename  # Returning the filename

#     except Exception as e:
#         print(f"Error generating image: {e}")
#         return None

    


def image_text_to_text(request, prompt, image, memory):
    memory = get_or_create_memory(request)
  
    

    
    image_name = os.path.basename(image)
    file_name = os.path.join(settings.MEDIA_ROOT, 'User_Uploaded', image_name)

    try:
       
        if not os.path.exists(file_name):
            return "The specified image file does not exist."

        with open(file_name, "rb") as f:
            encoded_image = base64.b64encode(f.read()).decode('utf-8')

       
        url = settings.IMAGE_TEXT_TO_TEXT
        payload = json.dumps({
            "model": "llava",
            "prompt": prompt,
            "images": [encoded_image]
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer 4321'  
        }

        
        response = requests.post(url, headers=headers, data=payload, verify=False)
        
        if response.status_code == 200:
            data = json.loads(response.text)
            
            if 'output' in data:
                memory.save_context({"input": prompt}, {"output": data['output']})
                chat_save = chat_history.objects.create(
                    user_message=prompt,
                    bot_response=data['output'],
                    input_image=f"User_Uploaded/{image_name}",
                    username=request.user.username
                )
                chat_save.save()
                return data['output'] 
            else:
                return "Unexpected response structure from API."
        else:
            return "I can't understand, please try again."

    except Exception as e:
        print(f"Error in image to text processing: {e}") 
        chat_save = chat_history.objects.create(
            user_message=prompt,
            bot_response=str(e),
            input_image=f"User_Uploaded/{image_name}",
            username=request.user.username
        )
        chat_save.save()
        return "Something went wrong..!!!"



def authentication(request):
    if request.method == "POST":
        username = request.POST.get('email', '')
        password = request.POST.get('password', '')
        if not User.objects.filter(username=username).exists():
            user = User.objects.filter(username=username)
        
            if user.exists():
                messages.info(request, "Username already taken!")
                return redirect('authentication')
            else:
                user = User.objects.create_user(
                    username=username,
                    email=username
                )
                user.set_password(password)
                user.save()
                user = authenticate(username=username, password=password)
                login(request, user)
                return redirect('home')
        else:
            user = authenticate(username=username, password=password)
            if user is None:
                messages.error(request, "Invalid Password")
                return redirect('authentication')
            else:
               
                login(request, user)
                return redirect('home')

        
        
    return render(request, 'login.html')

def handlelogout(request):
    logout(request)
    return redirect('home')

@csrf_exempt
def session_chat(request):
    if request.method=="POST":
        
        date = request.POST.get('date', '')
        dt = datetime.strptime(date, "%b. %d, %Y")
        formatted_date = dt.strftime("%Y-%m-%d")
 
        try:
            user_chat_history = chat_history.objects.filter(date=formatted_date, username=request.user.username)
            user_history_serialized = serialize('json', user_chat_history)
            return JsonResponse({'success': True, 'user_history':user_history_serialized })
        except Exception as e:
            print("Chat History Error : ", e)
            return JsonResponse({'success':False, 'user_history':"Something went wrong..!! Try Again..!"})
    else:
        return JsonResponse({'success':False, 'user_history':"Something went wrong..!! Try Again..!"})
    






@csrf_exempt
def chat_with_bot(request):
    try:
        if request.method == "POST":
            prompt = request.POST.get('prompt', '')
            file = request.FILES.get('file', None)
            option = request.POST.get('option')
            
            
            memory = ConversationBufferMemory(memory_key="chat_history", input_key="input", output_key="output")
            try:
                def process_request(response):
                    if option:
                        if option == "Text to Image":
                            response['content'] = generate_text_to_image(request, prompt, memory)
                        elif option == "Image Text to Text":
                            media_directory = os.path.join(settings.MEDIA_ROOT, 'User_Uploaded')
                            os.makedirs(media_directory, exist_ok=True)
                            file_path = os.path.join(media_directory, file.name)
                            with open(file_path, 'wb+') as destination:
                                for chunk in file.chunks():
                                    destination.write(chunk)
                            response['content'] = image_text_to_text(request, prompt, file_path, memory)
                        else:

                            chat_uuid = request.session.get('new_uuid', generate_unique_uuid())
                    
                            response['content'] = generate_text(request, prompt, memory)
                    else:
                        response['error'] = 'Invalid option provided.'
            except Exception as e:
                print(e)
                

            response = {}

            thread = threading.Thread(target=process_request, args=(response,))
            thread.start()
            thread.join(timeout=30)

            if thread.is_alive():
                return JsonResponse({'success': False, 'message': 'Connection timed out. Please try again later.'})
            else:
                return JsonResponse({'success': True, 'message': response.get('content', response.get('error', 'Something went wrong.'))})

        else:
            return JsonResponse({'success': False, 'message': 'Invalid request method.'})

    except Exception as e:
        error_message = str(e)
        error_code = type(e).__name__
       
        user_friendly_message = 'Something went wrong. Please try again later.'

        return JsonResponse({
            'success': False,
            'message': user_friendly_message,
            'error_details': {
                'message': error_message,
                'code': error_code
            }
        })


@csrf_exempt
def new_chat(request):

    if request.user.is_authenticated:
        try:
            if 'new_uuid' in request.session:
                
                del request.session['new_uuid']
            else:
                new_chat_id = generate_unique_uuid()
                
                request.session['new_uuid'] = new_chat_id

        except:
            pass
    else:
        pass
    return JsonResponse({'success': True, 'redirect_url':('')})


