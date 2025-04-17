from django.shortcuts import render, redirect,  get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from DASA.models import AspectoSeguridad, Nomina, ResponsableObra, Planilla, Obra, Empresa, DocumentoObra, ART, HistorialPlanilla
from django.http import HttpResponseRedirect, HttpResponse
from DASA.forms import  UserEmpresaForm, NominaForm, UserResponsableForm, DocumentosObraForm, DocumentosObraEditForm, PlanillaFormSimple, PlanillaFormVerificacion,PlanillaFormAdicional, AspectoSeguridadFormSet, ObraForm, EmpresaForm, ARTForm
from django.db.models import Max, Q
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

@login_required
def inicioUsuario(request):
    if request.user.groups.filter(name='Administrador DASA').exists():
        empresas = Empresa.objects.all()
        licenciados = ResponsableObra.objects.all()
        return render(request, 'panel_admin.html', {'empresas':empresas, 'licenciados':licenciados})
    elif request.user.groups.filter(name='Empresas').exists():
        empresa = Empresa.objects.filter(usuario = request.user).first()
        obras = Obra.objects.filter(empresa = empresa.CUIT) #hay que filtrar con las obras del responsable logueado
        return render(request,"panel_empresa.html", {'obras':obras})
    else:
        lic = ResponsableObra.objects.filter(usuario = request.user).first()
        obras = Obra.objects.filter(firma= lic.CUIL) #hay que filtrarcon las obras del responsable logueado
        return render(request,"panel_licenciado.html", {'obras':obras})
       
# Vistas relacionadas al modelo Obra
@login_required
def añadir_obra(request):
    if request.method == "POST":
        form = ObraForm(request.POST)
        if form.is_valid(): 
            obra=form.save()  # Guarda en la BD
            return redirect('detalle_obra',obra.id)
    else:
        form = ObraForm()

    return render(request, 'obra/añadir_obra.html', {'form': form})


@login_required
def detalle_obra(request, id_obra):
    obra = get_object_or_404(Obra, id=id_obra)

    documentos = obra.documentos.order_by('orden').all()
    historial = HistorialPlanilla.objects.filter(obra=obra).order_by('-fecha')
    planillas = Planilla.objects.filter(obra=obra, completa=True).order_by('-fecha')
    nomina = Nomina.objects.filter(obra=obra).order_by('nombre', 'apellido')
    return render(request, 'obra/detalle_obra.html', {'obra': obra,'documentos':documentos, 'planillas': planillas, 'historial':historial, 'nomina': nomina})

@login_required
def editar_documentos_obra(request, id_doc):
    doc = get_object_or_404(DocumentoObra, id=id_doc)     
    if request.method == "POST":
        form = DocumentosObraEditForm(request.POST, request.FILES, instance=doc)  
        if form.is_valid():
            form.save()
            # messages.success(request, "Planilla editada con éxito")
            return redirect('detalle_obra', doc.obra.id)  
    else:
       form = DocumentosObraEditForm(instance=doc) 

    return render(request, 'regulacion/editar_documento.html', {'form': form, 'doc': doc})

@login_required
def añadir_documentos_obra(request, id_obra):
    # Obtener la obra con el id proporcionado
    obra = get_object_or_404(Obra, id=id_obra)    
    
    if request.method == "POST":
        form = DocumentosObraForm(request.POST, request.FILES)
        
        if form.is_valid():
            nuevo_documento = form.save(commit=False)
            nuevo_documento.obra = obra  
            nuevo_documento.save()  
            return redirect('detalle_obra', id_obra=obra.id)  
    
    else:
        
        form = DocumentosObraForm(initial={'obra': obra.id})

    return render(request, 'regulacion/añadir_documento.html', {'form': form, 'obra': obra})

