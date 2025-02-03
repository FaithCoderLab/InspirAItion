from django import forms
from .models import Artwork, ArtworkComment

class ArtworkForm(forms.ModelForm):
    class Meta:
        model = Artwork
        fields = ['title', 'description', 'image_url', 'is_public', 'prompt', 'negative_prompt', 'ai_metadata']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'prompt': forms.Textarea(attrs={'rows': 3}),
            'image_url': forms.HiddenInput(),
            'ai_metadata': forms.HiddenInput()
        }

class ArtworkCommentForm(forms.ModelForm):
    class Meta:
        model = ArtworkComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3})
        }