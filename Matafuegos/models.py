from django.db import models
from django.contrib.auth.models import User  # Para asignar usuarios responsables
# from Clientes.models import Cliente  # Relación con la app de clientes

class Matafuego(models.Model):
    """
    Modelo principal para gestionar los matafuegos.
    """
    # cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="matafuegos")
    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código del Matafuego")
    tipo = models.CharField(max_length=100, verbose_name="Tipo de Matafuego")  # Ej: Polvo ABC, CO2, etc.
    capacidad = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Capacidad (kg)")
    fecha_compra = models.DateField(verbose_name="Fecha de Compra")
    fecha_ultima_recarga = models.DateField(verbose_name="Fecha Última Recarga")
    fecha_vencimiento = models.DateField(verbose_name="Fecha de Vencimiento")
    ubicacion = models.CharField(max_length=255, verbose_name="Ubicación")  # Ej: "Oficina 1, piso 2"
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                     verbose_name="Responsable de Supervisión")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones Adicionales")
    
    class Meta:
        verbose_name = "Matafuego"
        verbose_name_plural = "Matafuegos"
        ordering = ["fecha_vencimiento"]

    def __str__(self):
        return f"{self.codigo} - {self.tipo} "

    def esta_vencido(self):
        """
        Verifica si el matafuego está vencido.
        """
        from datetime import date
        return self.fecha_vencimiento < date.today()


class RegistroMantenimiento(models.Model):
    """
    Historial de mantenimientos realizados en cada matafuego.
    """
    matafuego = models.ForeignKey(Matafuego, on_delete=models.CASCADE, related_name="mantenimientos")
    fecha = models.DateField(auto_now_add=True, verbose_name="Fecha del Mantenimiento")
    descripcion = models.TextField(verbose_name="Descripción del Mantenimiento")
    realizado_por = models.CharField(max_length=100, verbose_name="Realizado Por")  # Técnico o empresa
    costo = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Costo del Mantenimiento", null=True, blank=True)
    
    class Meta:
        verbose_name = "Registro de Mantenimiento"
        verbose_name_plural = "Registros de Mantenimiento"
        ordering = ["-fecha"]

    def __str__(self):
        return f"Mantenimiento de {self.matafuego} en {self.fecha}"


class AlertaVencimiento(models.Model):
    """
    Modelo para gestionar las alertas de vencimiento.
    """
    matafuego = models.OneToOneField(Matafuego, on_delete=models.CASCADE, related_name="alerta")
    fecha_alerta = models.DateField(verbose_name="Fecha de Alerta Generada")
    enviada = models.BooleanField(default=False, verbose_name="¿Alerta Enviada?")
    
    class Meta:
        verbose_name = "Alerta de Vencimiento"
        verbose_name_plural = "Alertas de Vencimiento"

    def __str__(self):
        return f"Alerta para {self.matafuego} - Enviada: {'Sí' if self.enviada else 'No'}"