@login_required
def lista_obra(request):
    obras_agro = Obra.objects.none()
    obras_construccion = Obra.objects.none()
    obras_industria_comercio = Obra.objects.none()
    if request.user.groups.filter(name='Administrador DASA').exists():
        obras_agro = Obra.objects.filter(sector = 'AGRO')
        obras_construccion = Obra.objects.filter(sector = 'CONSTRUCCION')
        obras_industria_comercio = Obra.objects.filter(sector = 'INDUSTRIA_COMERCIO')
    elif request.user.groups.filter(name='Licenciados').exists():
        try:
            licenciado = ResponsableObra.objects.get(usuario=request.user)
            obras_agro = Obra.objects.filter(firma=licenciado, sector = 'AGRO')
            obras_construccion = Obra.objects.filter(firma=licenciado, sector = 'CONSTRUCCION')
            obras_industria_comercio = Obra.objects.filter(firma=licenciado, sector = 'INDUSTRIA_COMERCIO')
        except ResponsableObra.DoesNotExist:
            obras_agro = Obra.objects.none()
            obras_construccion = Obra.objects.none()
            obras_industria_comercio = Obra.objects.none()
    elif request.user.groups.filter(name='Empresas').exists():
        try:
            empresa = Empresa.objects.get(usuario=request.user)
            obras_agro = Obra.objects.filter(empresa=empresa, sector = 'AGRO')
            obras_construccion = Obra.objects.filter(empresa=empresa, sector = 'CONSTRUCCION')
            obras_industria_comercio = Obra.objects.filter(empresa=empresa, sector = 'INDUSTRIA_COMERCIO')
        except ResponsableObra.DoesNotExist:
            obras_agro = Obra.objects.none()
            obras_construccion = Obra.objects.none()
            obras_industria_comercio = Obra.objects.none()
    query = request.GET.get("query")
    if query:
        obras_agro = obras_agro.filter(Q(empresa__razon_social__icontains=query) | Q(dir_calle__icontains=query) | Q(dir_altura__icontains=query) )
        obras_construccion = obras_construccion.filter(Q(empresa__razon_social__icontains=query) | Q(dir_calle__icontains=query) | Q(dir_altura__icontains=query))
        obras_industria_comercio = obras_industria_comercio.filter(Q(empresa__razon_social__icontains=query) | Q(dir_calle__icontains=query) | Q(dir_altura__icontains=query))
    return render(request, 'obra/lista_obra.html', {'obras_construccion': obras_construccion, 'obras_agro':obras_agro, 'obras_industria_comercio': obras_industria_comercio})

@login_required
def editar_obra(request, id_obra):
    obra = get_object_or_404(Obra, id=id_obra)    

    if request.method == "POST":
        form = ObraForm(request.POST, request.FILES, instance=obra)
        if form.is_valid(): 
            form.save()  # Guarda en la BD
            return redirect('detalle_obra', obra.id)
    else:
        form = ObraForm(instance=obra)

    return render(request, 'obra/editar_obra.html', {'form': form,'obra':obra})

@login_required
def eliminar_obra(request, id_obra):
    obra = get_object_or_404(Obra, id=id_obra)    
    
    if request.method == "POST":
        obra.delete()
        return redirect('lista_obra') 
    return render(request, 'obra/eliminar_obra.html', {'obra': obra})


# Vistas relacionadas al modelo empresa
@login_required
def añadir_empresa(request):
    if request.method == "POST":
        form = UserEmpresaForm(request.POST, request.FILES)
        if form.is_valid(): 
            form.save()  # Guarda en la BD
            return redirect('lista_obra')
    else:
        form = UserEmpresaForm()

    return render(request, 'empresa/añadir_empresa.html', {'form': form})

