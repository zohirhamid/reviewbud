from django import forms
from django.contrib.auth import authenticate
from .models import User, Business, CustomerReview
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model  

User = get_user_model() 

# Your existing form (keep exactly as is):
class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    
    class Meta:
        model = User  # ← This now references your custom User
        fields = ['username', 'email', 'password']
    
    # checks if 2 password fields match
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords don't match")
        
        return cleaned_data
class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("Invalid username or password")
        return self.cleaned_data
    
class BusinessForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = ['name', 'address', 'google_review_url']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'google_review_url': forms.URLInput(attrs={
                'placeholder': 'https://search.google.com/local/writereview?placeid=...'
                })

        }

        '''
        this widget will render the HTML like this:
        <input type="url" name="google_review_url" placeholder="https://search.google.com/local/writereview?placeid=..." />
        '''


class CustomerReviewForm(forms.ModelForm):
    class Meta:
        model = CustomerReview
        fields = ['rating', 'feedback']
        widgets = {
            'rating': forms.Select(choices=CustomerReview.RATING_CHOICES),
            'feedback': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us about your experience...'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Enter your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Enter your last name'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter your email address'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True