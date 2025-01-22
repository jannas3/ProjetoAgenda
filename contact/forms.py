import re
from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from . import models
class ContactForm(forms.ModelForm):
    picture = forms.ImageField(
        widget=forms.FileInput(attrs={'accept': 'image/*'}),
        required=False
    )

    phone = forms.CharField(
        required=True,
        max_length=15,  # Ajuste o comprimento máximo conforme necessário
        widget=forms.TextInput(attrs={'placeholder': 'Telefone', 'pattern': '[0-9]{2}[0-9]{4,5}[0-9]{4}'}),
    )

    class Meta:
        model = models.Contact
        fields = ('first_name', 'last_name', 'phone', 'email', 'description', 'category', 'picture')

    def clean(self):
        cleaned_data = self.cleaned_data
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')

        # Validação para garantir que primeiro nome e sobrenome não sejam iguais
        if first_name == last_name:
            msg = ValidationError('Primeiro nome não pode ser igual ao segundo', code='invalid')
            self.add_error('first_name', msg)
            self.add_error('last_name', msg)

        # Regex para garantir que nomes não tenham números ou caracteres especiais
        name_regex = r'^[A-Za-zÀ-ÿ]+$'  # A regex agora aceita caracteres acentuados
        if not re.match(name_regex, first_name):
            self.add_error('first_name', ValidationError('O primeiro nome só pode conter letras.'))
        if not re.match(name_regex, last_name):
            self.add_error('last_name', ValidationError('O sobrenome só pode conter letras.'))

        return super().clean()

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')

        # Validação para um nome específico
        if first_name == 'ABC':
            self.add_error('first_name', ValidationError('Nome inválido.'))

        return first_name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        # Verifica o formato do telefone (somente DDD e número, sem o +55)
        phone_regex = r'^\d{2}\d{4,5}\d{4}$'  # DDD + número, por exemplo: 11987654321
        if not re.match(phone_regex, phone):
            raise ValidationError('Número de telefone inválido. Use o formato: DDD XXXXX-XXXX ou DDD XXXXXXX.')

        return phone

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(required=True, min_length=3)
    last_name = forms.CharField(required=True, min_length=3)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')

        # Verifica o formato básico do e-mail com regex
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            raise ValidationError('Formato de e-mail inválido.')

        # Validação do domínio do e-mail
        domain = email.split('@')[-1]
        if not re.match(r'^[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$', domain):
            raise ValidationError('Domínio de e-mail inválido.')

        # Verifica se o e-mail já existe
        if User.objects.filter(email=email).exists():
            self.add_error('email', ValidationError('Já existe este e-mail', code='invalid'))

        return email


class RegisterUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        min_length=2,
        max_length=30,
        required=True,
        help_text='Required.',
        error_messages={'min_length': 'Please, add more than 2 letters.'}
    )
    last_name = forms.CharField(
        min_length=2,
        max_length=30,
        required=True,
        help_text='Required.'
    )

    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html(),
        required=False,
    )

    password2 = forms.CharField(
        label="Password 2",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text='Use the same password as before.',
        required=False,
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username')

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        user = super().save(commit=False)
        password = cleaned_data.get('password1')

        if password:
            user.set_password(password)

        if commit:
            user.save()

        return user

    def clean(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 or password2:
            if password1 != password2:
                self.add_error('password2', ValidationError('Senhas não batem'))

        return super().clean()

    def clean_email(self):
        email = self.cleaned_data.get('email')

        # Validação do e-mail (com regex e verificação do domínio)
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            raise ValidationError('Formato de e-mail inválido.')

        # Verifica se o domínio do e-mail é válido
        domain = email.split('@')[-1]
        if not re.match(r'^[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$', domain):
            raise ValidationError('Domínio de e-mail inválido.')

        # Verifica se o e-mail já existe
        if User.objects.filter(email=email).exists():
            self.add_error('email', ValidationError('Este e-mail já está em uso.'))

        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')

        if password1:
            try:
                password_validation.validate_password(password1)
            except ValidationError as errors:
                self.add_error('password1', ValidationError(errors))

        return password1
