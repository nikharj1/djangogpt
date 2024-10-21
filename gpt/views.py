from django.shortcuts import render, redirect
from django.http import JsonResponse
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
from huggingface_hub import InferenceClient
client = InferenceClient(api_key=settings.API_KEY_HUGGINGFACE)


def home(request):
    all_chats = chat_history.objects.filter(
        username=request.user.username
    ).annotate(
        chat_date=TruncDate('timestamp')
    ).distinct('chat_date').order_by('-chat_date')  
    formatted_dates = [chat.chat_date.strftime('%b. %d, %Y') for chat in all_chats]
    return render(request, 'index.html',{'all_chats':formatted_dates})






def generate_text(request, prompt):
    content = ""
    url = settings.TEXT_TO_TEXT
    
    payload = json.dumps({
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "mode": "instruct",
        "max_new_tokens": 200,
        "temperature": 0.8
    })
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer 4321' 
    }
    
    response = requests.post(url, headers=headers, data=payload)
    
    if response.status_code == 200:
       
        data = json.loads(response.text)
        
        content = data['choices'][0]['message']['content']
        clean_content = re.sub(r'<[^>]+>', '', content)
    
        
        chat_save = chat_history.objects.create(user_message=prompt, bot_response=content, username=request.user.username)
        chat_save.save()
    else:
        clean_content = "i can't understand please try again"
        chat_save = chat_history.objects.create(user_message=prompt, bot_response=content, username=request.user.username)
        chat_save.save()
    return clean_content

def generate_text_to_image(request, prompt):
    try:
        url = settings.TEXT_TO_IMAGE
        payload = {
            "prompt": prompt,
            "steps": 5
        }
        response = requests.post(url=f'{url}', json=payload, verify=False)
        r = response.json()

        image_data = base64.b64decode(r['images'][0])
        image_filename = f"{prompt.replace(' ', '_')}.png"
        media_directory = os.path.join(settings.MEDIA_ROOT, 'Bot_response') 
        media_path = os.path.join(media_directory, image_filename)

       
        os.makedirs(media_directory, exist_ok=True)

        
        with open(media_path, 'wb') as f:
            f.write(image_data)

        # Save the chat history with the image path
        chat_save = chat_history.objects.create(
            user_message=prompt,
            bot_response="Generated Image",
            image_path=os.path.join('Bot_response', image_filename),
            username=request.user.username
        )
        chat_save.save()
        return image_filename
        

    except Exception as e:
        print(f"Error generating image: {e}")
        chat_save = chat_history.objects.create(
            user_message=prompt,
            bot_response=e,
            username=request.user.username
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

    
def image_text_to_text(request, prompt, image):
    file_name = os.path.basename(image)
    try:
        encoded_image = base64.b64encode(image.read()).decode('utf-8')
        url = settings.IMAGE_TEXT_TO_TEXT
        payload = json.dumps({
            "model": "llava",
            "prompt": prompt,
            "images":[encoded_image]
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer 4321'
        }
        response = requests.post(url, headers=headers, data=payload, verify=False)
        if response.status_code == 200:
            data = json.loads(response.text)
            chat_save = chat_history.objects.create(
                user_message=prompt,
                bot_response=data,
                input_image =f"User_Uploaded/{file_name}",
                username=request.user.username
            )
            chat_save.save()
        else:
            content = "i can't understand please try again"
        return content
    except Exception as e:
        print(f"Error image to text visionary: {e}")
        chat_save = chat_history.objects.create(
            user_message=prompt,
            bot_response=e,
            input_image =f"User_Uploaded/{file_name}",
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
                # Log in the user and redirect to the home page upon successful login
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

            
            def process_request(response):
                if option:
                    if option == "Text to Image":
                        response['content'] = generate_text_to_image(request, prompt)
                    elif option == "Image Text to Text":
                        media_directory = os.path.join(settings.MEDIA_ROOT, 'User_Uploaded')
                        os.makedirs(media_directory, exist_ok=True)
                        file_path = os.path.join(media_directory, file.name)
                        with open(file_path, 'wb+') as destination:
                            for chunk in file.chunks():
                                destination.write(chunk)
                        response['content'] = image_text_to_text(request, prompt, file_path)
                    else:
                        response['content'] = generate_text(request, prompt)
                else:
                    response['error'] = 'Invalid option provided.'

           
            response = {}

        
            thread = threading.Thread(target=process_request, args=(response,))
            thread.start()

           
            thread.join(timeout=30)

           
            if thread.is_alive():
                return JsonResponse({'success': False, 'message': 'Connection timed out. Please try again later.'})
            else:
                # Return the processed response
                if 'content' in response:
                    return JsonResponse({'success': True, 'message': response['content']})
                else:
                    return JsonResponse({'success': False, 'message': response.get('error', 'Something went wrong.')})

        else:
            return JsonResponse({'success': False, 'message': 'Invalid request method.'})

    except Exception as e:
        error_message = str(e)
        error_code = type(e).__name__
        print(f'Error! Code: {error_code}, Message: {error_message}')
        user_friendly_message = 'Something went wrong. Please try again later.'

        return JsonResponse({
            'success': False,
            'message': user_friendly_message,
            'error_details': {
                'message': error_message,
                'code': error_code
            }
        })



