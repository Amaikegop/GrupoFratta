
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Frame, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from reportlab.lib.units import inch
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def limitar_tamano_imagen(path):
    max_ancho = A4[0] - 2 * inch  # ancho de la hoja menos márgenes
    max_alto = A4[1] - 2 * inch   # alto de la hoja menos márgenes

    img = Image(path)
    # Escalado proporcional
    proporcion = min(max_ancho / img.imageWidth, max_alto / img.imageHeight, 1.0)
    img.drawWidth = img.imageWidth * proporcion
    img.drawHeight = img.imageHeight * proporcion
    return img

def generar_pdf_buffer(planilla):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    w, h = A4 
    w = w * 0.80
    h = h * 0.85
    elements = []
    styles = getSampleStyleSheet()

    logo = [["DASA"], ["CONSULTORIA EN SEHT"]]
    tabla_logo = Table(logo)
    tabla_logo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, 1), 'Helvetica'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('LINEBELOW', (0,0), (0,0), 0, colors.transparent),
        ('LINEABOVE', (0,1), (0,1), 0, colors.transparent),
        ('SIZE', (0, 0), (0, 0), 25),
        ('TOPPADDING', (0, 1), (0, 1), 15),
    ]))

    nro_planilla = Paragraph("Planilla N° " + str(planilla.id))
    encabezado_data = [[tabla_logo, "OBSERVACIONES", nro_planilla]]
    encabezado = Table(encabezado_data, colWidths=[w*0.35, w*0.55, w*0.2], rowHeights=80)
    encabezado.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (2, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('SIZE', (1, 0), (1, 0), 15),
    ]))

    elements.append(encabezado)
    elements.append(Spacer(1, 20))

    obra =[["Registro de observaciones", ""],
           ["Obra: "+str(planilla.obra.dir_calle)+" "+str(planilla.obra.dir_altura), "Sector: "+str(planilla.obra.get_sector_display())],
           ["Empresa observada: "+str(planilla.obra.empresa), "Fecha: "+str(planilla.fecha)]]
    tabla_obra = Table(obra, colWidths=[w*0.55, w*0.55])
    tabla_obra.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('FONTNAME', (0, 1), (0, 1), 'Helvetica'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (0, 0), colors.gray),
        ('SPAN', (0, 0), (1, 0)),
    ]))
    elements.append(tabla_obra)


    aspectos = list(planilla.aspectos.all())
    mitad = len(aspectos) // 2
    aspectos_col1 = aspectos[:mitad]
    aspectos_col2 = aspectos[mitad:]
    index =0
    data_img = []
    data = [["Aspectos", "CS", "CI", "NA", "Aspectos", "CS", "CI", "NA"]]
    for i in range(len(aspectos_col1)):
        index=index+1
        na_col1 = "x" if not aspectos_col1[i].ci else None
        na_col2 = "x" if i < len(aspectos_col2) and not aspectos_col2[i].ci else None

        if aspectos_col1[i].imagen:
            texto = Paragraph("Imagen correspondiente al aspecto:"+str(index), styles['Normal'])
            data_img.append(texto)
            data_img.append(Spacer(0, 5))
            imagen = limitar_tamano_imagen(aspectos_col1[i].imagen.path)
            data_img.append(imagen)
            data_img.append(Spacer(0, 12))

        col1_data = [str(index)+". "+aspectos_col1[i].get_tipo_display(), aspectos_col1[i].cs, aspectos_col1[i].ci, na_col1]
        index=index+1
        if aspectos_col2[i].imagen:
            texto = Paragraph("Imagen correspondiente al aspecto:"+str(index), styles['Normal'])
            data_img.append(texto)
            data_img.append(Spacer(0, 5))
            imagen = limitar_tamano_imagen(aspectos_col2[i].imagen.path)
            data_img.append(imagen)
            data_img.append(Spacer(0, 12))

        col2_data = [str(index)+". "+aspectos_col2[i].get_tipo_display(), aspectos_col2[i].cs, aspectos_col2[i].ci, na_col2] if i < len(aspectos_col2) else ["", "", "", ""]
        data.append(col1_data + col2_data)

    tabla = Table(data, colWidths=[w*0.40, w*0.05, w*0.05, w*0.05, w*0.40, w*0.05, w*0.05, w*0.05])
    estilo = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (1, 0), (3, 0), 'CENTER'),
        ('ALIGN', (5, 0), (7, 0), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ])
    tabla.setStyle(estilo)
    elements.append(tabla)

    comentario = Paragraph("Comentarios del observador: " + planilla.comentarios)
    p1 = Paragraph("El número expuesto en cada celda por punto observado hace referencia a la cantidad de personas afectadas, es decir por personal con riesgo de AT dada la condición laboral")
    responsable = Paragraph("Responsable en obra: "+ str(planilla.responsable_obra))
    acciones = Paragraph("Accciones inmediatas: " + planilla.acciones)
    if (planilla.fecha_efectiva):
        verificacion = Paragraph("Verificación: " +str(planilla.fecha_efectiva)+str(planilla.verificacion))
    else: verificacion = Paragraph("Verificación: " )

    data_info = [[p1, "", ""],
                 ["CS: condición segura de trabajo", "CI: condición insegura de trabajo", "NA: no aplica"],
                 ["Las condiciones inseguras de trabajo deben ser solucionadas a la brevedad sin excepción", "", ""],
                 [comentario, "", ""],
                 [responsable, "", ""],
                 [acciones, "", ""], 
                 ["Evaluación de las acciones tomadas", "", ""], 
                 [verificacion, "", ""]]

    tabla_info = Table(data_info, colWidths=[w*0.3666, w*0.3666, w*0.3666])
    tabla_info.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (2, 2), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 1), (-1, 2), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, 2), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('SPAN', (0, 0), (2, 0)),
        ('SPAN', (0, 2), (2, 2)), 
        ('SPAN', (0, 3), (2, 3)),
        ('SPAN', (0, 4), (2, 4)),
        ('SPAN', (0, 5), (2, 5)),
        ('SPAN', (0, 6), (2, 6)),
        ('BACKGROUND', (0, 6), (2, 6),colors.gray),
        ('ALIGN', (0, 6), (2, 6),'CENTER'),
        ('SPAN', (0, 7), (2, 7)),
    ]))

    elements.append(tabla_info)
    elements.append(PageBreak())
    elements.extend(data_img)
    doc.build(elements)
    buffer.seek(0)
    return buffer

def enviar_mail_planilla(planilla):
    subject = 'Visita semanal-'+str(planilla.obra.dir_calle)+ " "+ str(planilla.obra.dir_altura)
    from_email = None
    to_email = planilla.obra.empresa.usuario.email

    html_content = render_to_string("envio_planilla.html", {
        "empresa": planilla.obra.empresa.usuario.first_name,
        "direccion_obra": str(planilla.obra.dir_calle)+ " "+ str(planilla.obra.dir_altura),
        "sector": planilla.obra.get_sector_display(),
        "fecha": planilla.fecha.strftime("%d/%m/%Y")
    })
    msg = EmailMultiAlternatives(subject, '', from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    # Adjuntamos el archivo PDF desde el campo archivo de la planilla
    if planilla.archivo:
        # Aseguramos que el archivo está disponible
        archivo_pdf = planilla.archivo
        nombre_archivo = f"planilla_{planilla.obra}_{planilla.fecha}.pdf"
        msg.attach(nombre_archivo, archivo_pdf.read(), 'application/pdf')
    msg.send()
    