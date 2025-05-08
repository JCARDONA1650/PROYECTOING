from django.db import models
# Puedes personalizarlo más adelante si deseas
from django.contrib.auth.models import User

# ---------------------
# Modelo Persona
# ---------------------


class Persona(models.Model):
    usuario = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True)

    TIPO_DOCUMENTO = [
        ('CC', 'Cédula de ciudadanía'),
        ('TI', 'Tarjeta de identidad'),
        ('CE', 'Cédula de extranjería'),
    ]

    tipo_documento = models.CharField(max_length=2, choices=TIPO_DOCUMENTO)
    numero_documento = models.CharField(max_length=20, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    sexo = models.CharField(max_length=10)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"


class Paciente(models.Model):
    persona = models.OneToOneField(Persona, on_delete=models.CASCADE)
    eps = models.CharField(max_length=100)
    historial_clinico = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Paciente: {self.persona}"

# ---------------------
# Medicamento
# ---------------------


class Medicamento(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    fecha_vencimiento = models.DateField()
    laboratorio = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

# ---------------------
# Registro de Muestra por Enfermería
# ---------------------


class Muestra(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    enfermero = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        limit_choices_to={'groups__name': 'enfermeria'}
    )
    medicamento = models.ForeignKey(
        Medicamento, on_delete=models.SET_NULL, null=True)
    fecha_toma = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True, null=True)
    enviada_laboratorio = models.BooleanField(default=False)

    def __str__(self):
        return f"Muestra de {self.paciente.persona} - {self.medicamento}"

# ---------------------
# Resultado del Laboratorio
# ---------------------


class ResultadoLaboratorio(models.Model):
    muestra = models.OneToOneField(Muestra, on_delete=models.CASCADE)
    laboratorio = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        limit_choices_to={'groups__name': 'laboratorio'}
    )
    resultado = models.TextField()
    fecha_resultado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resultado de {self.muestra}"

# ---------------------
# Entrega de Medicamento (por Farmacia)
# ---------------------


class ProcesoMedicamento(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE)
    farmacia = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        limit_choices_to={'groups__name': 'farmacia'}
    )
    fecha_entrega = models.DateTimeField(auto_now_add=True)
    dosis = models.CharField(max_length=50)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Entrega a {self.paciente.persona} - {self.medicamento}"
