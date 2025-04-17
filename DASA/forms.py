from django import forms
from .models import Planilla, AspectoSeguridad, ResponsableObra, Empresa, Obra, ART, DocumentoObra, Nomina
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import string
import secrets

def generar_contraseña(longitud=10):
    caracteres = string.ascii_letters + string.digits  # sin símbolos
    contraseña = ''.join(secrets.choice(caracteres) for _ in range(longitud))
    return contraseña

def enviar_mail(usuario_email, nombre_usuario, usuario, contraseña):
    subject = 'Bienvenido/a a la Plataforma de Gestión de DASA'
    from_email = None
    to_email = usuario_email

    html_content = render_to_string("email_bienvenida.html", {'usuario':usuario, 'nombre':nombre_usuario, 'contraseña':contraseña})

    msg = EmailMultiAlternatives(subject, '', from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

class PlanillaFormSimple(forms.ModelForm):
    class Meta:
        model = Planilla
        fields = ["obra"]

    def __init__(self, *args, obra=None, **kwargs):
        super().__init__(*args, **kwargs)
        if obra:
            self.fields['obra'].initial = obra
        self.fields['obra'].disabled = True

class PlanillaFormAdicional(forms.ModelForm):
    class Meta:
        model = Planilla
        fields = ["fecha","comentarios", "responsable_obra", "acciones"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
   

class PlanillaFormVerificacion(forms.ModelForm):
    class Meta:
        model = Planilla
        fields = ['verificacion', 'fecha_efectiva']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_efectiva'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
   

class AspectoSeguridadForm(forms.ModelForm):
    class Meta:
        model = AspectoSeguridad
        fields = '__all__'
        exclude = ['planilla']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo'].disabled = True


# Formulario para múltiples aspectos de seguridad
AspectoSeguridadFormSet = forms.modelformset_factory(
    AspectoSeguridad,
    form=AspectoSeguridadForm,
    extra=0  # No permite agregar nuevos aspectos, solo editar los existentes
)

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = '__all__'
        exclude = ['usuario']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ObraForm(forms.ModelForm):
    class Meta:
        model = Obra
        fields = '__all__'
        exclude = ['estado']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ARTForm(forms.ModelForm):
    class Meta:
        model = ART
        fields = '__all__'

class NominaForm(forms.ModelForm):
    class Meta:
        model = Nomina
        fields = '__all__'
        exclude = ['obra']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_incorporacion'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})

        if self.instance and self.instance.fecha_incorporacion:
            self.initial['fecha_incorporacion'] = self.instance.fecha_incorporacion.strftime('%Y-%m-%d')

class DocumentosObraEditForm(forms.ModelForm):
    class Meta:
        model = DocumentoObra
        fields = ['fecha_vencimiento', 'doc']
        exclude = ['fecha_carga', 'obra']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['tipo'].disabled = True
        self.fields['fecha_vencimiento'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})

        if self.instance and self.instance.fecha_vencimiento:
            self.initial['fecha_vencimiento'] = self.instance.fecha_vencimiento.strftime('%Y-%m-%d')

class DocumentosObraForm(forms.ModelForm):
    class Meta:
        model = DocumentoObra
        fields = ['tipo', 'fecha_vencimiento', 'doc']
        exclude = ['fecha_carga', 'obra']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_vencimiento'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})




class RegulacionObraForm(forms.ModelForm):
    class Meta:
        model = DocumentoObra
        fields = ['fecha_vencimiento', 'doc']
        exclude = ['fecha_carga', 'obra']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_vencimiento'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})


class UserResponsableForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False, label="Nombre")
    last_name = forms.CharField(max_length=30, required=False, label="Apellido")
    email = forms.EmailField(required=False)

    class Meta:
        model = ResponsableObra
        fields = ['CUIL']  # Solo el campo CUIL de ResponsableObra

    def save(self, commit=True):
        # Si el responsable ya tiene un usuario asociado, lo actualizamos
        responsable = super().save(commit=False)
        if responsable.usuario:
            # Si el responsable tiene un usuario, actualizamos los campos del usuario
            user = responsable.usuario
            user.first_name = self.cleaned_data.get('first_name', user.first_name)
            user.last_name = self.cleaned_data.get('last_name', user.last_name)
            user.username = self.cleaned_data.get('username', user.username)
            user.email = self.cleaned_data.get('email', user.email)
            user.save()  # Guardamos el usuario actualizado
        else:
            # Si no tiene un usuario asociado, creamos uno nuevo
            username = self.cleaned_data['CUIL']
            password = generar_contraseña()
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=self.cleaned_data.get('first_name', ''),
                last_name=self.cleaned_data.get('last_name', ''),
                email=self.cleaned_data.get('email', '')
            )
            responsable.usuario = user  # Asignamos el usuario al ResponsableObra
            enviar_mail(user.email, user.first_name, user.username, password)

        if commit:
            responsable.save()  # Guardamos el ResponsableObra

        return responsable


class UserEmpresaForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False, label="Nombre")
    email = forms.EmailField(required=False)

    class Meta:
        model = Empresa
        fields = ['CUIT','cel']  # Solo el campo CUIL de ResponsableObra
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Insertar campos del usuario en el orden deseado
        # Usamos OrderedDict para definir el orden exacto de los campos
        from collections import OrderedDict
        self.fields = OrderedDict([
            ('first_name', self.fields['first_name']),
            ('email', self.fields['email']),
            ('CUIT', self.fields['CUIT']),
            ('cel', self.fields['cel']),
        ])

    def save(self, commit=True):
        empresa = super().save(commit=False)
        if empresa.usuario:
            # Si la empresa tiene un usuario, actualizamos los campos del usuario
            user = empresa.usuario
            user.first_name = self.cleaned_data.get('first_name', user.first_name)
            user.username = self.cleaned_data.get('username', user.username)
            user.email = self.cleaned_data.get('email', user.email)
            user.password = self.cleaned_data.get('password', user.password)
            user.save()  # Guardamos el usuario actualizado
        else:
            # Si no tiene un usuario asociado, creamos uno nuevo
            username = self.cleaned_data['CUIT']
            password = generar_contraseña()
            user = User.objects.create_user(
                username=username,
                password= password,
                first_name=self.cleaned_data.get('first_name', ''),
                email=self.cleaned_data.get('email', '')
            )
            empresa.usuario = user  # Asignamos el usuario al ResponsableObra
            enviar_mail(user.email, user.first_name, user.username, password)

        if commit:
            empresa.save()  # Guardamos el ResponsableObra

        return empresa
    