@login_required
def editar_empresa(request, id_empresa):
    empresa = Empresa.objects.none()   
    if request.user.groups.filter(name='Administrador DASA').exists():
        empresa = get_object_or_404(Empresa, CUIT=id_empresa) 
    elif request.user.groups.filter(name='Empresas').exists():
        empresa = get_object_or_404(Empresa, usuario=id_empresa) 

    if empresa.usuario:
        initial_data = {
            'first_name': empresa.usuario.first_name,
            'email': empresa.usuario.email,
        }
    else:
        initial_data = {}
    if request.method == "POST":
        form = UserEmpresaForm(request.POST, request.FILES, instance=empresa)
        if form.is_valid(): 
            form.save()  # Guarda en la BD
            if request.user.groups.filter(name='Empresas').exists():
                return redirect('inicio_usuario')
            else: return redirect('detalle_empresa', empresa.CUIT)
    else:
        form = UserEmpresaForm(instance=empresa, initial=initial_data)

    return render(request, 'empresa/editar_empresa.html', {'form': form,'empresa':empresa})

@login_required
def eliminar_empresa(request, id_empresa):
    empresa = get_object_or_404(Empresa, CUIT=id_empresa)
    
    if request.method == "POST":
        empresa.delete()
        return redirect('lista_empresa')  

    return render(request, 'empresa/eliminar_empresa.html', {'empresa': empresa})

@login_required
def detalle_empresa(request, id_empresa):
    empresa = Empresa.objects.none()
    obras_agro = Obra.objects.none()
    obras_construccion = Obra.objects.none()
    obras_industria_comercio = Obra.objects.none()
    if request.user.groups.filter(name='Empresas').exists():
        try:
            empresa = Empresa.objects.get(usuario=request.user)
        except ResponsableObra.DoesNotExist:
            empresa = Empresa.objects.none()
    if (request.user.groups.filter(name='Licenciados').exists()) or (request.user.groups.filter(name='Administrador DASA').exists()):
        empresa = get_object_or_404(Empresa, CUIT=id_empresa) 
        obras_agro = Obra.objects.filter(empresa=empresa, sector = 'AGRO')
        obras_construccion = Obra.objects.filter(empresa=empresa, sector = 'CONSTRUCCION')
        obras_industria_comercio = Obra.objects.filter(empresa=empresa, sector = 'INDUSTRIA_COMERCIO')
    return render(request, 'empresa/detalle_empresa.html', {'empresa': empresa,'obras_construccion': obras_construccion, 'obras_agro':obras_agro, 'obras_industria_comercio': obras_industria_comercio})

@login_required
def lista_empresa(request):
    query = request.GET.get("query")
    empresas = Empresa.objects.all()
    if query:
        empresas = empresas.filter(razon_social__icontains=query) 
    return render(request, 'empresa/lista_empresa.html', {'empresas': empresas})



# Vistas relacionadas al modelo Licenciado

@login_required
def lista_licenciado(request):
    licenciados = ResponsableObra.objects.all()
    query = request.GET.get("query")
    if query:
        licenciados = licenciados.filter(Q(usuario__first_name__icontains=query) | Q(usuario__last_name__icontains=query))
    return render(request, 'licenciado/lista_licenciado.html', {'licenciados': licenciados})
  
@login_required
def añadir_licenciado(request):
    if request.method == "POST":
        form = UserResponsableForm(request.POST)
        if form.is_valid(): 
            form.save()  # Guarda en la BD
            return redirect('lista_licenciado')
    else:
        form = UserResponsableForm()

    return render(request, 'licenciado/añadir_licenciado.html', {'form': form})

@login_required
def detalle_licenciado(request, id_licenciado):
    licenciado = get_object_or_404(ResponsableObra, CUIL=id_licenciado) 
    obras = licenciado.obras.all()
    return render(request, 'licenciado/detalle_licenciado.html', {'licenciado': licenciado, 'obras':obras})

