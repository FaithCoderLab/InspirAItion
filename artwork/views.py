from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.conf import settings
from azure.storage.blob import BlobServiceClient
import random
import json
import requests
from io import BytesIO
from .models import Artwork, ArtworkComment, ArtworkTag
from .forms import ArtworkForm, ArtworkCommentForm

# 데모용 샘플 데이터
SAMPLE_STYLES = [
    "realistic", "anime", "digital art", "oil painting",
    "watercolour", "pencil sketch", "3D render", "pixel art"
]

SAMPLE_SUBJECTS = [
    "landscape", "portrait", "still life", "abstract",
    "fantasy scene", "sci-fi city", "nature", "character"
]

SAMPLE_PROMPTS = [
    "A serene mountain landscape at sunset with a lake reflecting the sky",
    "A futuristic cityscape with flying cars and neon lights",
    "A mystical forest with glowing mushrooms and fairy lights",
    "An abstract representation of human emotions using vibrant colours",
    "A cosy cafe interior with warm lighting and vintage decorations"
]

def save_image_to_blob(image_url, filename):
    """외부 이미지를 Blob Storage에 저장"""
    try:
        response = requests.get(image_url)
        if response.status_code != 200:
            print(f"이미지 다운로드 실패: {response.status_code}")
            return None

        image_content = BytesIO(response.content)

        blob_service_client = BlobServiceClient.from_connection_string(
            settings.AZURE_CONNECTION_STRING
        )
        container_name = settings.CONTAINER_NAME
        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob=filename
        )

        blob_client.upload_blob(image_content, overwrite=True)
        print("Blob URL: {blob_client.url}")
        return blob_client.url
    except Exception as e:
        print("==== Blob 업로드 실패 ====")
        print("에러:", str(e))
        return None
    
@login_required
def demo_generate_image(request):
    """데모용 이미지 생성 페이지"""
    if request.method == 'POST':
        if 'generate' in request.POST:
            selected_style = request.POST.get('style', random.choice(SAMPLE_STYLES))
            selected_subject = request.POST.get('subject', random.choice(SAMPLE_SUBJECTS))
            prompt = request.POST.get('prompt', random.choice(SAMPLE_PROMPTS))

            image_number = random.randint(1, 1000)
            temp_image_url = f"https://placekitten.com/512/512"

            filename = f"artwork_{request.user.id}_{image_number}.jpg"
            blob_image_url = save_image_to_blob(temp_image_url, filename)

            if not blob_image_url:
                messages.error(request, '이미지 저장에 실패했습니다.')
                return redirect('artwork:demo_generate')

            metadata = {
                'model': 'stable-diffusion-v1.5',
                'style': selected_style,
                'subject': selected_subject,
                'steps': random.randint(20, 50),
                'cfg_scale': round(random.uniform(5.0, 8.0), 1),
                'seed': random.randint(1000000, 9999999)
            }

            return render(request, 'artwork/artwork_form.html', {
                'styles': SAMPLE_STYLES,
                'subjects': SAMPLE_SUBJECTS,
                'sample_prompts': SAMPLE_PROMPTS,
                'generated_image': {
                    'url': blob_image_url,
                    'style': selected_style,
                    'subject': selected_subject,
                    'metadata': metadata
                },
                'form': ArtworkForm(initial={
                    'title': f"{selected_style.title()} {selected_subject}",
                    'description': f"Generated using prompt: {prompt}",
                    'image_url': blob_image_url,
                    'prompt': 'prompt',
                    'ai_metadata': json.dumps(metadata),
                    'is_public': True
                })
            })
        else:
            form = ArtworkForm(request.POST)
            if form.is_valid():
                artwork = form.save(commit=False)
                artwork.user = request.user
                artwork.save()
                messages.success(request, '작품이 성공적으로 저장되었습니다.')
                return redirect('artwork:list')
            else:
                messages.error(request, '작품 저장에 실패했습니다. 입력을 확인해주세요.')
    
    return render(request, 'artwork/demo_generate.html', {
        'styles': SAMPLE_STYLES,
        'subjects': SAMPLE_SUBJECTS,
        'sample_prompts': SAMPLE_PROMPTS
    })

@login_required
def create_artwork(request):
    """AI 생성 이미지 작품 저장"""
    if request.method == 'POST':
        form = ArtworkForm(request.POST)
        if form.is_valid():
            artwork = form.save(commit=False)
            artwork.user = request.user
            artwork.save()

            tags = request.POST.get('tags', '').split(',')
            for tag_name in tags:
                tag_name = tag_name.strip()
                if tag_name:
                    tag, _ = ArtworkTag.objects.get_or_create(name=tag_name)
                    artwork.tags.add(tag)

            messages.success(request, '작품이 성공적으로 저장되었습니다.')
            return redirect('artwork_detail', pk=artwork.pk)
    else:
        initial_data = {
            'image_url': request.GET.get('image_url'),
            'prompt': request.GET.get('prompt'),
            'negative_prompt': request.GET.get('negative_prompt'),
            'ai_metadata': request.GET.get('metadata', '{}')
        }
        form = ArtworkForm(initial=initial_data)

    return render(request, 'artwork/artwork_form.html', {'form': form})

def artwork_list(request):
    """작품 목록 표시"""
    if request.user.is_authenticated:
        artworks = Artwork.objects.filter(
            Q(is_public=True) | Q(user=request.user)
        ).select_related('user')
    else:
        artworks = Artwork.objects.filter(is_public=True).select_related('user')

    return render(request, 'artwork/artwork_list.html', {
        'artworks': artworks
    })

def artwork_detail(request, pk):
    """작품 상세 정보"""
    artwork = get_object_or_404(Artwork, pk=pk)

    if not artwork.is_public and artwork.user != request.user:
        messages.error(request, '접근 권한이 없습니다.')
        return redirect('artwork_list')

    return render(request, 'artwork/artwork_detail.html', {
        'artwork': artwork
    })

@login_required
def artwork_edit(request, pk):
    """작품 정보 수정"""
    artwork = get_object_or_404(Artwork, pk=pk, user=request.user)

    if request.method == 'POST':
        form = ArtworkForm(request.POST, instance=artwork)
        if form.is_valid():
            form.save()
            messages.success(request, '작품 정보가 수정되었습니다.')
            return redirect('artwork:detail', pk=pk)
    else:
        form = ArtworkForm(instance=artwork)

    return render(request, 'artwork/artwork_form.html', {
        'form': form,
        'artwork': artwork
    })

@login_required
def delete_artwork(request, pk):
    """작품 삭제"""
    artwork = get_object_or_404(Artwork, pk=pk, user=request.user)
    if request.method == 'POST':
        artwork.delete()
        messages.success(request, '작품이 삭제되었습니다.')
        return redirect('artwork:list')
    return redirect('artwork:detail', pk=pk)