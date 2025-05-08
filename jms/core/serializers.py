from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import Persona, Paciente, Medicamento, Muestra, ResultadoLaboratorio, ProcesoMedicamento

# ---------------------
# Usuario (solo para mostrar nombre)
# ---------------------


class RegistroPacienteSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    # Datos personales
    tipo_documento = serializers.ChoiceField(choices=Persona.TIPO_DOCUMENTO)
    numero_documento = serializers.CharField()
    nombres = serializers.CharField()
    apellidos = serializers.CharField()
    fecha_nacimiento = serializers.DateField()
    sexo = serializers.CharField()
    direccion = serializers.CharField()
    telefono = serializers.CharField()
    eps = serializers.CharField()

    def create(self, validated_data):
        # Extraer campos
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        eps = validated_data.pop('eps')

        # Crear usuario
        user = User.objects.create_user(
            username=username, email=email, password=password)

        # Asignar al grupo "paciente"
        grupo = Group.objects.get(name='paciente')
        user.groups.add(grupo)

        # Crear persona
        persona = Persona.objects.create(**validated_data)

        # Crear paciente
        Paciente.objects.create(persona=persona, eps=eps)

        return user


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

# ---------------------
# Persona
# ---------------------


class PersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = '__all__'

# ---------------------
# Paciente (incluye datos de persona)
# ---------------------


class PacienteSerializer(serializers.ModelSerializer):
    persona = PersonaSerializer()

    class Meta:
        model = Paciente
        fields = ['id', 'persona', 'eps', 'historial_clinico']

    def create(self, validated_data):
        persona_data = validated_data.pop('persona')
        persona = Persona.objects.create(**persona_data)
        paciente = Paciente.objects.create(persona=persona, **validated_data)
        return paciente

    def update(self, instance, validated_data):
        persona_data = validated_data.pop('persona')
        for attr, value in persona_data.items():
            setattr(instance.persona, attr, value)
        instance.persona.save()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

# ---------------------
# Medicamento
# ---------------------


class MedicamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicamento
        fields = '__all__'

# ---------------------
# Muestra
# ---------------------


class MuestraSerializer(serializers.ModelSerializer):
    paciente = serializers.PrimaryKeyRelatedField(
        queryset=Paciente.objects.all())
    enfermero = UsuarioSerializer(read_only=True)
    medicamento = MedicamentoSerializer(read_only=True)
    medicamento_id = serializers.PrimaryKeyRelatedField(
        source='medicamento', queryset=Medicamento.objects.all(), write_only=True
    )

    class Meta:
        model = Muestra
        fields = [
            'id', 'paciente', 'enfermero', 'medicamento', 'medicamento_id',
            'fecha_toma', 'observaciones', 'enviada_laboratorio'
        ]

    def create(self, validated_data):
        return Muestra.objects.create(**validated_data)

# ---------------------
# Resultado de Laboratorio
# ---------------------


class ResultadoLaboratorioSerializer(serializers.ModelSerializer):
    muestra = serializers.PrimaryKeyRelatedField(
        queryset=Muestra.objects.all())
    laboratorio = UsuarioSerializer(read_only=True)

    class Meta:
        model = ResultadoLaboratorio
        fields = ['id', 'muestra', 'laboratorio',
                  'resultado', 'fecha_resultado']

# ---------------------
# Proceso Medicamento
# ---------------------


class ProcesoMedicamentoSerializer(serializers.ModelSerializer):
    paciente = serializers.PrimaryKeyRelatedField(
        queryset=Paciente.objects.all())
    medicamento = MedicamentoSerializer(read_only=True)
    medicamento_id = serializers.PrimaryKeyRelatedField(
        source='medicamento', queryset=Medicamento.objects.all(), write_only=True
    )
    farmacia = UsuarioSerializer(read_only=True)

    class Meta:
        model = ProcesoMedicamento
        fields = ['id', 'paciente', 'medicamento', 'medicamento_id',
                  'farmacia', 'fecha_entrega', 'dosis', 'observaciones']