@login_required
def editar_licenciado(request, id_licenciado):
    licenciado = ResponsableObra.objects.none()
    if request.user.groups.filter(name='Administrador DASA').exists():
        licenciado = get_object_or_404(ResponsableObra, CUIL=id_licenciado)     
    elif request.user.groups.filter(name='Licenciados').exists():
        licenciado = get_object_or_404(ResponsableObra, usuario=id_licenciado)

    if licenciado.usuario:
        initial_data = {
            'first_name': licenciado.usuario.first_name,
            'last_name': licenciado.usuario.last_name,
            'email': licenciado.usuario.email,
        }
    else:
        initial_data = {}

    if request.method == "POST":
        form = UserResponsableForm(request.POST, instance=licenciado)
        if form.is_valid(): 
            form.save()  # Guarda en la BD
            if request.user.groups.filter(name='Licenciados').exists():
                return redirect('inicio_usuario')
            else:
                return redirect('detalle_licenciado', licenciado.CUIL)
    else:
        form = UserResponsableForm(instance=licenciado, initial=initial_data)

    return render(request, 'licenciado/editar_licenciado.html', {'form': form,'licenciado':licenciado})

@login_required
def eliminar_licenciado(request, id_licenciado):
    licenciado = get_object_or_404(ResponsableObra, CUIL=id_licenciado)     
    
    if request.method == "POST":
        licenciado.delete()
        return redirect('lista_licenciado')  

    return render(request, 'licenciado/eliminar_licenciado.html', {'licenciado': licenciado})


# Vistas relacionadas al modelo ART

@login_required
def añadir_ART(request):
    if request.method == "POST":
        form = ARTForm(request.POST)
        if form.is_valid(): 
            form.save()  
            return redirect('lista_ART')
    else:
        form = ARTForm()

    return render(request, 'art/añadir_ART.html', {'form': form})

@login_required
def eliminar_ART(request, id_ART):
    art = get_object_or_404(ART, id=id_ART)     
    
    if request.method == "POST":
        art.delete()
        return redirect('lista_ART')  

    return render(request, 'ART/eliminar_ART.html', {'ART': art})

@login_required
def editar_ART(request, id_ART):
    art = get_object_or_404(ART, id=id_ART)     

    if request.method == "POST":
        form = ARTForm(request.POST, instance=art)
        if form.is_valid(): 
            form.save()  # Guarda en la BD
            return redirect('lista_ART')
    else:
        form = ARTForm(instance=art)

    return render(request, 'ART/editar_ART.html', {'form': form,'ART':art})

@login_required
def lista_ART(request):
    ARTs = ART.objects.all()
    query = request.GET.get("query")
    if query:
        ARTs = ARTs.filter(nombre__icontains=query)
    return render(request, 'ART/lista_ART.html', {'ARTs': ARTs})
  

# Vistas relacionadas al modelo Planilla

@login_required
def editar_planilla(request, id_planilla):
    planilla = get_object_or_404(Planilla, id=id_planilla)
    if request.method == "POST":
        if request.POST.get("cancelar") == "true":
            if not planilla.completa:
                planilla.delete()
            return redirect('inicio_usuario')
        form = PlanillaFormVerificacion(request.POST, instance=planilla) 
        if form.is_valid():
            planilla = form.save(commit=False)
            planilla.completa = True
            planilla.save()
            # messages.success(request, "Planilla editada con éxito")
            return redirect('detalle_obra', planilla.obra.id)  
    else:
        form = PlanillaFormVerificacion(instance=planilla)  

    return render(request, 'planilla/editar_planilla.html', {'form': form, 'planilla': planilla})

@login_required
def añadir_informacion_planilla(request, id_planilla):
    planilla = get_object_or_404(Planilla, id=id_planilla)  
    
    if request.method == "POST":
        form = PlanillaFormAdicional(request.POST, instance=planilla)  
        if form.is_valid():
            planilla = form.save(commit=False)
            planilla.completa = True
            planilla.save()
            # messages.success(request, "Planilla editada con éxito")
            return redirect('detalle_obra', planilla.obra.id)  
    else:
       form = PlanillaFormAdicional(instance=planilla) 

    return render(request, 'planilla/añadir_informacion_planilla.html', {'form': form, 'planilla': planilla})

