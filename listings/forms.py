from django import forms
from .models import Listing, ListingImage

class ListingForm(forms.ModelForm):
    images = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)

    class Meta:
        model = Listing
        fields = ['title', 'description', 'price', 'location', 'status']

    def save(self, commit=True):
        listing = super().save(commit=False)
        if commit:
            listing.save()
        return listing
