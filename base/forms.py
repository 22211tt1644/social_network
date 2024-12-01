from .models import Profile,Post,Comment,Message
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User

class EditProfileNewForm(forms.ModelForm):
     class Meta:
        model=Profile
        fields = ['full_name', 'bio', 'location', 'avatar']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'rows': 3,'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class ProfilePageForm(forms.ModelForm):
    class Meta:
        model=Profile
        fields = ['full_name', 'bio', 'location', 'avatar']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'rows': 3,'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'image')  # Chỉ lấy title và image

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class PasswordChangingForm(PasswordChangeForm):
    old_password=forms.CharField(widget=forms.PasswordInput(attrs={'class' : 'form-control', 'type':'password'}))
    new_password1=forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control', 'type':'password'}))
    new_password2=forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control', 'type':'password'}))

    class Meta:
        model= User
        fields = ('old_password','new_password1','new_password2')

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', 'parent']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'parent': forms.HiddenInput(),
        }

class EditForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'image')  # Chỉ lấy title và image

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control'}),
        }



class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6, required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter OTP', 'class': 'otp-input'}))

class RequestOTPForm(forms.Form):
    email = forms.EmailField()

class VerifyOTPForm(forms.Form):
    otp = forms.CharField(max_length=6, required=True, widget=forms.TextInput(attrs={'placeholder': 'Nhập mã OTP', 'class': 'otp-input'}))
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Nhập mật khẩu mới', 'class': 'password-input'}), required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Xác nhận mật khẩu mới', 'class': 'password-input'}), required=True)

    # Kiểm tra xác nhận mật khẩu mới
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password != confirm_password:
            raise forms.ValidationError("Mật khẩu mới và xác nhận mật khẩu không khớp.")

        return cleaned_data
    