@login_required
def visitas(request):
    obras = Obra.objects.all()
    return render(request,"visitas.html", {'obras':obras})

@login_required
def detalle_planilla(request, id_planilla):
    planilla = get_object_or_404(Planilla, id=id_planilla)
    aspectos = planilla.aspectos.all()
    return render(request,"planilla/detalle_planilla.html", {'planilla':planilla, 'aspectos':aspectos})

@login_required
def añadir_planilla(request, obra):
    obra = get_object_or_404(Obra, id=obra)

    if request.method == "POST":
        if request.POST.get("cancelar") == "true":
            if not planilla.completa:
                planilla.delete()
            return redirect('inicio_usuario')
        form = PlanillaFormSimple(request.POST, obra=obra)
        if form.is_valid():
            planilla = form.save()
            # messages.success(request, "Planilla creada con éxito")
            return redirect('editar_aspectos_planilla', id_planilla=planilla.id)
    else:
        form = PlanillaFormSimple(obra=obra)
    return render(request, 'planilla/añadir_planilla.html', {'form': form, 'obra': obra})


@login_required
def editar_aspectos_planilla(request, id_planilla):
    planilla = get_object_or_404(Planilla, id=id_planilla)
    aspectos = AspectoSeguridad.objects.filter(planilla=planilla)  

    if request.method == "POST":
        if request.POST.get("cancelar") == "true":
            if not planilla.completa:
                planilla.delete()
            return redirect('inicio_usuario')
        formset = AspectoSeguridadFormSet(request.POST, request.FILES, queryset=aspectos)
        if formset.is_valid():
            formset.save()  
            return redirect('añadir_informacion_planilla', id_planilla=planilla.id)

    else:
        formset = AspectoSeguridadFormSet(queryset=aspectos)

    return render(request, 'planilla/editar_aspectos.html', {'formset': formset, 'planilla': id_planilla})

# Vistas por modelo Usuario

@login_required
def cambiar_contraseña(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Mantiene la sesión activa
            # messages.success(request, 'Tu contraseña fue cambiada exitosamente.')
            return redirect('inicio')  # O donde quieras redirigir
        # else:
        #     messages.error(request, 'Por favor corregí los errores.')
    else:
        form = PasswordChangeForm(user=request.user)
    
    return render(request, 'usuario/cambiar_contraseña.html', {'form': form})


# Vistas relacionadas al modelo Nomina

@login_required
def añadir_nomina(request, obra):
    obra = get_object_or_404(Obra, id=obra)
    if request.method == "POST":
        form = NominaForm(request.POST)
        if form.is_valid(): 
            nomina = form.save(commit=False)
            nomina.obra = obra  # acá le estás diciendo a qué obra pertenece
            nomina.save()
            return redirect('detalle_obra', obra.id) 
    else:
        form = NominaForm()

    return render(request, 'nomina/añadir_nomina.html', {'form': form, 'obra':obra})

@login_required
def eliminar_nomina(request, id_persona):
    nomina = get_object_or_404(Nomina, CUIL=id_persona)     
    
    if request.method == "POST":
        nomina.delete()
        return redirect('detalle_obra', nomina.obra.id)  

    return render(request, 'nomina/eliminar_nomina.html', {'nomina': nomina})

@login_required
def editar_nomina(request, id_persona):
    nomina = get_object_or_404(Nomina, CUIL=id_persona)     

    if request.method == "POST":
        form = NominaForm(request.POST, instance=nomina)
        if form.is_valid(): 
            form.save()  # Guarda en la BD
            return redirect('detalle_obra', nomina.obra.id)
    else:
        form = NominaForm(instance=nomina)

    return render(request, 'nomina/editar_nomina.html', {'form': form,'nomina':nomina})
